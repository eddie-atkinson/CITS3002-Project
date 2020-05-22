#ifndef UDP_H
#define UDP_H
#include <iostream>
#include <string>
#include <list>
#include <sstream>
#include "node.h"
#include "frame.h"
#include "frametype.h"
using std::string;
using std::endl;
using std::list;
using std::cout;
void handle_udp(Node& this_node, std::string& transmission, uint16_t port);
#endif


