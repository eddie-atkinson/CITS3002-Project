#include "station.h"

Node parse_args(int argc, char* argv[]) {
  Node this_node = Node();
  this_node.name = argv[1];
  this_node.tcp_port = atoi(argv[2]);
  this_node.udp_port = atoi(argv[3]);

  for (int i = 4; i < argc; ++i) {
    int port = atoi(argv[i]);
    this_node.neighbours.insert({port, ""});
  }
  return this_node;
}

void init_ports(Node& this_node) {
  struct sockaddr_in tcpaddr, udpaddr;

  this_node.tcp_socket = socket(AF_INET, SOCK_STREAM, 0);
  if(this_node.tcp_socket < 0) {
    cout << "Failed to allocate TCP socket, exiting" << endl;
    exit(1);
  }

  tcpaddr.sin_family = AF_INET;
  tcpaddr.sin_port = htons(this_node.tcp_port);
  tcpaddr.sin_addr.s_addr = HOST; 


  int result = bind(
    this_node.tcp_socket,
    (struct sockaddr *) &tcpaddr,
    sizeof(struct sockaddr_in)
  );

  if(result < 0 ) {
    cout << "Failed to bind TCP socket, exiting" << endl;
    close_sockets(this_node);  
    exit(1);
  }

  if(listen(this_node.tcp_socket, 5) != 0) {
    cout << "TCP socket failed to listen, exiting" << endl;
    close_sockets(this_node);
    exit(1);
  }
  if(fcntl(this_node.tcp_socket, F_SETFL, O_NONBLOCK) != 0) {
    cout << "TCP socket failed to set non-blocking, exiting" << endl;
    close_sockets(this_node);
    exit(1);
  }
  udpaddr.sin_family = AF_INET;
  udpaddr.sin_port = htons(this_node.udp_port);
  udpaddr.sin_addr.s_addr = HOST; 
  udpaddr.sin_family = AF_INET;

  this_node.udp_socket = socket(AF_INET, SOCK_DGRAM, 0);
  if(this_node.udp_socket < 0) {
    cout << "Failed to allocate UDP socket, exiting" << endl;
    close_sockets(this_node);
    exit(1);
  }
  
  result = bind(
    this_node.udp_socket,
    (struct sockaddr *) &udpaddr,
    sizeof(struct sockaddr_in)
  );
  if(result < 0 ) {
    cout << "Failed to bind UDP socket, exiting" << endl;
    close_sockets(this_node);
    exit(1);
  }

  if(fcntl(this_node.udp_socket, F_SETFL, O_NONBLOCK) != 0) {
    cout << "UDP socket failed to set non-blocking, exiting" << endl;
    close_sockets(this_node);
    exit(1);
  }

  // Wait for everyone else to bind their ports
  sleep(5);
  cout << "You can send frames now" << endl;
}

void send_name_frames(Node& this_node) {
  Frame name_frame = Frame(
    this_node.name.c_str(),
    "",
    list<string>(),
    -1,
    -1,
    NAME_FRAME
  );
  string frame_str = name_frame.to_string();
  size_t len = frame_str.size();
  struct sockaddr_in out_addr;
  out_addr.sin_family = AF_INET;
  out_addr.sin_addr.s_addr = HOST;

  for(std::pair<int, std::string> element : this_node.neighbours) {
    int port = element.first;
    out_addr.sin_port = htons(port);
    int sent = sendto(
      this_node.udp_socket,
      frame_str.c_str(),
      len,
      0,
      (struct sockaddr*)& out_addr,
      sizeof out_addr
    );
    if(sent < 0) {
      cout << "Error in sending frame " << frame_str << endl;
      close_sockets(this_node);
      exit(1);
    }
  }
  return;
}

void handle_sockets(Node& this_node, fd_set* rfds) {
  char buf[MAX_PACKET_LEN];
  size_t len = MAX_PACKET_LEN;
  struct sockaddr_in from;
  socklen_t fromlen;

  if(FD_ISSET(this_node.udp_socket, rfds)) {
    // We have UDP
    size_t read = recvfrom(
      this_node.udp_socket,
      &buf,
      len,
      0,
      (struct sockaddr *) &from,
      &fromlen
    );
    string frame(buf, read);
    uint16_t port = ntohs(from.sin_port);
    handle_udp(this_node, frame, port);
  } 

  if(FD_ISSET(this_node.tcp_socket, rfds)) {
    cout << "TCP socket has a frame" << endl;
  }
}

void listen_on_ports(Node& this_node) {
  this_node.input_sockets.push_back(this_node.tcp_socket);
  this_node.input_sockets.push_back(this_node.udp_socket);
  struct timeval tv; 
  tv.tv_sec = 10;
  tv.tv_usec = 0;
  fd_set rfds;
  int fdsready = 0;
  int largestfd = -1;
  int nfds = 0;
  while(1) {
      tv.tv_sec = 10;
      tv.tv_usec = 0;
      // Refresh the set of fds being watched
      FD_ZERO(&rfds);
      nfds = this_node.input_sockets.size();
      for(int i = 0; i < nfds; ++i) {
        int sock_fd = this_node.input_sockets.at(i);
        if(sock_fd > largestfd) {
          largestfd = sock_fd;
        }
        FD_SET(sock_fd, &rfds);
      }

      fdsready = select(largestfd + 1, &rfds, NULL, NULL, &tv);
      if(fdsready == -1) {
        cout << "Error in select, exiting" << endl;
        close_sockets(this_node);
        exit(1);
      } else if(fdsready > 0) {
        handle_sockets(this_node, &rfds);
      }
  }
}

int main(int argc, char *argv[]) {
  if(argc <= 2) {
    cout << "Server needs arguments to work" << endl;
    exit(1);
  }
  Node this_node = parse_args(argc, argv);
  cout << "Node: "
            << this_node.name
            << " running with PID "
            << getpid() << endl;
  init_ports(this_node);
  send_name_frames(this_node);
  listen_on_ports(this_node);
  return 0;
}


