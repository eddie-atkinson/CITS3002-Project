#ifndef JOURNEY_H
#define JOURNEY_H
#include "common.h"
#include "node.h"
#include "util.h"
#include <iostream>
#include <sstream>
#include <string.h>
#include <time.h>

class Journey {
public:
  string string_rep;
  string destination;
  int departure_time;
  int arrival_time;
  Journey(const string &in_str);
  string to_string() const;
};
#endif
