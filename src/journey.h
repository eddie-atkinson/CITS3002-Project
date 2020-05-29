#ifndef JOURNEY_H
#define JOURNEY_H
#include "common.h"
#include "node.h"
#include "util.h"
#include <iostream>
#include <string.h>
#include <time.h>

/*
Class for storing information about individual journeys in timetables

Attributes:
  string_rep: string representation of the journey as it appeared in the timetable file
  destination: name of the destination node of the journey
  departure_time: the departure time of the journey in minutes after midnight
  arrival_time: the arrival time at the destination in minutes after midnight
*/
class Journey {
public:
  string string_rep;
  string destination;
  int departure_time;
  int arrival_time;
  // Constructor
  Journey(const string &in_str);
  // Public method
  string to_string() const;
};
#endif
