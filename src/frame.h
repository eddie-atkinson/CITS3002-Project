#ifndef FRAME_H
#define FRAME_H
#include "common.h"
#include "frametype.h"
#include "node.h"
#include <iostream>
/*
  Class for storing the essential information about a UDP frame.

  Atributes:
    origin: the name of the node where the frame originated
    dest: the name of the destination node of the frame
    src: a list of strings containing the names of the nodes the frame has passed through in order
    seqno: the sequence number applied to the frame by the original sender
    time: the time, in minutes after midnight that the previous sender can arrive at the recipient
    type: Enum for frametype
*/
class Frame {
public:
  string origin;
  string dest;
  list<string> src;
  int seqno;
  int time;
  FrameType type;
  // Constructors
  Frame();
  Frame(string origin, string dest, list<string> &src, int seqno, int time,
        FrameType type);
  // Public methods
  string to_string();
  void from_string(string &in_str);
};
#endif
