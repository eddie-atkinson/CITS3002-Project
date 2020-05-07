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
import types

HOST = "127.0.0.1"

def main() -> None:
    node_info = parse_args()
    meet_the_neighbours()
    print(f"Node: {node_info['name']} running with PID {os.getpid()}")
    open_ports(node_info)


def open_ports(node_info: dict) -> None:
    sel = selectors.DefaultSelector()
    tcp_host_port = (
        HOST,
        node_info["tcp"]
    )

    udp_host_port = (
        HOST,
        node_info["udp"]
    )

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    tcp_socket.bind(tcp_host_port)
    udp_socket.bind(udp_host_port)
    tcp_socket.listen()
    tcp_socket.setblocking(False)
    udp_socket.setblocking(False)

    sel.register(tcp_socket, selectors.EVENT_READ, None)
    sel.register(udp_socket, selectors.EVENT_READ, None)

    while True:
        events = sel.select()
        for key, mask in events:
            if key.data is None:
                # Should be a new connection
                print(key.fileobj.type)
                print(socket.SOCK_DGRAM)
                print(socket.SOCK_STREAM)
                if key.fileobj == udp_socket:
                    print(f"Receiving UDP data {key.fileobj.recv(1024)}")
                else:
                    print("receving TCP connection")
                    accept(key.fileobj, sel)
            else:
                # Existing connection 
                # service_connection(key, mask)
                1+1


def accept(sock: socket.socket, sel: selectors.DefaultSelector) -> None:
    conn, addr = sock.accept()
    print(f"Accepting connection from {addr}")
    conn.setblocking(False)
    data: list = []
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


# def service_connection(key: selectors.SelectorKey, mask: int) -> None:
#     sock = key.fileobj
#     data = key.data
#     if mask & selectors.EVENT_READ:
#         recv_data = sock.recv(1024)
#         if recv_data:
#             if sock.SOCK_STREAM:
#                 print("Received data over TCP, data :" + recv_data)
#             else:
#                 print("Received data over UDP, data :" + recv_data)
#         else:
#             print("Closing socket")
#             sel.unregister(sock)
#             sock.close()
#     if mask & selectors.EVENT_WRITE:
#         print("Sending data")
#         sock.send("Hello, World")


def meet_the_neighbours() -> None:
    return None

def parse_args() -> dict:
    node_info: dict = {}  
    args = list(sys.argv)
    # Don't really care about the program name
    args.pop(0)
    # Now to the real arguments
    node_info["name"] = args.pop(0)
    node_info["tcp"] = int(args.pop(0))
    node_info["udp"] = int(args.pop(0))
    node_info["neighbours"] = []

    # The rest of the arguments should be our neighbours
    while(args):
        node_info["neighbours"].append(int(args.pop(0)))    
    return(node_info)

if __name__ == "__main__":
    main()
    