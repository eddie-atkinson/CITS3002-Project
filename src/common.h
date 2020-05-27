#ifndef COMMON_H
#define COMMON_H
#include <errno.h>
#include <fstream>
#include <iostream>
#include <list>
#include <map>
#include <sstream>
#include <string>
#include <vector>
using std::cerr;
using std::cout;
using std::endl;
using std::list;
using std::map;
using std::ostringstream;
using std::string;
using std::vector;
#define MAX_INT 4294967295 // 2^32 - 1
#define MAX_PACKET_LEN 1024
#define HOST_IP "127.0.0.1" // localhost
#define SECONDS_IN_DAY (time_t)86400
#endif