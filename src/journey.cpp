#include "journey.h"

Journey::Journey(const string& in_str): string_rep(in_str) {
  std::tm arrival_time;
  // Zero time structs to start at common epoch
  memset(&departure_time, 0, sizeof(struct tm));
  memset(&arrival_time, 0, sizeof(struct tm));

  // Set the month to january
  departure_time.tm_mday = 1;
  arrival_time.tm_mday = 1;

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
  ss << "String representation: " << string_rep << endl
     << "Destination: " << destination << endl
     << "Departure time: " << asctime(&departure_time)
     << "Duration in secs: " << duration_in_secs << endl << endl;
      
  return ss.str();
}

// bool Journey::operator < (const Journey& journeyObj) const {
//   struct tm temp_a = departure_time;
//   struct tm temp_b = journeyObj.departure_time;
//   return mktime(&temp_a) < mktime(&temp_b);
// }
