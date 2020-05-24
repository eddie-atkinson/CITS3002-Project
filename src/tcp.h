#ifndef TCP_H
#define TCP_H
#include <iostream>
#include <regex>
#include "common.h"
#include "node.h"
#include "frametype.h"
#include "frame.h"
#include "udp.h"
void handle_tcp(Node& this_node, string& message, int socket);
#endif




