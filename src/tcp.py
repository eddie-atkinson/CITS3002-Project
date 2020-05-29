"""Module responsible for handling TCP communication for a node.

Parses TCP requests provided by the browser and either initiates a request to a
node's neighbours or closes the TCP connection if an invalid request is made
"""
import socket
import re
from Node import Node
from FrameType import FrameType
from util import http_string
from Frame import Frame
from constants import MAX_INT
from udp import send_frame_to_neighbours
from timetable import check_timetable


def process_tcp(this_node: Node, transmission: bytes, sock: socket.socket) -> None:
    """Parses TCP requests sent by the browser.

    Uses regex to search for destination information and sends a request to a node's neighbours
    or closes the connection to the browser if the request is invalid.

    Arguments:
        this_node: instance of the node class representing a given node in the network.
        transmission: byte array containing the TCP packet
        sock: socket object representing the socket the TCP packet originated from
    Returns:
        None
    """
    transmission_str = transmission.decode("utf-8")
    destination = re.search(r"to=\w+", transmission_str)
    if not destination:
        response = http_string(400, "Bad Request", ["Ouch! Bad request"])
        sock.send(response.encode("utf-8"))
        this_node.input_sockets.remove(sock)
        sock.shutdown(socket.SHUT_RD)
        sock.close()
    else:

        destination = destination.group(0).split("=")[-1]
        request_frame = Frame(
            origin=this_node.name,
            dest=destination,
            src=[],
            seqno=this_node.seqno,
            time=-1,
            type=FrameType.REQUEST,
        )
        this_node.response_sockets[this_node.seqno] = sock
        this_node.seqno = (this_node.seqno + 1) % MAX_INT
        check_timetable(this_node)
        send_frame_to_neighbours(this_node, request_frame)
