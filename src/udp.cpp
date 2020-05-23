#include "udp.h"

void handle_udp(Node& this_node, string& transmission, uint16_t port) {
	cout << "Received UDP packet from port " << port << endl;
  Frame in_frame = Frame();
  in_frame.from_string(transmission);
}