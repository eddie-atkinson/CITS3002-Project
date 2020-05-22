#include "frame.h"
Frame::Frame(
  const char* origin,
  const char* dest,
  std::vector<std::string> src,
  int seqno,
  int time, 
  FrameType type
): origin(origin),
   dest(dest), 
   src(src),
   seqno(seqno),
   time(time),
   type(type) {}