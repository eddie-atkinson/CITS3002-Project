#ifndef UDP_H
#define UDP_H
#include "common.h"
#include "frame.h"
#include "frametype.h"
#include "node.h"
#include "response.h"
#include <algorithm>
#include <iostream>
#include <list>
#include <netinet/in.h>
#include <string>
#include <unordered_set>
void process_udp(Node& this_node, string& transmission, uint16_t port);
void process_request_frame(Node& this_node, Node& in_frame);
void process_response_frame();
void send_frame_to_neighbours(Node& this_node, Frame& out_frame);
#endif
