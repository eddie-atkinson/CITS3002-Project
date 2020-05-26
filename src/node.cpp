#include "node.h"

Node::Node() {}

void Node::quit(int status) {
  // Add colour to output to notice errors more easily
  cout << "\033[0;31m";
  cout << "Closing sockets and getting out of here" << endl;
  cout << "\033[0m";
  for (auto const &socket : input_sockets) {
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

class Journey *Node::find_next_trip(string &node_name, int start_time) {
  if (timetables.find(node_name) == timetables.end()) {
    cout << "Couldn't find timetable for " << node_name << " exiting" << endl;
    quit(1);
  }
  Journey *next_journey = NULL;
  list<class Journey> timetable = timetables[node_name];
  for (auto journey : timetable) {
    if (journey.departure_time > start_time) {
      next_journey = &journey;
      break;
    }
  }
  return next_journey;
}