import socket
import sys
import os
from constants import ANSI_COLOR_RESET
from constants import ANSI_COLOR_RED
from constants import ANSI_COLOR_GREEN
from constants import KILL_FILE


class Node:
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

    def __init__(self, name, neighbours, tcp_port, udp_port):
        self.name = name
        self.neighbours = neighbours
        self.udp_port = udp_port
        self.tcp_port = tcp_port

    def check_kill(self):
        for entry in os.listdir():
            if entry == "killfile":
                self.quit(0)

    def quit(self, status):
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
            for sock in self.input_sockets:
                sock.close()
        sys.exit(status)
