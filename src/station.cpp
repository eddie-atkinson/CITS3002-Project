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
  uint32_t host = 0;

  this_node.tcp_socket = socket(AF_INET, SOCK_STREAM, 0);
  if(this_node.tcp_socket < 0) {
    std::cout << "Failed to allocate TCP socket, exiting" << std::endl;
    exit(1);
  }

  tcpaddr.sin_family = AF_INET;
  tcpaddr.sin_port = htons(this_node.tcp_port);
  tcpaddr.sin_addr.s_addr = host; 
  tcpaddr.sin_family = AF_INET;

  int result = bind(
    this_node.tcp_socket,
    (struct sockaddr *) &tcpaddr,
    sizeof(struct sockaddr_in)
  );

  if(result < 0 ) {
    std::cout << "Failed to bind TCP socket, exiting" << std::endl;
    close_sockets(this_node);  
    exit(1);
  }

  if(listen(this_node.tcp_socket, 5) != 0) {
    std::cout << "TCP socket failed to listen, exiting" << std::endl;
    close_sockets(this_node);
    exit(1);
  }
  if(fcntl(this_node.tcp_socket, F_SETFL, O_NONBLOCK) != 0) {
    std::cout << "TCP socket failed to set non-blocking, exiting" << std::endl;
    close_sockets(this_node);
    exit(1);
  }
  udpaddr.sin_family = AF_INET;
  udpaddr.sin_port = htons(this_node.udp_port);
  udpaddr.sin_addr.s_addr = host; 
  udpaddr.sin_family = AF_INET;

  this_node.udp_socket = socket(AF_INET, SOCK_DGRAM, 0);
  if(this_node.udp_socket < 0) {
    std::cout << "Failed to allocate UDP socket, exiting" << std::endl;
    close_sockets(this_node);
    exit(1);
  }
  
  result = bind(
    this_node.udp_socket,
    (struct sockaddr *) &udpaddr,
    sizeof(struct sockaddr_in)
  );
  if(result < 0 ) {
    std::cout << "Failed to bind UDP socket, exiting" << std::endl;
    close_sockets(this_node);
    exit(1);
  }

  if(fcntl(this_node.udp_socket, F_SETFL, O_NONBLOCK) != 0) {
    std::cout << "UDP socket failed to set non-blocking, exiting" << std::endl;
    close_sockets(this_node);
    exit(1);
  }

  // Wait for everyone else to bind their ports
  sleep(5);
  std::cout << "You can send frames now" << std::endl;
}



void send_name_frames(Node& this_node) {
  return;
}

void handle_sockets(Node& this_node, fd_set* rfds) {
  char buf[MAX_PACKET_LEN];
  size_t len = MAX_PACKET_LEN;
  struct sockaddr from;
  socklen_t fromlen;

  if(FD_ISSET(this_node.udp_socket, rfds)) {
    // We have UDP
    size_t read = recvfrom(this_node.udp_socket, &buf, len, 0, &from, &fromlen);
    std::string frame(buf, read);
    handle_udp(this_node, frame);
  } 

  if(FD_ISSET(this_node.tcp_socket, rfds)) {
    std::cout << "TCP socket has a frame" << std::endl;
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
        std::cout << "Error in select, exiting" << std::endl;
        close_sockets(this_node);
        exit(1);
      } else if(fdsready > 0) {
        handle_sockets(this_node, &rfds);
      }
  }
}

int main(int argc, char *argv[]) {
  if(argc <= 2) {
    std::cout << "Server needs arguments to work" << std::endl;
    exit(1);
  }
  Node this_node = parse_args(argc, argv);
  std::cout << "Node: "
            << this_node.name
            << " running with PID "
            << getpid() << std::endl;
  init_ports(this_node);
  // send_name_frames(this_node);
  listen_on_ports(this_node);
  return 0;
}


