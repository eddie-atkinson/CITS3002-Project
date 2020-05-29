/*
Implementation of the Node class and its methods
*/
#include "node.h"

/*
No args constructor for a node.

Initialises the sequence number to 0, sets the last timetable check to an unresasonable
value to guarantee the timetable is parsed, sets the packet count to 0 and initiliases
the outstanding_frames list.

*/
Node::Node(void) {
  seqno = 0;
  last_timetable_check = -1;
  packet_count = 0;
  outstanding_frames = list<class Response>();
}
/*
Method to check whether another node has exited and the network has been compromised.

Scans the local directory for a killfile, which is created when other nodes exit with an error.
If this file is found the quit method is called to halt execution gracefully.

Arguments:
  void
Returns:
  void
*/
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

/*
Method to initialise a node's TCP and UDP ports.

Initialises the appropriate ports and then waits 5 seconds to ensure all the other
nodes in the network have bound their ports.

Arguments:
  void
Returns:
  void
*/
void Node::init_ports() {
  init_tcp();
  init_udp();
  sleep(5);
  cout << "You can send frames now" << endl;
}

/*
Private method to initialise a node's TCP port.

Requests a file descriptor for a TCP socket, set's it to be non-blocking (though
it probably doesn't have to be), binds the socket, sets it to listen for 5 concurrent 
connections and adds the socket to the list of sockets to listen on. If there is an
error at any point the node calls quit and exits gracefully.

Arguments:
  void
Returns:
  void
*/
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

/*
Private method to initialise a node's UDP port.

Requests a file descriptor for a UDP socket, sets it to be non-blocking (again,
not strictly necessary), binds the socket and adds it the list of file descriptors
that select should watch. If unsuccesful it simply calls quit and exits gracefully.

Arguments:
  void
Returns:
  void
*/
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

/*
Method to halt execution gracefully and close any open sockets.

Prints an appropriate error message in an appropriate colour, closes any open TCP
and UDP sockets, and exits with an appropriate status value.

Arguments:
  void
Returns:
  void
*/
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
  cout << "Packets forwarded by " << name << " is " << packet_count << endl; 
  for (auto socket : input_sockets) {
    shutdown(socket, SHUT_RD);
    close(socket);
  }
  exit(status);
}

/*
Method to check a node's timetables, only refreshing the timetable if it has changed
since the last check.

Stats the node's timetable file, if the modification time is greater than the last
time the timetable was parsed, all current timetable information is dumped and the timetable
is reparsed. 

Arguments:
  void
Returns:
  void
*/
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

/*
Method to remove a socket when it has been responded to.

Iterates through the list of input sockets to listen on, deletes the appropriate
file descriptor and closes the connection.

Arguments:
  fd: the file descriptor of the socket to remove
Returns:
  void
*/
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

/*
Method for finding out the port a neighbour should be contacted from given their name.

Simply iterates through the map of port numbers and neighbour names and finds the
appropriate port for the name.

Arguments:
  node_name: the node's name as string
Returns:
  the node's port number as an unsigned 16 bit integer or -1 if it couldn't be found
*/ 
uint16_t Node::get_port_from_name(string &node_name) {
  for (auto neighbour : neighbours) {
    if (neighbour.second == node_name) {
      return neighbour.first;
    }
  }
  cout << "Couldn't find port for neighbour " << node_name << endl;
  return -1;
}
/*
Method for finding the next journey to a given node at a given start time.

Arguments:
  node_name: the destination node's name as a string
  start_time: the time, in minutes after midnight that a propsective trip must depart
Returns:
  a string representation of the next possible journey
*/
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

/*
Method to find the earliest time which a person could arrive at a given node if they
departed after a given time.

Arguments:
  node_name: the name of the destination node as a string
  start_time: the time, in minutes after midnight, after which a trip to the node must depart
Returns:
  void
*/
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

/*
Method for sending a UDP packet to a given port

Arguments:
  port: the port number to send the packet to over localhost
  transmission: string representation of the packet to be sent
Returns:
  void
*/
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

/*
Method for sending a TCP packet to a given file descriptor.

Arugments:
  fd: file descriptor to send the TCP packet to
  transmission: string representation of the packet to be sent
Returns:
  void
*/
void Node::send_tcp(int fd, string &transmission) {
  if (send(fd, transmission.c_str(), transmission.size(), 0) < 0) {
    cout << "Failed to send a browser rejection, exiting" << endl;
    quit(1);
  }
}

/*
Method to find the response object associated with a given frame.

Performs a triple-lock check on the response object, ensuring the given destination matches
the response object's origin, the sequence numbers match and the src path that the frame
and the response object have taken to reach a given node match.

Arugments:
  dest: the destination of a given frame
  seqno: the sequence number of a given frame
  in_src: the list of nodes a frame has passed through =
Returns:
  a pointer to the response object which corresponds to the frame whose details 
  have been provided or NULL if no object was found
*/
Response *Node::find_response_obj(string &dest, int seqno, list<string> &in_src) {
  Response *resp_obj = NULL;
  for (auto &resp : outstanding_frames) {
    bool token_match = resp.origin == dest && resp.seqno == seqno;
    if (token_match && resp.src == in_src) {
      resp_obj = &resp;
      break;
    }
  }
  return resp_obj;
}

/*
Method to remove an outstanding frame object when it is no longer needed. 

Arguments:
  resp_ptr: a pointer to the Response object to remove
Returns:
  void
*/
void Node::remove_outstanding_frame(Response *resp_ptr) {
  list<Response>::iterator iter;
  for (iter = outstanding_frames.begin(); iter != outstanding_frames.end();
       ++iter) {
    bool match = resp_ptr->origin == iter->origin &&
                 resp_ptr->seqno == iter->seqno &&
                 resp_ptr->src == iter->src;
    if (match) {
      iter = outstanding_frames.erase(iter);
      return;
    }
  }
}