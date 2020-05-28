#include "udp.h"
void process_request_frame(Node &this_node, Frame &in_frame) {
  cout << this_node.name << " received request " << in_frame.to_string()
       << endl;
  cout << "from " << in_frame.src.back() << endl;

  uint16_t out_port = this_node.get_port_from_name(in_frame.src.back());
  if (out_port < 0) {
    cout << "Failed to find " << in_frame.src.back() << " in neighbours list"
         << endl;
    this_node.quit(1);
  }
  if (in_frame.dest == this_node.name) {
    // You've got mail!
    in_frame.src.push_back(this_node.name);
    Frame response_frame = Frame(this_node.name, in_frame.origin, in_frame.src,
                                 in_frame.seqno, in_frame.time, RESPONSE);
    string response_str = response_frame.to_string();
    size_t len = response_str.size();
    struct sockaddr_in to;
    to.sin_family = AF_INET;
    to.sin_port = htons(out_port);
    inet_pton(AF_INET, HOST_IP, &(to.sin_addr));

    sendto(this_node.udp_socket, response_str.c_str(), len, 0,
           (struct sockaddr *)&to, sizeof(to));
  } else if (std::find(in_frame.src.begin(), in_frame.src.end(),
                       this_node.name) == in_frame.src.end()) {
    send_frame_to_neighbours(this_node, in_frame);
  } else {
    // We have a cycle
    in_frame.src.push_back(this_node.name);
    Frame response_frame = Frame(in_frame.dest, in_frame.origin, in_frame.src,
                                 in_frame.seqno, -1, RESPONSE);
    string response_str = response_frame.to_string();
    size_t len = response_str.size();
    struct sockaddr_in to;
    to.sin_family = AF_INET;
    to.sin_port = htons(out_port);
    inet_pton(AF_INET, HOST_IP, &(to.sin_addr));

    sendto(this_node.udp_socket, response_str.c_str(), len, 0,
           (struct sockaddr *)&to, sizeof(to));
  }
}

void process_response_frame(Node &this_node, Frame &in_frame) {
  cout << this_node.name << " received response " << in_frame.to_string()
       << " from " << in_frame.src.back() << endl;
  cout << "Number of response objects we have "
       << this_node.outstanding_frames.size() << endl;
  string src_node = in_frame.src.back();
  // Take ourselves out of the src
  in_frame.src.pop_back();
  Response *resp_obj = NULL;
  list<class Response>::iterator resp;
  for (resp = this_node.outstanding_frames.begin();
       resp != this_node.outstanding_frames.end(); ++resp) {
    if (resp->origin == in_frame.dest && resp->seqno == in_frame.seqno &&
        resp->sender == in_frame.src.back()) {
      resp_obj = &(*resp);
      break;
    }
  }
  if (resp_obj == NULL) {
    cout << "Couldn't find response object for frame " << in_frame.to_string()
         << endl;
    this_node.quit(1);
  }
  if (resp_obj->time == -1 && in_frame.time > 0) {
    // Anything is faster than not getting there at all
    resp_obj->time = in_frame.time;
    resp_obj->stop = src_node;
  } else if (in_frame.time < resp_obj->time && in_frame.time > 0) {
    // We've found a faster route
    resp_obj->time = in_frame.time;
    resp_obj->stop = src_node;
  }
  --resp_obj->remaining_responses;
  if (resp_obj->remaining_responses == 0) {
    if (in_frame.dest == this_node.name) {
      cout << "End of the line, respond to TCP socket" << endl;
      ostringstream arrival_time;
      // string arrival_time;
      // string itinerary;
      ostringstream itinerary;
      arrival_time << "Arrival Time: ";
      itinerary << "Next leg of trip: ";
      if (resp_obj->time < 0) {
        // We couldn't get there
        arrival_time << "couldn't get there";
        itinerary << "None";
      } else {
        time_t epoch_time = time(NULL);
        struct tm *current_time = localtime(&epoch_time);
        int start_time = (current_time->tm_hour * 60) + current_time->tm_min;
        string next_journey =
            this_node.find_itinerary(resp_obj->stop, start_time);
        if (next_journey.size() == 0) {
          cout << "Couldn't find itinerary to return, exiting" << endl;
          this_node.quit(1);
        }
        int hours = resp_obj->time / 60;
        int minutes = resp_obj->time % 60;
        cout << "Hours: " << hours << endl;
        cout << "Minutes: " << minutes << endl;
        arrival_time << hours << ":";
        if (minutes < 10) {
          arrival_time << "0" << minutes;
        } else {
          arrival_time << minutes;
        }
        itinerary << next_journey;
        cout << "Still here" << endl;
      }
      list<string> http_lines({arrival_time.str(), itinerary.str()});
      string http_response = http_string(200, "OK", http_lines);
      int out_socket = this_node.response_sockets[resp_obj->seqno];
      this_node.send_tcp(out_socket, http_response);
      this_node.remove_socket(out_socket);
    } else {
      uint16_t out_port = this_node.get_port_from_name(in_frame.src.back());
      // We're sending the frame on so put ourselves back in the src
      in_frame.src.push_back(this_node.name);
      Frame response_frame =
          Frame(in_frame.origin, resp_obj->origin, in_frame.src,
                resp_obj->seqno, resp_obj->time, RESPONSE);
      string response_str = response_frame.to_string();
      this_node.send_udp(out_port, response_str);
    }
    // Remove response object from outstanding_frame
  }
}

void send_frame_to_neighbours(Node &this_node, Frame &out_frame) {
  cout << "sending frame to neighbours" << endl;
  int sent_frames = 0;
  uint16_t out_port;
  string sender_name;
  if (out_frame.origin == this_node.name) {
    sender_name = this_node.name;
  } else {
    sender_name = out_frame.src.back();
  }
  out_frame.src.push_back(this_node.name);
  int start_time;
  if (out_frame.time == -1) {
    start_time = current_time();
    cout << "Start time for " << this_node.name << " " << start_time << endl;
  } else {
    start_time = out_frame.time;
  }
  std::unordered_set<string> src_set;
  // Add src list to set for (almost) constant time checks
  std::copy(out_frame.src.begin(), out_frame.src.end(),
            std::inserter(src_set, src_set.end()));
  for (auto neighbour : this_node.neighbours) {
    cout << "Inside neighbours loop" << endl;
    if (src_set.find(neighbour.second) == src_set.end()) {
      // We haven't sent the frame here before
      cout << "Looking for journey for " << neighbour.second << endl;
      int arrival_time =
          this_node.find_arrival_time(neighbour.second, start_time);
      if (arrival_time == -1) {
        // Don't send frame if we can't get there today
        continue;
      }
      cout << "Found journey for neighbour sending frame with arrival time "
           << arrival_time << endl;
      out_frame.time = arrival_time;
      string out_str = out_frame.to_string();
      this_node.send_udp(neighbour.first, out_str);
      cout << this_node.name << " sent frame " << out_str << " to "
           << neighbour.second << endl;
      sent_frames = sent_frames + 1;
    }
  }
  cout << this_node.name << " has sent " << sent_frames << " frames" << endl;

  if (sent_frames == 0) {
    cout << "Sent 0 frames origin of frame is " << out_frame.origin << endl;
    if (out_frame.origin == this_node.name) {
      // We can't get anywhere today, respond to browser
      cout << "Sending rejection to browser" << endl;
      int out_socket = this_node.response_sockets[out_frame.seqno];
      list<string> http_strings(
          {"Arrival time at destination: Couldn't get there",
           "Next leg of trip: None"});
      string http_response = http_string(200, "OK", http_strings);
      this_node.send_tcp(out_socket, http_response);
      this_node.remove_socket(out_socket);
    } else {
      // Sending a response to the guy who sent it to us
      Frame response_frame =
          Frame(out_frame.dest, out_frame.origin, out_frame.src,
                out_frame.seqno, -1, RESPONSE);
      out_port = this_node.get_port_from_name(sender_name);
      string response_str = response_frame.to_string();
      this_node.send_udp(out_port, response_str);
    }
  } else {
    // We need to keep a track of the frames we sent out
    Response outstanding_response =
        Response(sent_frames, sender_name, out_frame.origin, out_frame.seqno);
    this_node.outstanding_frames.push_back(outstanding_response);
  }
}

void process_udp(Node &this_node, string &transmission, uint16_t port) {
  Frame in_frame = Frame();
  in_frame.from_string(transmission);
  this_node.check_timetable();
  // for(auto neighbour: this_node.timetables) {
  //   for(auto journey: neighbour.second) {
  //     cout << journey.to_string() << endl;
  //   }
  // }
  if (in_frame.type == NAME_FRAME) {
    this_node.neighbours[port] = in_frame.origin;
  } else if (in_frame.type == REQUEST) {
    process_request_frame(this_node, in_frame);
  } else {
    process_response_frame(this_node, in_frame);
  }
}