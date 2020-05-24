#include "udp.h"
void process_request_frame(){}

void process_response_frame(){}

void send_frame_to_neighbours(Node& this_node, Frame& out_frame) {
  // int sent_frames = 0;
  out_frame.src.push_back(this_node.name);
  // time_t start_time;
  if(out_frame.time == -1) {
    // start_time = time(NULL);
  } else {
    // start_time = out_frame.time;
  }

  return;
}

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