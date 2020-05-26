#ifndef FRAME_H
#define FRAME_H
#include "common.h"
#include "frametype.h"
#include "node.h"
#include <iostream>
#include <sstream>

class Frame {
public:
  string origin;
  string dest;
  list<string> src;
  int seqno;
  time_t time;
  FrameType type;
  Frame();
  Frame(string origin, string dest, list<string> src, int seqno, time_t time,
        FrameType type);
  string to_string();
  void from_string(string &in_str);
};
#endif
