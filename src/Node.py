import socket
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

	def __init__(
		self,
		name,
		neighbours,
		tcp_port,
		udp_port
	):
		self.name = name
		self.neighbours = neighbours
		self.udp_port = udp_port
		self.tcp_port = tcp_port
