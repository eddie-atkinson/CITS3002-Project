#include "response.h"
Response::Response(int remaining_responses, list<string>& src, string &origin,
                   int seqno)
    : remaining_responses(remaining_responses), src(src), origin(origin),
      seqno(seqno) {
  time = -1;
}
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