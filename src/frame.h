#ifndef FRAME_H
#define FRAME_H
#include <iostream>
#include <sstream>
#include "node.h"
#include "common.h"
#include "frametype.h"

class Frame {
  public:
    string origin;
    string dest;
    list<string> src;
    int seqno;
    time_t time;
    FrameType type;
    Frame();
    Frame(
      const char* origin,
      const char* dest,
      list<string> src,
      int seqno,
      time_t time,
      FrameType type
    );
    string to_string();
    void from_string(string);
};
#endif
