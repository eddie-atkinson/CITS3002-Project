#ifndef JOURNEY_H
#define JOURNEY_H
#include <iostream>
#include <string>
#include <list>
#include <sstream>
#include "node.h"
// #include "timetable.h"
using std::string;
using std::endl;
using std::list;
using std::cout;
using std::ostringstream;
class Journey {
	public:
    string string_rep;
    string destination;
    string departure_time;
    string arrival_time;
    Journey(string& in_str);
    string to_string();
};
#endif


