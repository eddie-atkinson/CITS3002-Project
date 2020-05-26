// Include guard
#ifndef NODE_H
#define NODE_H
#include "common.h"
#include "journey.h"
#include "util.h"
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <locale>
#include <sstream>
#include <sys/socket.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

class Node {
public:
  string name;
  uint16_t udp_port;
  uint16_t tcp_port;
  map<uint16_t, string> neighbours;
  int udp_socket;
  int tcp_socket;
  map<int, int> response_sockets;
  vector<int>
      outstanding_frames; // TODO: change to Response objects when implemented
  int seqno;
  vector<int> input_sockets;
  map<string, list<class Journey>> timetables;
  time_t last_timetable_check;
  Node(void);
  void check_timetable(void);
  void quit(int status);
  void remove_socket(int fd);
  uint16_t get_port_from_name(string &node_name);
  class Journey *find_next_trip(string &node_name, int start_time);
};
#endif