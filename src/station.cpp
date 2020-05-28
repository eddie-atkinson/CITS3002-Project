#include "station.h"

Node parse_args(int argc, char *argv[]) {
  Node this_node = Node();
  this_node.name = argv[1];
  this_node.tcp_port = (uint16_t)atoi(argv[2]);
  this_node.udp_port = (uint16_t)atoi(argv[3]);

  for (int i = 4; i < argc; ++i) {
    uint16_t port = (uint16_t)atoi(argv[i]);
    this_node.neighbours.insert({port, ""});
  }
  return this_node;
}

void send_name_frames(Node &this_node) {
  list<string> new_src;
  Frame name_frame = Frame(this_node.name, "", new_src, -1, -1, NAME_FRAME);
  string frame_str = name_frame.to_string();
  size_t len = frame_str.size();
  struct sockaddr_in out_addr;
  out_addr.sin_family = AF_INET;
  inet_pton(AF_INET, HOST_IP, &(out_addr.sin_addr));

  for (auto neighbour : this_node.neighbours) {
    uint16_t port = neighbour.first;
    out_addr.sin_port = htons(port);
    if (sendto(this_node.udp_socket, frame_str.c_str(), len, 0,
               (struct sockaddr *)&out_addr, sizeof out_addr) < 0) {
      cout << this_node.name << " error in sending frame " << frame_str << endl;
      this_node.quit(1);
    }
  }
  return;
}

void handle_sockets(Node &this_node, fd_set *rfds) {
  char buf[MAX_PACKET_LEN];
  size_t len = MAX_PACKET_LEN;
  struct sockaddr_in from;
  socklen_t fromlen = sizeof(from);
  bzero(&from, fromlen);
  ssize_t read;
  for (unsigned int i = 0; i < this_node.input_sockets.size(); ++i) {
    int socket = this_node.input_sockets.at(i);
    if (FD_ISSET(socket, rfds)) {
      if (socket == this_node.udp_socket) {
        // UDP received
        read = recvfrom(this_node.udp_socket, &buf, len, 0,
                        (struct sockaddr *)&from, &fromlen);
        string frame(buf, read);
        uint16_t port = ntohs(from.sin_port);
        process_udp(this_node, frame, port);
      } else if (socket == this_node.tcp_socket) {
        // New TCP connection
        int new_sock =
            accept(this_node.tcp_socket, (struct sockaddr *)&from, &fromlen);
        if (fcntl(new_sock, F_SETFL, O_NONBLOCK) != 0) {
          cout << "New socket failed to set non-blocking, exiting" << endl;
          this_node.quit(1);
        }
        this_node.input_sockets.push_back(new_sock);
        cout << "Received new connection from " << inet_ntoa(from.sin_addr)
             << ":" << ntohs(from.sin_port) << endl;
      } else {
        // Servicing existing TCP connections
        size_t tcp_read = 0;
        tcp_read = recv(socket, buf, len, 0);
        if (tcp_read == 0) {
          // Connection has closed
          this_node.remove_socket(socket);
          cout << "Closing connection to " << socket << endl;
        } else if (tcp_read > 0) {
          string frame(buf, read);
          handle_tcp(this_node, frame, socket);
        } else {
          cout << "Failed read operation on TCP socket, exiting" << endl;
          this_node.quit(1);
        }
      }
    }
  }
}

void listen_on_ports(Node &this_node) {
  struct timeval tv;
  fd_set read_fds;
  int fdsready;
  int largestfd;
  while (true) {
    this_node.check_kill();
    FD_ZERO(&read_fds);
    tv.tv_sec = 5;
    tv.tv_usec = 0;
    fdsready = 0;
    largestfd = -1;
    for (auto socket : this_node.input_sockets) {
      if (socket > largestfd) {
        largestfd = socket;
      }
      FD_SET(socket, &read_fds);
    }
    fdsready = select(largestfd + 1, &read_fds, NULL, NULL, &tv);
    switch (fdsready) {
    case (-1):
      cout << "Error with select, exiting" << endl;
      this_node.quit(1);
      break;
    case (0):
      break;
    default:
      handle_sockets(this_node, &read_fds);
      break;
    }
  }
}

int main(int argc, char *argv[]) {
  if (argc <= 2) {
    cout << "Server needs arguments to work" << endl;
    exit(1);
  }
  Node this_node = parse_args(argc, argv);
  cout << "Node: " << this_node.name << " running with PID " << getpid()
       << endl;
  this_node.init_ports();
  send_name_frames(this_node);
  listen_on_ports(this_node);
  return 0;
}
