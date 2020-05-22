#include "tcp.h"

void handle_tcp(Node& this_node, std::string message, int socket) {
	std::cout << "Received UDP tranmission " << message << std::endl;
}