// Include guard
#ifndef NODE_H
#define NODE_H
#include "common.h"
#include "journey.h"
#include "response.h"
#include "util.h"
#include <algorithm>
#include <arpa/inet.h>
#include <dirent.h>
#include <fcntl.h>
#include <iomanip>
#include <iostream>
#include <locale>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

/*
Class for storing the essential information and data structures necessary for the functioning
of a node in the network.

Attributes:
  name: the node's name as string
  udp_port: the UDP port the node uses for communication with other nodes
  tcp_port: the TCP port the node uses for communication with the browser
  neighbours: a map containing a node's neighbours UDP ports mapped
  to their names
  udp_socket: file descriptor of the UDP socket used by the node
  tcp_socket: file descriptor of the TCP socket used by the node
  response_sockets: map of frame sequence numbers to TCP socket file descriptors to respond to
  outstanding_frames: a list of Response objects for frames that require a response
  seqno: the current sequence number
  timetables: a map of neighbouring node names to a list of Journey objects
  input_sockets: a list of socket objects that are listened on
  last_timetable_check: the last time the node's timetable file was parsed
  packet_count: count of the number of packets forwarded by a node
*/
class Node {
public:
  string name;
  uint16_t udp_port;
  uint16_t tcp_port;
  map<uint16_t, string> neighbours;
  int udp_socket;
  int tcp_socket;
  map<int, int> response_sockets;
  list<class Response> outstanding_frames;
  int seqno;
  vector<int> input_sockets;
  map<string, list<class Journey>> timetables;
  time_t last_timetable_check;
  int packet_count;
  // Constructor
  Node();
  // Public methods
  void check_timetable();
  void check_kill();
  void quit(int status);
  void remove_socket(int fd);
  uint16_t get_port_from_name(string &node_name);
  void init_ports();
  int find_arrival_time(string &node_name, int start_time);
  string find_itinerary(string &node_name, int start_time);
  void send_udp(uint16_t port, string &transmission);
  void send_tcp(int fd, string &transmission);
  Response *find_response_obj(string &dest, int seqno, list<string> &in_src);
  void remove_outstanding_frame(Response *resp_ptr);

private:
  void init_tcp();
  void init_udp();
};
#endif