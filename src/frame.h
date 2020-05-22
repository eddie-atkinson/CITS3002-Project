#ifndef FRAME_H
#define FRAME_H
#include <iostream>
#include <string>
#include <sstream>
#include <list>
#include <map>
#include <vector>
#include "node.h"
#include "frametype.h"
using std::string;
using std::map;
using std::endl;
using std::list;
using std::cout;
using std::ostringstream;
class Frame {
  public:
    std::string origin;
    std::string dest;
    std::list<std::string> src;
    int seqno;
    int time;
    FrameType type;
    Frame();
    Frame(
      const char* origin,
      const char* dest,
      std::list<std::string> src,
      int seqno,
      int time,
      FrameType type
    );
    std::string to_string();
    void from_string(std::string);
};
#endif
