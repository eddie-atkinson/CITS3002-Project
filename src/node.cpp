#include "node.h"

Node::Node(void) {
  seqno = 0;
  last_timetable_check = -1;
  outstanding_frames = list<class Response>();
}

void Node::check_kill() {
  DIR *dir;
  struct dirent *ent;
  if ((dir = opendir(".")) != NULL) {
    while ((ent = readdir(dir)) != NULL) {
      if (strcmp(ent->d_name, KILL_FILE) == 0) {
        quit(0);
      }
    }
    closedir(dir);
  } else {
    cout << "Failed to read file system, exiting" << endl;
    quit(1);
  }
}

void Node::init_ports() {
  init_tcp();
  init_udp();
  sleep(5);
  cout << "You can send frames now" << endl;
}

void Node::init_tcp() {
  struct sockaddr_in addr;
  tcp_socket = socket(AF_INET, SOCK_STREAM, 0);
  if (fcntl(tcp_socket, F_SETFL, O_NONBLOCK) < 0) {
    cout << "Failed to set TCP socket non-binding, exiting" << endl;
    quit(1);
  }
  bzero(&addr, sizeof(struct sockaddr));
  addr.sin_family = AF_INET;
  addr.sin_port = htons(tcp_port);
  inet_pton(AF_INET, HOST_IP, &(addr.sin_addr));
  if (bind(tcp_socket, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    cout << "Failed to bind TCP socket, is it still in use?" << endl;
    quit(1);
  }
  if (listen(tcp_socket, 5) < 0) {
    cout << "TCP socket failed to listen" << endl;
    quit(1);
  }
  input_sockets.push_back(tcp_socket);
}

void Node::init_udp() {
  struct sockaddr_in addr;
  udp_socket = socket(AF_INET, SOCK_DGRAM, 0);
  if (fcntl(udp_socket, F_SETFL, O_NONBLOCK) < 0) {
    cout << "Failed to set UDP socket non-binding, exiting" << endl;
    quit(1);
  }
  bzero(&addr, sizeof(struct sockaddr));
  addr.sin_family = AF_INET;
  addr.sin_port = htons(udp_port);
  inet_pton(AF_INET, HOST_IP, &(addr.sin_addr));
  if (bind(udp_socket, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    cout << "Failed to bind UDP socket, is it still in use?" << endl;
    quit(1);
  }
  input_sockets.push_back(udp_socket);
}

void Node::quit(int status) {
  // Add colour to output to notice errors more easily
  if (status == 0) {
    cout << ANSI_COLOR_GREEN;
    cout << name << " received signal to exit, leaving gracefully" << endl;
    cout << ANSI_COLOR_RESET;
  } else {
    cout << ANSI_COLOR_RED;
    cout << name << " exited with error state" << endl;
    cout << ANSI_COLOR_RESET;
    // Create kill file,  to bring down the other servers
    FILE *fp = fopen(KILL_FILE, "w");
    fclose(fp);
  }
  for (auto socket : input_sockets) {
    shutdown(socket, SHUT_RD);
    close(socket);
  }
  exit(status);
}

void Node::check_timetable(void) {
  struct stat st;
  string file_name = "tt-" + name;
  if (stat(file_name.c_str(), &st) < 0) {
    cout << "Error reading " << file_name << endl;
    quit(1);
  }
  if (st.st_mtim.tv_sec > last_timetable_check) {
    cout << name << " refreshing timetable" << endl;
    timetables.clear();
    std::ifstream file(file_name);

    string line;
    // Don't care about the header line
    std::getline(file, line);
    list<string> tokens;
    while (std::getline(file, line)) {
      if (line.at(0) == '#') {
        continue;
      }
      Journey nxt_jrn = Journey(line);
      if (timetables.find(nxt_jrn.destination) == timetables.end()) {
        timetables[nxt_jrn.destination] = list<class Journey>();
      }
      timetables[nxt_jrn.destination].push_back(nxt_jrn);
    }
    for (auto timetable : timetables) {
      timetable.second.sort([](const Journey &jrn_a, const Journey &jrn_b) {
        return jrn_a.departure_time < jrn_b.departure_time;
      });
    }

    last_timetable_check = time(NULL);
  }
}

void Node::remove_socket(int fd) {
  for (unsigned int i = 0; i < input_sockets.size(); ++i) {
    if (input_sockets.at(i) == fd) {
      input_sockets.erase(input_sockets.begin() + i);
      break;
    }
  }
  shutdown(fd, SHUT_RD);
  close(fd);
}

uint16_t Node::get_port_from_name(string &node_name) {
  for (auto neighbour : neighbours) {
    if (neighbour.second == node_name) {
      return neighbour.first;
    }
  }
  return -1;
}

string Node::find_itinerary(string &node_name, int start_time) {
  if (timetables.find(node_name) == timetables.end()) {
    cout << "Couldn't find timetable for " << node_name << " exiting" << endl;
    quit(1);
  }
  string itinerary;
  list<class Journey> timetable = timetables[node_name];
  for (auto journey : timetable) {
    if (journey.departure_time > start_time) {
      itinerary = journey.string_rep;
      break;
    }
  }
  return itinerary;
}

int Node::find_arrival_time(string &node_name, int start_time) {
  if (timetables.find(node_name) == timetables.end()) {
    cout << "Couldn't find timetable for " << node_name << " exiting" << endl;
    return -1;
  }
  int arrival_time = -1;
  list<class Journey> timetable = timetables[node_name];
  for (auto journey : timetable) {
    if (journey.departure_time > start_time) {
      arrival_time = journey.arrival_time;
      break;
    }
  }
  return arrival_time;
}

void Node::send_udp(uint16_t port, string &transmission) {
  struct sockaddr_in to;
  to.sin_family = AF_INET;
  inet_pton(AF_INET, HOST_IP, &(to.sin_addr));
  to.sin_port = htons(port);
  if (sendto(udp_socket, transmission.c_str(), transmission.size(), 0,
             (struct sockaddr *)&to, sizeof(to)) < 0) {
    cout << "Failed to send frame to neighbour" << endl;
    quit(1);
  }
}

void Node::send_tcp(int fd, string &transmission) {
  if (send(fd, transmission.c_str(), transmission.size(), 0) < 0) {
    cout << "Failed to send a browser rejection, exiting" << endl;
    quit(1);
  }
}

Response *Node::find_response_obj(string &dest, int seqno, string &sender) {
  Response *resp_obj = NULL;
  for (auto &resp : outstanding_frames) {
    bool token_match = resp.origin == dest && resp.seqno == seqno;
    if (token_match && (resp.sender == sender || dest == name)) {
      resp_obj = &resp;
      break;
    }
  }
  return resp_obj;
}

void Node::remove_outstanding_frame(Response *resp_ptr) {
  list<Response>::iterator iter;
  for (iter = outstanding_frames.begin(); iter != outstanding_frames.end();
       ++iter) {
    bool match = resp_ptr->origin == iter->origin &&
                 resp_ptr->seqno == iter->seqno &&
                 resp_ptr->sender == iter->sender;
    if (match) {
      outstanding_frames.erase(iter);
      return;
    }
  }
}