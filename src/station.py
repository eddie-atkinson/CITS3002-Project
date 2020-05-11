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
from typing import Any
from time import time
from time import sleep
import random
from Frame import Frame
from FrameType import FrameType
from Packet import DisconnectionError
from Journey import Journey


HOST = "127.0.0.1"
# Keep the seqnos bounded to 32 bits for our C friends
MAX_INT = (2 ** 32) - 1
MAX_PACKET_LEN = 1024
NAME: str
TCP_PORT: int
UDP_PORT: int
NEIGHBOURS: dict = {}
TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TIMEOUT_IN_SECS = 5
MAX_FAILURES = 15


def main() -> None:
    parse_args()
    print(f"Node: {NAME} running with PID {os.getpid()}")
    open_ports()


def check_timetable(timetables: dict, last_check: int) -> int:
    file_name = f"tt-{NAME}"
    try:
        stat_info = os.stat(file_name)
        if stat_info.st_mtime > last_check:
            last_check = int(time())
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
    
    except FileNotFoundError:
        print(f"{file_name} for node {NAME} not found, exiting")
        sys.exit(0)

    return last_check


def open_ports() -> None:
    seqno = 0
    input_sockets = [TCP_SOCKET, UDP_SOCKET]
    output_sockets = [TCP_SOCKET, UDP_SOCKET]
    sending_queue = {}
    sending_queue[TCP_SOCKET] = []
    sending_queue[UDP_SOCKET] = []
    timetables = {}
    last_timetable_check = 0
    TCP_SOCKET.bind((HOST, TCP_PORT))
    UDP_SOCKET.bind((HOST, UDP_PORT))

    # Only allow a single client for now
    TCP_SOCKET.listen(1)

    TCP_SOCKET.setblocking(False)
    UDP_SOCKET.setblocking(False)
    # Parse out timetable
    last_timetable_check = check_timetable(timetables, last_timetable_check)

    # Sleep so that the other servers can bind their ports
    sleep(2)

    # Introduce ourselves to the neighbours
    for neighbour in NEIGHBOURS.keys():
        name_frame = Frame(NAME, "", seqno, NAME, int(time()),
                           FrameType.NAME_FRAME)
        sending_queue[UDP_SOCKET].append((name_frame.to_bytes(), neighbour))
        seqno = (seqno + 1) % MAX_INT

    while True:
        readers, writers, errors = select.select(input_sockets,
                                                 output_sockets, input_sockets)
        for reader in readers:
            if reader == UDP_SOCKET:
                frame = UDP_SOCKET.recvfrom(MAX_PACKET_LEN)
                process_udp(sending_queue, frame)

            elif reader == TCP_SOCKET:
                conn, addr = TCP_SOCKET.accept()
                print(f"New connection from {addr}")
                conn.setblocking(False)
                sending_queue[conn] = []
                input_sockets.append(conn)
                output_sockets.append(conn)

            else:
                # Existing TCP sockets
                incoming_bytes = reader.recv(MAX_PACKET_LEN)
                if not incoming_bytes:
                    # Disconnection message
                    print(f"Disconnecting from {reader}")
                    if reader in output_sockets:
                        output_sockets.remove(reader)
                    input_sockets.remove(reader)
                else:
                    # They have something to say
                    request_string = incoming_bytes.decode("utf-8")
                    print(request_string)

        for writer in writers:
            if sending_queue[writer]:
                out_tup = sending_queue[writer].pop(0)
                if writer != UDP_SOCKET:
                    # If its a TCP Socket use send
                    writer.send(out_tup[0])
                else:
                    # It's UDP
                    writer.sendto(out_tup[0], (HOST, out_tup[1]))

        for error in errors:
            # Something has gone wrong, kill the socket
            input_sockets.remove(error)
            if error in output_sockets:
                output_sockets.remove(error)
            error.close()
            del sending_queue[error]


def process_udp(sending_queue: dict, frame_bytes: bytes) -> None:

    # Read 4 byte header giving frame length
    origin_port = frame_bytes[1][1]
    frame_str: str = frame_bytes[0].decode("utf-8")
    incoming_frame = Frame()
    incoming_frame.from_string(frame_str)

    if incoming_frame.type == FrameType.NAME_FRAME:
        NEIGHBOURS[origin_port] = incoming_frame.origin
        


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
