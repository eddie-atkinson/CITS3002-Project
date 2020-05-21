#include "station.h"
#include "node.h"

Node parse_args(int argc, char* argv[]) {
    Node this_node = Node();
    this_node.name = argv[1];
    this_node.tcp_port = atoi(argv[2]);
    this_node.udp_port = atoi(argv[3]);

    for(int i = 4; i < argc; ++i) {
        int port = atoi(argv[i]);
        this_node.neighbours.insert({port, ""});
        // this_node.neighbours[atoi(argv[i])] = "";
    }

    return this_node;
}

int main(int argc, char *argv[]) {
    Node this_node = parse_args(argc, argv);
    return 0;
}


