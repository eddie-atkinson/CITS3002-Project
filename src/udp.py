import time
import socket
from FrameType import FrameType
from Node import Node
from Frame import Frame
from timetable import calc_arrival_time
from timetable import check_timetable
from timetable import find_next_trip
from Journey import Journey
from constants import SECONDS_IN_DAY
from constants import HOST
from util import get_port_from_name
from util import http_string
from Response import Response
from FrameType import FrameType
import sys

def process_udp(
    this_node: Node,
    transmission: tuple
) -> None:
    origin_port = transmission[1][1]
    frame_str = transmission[0].decode("utf-8")
    frame_obj = Frame()
    frame_obj.from_string(frame_str)
    check_timetable(this_node)

    if frame_obj.type == FrameType.NAME_FRAME:
        this_node.neighbours[origin_port] = frame_obj.origin
    elif frame_obj.type == FrameType.REQUEST:
        process_request_frame(this_node, frame_obj)
    else:
        process_response_frame(this_node, frame_obj)
	

def send_frame_to_neighbours(
    this_node: Node,
    out_frame: Frame
) -> None:
    # Add this node to src and push to all neighbours not currently in src
    sent_frames = 0
    out_frame.src.append(this_node.name)
    if out_frame.time == -1:
        time_obj = time.localtime(int(time.time()))
        start_time = (time_obj.tm_hour * 60) + time_obj.tm_min
    else:
        start_time = out_frame.time
    for port, name in this_node.neighbours.items():
        if name not in out_frame.src:
            try:
                timetable = this_node.timetables[name]
                arrival_time = calc_arrival_time(timetable, start_time)
                if arrival_time is None:
                    continue
                out_frame.time = arrival_time
                this_node.udp_socket.sendto(out_frame.to_bytes(), (HOST, port))
                sent_frames += 1
            except KeyError:
                print(f"{this_node.name} failed to find timetable for {name} forwarding frame {out_frame.to_string()}")
            
    
    if sent_frames == 0:
        # Everyone around us has seen this frame
        response_frame = Frame(
            origin=out_frame.dest,
            dest=out_frame.origin,
            src=out_frame.src,
            seqno=out_frame.seqno,
            time=-1,
            type=FrameType.RESPONSE            
        )
        out_port = get_port_from_name(this_node, out_frame.src[-2])
        this_node.udp_socket.sendto(
            response_frame.to_bytes(),
            (HOST, out_port)
        )
    else:
        outstanding_response = Response(
            sent_frames,
            out_frame,
            -1,
            "Nowhere"
        )
        this_node.outstanding_frames.append(outstanding_response)




def process_request_frame(
    this_node: Node,
    in_frame: Frame
) -> None:
    print(
        f"{this_node.name} received request {in_frame.to_string()} from"
        f"{in_frame.src[-1]}"
    )
    out_port = get_port_from_name(this_node, in_frame.src[-1])
    if in_frame.dest == this_node.name:
        in_frame.src.append(this_node.name)
        # You've got mail!
        response_frame = Frame(
            origin=this_node.name,
            dest=in_frame.origin,
            src=in_frame.src,
            seqno=in_frame.seqno,
            time=in_frame.time,
            type=FrameType.RESPONSE
        )
        this_node.udp_socket.sendto(
            response_frame.to_bytes(),
            (HOST, out_port)
        )
    elif this_node.name not in in_frame.src:
        send_frame_to_neighbours(this_node, in_frame)
    else:
        # We have a cycle
        in_frame.src.append(this_node.name)
        response_frame = Frame(
            origin=in_frame.dest,
            dest=in_frame.origin,
            src=in_frame.src,
            seqno=in_frame.seqno,
            time=-1,
            type=FrameType.RESPONSE
        )
        this_node.udp_socket.sendto(
            response_frame.to_bytes(),
            (HOST, out_port)
        )
    return

def process_response_frame(
     this_node: Node,
     in_frame: Frame
 ) -> None:
    print(
        f"{this_node.name} received response {in_frame.to_string()} from"
        f"{in_frame.src[-1]}"
    )
    # unpeel the last node in the src and store it as the next node in the journey
    # compare the seqno, origin and src chain for the frame to see which response object it belongs to
    # compare the time to the stored time and see if it needs changing, if so change the recorded node to be the unpeeled node
    # decrement the appropriate count variable and if the count variable is 0 check the node before you on the src chain and send the response to them
    src_node = in_frame.src.pop(-1)
    response_obj = None
    for resp in this_node.outstanding_frames:
        if (
            resp.frame.dest == in_frame.origin 
            and resp.frame.seqno == in_frame.seqno
            and resp.frame.src == in_frame.src
        ):
            response_obj = resp
            break
    
    if response_obj is None:
        print(
            f"{this_node.name} couldn't find response for frame " 
            f"{in_frame.to_string()}"
        )
        sys.exit(0)

    if response_obj.time == -1 and in_frame.time > 0:
        # Anything is faster than not getting there at all
        response_obj.stop = src_node
        response_obj.time = in_frame.time
    elif in_frame.time < response_obj.time and in_frame.time > 0:
        # We've found a faster route
        response_obj.stop = src_node
        response_obj.time = in_frame.time

    response_obj.remaining_responses -= 1
    if response_obj.remaining_responses == 0:
        if in_frame.dest == this_node.name:
            print(f"End of the line, let's respond to the TCP socket")
            timetable = this_node.timetables[response_obj.stop]
            
            time_obj = time.localtime(int(time.time()))
            start_time = (time_obj.tm_hour * 60) + time_obj.tm_min
            
            next_journey = find_next_trip(timetable, start_time)
            hours = response_obj.time // 60 
            minutes = response_obj.time % 60
            if minutes < 10:
                minutes = f"0{minutes}"
            arrival_time = f"{hours}:{minutes}"
            http_lines = [
                f"Arrival time at destination: {arrival_time}",
                f"Next leg of trip: {next_journey.string_rep}"
            ]
            http_response = http_string(200, "OK", http_lines)
            out_socket = this_node.response_sockets[response_obj.frame.seqno]
            out_socket.send(http_response.encode("utf-8"))
            this_node.input_sockets.remove(out_socket)
            out_socket.shutdown(socket.SHUT_RD)
            out_socket.close()
            
        else:
            response_frame = Frame(
                origin=response_obj.frame.dest,
                dest=response_obj.frame.origin,
                src=in_frame.src,
                seqno=response_obj.frame.seqno,
                time=response_obj.time,
                type=FrameType.RESPONSE
            )    
            out_port = get_port_from_name(this_node, in_frame.src[-2])
            this_node.udp_socket.sendto(
                response_frame.to_bytes(), 
                (HOST, out_port)
            )
            print(f"{this_node.name} responding to {in_frame.src[-2]} with {response_frame.to_string()}")
        this_node.outstanding_frames.remove(response_obj)