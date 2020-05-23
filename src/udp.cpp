#include "udp.h"
void process_request_frame(){}

void process_response_frame(){}

void process_udp(Node& this_node, string& transmission, uint16_t port) {
	cout << "Received UDP packet from port " << port << endl;
  Frame in_frame = Frame();
  in_frame.from_string(transmission);
  this_node.check_timetable();
  
  if(in_frame.type == NAME_FRAME) {
    this_node.neighbours[port] = in_frame.origin;
  } else if(in_frame.type == REQUEST) {
    process_request_frame();
  } else {
    process_response_frame();
  }
}