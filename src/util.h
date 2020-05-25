#ifndef UTIL_H
#define UTIL_H
#include <sstream>
#include <time.h>
#include <string.h>
#include "journey.h"
#include "common.h"
list<string> split(const string& s, char delimiter);
string http_string(
	int response_code,
	string response_msg,
	list<string> messages
);
class Journey& find_next_trip(list<class Journey>& timetable, int start_time);
#endif