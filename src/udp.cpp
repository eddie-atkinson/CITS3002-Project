#include "udp.h"
void process_request_frame(Node &this_node, Frame &in_frame)
{
  cout << this_node.name << " received request " << in_frame.to_string() << endl;
  cout << "from " << in_frame.src.back() << endl;

  uint16_t out_port = this_node.get_port_from_name(in_frame.src.back());
  if (out_port < 0)
  {
    cout << "Failed to find " << in_frame.src.back() << " in neighbours list"
         << endl;
    this_node.quit(1);
  }
  if (in_frame.dest == this_node.name)
  {
    // You've got mail!
    in_frame.src.push_back(this_node.name);
    Frame response_frame = Frame(this_node.name, in_frame.origin, in_frame.src,
                                 in_frame.seqno, in_frame.time, RESPONSE);
    string response_str = response_frame.to_string();
    size_t len = response_str.size();
    struct sockaddr_in to;
    to.sin_family = AF_INET;
    to.sin_port = htons(out_port);
    to.sin_addr.s_addr = HOST;

    sendto(this_node.udp_socket, response_str.c_str(), len, 0,
           (struct sockaddr *)&to, sizeof(to));
  }
}

void process_response_frame() {}

void send_frame_to_neighbours(Node &this_node, Frame &out_frame)
{
  int sent_frames = 0;
  struct sockaddr_in to;
  to.sin_family = AF_INET;
  to.sin_addr.s_addr = HOST;
  string &sender_name = out_frame.src.back();
  out_frame.src.push_back(this_node.name);
  int start_time;
  if (out_frame.time == -1)
  {
    time_t temp_time = time(NULL);
    struct tm *temp_struct = localtime(&temp_time);
    start_time = (temp_struct->tm_hour * 60) + temp_struct->tm_min;
  }
  else
  {
    start_time = out_frame.time;
  }
  std::unordered_set<string> src_set;
  // Add src list to set for (almost) constant time checks
  std::copy(out_frame.src.begin(), out_frame.src.end(),
            std::inserter(src_set, src_set.end()));
  for (auto neighbour : this_node.neighbours)
  {
    if (src_set.find(neighbour.second) == src_set.end())
    {
      // We haven't sent the frame here before
      Journey *next_journey =
          this_node.find_next_trip(neighbour.second, start_time);
      if (next_journey == NULL)
      {
        // Don't send frame if we can't get there today
        continue;
      }
      out_frame.time = next_journey->arrival_time;
      string out_str = out_frame.to_string();
      to.sin_port = htons(neighbour.first);
      if (sendto(this_node.udp_socket, out_str.c_str(), out_str.size(), 0,
                 (struct sockaddr *)&to, sizeof(to)) < 0)
      {
        cout << "Failed to send frame to neighbour" << endl;
        this_node.quit(1);
      }
      cout << this_node.name << " sent frame " << out_str
           << " to " << neighbour.second << endl;
      ++sent_frames;
    }
    if (sent_frames == 0)
    {
      if (out_frame.origin == this_node.name)
      {
        // We can't get anywhere today, respond to browser
        int out_socket = this_node.response_sockets[out_frame.seqno];
        list<string> http_strings(
            {"Arrival time at destination: Couldn't get there",
             "Next leg of trip: None"});
        string http_response = http_string(200, "OK", http_strings);
        if (send(out_socket, http_response.c_str(), http_response.size(), 0) <
            0)
        {
          cout << "Failed to send a frame, exiting" << endl;
          this_node.quit(1);
        }
        this_node.remove_socket(out_socket);
      }
      else
      {
        // Sending a response to the guy who sent it to us
        Frame response_frame =
            Frame(out_frame.dest, out_frame.origin, out_frame.src,
                  out_frame.seqno, -1, RESPONSE);
        uint16_t out_port = this_node.get_port_from_name(sender_name);
        to.sin_port = htons(out_port);
        string response_str = response_frame.to_string();
        if (sendto(this_node.udp_socket, response_str.c_str(),
                   response_str.size(), 0, (struct sockaddr *)&to,
                   sizeof(to)) < 0)
        {
          cout << "Failed to send a frame, exiting" << endl;
          this_node.quit(1);
        }
      }
    }
    else
    {
      // We need to keep a track of the frames we sent out
      Response outstanding_response =
          Response(sent_frames, &out_frame, -1, string());
      this_node.outstanding_frames.push_back(outstanding_response);
    }
  }
}

void process_udp(Node &this_node, string &transmission, uint16_t port)
{
  Frame in_frame = Frame();
  in_frame.from_string(transmission);
  this_node.check_timetable();
  // for(auto neighbour: this_node.timetables) {
  //   for(auto journey: neighbour.second) {
  //     cout << journey.to_string() << endl;
  //   }
  // }
  if (in_frame.type == NAME_FRAME)
  {
    this_node.neighbours[port] = in_frame.origin;
  }
  else if (in_frame.type == REQUEST)
  {
    process_request_frame(this_node, in_frame);
  }
  else
  {
    process_response_frame();
  }
}