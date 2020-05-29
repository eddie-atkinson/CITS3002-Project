/* 
Implementation of Response class and its methods
*/
#include "response.h"
/*
Constructor for Response objects.

Sets the best time to -1 to ensure any valid time will be recorded. 
*/
Response::Response(int remaining_responses, list<string>& src, string &origin,
                   int seqno)
    : remaining_responses(remaining_responses), src(src), origin(origin),
      seqno(seqno) {
  time = -1;
}
/*
Method to return a string representation of a Response object for easy printing

Arguments:
  void
Returns:
  string representation of Response object
*/
string Response::to_string() {
  ostringstream ss;
  ostringstream src_ss;
  for(auto node: src) {
    src_ss << node << ".";
  }
  ss << "Remaining responses: " << remaining_responses << endl
     << "Frame origin: " << origin << endl
     << "SRC " << src_ss.str() << endl
     << "Seqno: " << seqno << endl
     << "Best time: " << time << endl
     << "Best stop: " << stop << endl;
  return ss.str();
}