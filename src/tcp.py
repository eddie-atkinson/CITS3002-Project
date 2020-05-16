import socket
import re
from Node import Node
from FrameType import FrameType
from util import http_string
from Frame import Frame
from constants import MAX_INT
from udp import send_frame_to_neighbours
from timetable import check_timetable
from time import sleep


def process_tcp(
	this_node: Node,
	transmission: bytes,
	sock: socket.socket
) -> None:
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
			type=FrameType.REQUEST
		)
		this_node.response_sockets[this_node.seqno] = sock
		this_node.seqno = (this_node.seqno +1) % MAX_INT
		check_timetable(this_node)
		send_frame_to_neighbours(this_node, request_frame)


