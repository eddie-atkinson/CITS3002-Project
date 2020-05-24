#ifndef COMMON_H
#define COMMON_H
#include <iostream>
#include <string>
#include <list>
#include <vector>
#include <map>
#include <fstream>
using std::string;
using std::map;
using std::vector;
using std::endl;
using std::list;
using std::cout;
#define MAX_INT 4294967295 // 2^32 - 1
#define MAX_PACKET_LEN 1024
#define HOST 0 // 0 works for localhost in C sockets (at least in my implementation it does)
#define SECONDS_IN_DAY 86400
#endif