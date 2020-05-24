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
void normalise_tm_struct(struct tm* time);
time_t calc_arrival_time(list<class Journey>& timetable, time_t start_time);
Journey find_next_trip(list<class Journey>& timetable, struct tm* local_time);
#endif