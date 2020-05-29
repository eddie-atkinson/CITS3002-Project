"""Module containing a class to store the essential information
and data structures for a node in the network.
"""
import socket
import sys
import os
from constants import ANSI_COLOR_RESET
from constants import ANSI_COLOR_RED
from constants import ANSI_COLOR_GREEN
from constants import KILL_FILE


class Node:
    """Class representing nodes within a network.

    Contains all the data structures and information essential for a node to function.

    Attributes:
        name: the node's name as string
        udp_port: the UDP port the node uses for communication with other nodes
        tcp_port: the TCP port the node uses for communication with the browser
        neighbours: a dictionary containing a node's neighbours UDP ports mapped
        to their names
        udp_socket: socket object representing the UDP socket used by the node
        tcp_socket: socket object representing the TCP socket used by the node
        response_sockets: dictionary frame sequence numbers to sockets to respond to
        outstanding_frames: a list of Response objects for frames that require a response
        seqno: the current sequence number
        timetables: a dictionary of neighbour node names to a list of Journey objects
        input_sockets: a list of socket objects that are listened on
        last_timetable_check: the last time the node's timetable file was parsed
        packet_count: count of the number of packets forwarded by a node
    """

    name: str = ""
    udp_port: int = -1
    tcp_port: int = -1
    neighbours: dict = {}
    udp_socket: socket.socket
    tcp_socket: socket.socket
    response_sockets: dict = {}
    outstanding_frames: list = []
    seqno: int = 0
    timetables: dict = {}
    input_sockets: list = []
    last_timetable_check = -1
    packet_count: int = 0

    def __init__(self, name, neighbours, tcp_port, udp_port):
        """Initialises instance
        """
        self.name = name
        self.neighbours = neighbours
        self.udp_port = udp_port
        self.tcp_port = tcp_port

    def check_kill(self):
        """Checks for presence of killfile in directory indicating network failure
        """
        for entry in os.listdir():
            if entry == "killfile":
                self.quit(0)

    def quit(self, status):
        """Method to exit gracefully when an error state is detected for this node
        or one of the other nodes in the network, prints useful packet count on exit.
        """
        fd = open(KILL_FILE, "w")
        fd.close()
        if status == 1:
            print(
                f"{ANSI_COLOR_RED} {self.name} quitting in error state {ANSI_COLOR_RESET}",
                file=sys.stderr,
            )
        else:
            print(
                f"{ANSI_COLOR_GREEN} {self.name} exiting gracefully {ANSI_COLOR_RESET}",
                file=sys.stderr,
            )
            print(f"{self.name} forwarded {self.packet_count} packets")
            for sock in self.input_sockets:
                sock.close()
        sys.exit(status)
