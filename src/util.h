#ifndef UTIL_H
#define UTIL_H
#include <sstream>
#include <time.h>
#include <string.h>
#include "common.h"
list<string> split(const string& s, char delimiter);
string http_string(
	int response_code,
	string response_msg,
	list<string> messages
);
struct tm* normalise_time();
#endif