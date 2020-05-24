#include "node.h"

Node::Node() {}

void Node::quit(int status) {
	std::cout << "Closing sockets and getting out of here" << std::endl;
	close(tcp_socket);
	close(udp_socket);
	exit(status);
}

void Node::check_timetable(void) {
	struct stat st;
	string file_name = "tt-" + name;
	if(stat(file_name.c_str(), &st) < 0) {
    cout << "Error reading " << file_name << endl;
    quit(1);
  }
  if(st.st_mtim.tv_sec > last_timetable_check) {
    cout << name << " refreshing timetable" << endl;
    std::ifstream file(file_name);
    string line;
    // Don't care about the header line
    std::getline(file, line);
    while(std::getline(file, line)) {
      cout << line << endl;

    }
    last_timetable_check = time(NULL);
  }

}