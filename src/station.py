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
from typing import Tuple
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
from udp import process_udp
from tcp import process_tcp
from Node import Node

# TODO: Take almost all variables out of global scope
# NAME: str
# TCP_PORT: int
# UDP_PORT: int
# NEIGHBOURS: dict = {}
TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def main() -> None:
    this_node = parse_args()
    print(f"Node: {this_node.name} running with PID {os.getpid()}")
    init_ports(this_node)
    send_name_frames(this_node)
    listen_on_ports(this_node)
    # open_ports()


def init_ports(this_node: Node) -> None:

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST, this_node.tcp_port))
    # Restrict ourselves to a single client for now
    tcp_socket.listen(1)
    tcp_socket.setblocking(False)

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, this_node.udp_port))
    udp_socket.setblocking(False)

    # Wait for everyone else to bind their ports
    sleep(5)

    this_node.tcp_socket = tcp_socket
    this_node.udp_socket = udp_socket
    print("You can send frames now")



def send_name_frames(this_node: Node) -> None:
    name_frame = Frame(
        this_node.name,
        "",
        [this_node.name],
        -1,
        -1,
        FrameType.NAME_FRAME
    )
    for port in this_node.neighbours.keys():
        this_node.udp_socket.sendto(name_frame.to_bytes(), (HOST, port))


def listen_on_ports(this_node: Node) -> None:

    this_node.input_sockets = [this_node.tcp_socket, this_node.udp_socket]
    while True:
        readers = select.select(this_node.input_sockets, [], [])[0]
        for reader in readers:
            if reader is this_node.udp_socket:
                # Do something
                transmission = reader.recvfrom(MAX_PACKET_LEN)
                process_udp(this_node, transmission)
            elif reader is this_node.tcp_socket:
                #  We have a new tcp connection
                conn, addr = reader.accept()
                print(f"New connection from {addr}")
                conn.setblocking(False)
                this_node.input_sockets.append(conn)
            else:
                transmission = reader.recv(MAX_PACKET_LEN)
                if not transmission:
                    # Disconnection
                    print(f"{reader} has disconnected")
                    this_node.input_sockets.remove(reader)
                    reader.shutdown(socket.SHUT_RD)
                    reader.close()
                else:
                    process_tcp(this_node, transmission, reader)



def open_ports() -> None:
    seqno = 0
    input_sockets = [TCP_SOCKET, UDP_SOCKET]
    timetables: dict = {}
    outstanding_frames = []
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
        name_frame = Frame(NAME, "", [], -1, -1, FrameType.NAME_FRAME,)
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
                        frame, timetables, outstanding_frames,
                    )
                else:
                    process_response(
                        frame,
                        outstanding_frames,
                        response_sockets,
                        input_sockets,
                        timetables
                    )

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
                        NAME, destination, [], seqno, -1, FrameType.REQUEST,
                    )
                    send_frame_to_neighbours(
                        request_frame, timetables, outstanding_frames
                    )
                    response_sockets[seqno] = reader
                    seqno = (seqno + 1) % MAX_INT


# def list_equals(lst1: list, lst2: list) -> bool:
#     if len(lst1) != len(lst2):
#         return False
#     for i in range(len(lst1)):
#         if lst1[i] != lst2[i]:
#             return False
#     return True


def parse_args() -> Node:
    args = list(sys.argv)
    # Don't really care about the program name
    args.pop(0)

    name = args.pop(0)
    tcp_port = int(args.pop(0))
    udp_port = int(args.pop(0))

    neighbours = {}
    # The rest of the arguments should be our neighbours ports
    while args:
        neighbours[int(args.pop(0))] = ""

    this_node = Node(
        name,
        neighbours,
        tcp_port,
        udp_port
    )
    return this_node

def exit_gracefully(sig, frame) -> None:
    print("Interrupt: closing sockets and exiting gracefully")
    UDP_SOCKET.close()
    TCP_SOCKET.close()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)
    main()
