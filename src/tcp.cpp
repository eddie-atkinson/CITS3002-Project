#include "tcp.h"

void handle_tcp(Node &this_node, string &message, int socket) {
  std::regex reg_str("to=\\w+");
  std::smatch match;
  std::regex_search(message, match, reg_str);
  string destination = match.str();
  if (match.size() == 0) {
    list<string> msgs({"Ouch! bad request"});
    string response = http_string(400, "Bad request", msgs);
    this_node.send_tcp(socket, response);
    this_node.remove_socket(socket);
    return;
  }
  size_t pos = destination.find("=");
  // Trim off prefix
  destination.erase(0, pos + 1);
  list<string> new_src;
  Frame request_frame =
      Frame(this_node.name, destination, new_src, this_node.seqno, -1, REQUEST);
  this_node.response_sockets[this_node.seqno] = socket;
  this_node.seqno = (this_node.seqno + 1) % MAX_INT;
  this_node.check_timetable();

  send_frame_to_neighbours(this_node, request_frame);
}