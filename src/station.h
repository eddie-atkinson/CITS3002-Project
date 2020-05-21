#ifndef STATION_H
#define STATION_H
#define _XOPEN_SOURCE_EXTENDED 1
#include <iostream>
#include <string>
#include <map>
#include <vector>
#include <sys/types.h> 
#include <sys/time.h> 
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include "node.h"
#include "util.h"
#define MAX_INT 4294967295 // 2^32 - 1
#define MAX_PACKET_LEN 1024
#define HOST "127.0.0.1"
#define SECONDS_IN_DAY 86400
#endif