#include "udp.h"
void process_request_frame(){}

void process_response_frame(){}

void send_frame_to_neighbours(Node& this_node, Frame& out_frame) {
  int sent_frames = 0;
  out_frame.src.push_back(this_node.name);
  time_t start_time;
  if(out_frame.time == -1) {
    start_time = time(NULL);
  } else {
    start_time = out_frame.time;
  }
  std::unordered_set<string> src_set;
  // Add src list to set for (almost) constant checks
  std::copy(
    out_frame.src.begin(),
    out_frame.src.end(),
    std::inserter(src_set, src_set.end())
  );
  for(auto neighbour: this_node.neighbours) {
    if(src_set.find(neighbour.second) == src_set.end()) {
      // We haven't sent the frame here before
      list<class Journey> timetable = this_node.timetables[neighbour.second];
      out_frame.time = calc_arrival_time(timetable, start_time);
      cout << out_frame.time << endl;
      cout << asctime(localtime(&out_frame.time)) << endl;
      ++sent_frames;
    }
  }


  return;
}

void process_udp(Node& this_node, string& transmission, uint16_t port) {
	cout << "Received UDP packet from port " << port << endl;
  Frame in_frame = Frame();
  in_frame.from_string(transmission);
  this_node.check_timetable();
  // for(auto neighbour: this_node.timetables) {
  //   for(auto journey: neighbour.second) {
  //     cout << journey.to_string() << endl;
  //   }
  // }
  if(in_frame.type == NAME_FRAME) {
    this_node.neighbours[port] = in_frame.origin;
  } else if(in_frame.type == REQUEST) {
    process_request_frame();
  } else {
    process_response_frame();
  }
}