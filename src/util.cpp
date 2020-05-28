#include "util.h"

list<string> split(const string &s, char delimiter) {
  list<string> tokens;
  string token;
  std::istringstream tokenStream(s);
  while (std::getline(tokenStream, token, delimiter)) {
    tokens.push_back(token);
  }
  return tokens;
}

string http_string(int response_code, string response_msg,
                   list<string> messages) {
  ostringstream ss;
  ss << "HTTP/1.0 " << response_code << " " << response_msg << endl
     << "Content-Type: text/html" << endl
     << "Connection: Closed" << endl
     << endl
     << "<html><body>";
  for (auto str : messages) {
    ss << "<p>" << str << "</p>";
  }
  ss << "</body></html>";
  return ss.str();
}

int current_time(void) {
  time_t temp_time = time(NULL);
  struct tm *temp_struct = localtime(&temp_time);
  return ((temp_struct->tm_hour * 60) + temp_struct->tm_min);
}
