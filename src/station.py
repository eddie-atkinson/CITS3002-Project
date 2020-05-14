#!/usr/bin/python3
"""
Author: Eddie Atkinson (22487668)
Date: 06/05/2020

CITS3002 project Python implementation of the required functionality for a
station.

Code conforming to Pylinter and Mypy
"""
import socket
import sys
import os
import select
import signal
import time
from typing import Any
from time import sleep
import regex as re
from Frame import Frame
from FrameType import FrameType
from Journey import Journey
from constants import SECONDS_IN_DAY
from constants import MAX_INT
from constants import HOST
from constants import MAX_PACKET_LEN
from Response import Response

# TODO: Take almost all variables out of global scope
NAME: str
TCP_PORT: int
UDP_PORT: int
NEIGHBOURS: dict = {}
TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def main() -> None:
    parse_args()
    print(f"Node: {NAME} running with PID {os.getpid()}")
    open_ports()


def check_timetable(timetables: dict, last_check: int) -> int:
    file_name = f"tt-{NAME}"
    try:
        stat_info = os.stat(file_name)
        if stat_info.st_mtime > last_check:
            last_check = int(time.time())
            # Clear all the old entries
            timetables.clear()

            with open(file_name, "r") as in_file:
                # We are not interested in the header info
                lines = in_file.readlines()[1:]
                for line in lines:
                    line = line.strip("\n")
                    info = line.split(",")
                    journey = Journey(line, info[-1], info[0], info[-2])
                    if journey.destination not in timetables.keys():
                        timetables[journey.destination] = []
                    timetables[journey.destination].append(journey)

        # Just in case the timetables were not in chronological order
        for timetable in timetables.values():
            timetable.sort(key=lambda x: x.departure_time)

    except FileNotFoundError:
        print(f"{file_name} for node {NAME} not found, exiting")
        sys.exit(0)

    return last_check


def open_ports() -> None:
    seqno = 0
    input_sockets = [TCP_SOCKET, UDP_SOCKET]
    timetables: dict = {}
    seqno_table: dict = {}
    outstanding_frames: dict = {}
    response_sockets: dict = {}
    timetable_check = 0
    TCP_SOCKET.bind((HOST, TCP_PORT))
    UDP_SOCKET.bind((HOST, UDP_PORT))

    # Only allow a single client for now
    TCP_SOCKET.listen(1)

    TCP_SOCKET.setblocking(False)
    UDP_SOCKET.setblocking(False)
    # Parse out timetable
    timetable_check = check_timetable(timetables, timetable_check)

    # Sleep so that the other servers can bind their ports
    sleep(5)

    # Introduce ourselves to the neighbours
    for neighbour in NEIGHBOURS.keys():
        name_frame = Frame(
            NAME, "", NAME, -1, -1, FrameType.NAME_FRAME,
        )
        UDP_SOCKET.sendto(name_frame.to_bytes(), (HOST, neighbour))

    # Fetch our timetable
    timetable_check = check_timetable(timetables, timetable_check)
    print("You can make requests now")
    while True:
        # Don't care about writers or errors
        readers = select.select(input_sockets, [], [])[0]
        for reader in readers:
            if reader == UDP_SOCKET:
                frame_bytes = UDP_SOCKET.recvfrom(MAX_PACKET_LEN)
                origin_port = frame_bytes[1][1]
                frame_str = frame_bytes[0].decode("utf-8")
                frame = Frame()
                frame.from_string(frame_str)
                if frame.type == FrameType.NAME_FRAME:
                    NEIGHBOURS[origin_port] = frame.origin

                elif frame.type == FrameType.REQUEST:
                    timetable_check = check_timetable(
                        timetables, timetable_check
                    )
                    process_request_frame(
                        frame, seqno_table, timetables, outstanding_frames,
                    )
                else:
                    process_response(
                        frame,
                        outstanding_frames,
                        response_sockets,
                        input_sockets,
                        timetables,
                    )

                # Update our seqno table
                if (
                    not seen_before(frame.origin, frame.seqno, seqno_table)
                    and frame.type == FrameType.REQUEST
                ):
                    seqno_table[frame.origin] = frame.seqno

            elif reader == TCP_SOCKET:
                conn, addr = TCP_SOCKET.accept()
                print(f"New connection from {addr}")
                conn.setblocking(False)
                input_sockets.append(conn)

            else:
                # Existing TCP sockets
                incoming_bytes = reader.recv(MAX_PACKET_LEN)
                if not incoming_bytes:
                    # Disconnection message
                    print(f"Disconnecting from {reader}")
                    input_sockets.remove(reader)
                else:
                    # They have something to say
                    request_string = incoming_bytes.decode("utf-8")
                    destination = re.search(r"to=\w+", request_string)
                    if not destination:
                        response = (
                            f"HTTP/1.1 400 Bad Request\n"
                            + f"Content-Type: text/html\n"
                            + f"Connection: Closed\n"
                            + f"\n"
                            + f"<html><body>Bad request"
                            + f"</body></html>"
                        ).encode("utf-8")
                        reader.send(response)
                        # Stop listening for socket and close
                        input_sockets.remove(reader)
                        reader.shutdown(socket.SHUT_RD)
                        reader.close()
                        continue

                    destination: str = destination.group(0)
                    destination = destination.split("=")[-1]

                    # Make sure our timetable hasn't changed
                    check_timetable(timetables, timetable_check)
                    request_frame = Frame(
                        NAME, destination, NAME, seqno, -1, FrameType.REQUEST,
                    )
                    seqno_table[NAME] = seqno
                    send_frame_to_neighbours(
                        request_frame, timetables, outstanding_frames
                    )
                    response_sockets[seqno] = reader
                    seqno = (seqno + 1) % MAX_INT


def normalise_time(time_struct: time.struct_time) -> time.struct_time:
    string_rep = f"{time_struct[3]}:{time_struct[4]}"
    return time.strptime(string_rep, "%H:%M")


def process_response(
    frame: Frame,
    outstanding_frames: dict,
    response_sockets: dict,
    input_sockets: list,
    timetables: dict,
) -> None:
    print(
        f"{NAME} Received response frame {frame.to_string()}\nfrom {frame.src}\n"
    )
    try:
        for resp in outstanding_frames[frame.dest]:
            if (
                resp.frame.seqno == frame.seqno
                and resp.frame.origin == frame.dest
            ):
                response = resp

        response.remaining_responses -= 1
        if response.time == -1 and frame.time > -1:
            # If we have found a route, select it
            response.stop = frame.src
            response.time = frame.time

        elif frame.time < response.time and frame.time > 0:
            # We've found a faster route
            response.stop = frame.src
            response.time = frame.time

        if response.remaining_responses == 0:
            # We've received all the responses we expect
            if response.frame.origin == NAME:
                # End of the line send the TCP response
                print("We are at the end of the line friends")

                out_sock = response_sockets[frame.seqno]
                tt = timetables[response.stop]
                next_journey = tt[0]
                current_time = time.localtime(int(time.time()))
                current_time_obj = normalise_time(current_time)
                for journey in tt:
                    if journey.departure_time > current_time_obj:
                        next_journey = journey
                        break

                response = (
                    f"HTTP/1.1 200 OK\n"
                    + f"Content-Type: text/html\n"
                    + f"Connection: Closed\n"
                    + f"\n"
                    + f"<html><body>Arrival time at dest: "
                    + f"{time.strftime('%c', time.localtime(response.time))}"
                    + f"<br>Trip Detail: "
                    + f"{next_journey.string_rep}"
                    + f"</body></html>"
                ).encode("utf-8")
                out_sock.send(response)
                # Stop listening for socket and close
                input_sockets.remove(out_sock)
                out_sock.shutdown(socket.SHUT_RD)
                out_sock.close()

            else:
                # Send UDP response to requesting station
                print(f"{NAME} sending response frame to {frame.dest }")
                response_frame = Frame(
                    frame.origin,
                    frame.dest,
                    NAME,
                    frame.seqno,
                    response.time,
                    frame.type,
                )
                out_port = None
                for port, name in NEIGHBOURS.items():
                    if name == response.frame.src:
                        out_port = port
                        break
                if not out_port:
                    print(
                        f"Received frame from {response.frame.src},"
                        f" not a neighbour, exiting."
                    )
                    sys.exit(0)
                UDP_SOCKET.sendto(response_frame.to_bytes(), (HOST, out_port))

    except KeyError:
        print(f"Received a response for something we haven't forwarded")
        sys.exit(0)


def send_frame_to_neighbours(
    out_frame: Frame, timetables: dict, outstanding_frames: dict
) -> None:
    orig_src = out_frame.src
    sent_frames = 0
    out_frame.src = NAME
    frame_time = out_frame.time

    for port, name in NEIGHBOURS.items():
        if out_frame.src == name or out_frame.origin == name:
            # Don't forward frames to senders
            print(f"{NAME} skipping sending a frame to {name}")
            continue
        try:
            neighbour_tt = timetables[name]
        except KeyError:
            print(
                f"Couldn't find {name} in neighbours,"
                f"skipping sending a frame to them"
            )
            continue

        if out_frame.origin != NAME:
            # This isn't our frame
            start_time = frame_time
        else:
            start_time = int(time.time())

        out_frame.time = calc_arrival_time(neighbour_tt, start_time)
        UDP_SOCKET.sendto(out_frame.to_bytes(), (HOST, port))
        sent_frames += 1

    out_frame.src = orig_src
    if out_frame.origin not in outstanding_frames.keys():
        outstanding_frames[out_frame.origin] = []

    resp = Response(sent_frames, out_frame, -1, "Nowhere")

    if out_frame.origin == NAME:
        outstanding_frames[NAME].append(resp)
    else:
        outstanding_frames[out_frame.origin].append(resp)


def calc_arrival_time(timetable: list, start_time) -> int:
    local_time = time.localtime(start_time)
    time_obj = normalise_time(local_time)
    # In case there isn't another journey till tomorrow
    next_journey = timetable[0]
    for journey in timetable:
        if journey.departure_time > time_obj:
            next_journey = journey
            break
    delta = int(
        time.mktime(next_journey.arrival_time) - time.mktime(time_obj)
    )
    if delta < 0:
        # Next journey is tomorrow
        arrival_time = start_time + (SECONDS_IN_DAY + delta)
    else:
        arrival_time = start_time + delta
    print(f"{NAME} Next journey is {next_journey}, arrival time is calculated to be {time.localtime(arrival_time)}")
    return arrival_time


def seen_before(origin: str, seqno: int, seqno_table: dict) -> bool:
    if origin not in seqno_table.keys():
        return False
    # In case int has rolled over
    elif seqno == 0 and seqno_table[origin] == MAX_INT:
        return False
    elif seqno > seqno_table[origin]:
        return False
    else:
        return True


def process_request_frame(
    in_frame: Frame,
    seqno_table: dict,
    timetables: dict,
    frames_outstanding: dict,
) -> None:
    print(
        f"{NAME} received request frame {in_frame.to_string()}\nfrom {in_frame.src}"
    )
    origin_port = None
    for port, name in NEIGHBOURS.items():
        if name == in_frame.src:
            origin_port = port

    if not origin_port:
        print(f"Couldn't find the port number of neighbour {in_frame.src}")
        sys.exit(0)

    if in_frame.dest == NAME:
        # You've got mail!
        response_frame = Frame(
            NAME,
            in_frame.origin,
            NAME,
            in_frame.seqno,
            in_frame.time,
            FrameType.RESPONSE,
        )
        print(f"{NAME} received request for itself, responding")
        UDP_SOCKET.sendto(response_frame.to_bytes(), (HOST, origin_port))
    elif not seen_before(in_frame.origin, in_frame.seqno, seqno_table):
        # Only forward the frame if we haven't seen it before
        if len(NEIGHBOURS) > 1:
            send_frame_to_neighbours(in_frame, timetables, frames_outstanding)
        else:
            # We have no other neighbours, respond immediately
            response_frame = Frame(
                in_frame.dest,
                in_frame.origin,
                NAME,
                in_frame.seqno,
                -1,
                FrameType.RESPONSE,
            )
            UDP_SOCKET.sendto(response_frame.to_bytes(), (HOST, origin_port))                                                                                                                                            
        seqno_table[in_frame.origin] = in_frame.seqno

    else:
        response_frame = Frame(
            in_frame.dest,
            in_frame.origin,
            NAME,
            in_frame.seqno,
            -1,
            FrameType.RESPONSE,
        )
        print(f"{NAME} dropping frame {in_frame.to_string()}")
        UDP_SOCKET.sendto(response_frame.to_bytes(), (HOST, origin_port))


def parse_args() -> None:
    args = list(sys.argv)
    # Don't really care about the program name
    args.pop(0)
    # Now to the real arguments
    global NAME
    global TCP_PORT
    global UDP_PORT
    global NEIGHBOURS

    NAME = args.pop(0)
    TCP_PORT = int(args.pop(0))
    UDP_PORT = int(args.pop(0))

    # The rest of the arguments should be our neighbours ports
    while args:
        NEIGHBOURS[int(args.pop(0))] = ""


def exit_gracefully(sig, frame) -> None:
    print("Interrupt: closing sockets and exiting gracefully")
    UDP_SOCKET.close()
    TCP_SOCKET.close()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)
    main()
