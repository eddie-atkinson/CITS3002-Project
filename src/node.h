// Include guard
#ifndef NODE_H
#define NODE_H
#include <iostream>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>
#include "common.h"
#include "journey.h"
#include "util.h"

class Node {
	public:
		std::string name;
		uint16_t udp_port;
		uint16_t tcp_port;
		std::map<uint16_t, std::string> neighbours;
		int udp_socket;
		int tcp_socket;
		std::map<int, int> response_sockets;
		std::vector<int> outstanding_frames; // TODO: change to Response objects when implemented
		int seqno;
		std::vector<int> input_sockets;
		std::map<std::string, std::vector<class Journey>> timetables;
		time_t last_timetable_check; 
		Node(void);
		void check_timetable(void);
		void quit(int status);
};
#endif