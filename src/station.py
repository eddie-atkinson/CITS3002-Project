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
from constants import MAX_INT
from constants import HOST
from constants import MAX_PACKET_LEN
from Response import Response
from udp import process_udp
from tcp import process_tcp
from Node import Node


def main() -> None:
    this_node = parse_args()
    print(f"Node: {this_node.name} running with PID {os.getpid()}")
    init_ports(this_node)
    send_name_frames(this_node)
    listen_on_ports(this_node)


def init_ports(this_node: Node) -> None:

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST, this_node.tcp_port))
    tcp_socket.listen(5)
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
        readers = select.select(this_node.input_sockets, [], [], 5.0)[0]
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
    print("Interrupt: exiting gracefully")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)
    main()
