#include "util.h"

void close_sockets(Node& this_node) {
	std::cout << "Closing sockets" << std::endl;
	close(this_node.tcp_socket);
	close(this_node.udp_socket);
}