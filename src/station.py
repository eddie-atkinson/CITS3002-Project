#!/usr/bin/env python3

"""Implementation of the Python server for the CITS3002 project.

Author: Eddie Atkinson (22487668)
Date: 06/05/2020

This module contains the main function for the program and is responsible for parsing the
command line arguments passed to it, initialising a node object,
opening the appropriate TCP and UDP ports, sending name frames to its
neighbours, and finally entering the select loop that is used to process
requests

Typical usage example:
./station.py <station-name> <tcp-port> <udp-port> <neighbour-1-udp-port> ...

Code linted using mypy
"""
import socket
import sys
import os
import select
from time import sleep
from Frame import Frame
from FrameType import FrameType
from constants import HOST
from constants import MAX_PACKET_LEN
from udp import process_udp
from tcp import process_tcp
from Node import Node


def main() -> None:
    """Starting point for the program

    Parses the command line args, initialises a node object representing this station,
    sends name frames to neighbours and then enters the select loop
    """
    this_node = parse_args()
    print(f"Node: {this_node.name} running with PID {os.getpid()}")
    try:
        init_ports(this_node)
        this_node.check_kill()
        send_name_frames(this_node)
        listen_on_ports(this_node)
    except OSError:
        print("Address most likely in use")
        this_node.quit(1)


def init_ports(this_node: Node) -> None:
    """Initialises the UDP and TCP ports for an node.

    Args:
        this_node: An instance of the node class representing a given node in the network.

    Returns:
        None
    """
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
    """Constructs a frame containing a node's name and send it to its neighbours.

    Args:
        this_node: An instance of the node class representing a given node in the network.
    Returns:
        None
    """
    name_frame = Frame(this_node.name, "", [this_node.name], -1, -1, FrameType.NAME_FRAME)
    for port in this_node.neighbours.keys():
        this_node.udp_socket.sendto(name_frame.to_bytes(), (HOST, port))


def listen_on_ports(this_node: Node) -> None:
    """Starts the node's select loop, handling both UDP and TCP packets.

    Args:
        this_node: An instance of the node class representing a given node in the network.
    Returns:
        None
    """
    this_node.input_sockets = [this_node.tcp_socket, this_node.udp_socket]
    while True:
        this_node.check_kill()
        readers = select.select(this_node.input_sockets, [], [], 10.0)[0]
        for reader in readers:
            if reader is this_node.udp_socket:
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
    """Parses the arguments passed to the program and returns an initialised node object.

    Args:
        None
    Returns:
        An instance of the Node class containing a node's name, TCP port, UDP port,
        and the UDP ports of its neighbours.
    """
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

    this_node = Node(name, neighbours, tcp_port, udp_port)
    return this_node


if __name__ == "__main__":
    main()
