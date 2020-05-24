#include "journey.h"

Journey::Journey(const string& in_str): string_rep(in_str) {
  struct tm arrival_time;
  normalise_tm_struct(&arrival_time);
  normalise_tm_struct(&departure_time);
  string temp_str = string_rep;
  list<string> tokens = split(temp_str, ',');
  strptime(tokens.front().c_str(), "%H:%M", &departure_time);
  tokens.pop_front();
  // Don't care about bus or stop name
  tokens.pop_front();
  tokens.pop_front();
  strptime(tokens.front().c_str(), "%H:%M", &arrival_time);
  duration_in_secs = mktime(&arrival_time) - mktime(&departure_time);
  tokens.pop_front();
  destination = tokens.front();
  tokens.pop_front();
}

string Journey::to_string() const {
  std::ostringstream ss;
  char outstr[200];
  strftime(outstr, sizeof(outstr), "%c", &departure_time);
  ss << "String representation: " << string_rep << endl
     << "Destination: " << destination << endl
     << "Departure time: " << outstr << endl
     << "Duration in secs: " << duration_in_secs << endl << endl;
      
  return ss.str();
}

// bool Journey::operator < (const Journey& journeyObj) const {
//   struct tm temp_a = departure_time;
//   struct tm temp_b = journeyObj.departure_time;
//   return mktime(&temp_a) < mktime(&temp_b);
// }
