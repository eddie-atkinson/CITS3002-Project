#include "util.h"

list < string > split(const string & s, char delimiter) {
  list < string > tokens;
  string token;
  std::istringstream tokenStream(s);
  while (std::getline(tokenStream, token, delimiter)) {
    tokens.push_back(token);
  }
  return tokens;
}

string http_string(
  int response_code,
  string response_msg,
  list < string > messages
) {
  std::ostringstream ss;
  ss << "HTTP/1.0 " << response_code <<
    " " << response_msg << endl <<
    "Content-Type: text/html" << endl <<
    "Connection: Closed" << endl << endl <<
    "<html><body>";
  for (auto str: messages) {
    ss << "<p>" << str << "</p>";
  }
  ss << "</body></html>";
  return ss.str();
}

Journey find_next_trip(list < class Journey > & timetable, struct tm * local_time) {
  // In case there isn't a journey until tomorrow
  Journey next_journey = timetable.front();
  time_t local_time_in_secs = mktime(local_time);
  for (auto journey: timetable) {
    time_t depart_in_secs = mktime(&journey.departure_time);
    if (depart_in_secs > local_time_in_secs) {
      next_journey = journey;
      break;
    }
  }
  return next_journey;
}

time_t calc_arrival_time(list < class Journey > & timetable, time_t start_time) {
  struct tm * local_time = localtime( & start_time);
  Journey next_journey = find_next_trip(timetable, local_time);
  time_t wait_time = mktime(&next_journey.departure_time) - mktime(local_time);
  time_t leaving_time;
  if (wait_time < 0) {
    // Next journey is tomorrow
    leaving_time = start_time + (SECONDS_IN_DAY + wait_time);
  } else {
    leaving_time = start_time + wait_time;
  }
  return (leaving_time + next_journey.duration_in_secs);
}

void normalise_tm_struct(struct tm* time) {
  memset(time, 0, sizeof(struct tm));
  time->tm_year = 70;
  time->tm_mday = 1;
  time->tm_wday = 5;
}