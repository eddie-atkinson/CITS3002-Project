#ifndef TCP_H
#define TCP_H
#include "common.h"
#include "frame.h"
#include "frametype.h"
#include "node.h"
#include "udp.h"
#include <iostream>
#include <regex>
void handle_tcp(Node& this_node, string& message, int socket);
#endif
