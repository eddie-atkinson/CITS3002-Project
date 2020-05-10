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
from Frame import Frame
from FrameType import FrameType
from Packet import Packet
from Packet import DisconnectionError
import random


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


def check_lost_frames(ack_queue: list, sending_queue: dict) -> None:
    if ack_queue:
        packet = ack_queue[0]
        frame_time = packet.time
        current_time = int(time())
        time_delta = current_time - frame_time
        while time_delta > TIMEOUT_IN_SECS:
            # Calculate backoff time for repeated packet or send if new packet
            ack_queue.pop(0)
            packet.time = int(time())
            if packet.failures <= MAX_FAILURES:
                packet.failures += 1
            else:
                raise DisconnectionError("Packet dropped 15 times")
            backoff_time = (random.randrange(0, packet.failures)
                            * TIMEOUT_IN_SECS)
            if backoff_time > 0:
                packet.time = int(time()) + backoff_time
                ack_queue.append(packet)
            else:
                sending_queue[UDP_SOCKET].append(packet)
            if ack_queue:
                # Check the remaining frames
                packet = ack_queue[0]
                frame_time = packet.time
                time_delta = current_time - frame_time
            else:
                # There are no more frames
                break


def open_ports() -> None:
    seqno = 0
    input_sockets = [TCP_SOCKET, UDP_SOCKET]
    output_sockets = [TCP_SOCKET, UDP_SOCKET]
    ack_queue = []
    sending_queue = {}
    sending_queue[TCP_SOCKET] = []
    sending_queue[UDP_SOCKET] = []
    TCP_SOCKET.bind((HOST, TCP_PORT))
    UDP_SOCKET.bind((HOST, UDP_PORT))

    # Only allow a single client for now
    TCP_SOCKET.listen(1)

    TCP_SOCKET.setblocking(False)
    UDP_SOCKET.setblocking(False)

    # Introduce ourselves to the neighbours
    for neighbour in NEIGHBOURS.keys():
        name_frame = Frame(NAME, "", seqno, NAME, int(time()),
                           FrameType.NAME_FRAME)
        sending_packet = Packet(name_frame.to_bytes(), neighbour,
                                int(time()), 0, FrameType.NAME_FRAME)
        sending_queue[UDP_SOCKET].append(sending_packet)
        seqno = (seqno + 1) % MAX_INT

    while True:
        # Check for lost frames
        check_lost_frames(ack_queue, sending_queue)

        readers, writers, errors = select.select(input_sockets,
                                                 output_sockets, input_sockets)
        for reader in readers:
            if reader == UDP_SOCKET:
                frame = UDP_SOCKET.recvfrom(MAX_PACKET_LEN)
                process_udp(sending_queue, ack_queue, frame)

            elif reader == TCP_SOCKET:
                conn, addr = TCP_SOCKET.accept()
                print(f"New connection from {addr}")
                conn.setblocking(False)
                sending_queue[conn] = []
                input_sockets.append(conn)
                output_sockets.append(conn)

            else:
                # Existing TCP sockets
                incoming_bytes = reader.recv(1024)
                if not incoming_bytes:
                    # Disconnection message
                    print(f"Disconnecting from {reader}")
                    if reader in output_sockets:
                        output_sockets.remove(reader)
                    input_sockets.remove(reader)
                else:
                    # They have something to say
                    print(incoming_bytes.decode("utf-8"))

        for writer in writers:
            if sending_queue[writer]:
                packet = sending_queue[writer].pop(0)
                if writer != UDP_SOCKET:
                    # If its a TCP Socket use send
                    writer.send(packet.frame_bytes)
                else:
                    # It's UDP
                    packet.time = int(time())
                    if (packet.type != FrameType.ACK
                            and packet.type != FrameType.NACK):
                        ack_queue.append(packet)
                    writer.sendto(packet.frame_bytes, (HOST, packet.port))

        for error in errors:
            # Something has gone wrong, kill the socket
            input_sockets.remove(error)
            if error in output_sockets:
                output_sockets.remove(error)
            error.close()
            del sending_queue[error]


def process_udp(sending_queue: dict, ack_queue: list,
                frame_bytes: bytes) -> None:

    # Read 4 byte header giving frame length
    origin_port = frame_bytes[1][1]
    frame_str: str = frame_bytes[0].decode("utf-8")
    incoming_frame = Frame()
    incoming_frame.from_string(frame_str)

    if incoming_frame.type == FrameType.NAME_FRAME:
        NEIGHBOURS[origin_port] = incoming_frame.origin
        ack = Frame(incoming_frame.origin, incoming_frame.origin,
                    incoming_frame.seqno, NAME, -1, FrameType.ACK)
        packet = Packet(ack.to_bytes(), origin_port, -1, 0, FrameType.ACK)
        sending_queue[UDP_SOCKET].append(packet)

    elif incoming_frame.type == FrameType.ACK:
        for i in range(len(ack_queue)):
            frame_str = ack_queue[i].frame_bytes.decode("utf-8")
            frame = Frame()
            frame.from_string(frame_str)
            if (frame.seqno == incoming_frame.seqno
               and incoming_frame.origin == NAME):
                ack_queue.pop(i)
                break


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
