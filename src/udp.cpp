#include "udp.h"

void handle_udp(Node& this_node, string& transmission, uint16_t port) {
	cout << "Received UDP packet from port " << port << " with frame " << transmission << endl;
  Frame in_frame = Frame();
  in_frame.from_string(transmission);
  cout << in_frame.to_string() << endl;
}