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
import selectors
import signal
from typing import Any
from time import time
from Frame import Frame
from FrameType import FrameType


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


def main() -> None:
    parse_args()
    print(f"Node: {NAME} running with PID {os.getpid()}")
    open_ports()


def open_ports() -> None:
    sel = selectors.DefaultSelector()
    seqno = 0
    TCP_SOCKET.bind((HOST, TCP_PORT))
    UDP_SOCKET.bind((HOST, UDP_PORT))
    TCP_SOCKET.listen()

    TCP_SOCKET.setblocking(False)
    # UDP_SOCKET.setblocking(False)

    sel.register(TCP_SOCKET, selectors.EVENT_READ, None)
    sel.register(UDP_SOCKET, selectors.EVENT_READ, None)

    # Introduce ourselves to the neighbours
    send_name_frame(seqno)
    seqno = (seqno + 1) % MAX_INT

    while True:
        events = sel.select()
        for key, mask in events:
            incoming_socket: Any = key.fileobj
            if key.data is None:
                # Should be a new connection
                if incoming_socket == UDP_SOCKET:
                    process_udp()
                else:
                    print("receving TCP connection")
                    accept(incoming_socket, sel)
            else:
                # Existing connection
                service_connection(key, mask, sel)


def process_udp() -> None:
    # Read 4 byte header giving frame length
    frame = UDP_SOCKET.recvfrom(MAX_PACKET_LEN)
    origin_port = frame[1][1]
    frame_str: str = frame[0].decode("utf-8")
    incoming_frame = Frame()
    incoming_frame.from_string(frame_str)
    if incoming_frame.type == FrameType.NAME_FRAME:
        NEIGHBOURS[origin_port] = incoming_frame.origin


def send_name_frame(seqno: int) -> None:
    name_frame = Frame(NAME, "", seqno, NAME, int(time()),
                       FrameType.NAME_FRAME)
    send_bytes = name_frame.to_bytes()
    for neighbour in NEIGHBOURS.keys():
        UDP_SOCKET.sendto(send_bytes, ((HOST, neighbour)))


def accept(sock: socket.socket, sel: selectors.DefaultSelector) -> None:
    conn, addr = sock.accept()
    print(f"Accepting connection from {addr}")
    conn.setblocking(False)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events)


def service_connection(key: selectors.SelectorKey, mask: int,
                       sel: selectors.DefaultSelector) -> None:
    sock: Any = key.fileobj
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print("Received data over TCP, data :" + str(recv_data))
            sock.send(b"HTTP/1.0 200 OK\n")
            sock.send(b"Content-Type: text/html\n")
            sock.send(b"\n")
            sock.send(b"""
                <html>
                    <body>
                    <h1> Hello World</h1>
                    </body>
                </html>
            """)
        else:
            print("Closing socket")
            sel.unregister(sock)
            sock.close()


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
