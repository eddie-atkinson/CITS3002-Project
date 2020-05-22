// Include guard
#ifndef NODE_H
#define NODE_H
#include <iostream>
#include <string> 
#include <map>
#include <vector>

class Node {
	public:
		std::string name;
		int udp_port;
		int tcp_port;
		std::map<int, std::string> neighbours;
		int udp_socket;
		int tcp_socket;
		std::map<int, int> response_sockets;
		std::vector<int> outstanding_frames; // TODO: change to Response objects when implemented
		int seqno;
		std::vector<int> input_sockets;
		int last_timetable_check; 
		Node();
};
#endif