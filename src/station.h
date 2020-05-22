#ifndef STATION_H
#define STATION_H
#define _XOPEN_SOURCE_EXTENDED 1
#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <list>
#include <sys/types.h> 
#include <sys/time.h> 
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include "udp.h"
#include "tcp.h"
#include "node.h"
#include "util.h"
#include "frame.h"
#include "frametype.h"
#define MAX_INT 4294967295 // 2^32 - 1
#define MAX_PACKET_LEN 1024
#define HOST 0 // 0 works for localhost in C sockets (at least in my implementation it does)
#define SECONDS_IN_DAY 86400
using std::cout;
using std::endl;
using std::vector;
using std::string;
using std::list;
#endif