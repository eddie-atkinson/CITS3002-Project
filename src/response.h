// Include guard
#ifndef RESPONSE_H
#define RESPONSE_H
#include "common.h"
#include "frame.h"
#include "journey.h"

class Response {
public:
  int remaining_responses;
  list<string> src;
  string origin;
  int seqno;
  int time;
  string stop;
  Response(int remaining_responses, list<string>& src, string &origin, int seqno);
  string to_string();
};
#endif