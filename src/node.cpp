#include "node.h"

Node::Node() {}

void Node::quit(int status) {
  // Add colour to output to notice errors more easily
  cout << "\033[0;31m";
	cout << "Closing sockets and getting out of here" << endl;
  cout << "\033[0m";
	for(auto const& socket: input_sockets) {
    shutdown(socket, SHUT_RD);
    close(socket);
  }
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
    timetables.clear();
    std::ifstream file(file_name);
    
    string line;
    // Don't care about the header line
    std::getline(file, line);
    list<string> tokens;
    while(std::getline(file, line)) {
      Journey nxt_jrn = Journey(line);
      if(timetables.find(nxt_jrn.destination) == timetables.end()) {
        timetables[nxt_jrn.destination] = list<class Journey>(); 
      }
      timetables[nxt_jrn.destination].push_back(nxt_jrn);
    }
    // TODO: Sort journeys in order of departure time
    last_timetable_check = time(NULL);
  }

}