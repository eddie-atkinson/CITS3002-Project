/*
Implementation of the Journey class
*/
#include "journey.h"

/*
Constructor for the Journey class.

Ingests a line from a timetable to initialise a Journey object. Splits the line
into a list of strings delimited by commas and then parses the string representations
of the arrival and departure times into minutes after midnight. 

*/
Journey::Journey(const string &in_str) : string_rep(in_str) {
  string temp_str = string_rep;
  list<string> tokens = split(temp_str, ',');
  int minutes = -1;
  int hours = -1;
  size_t pos = -1;
  pos = tokens.front().find(":");
  hours = atoi(tokens.front().substr(0, pos).c_str());
  minutes = atoi(tokens.front().substr(pos + 1).c_str());
  departure_time = (hours * 60) + minutes;
  tokens.pop_front();
  // Don't care about bus or stop name
  tokens.pop_front();
  tokens.pop_front();

  pos = tokens.front().find(":");
  hours = atoi(tokens.front().substr(0, pos).c_str());
  minutes = atoi(tokens.front().substr(pos + 1).c_str());
  arrival_time = (hours * 60) + minutes;
  tokens.pop_front();

  destination = tokens.front();
  tokens.pop_front();
}
/*
Method for returning string representation of Journey object for debug printing.

Arguments:
  void
Returns:
  string representation of the Journey object.
*/
string Journey::to_string() const {
  ostringstream ss;
  ss << "String representation: " << string_rep << endl
     << "Destination: " << destination << endl
     << "Departure time: " << departure_time << endl
     << "Arrival time: " << arrival_time << endl
     << endl;

  return ss.str();
}