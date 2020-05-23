#include "journey.h"

Journey::Journey(string& in_str) {
	string_rep = in_str;
	string delimiter = ",";
	list<string> tokens;
	size_t pos = 0;
	string token; 
	while((pos = in_str.find(delimiter)) != string::npos) {
    token = in_str.substr(0, pos);
    tokens.push_back(token);
	  in_str.erase(0, pos + delimiter.length());
  }
  // Run one last time for last token
  token = in_str.substr(0, pos);
  tokens.push_back(token);
  
  departure_time = tokens.front();
  tokens.pop_front();
  // Don't care about the name of the bus or the stop
  tokens.pop_front();
  tokens.pop_front();
  arrival_time = tokens.front();
  tokens.pop_front();
  destination = tokens.front();
  tokens.pop_front();
}
Journey::Journey() {}

string Journey::to_string() {
  std::ostringstream ss;
  ss << "String representation: " << string_rep << endl
     << "Destination: " << destination << endl
     << "Departure time: " << departure_time << endl
     << "Arrival time: " << arrival_time << endl;
      
  return ss.str();
}
