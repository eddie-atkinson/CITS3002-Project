#ifndef UDP_H
#define UDP_H
#include <iostream>
#include <string>
#include <list>
#include <sstream>
#include <netinet/in.h>
#include "node.h"
#include "frame.h"
#include "frametype.h"
#include "common.h"
void process_udp(Node& this_node, string& transmission, uint16_t port);
void process_request_frame(Node& this_node, Node& in_frame);
void process_response_frame();
#endif


