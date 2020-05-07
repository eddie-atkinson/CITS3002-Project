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

HOST = "127.0.0.1"

def main() -> None:
    node_info = parse_args()
    meet_the_neighbours()
    print(f"Node: {node_info['name']} running with PID {os.getpid()}")
    open_ports(node_info)


def open_ports(node_info: dict) -> None:
    host_port_tup = (
        HOST,
        node_info["tcp"]
    )
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(host_port_tup)
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"connected by {addr}")
            while True:
                data = conn.recv(1024)
                print(data)
                if not data:
                    break
                conn.sendall(data)  


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
    