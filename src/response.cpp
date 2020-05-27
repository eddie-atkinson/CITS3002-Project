#include "response.h"
Response::Response(int remaining_responses, string &sender, string &origin,
                   int seqno)
    : remaining_responses(remaining_responses), sender(sender), origin(origin),
      seqno(seqno) {
  time = -1;
}
string Response::to_string() {
  ostringstream ss;
  ss << "Remaining responses: " << remaining_responses << endl
     << "Frame origin: " << origin << endl
     << "Frame sender: " << sender << endl
     << "Seqno: " << seqno << endl
     << "Best time: " << time << endl
     << "Best stop: " << stop << endl;
  return ss.str();
}