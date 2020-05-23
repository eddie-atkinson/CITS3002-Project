#include "frame.h"
Frame::Frame(
  const char* origin,
  const char* dest,
  list<string> src,
  int seqno,
  int time,
  FrameType type
): 
origin(origin),
dest(dest),
src(src),
seqno(seqno),
time(time),
type(type) { }

Frame::Frame() {}

string Frame::to_string() {
  std::ostringstream src_string;
  std::ostringstream main_string;
  list<string>::iterator it;
  for(it = src.begin(); it != src.end(); ++it) {
    src_string << *it;
    if(it != --src.end()) {
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

void Frame::from_string(std::string in_str) {
  map<string, string> tokens; 
  string delimiter = ",";
  string inner_delimiter = ":";
  string token;
  string key;
  string value;
  size_t pos = 0; 
  size_t inner_pos;
  while((pos = in_str.find(delimiter)) != string::npos) {
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
  } catch(const std::out_of_range& oor) {
    cout << "Parsing frame failed, exiting" << endl;
    exit(1);
  }
  string src_delimiter = ".";
  pos = 0;
  while((pos = src_string.find(src_delimiter)) != string::npos) {
    string token = src_string.substr(0, pos);
    src.push_back(token);
    src_string.erase(0, pos + delimiter.length());
  }   
}