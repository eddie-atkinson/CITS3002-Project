/*
Implementation of the Frame class
*/
#include "frame.h"
/*
Constructor for Frame. 

Arguments:
  origin: the name of the node where the frame originated
  dest: the name of the destination node of the frame
  src: a list of strings containing the names of the nodes the frame has passed through in order
  seqno: the sequence number applied to the frame by the original sender
  time: the time, in minutes after midnight that the previous sender can arrive at the recipient
  type: Enum for frametype
*/
Frame::Frame(string origin, string dest, list<string> &src, int seqno, int time,
             FrameType type)
    : origin(origin), dest(dest), src(src), seqno(seqno), time(time),
      type(type) {}

/*
No args constructor for Frame
*/
Frame::Frame() {}

/*
Utility method to convert a Frame object to a string for easy printing

Arguments:
  None
Returns:
  String representation of the frame
*/
string Frame::to_string() {
  ostringstream src_string;
  ostringstream main_string;
  list<string>::iterator it;
  for (it = src.begin(); it != src.end(); ++it) {
    src_string << *it;
    if (it != --src.end()) {
      src_string << ".";
    }
  }
  main_string << "origin:" << origin << ","
              << "dest:" << dest << ","
              << "src:" << src_string.str() << ","
              << "seqno:" << seqno << ","
              << "time:" << time << ","
              << "type:" << type;
  return main_string.str();
}

/*
Method for initialising a Frame object from a string representation.

Used to initialise a Frame object from a string that has arrived over the network.
Iterates through the string breaking it up into tokens, and then erasing the tokens from the string.
The src is first ingested as a string and then broken up into a list.

Arguments:
  in_str: A string representation of a frame
Returns:
  void
*/

void Frame::from_string(string &in_str) {
  map<string, string> tokens;
  string delimiter = ",";
  string inner_delimiter = ":";
  string token;
  string key;
  string value;
  size_t pos = 0;
  size_t inner_pos;
  while ((pos = in_str.find(delimiter)) != string::npos) {
    inner_pos = 0;
    token = in_str.substr(0, pos);
    inner_pos = token.find(inner_delimiter);
    // We don't want the inner delimiter in our string
    key = token.substr(0, inner_pos);
    value = token.substr(inner_pos + 1, token.length());
    tokens.insert({key, value});
    in_str.erase(0, pos + delimiter.length());
  }
  // Run one last time for last token
  inner_pos = 0;
  token = in_str.substr(0, pos);
  inner_pos = token.find(inner_delimiter);
  key = token.substr(0, inner_pos);
  value = token.substr(inner_pos + 1, token.length());
  tokens.insert({key, value});
  in_str.erase(0, pos + delimiter.length());

  string src_string;
  try {
    origin = tokens.at("origin");
    dest = tokens.at("dest");
    seqno = atoi(tokens.at("seqno").c_str());
    time = atoi(tokens.at("time").c_str());
    type = static_cast<FrameType>(atoi(tokens.at("type").c_str()));
    src_string = tokens.at("src");
  } catch (const std::out_of_range &oor) {
    cout << "Parsing frame failed, exiting" << endl;
    fflush(stdout);
    exit(1);
  }
  string src_delimiter = ".";
  pos = 0;
  while ((pos = src_string.find(src_delimiter)) != string::npos) {
    token = src_string.substr(0, pos);
    src.push_back(token);
    src_string.erase(0, pos + delimiter.length());
  }
  // One last time for the final name in the string
  token = src_string.substr(0, pos);
  src.push_back(token);
  src_string.erase(0, pos + delimiter.length());
}