// Include guard
#ifndef RESPONSE_H
#define RESPONSE_H
#include "common.h"
#include "frame.h"
#include "journey.h"
/*
Class to represent the information required to process a response to a frame. 

Attributes:
  remaining_responses: the number of responses that remain to be received for
  a given frame
  origin: the name of the origin node of the frame
  seqno: the sequence number applied to the frame by the origin
  time: the time, in minutes after midnight, that the best response received so far could
  arrive at the destination
  stop: the name of the node the next leg of the fastest journey to the destination passes through
*/
class Response {
public:
  int remaining_responses;
  list<string> src;
  string origin;
  int seqno;
  int time;
  string stop;
  // Constructor
  Response(int remaining_responses, list<string>& src, string &origin, int seqno);
  // Public method
  string to_string();
};
#endif