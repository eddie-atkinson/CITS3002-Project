#ifndef UDP_H
#define UDP_H
#include <iostream>
#include <string>
#include <list>
#include <sstream>
#include <unordered_set>
#include "node.h"
#include "frame.h"
#include "frametype.h"
#include "common.h"
void process_udp(Node& this_node, std::string& transmission, uint16_t port);
void process_request_frame();
void process_response_frame();
void send_frame_to_neighbours(Node& this_node, Frame& out_frame);
#endif


