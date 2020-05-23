#include "node.h"

Node::Node() {}

void Node::quit(int status) {
	std::cout << "Closing sockets and getting out of here" << std::endl;
	close(tcp_socket);
	close(udp_socket);
	exit(status);
}