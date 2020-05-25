#ifndef JOURNEY_H
#define JOURNEY_H
#include <iostream>
#include <sstream>
#include <locale>
#include <string.h>
#include "node.h"
#include "util.h"
#include "common.h"

class Journey {
	public:
    string string_rep;
    string destination;
    int departure_time;
    int arrival_time;
    Journey(const string& in_str);
    string to_string() const;
};
#endif


