/*
Common header file.

Defines global constants, includes libraries of general utility and sets namespaces. 
*/
#ifndef COMMON_H
#define COMMON_H
#include <errno.h>
#include <fstream>
#include <iostream>
#include <list>
#include <map>
#include <sstream>
#include <stdio.h>
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
#define HOST_IP "127.0.0.1"  // localhost
#define KILL_FILE "killfile" // file name for killing servers

// Add some fun terminal printing colours
#define ANSI_COLOR_RED "\x1b[31m"
#define ANSI_COLOR_GREEN "\x1b[32m"
#define ANSI_COLOR_YELLOW "\x1b[33m"
#define ANSI_COLOR_BLUE "\x1b[34m"
#define ANSI_COLOR_MAGENTA "\x1b[35m"
#define ANSI_COLOR_CYAN "\x1b[36m"
#define ANSI_COLOR_RESET "\x1b[0m"
#endif