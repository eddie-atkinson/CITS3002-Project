#ifndef JOURNEY_H
#define JOURNEY_H
#include <iostream>
#include <sstream>
#include "node.h"
#include "common.h"

class Journey {
	public:
    string string_rep;
    string destination;
    string departure_time;
    string arrival_time;
    Journey(string& in_str);
    Journey();
    string to_string();
};
#endif


