#!/usr/bin/python3
"""
Author: Eddie Atkinson (22487668)
Date: 06/05/2020

CITS3002 project Python implementation of the required functionality for a
station.

Code conforming to Pylinter and Mypy.
"""
import socket
import sys
import os
import selectors
from typing import Any
from time import time
from Frame import Frame

HOST = "127.0.0.1"
NAME: str
TCP_PORT: int
UDP_PORT: int
NEIGHBOURS: list = []
TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SEQNO = 0


def main() -> None:
    parse_args()
    print(f"Node: {NAME} running with PID {os.getpid()}")
    open_ports()


def open_ports() -> None:
    sel = selectors.DefaultSelector()

    TCP_SOCKET.bind((HOST, TCP_PORT))
    UDP_SOCKET.bind((HOST, UDP_PORT))
    TCP_SOCKET.listen()

    TCP_SOCKET.setblocking(False)
    UDP_SOCKET.setblocking(False)

    sel.register(TCP_SOCKET, selectors.EVENT_READ, None)
    sel.register(UDP_SOCKET, selectors.EVENT_READ, None)

    global SEQNO
    test_frame = Frame(NAME, "East_Station", SEQNO, NAME, int(time()), 1)
    SEQNO += 1
    byte_array = test_frame.to_bytes()

    UDP_SOCKET.sendto(byte_array, (HOST, 3000))

    while True:
        events = sel.select()
        for key, mask in events:
            incoming_socket: Any = key.fileobj
            if key.data is None:
                # Should be a new connection
                if incoming_socket == UDP_SOCKET:
                    print(f"Receiving UDP data {incoming_socket.recv(1024)}")
                else:
                    print("receving TCP connection")
                    accept(incoming_socket, sel)
            else:
                # Existing connection
                service_connection(key, mask, sel)


def accept(sock: socket.socket, sel: selectors.DefaultSelector) -> None:
    conn, addr = sock.accept()
    print(f"Accepting connection from {addr}")
    conn.setblocking(False)
    data: list = []
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


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

    # The rest of the arguments should be our neighbours
    while args:
        NEIGHBOURS.append(int(args.pop(0)))


if __name__ == "__main__":
    main()
