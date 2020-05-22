#ifndef FRAME_H
#define FRAME_H
#include <iostream>
#include <string>
#include <vector>
#include "node.h"
#include "frametype.h"
class Frame {
  public:
    std::string origin;
    std::string dest;
    std::vector<std::string> src;
    int seqno;
    int time;
    FrameType type;
    Frame(
      const char* origin,
      const char* dest,
      std::vector<std::string> src,
      int seqno, 
      int time,
      FrameType type
    );
};
#endif
