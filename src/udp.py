"""Module responsible for handling UDP communication for a node.

Processes the UDP packets received by a node and forwards them to neighbours, responds,
or sends final responses to TCP clients.
"""
import time
import socket
from FrameType import FrameType
from Node import Node
from Frame import Frame
from timetable import check_timetable
from timetable import find_next_trip
from Journey import Journey
from constants import HOST
from util import get_port_from_name
from util import http_string
from Response import Response


def process_udp(this_node: Node, transmission: tuple) -> None:
    """Processes incoming UDP packets.

    Handles UDP packets by either forwarding them to a node's neighbours, responding
    directly to the sender, or responding to the browser.

    Args:
        this_node: instance of the node class representing a given node in the network.
        transmission: tuple containing the bytes of a UDP packet and origin port
    Returns:
        None
    """
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


def send_frame_to_neighbours(this_node: Node, out_frame: Frame) -> None:
    """Forwards a frame to a node's neighbours if they haven't seen it before.

    Determines whether a neighbour has seen a frame before by checking if they
    are in its src string, if they are not then the frame is forwarded to them.
    If all of a node's neighbours have seen the frame before, a response is immediately
    provided to the sender, whether it be another node or the browser client.

    Args:
        this_node: instance of the node class representing a given node in the network.
        out_frame: Frame object representing the frame to be forwarded.
    Returns:
        None
    """
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
                journey = find_next_trip(timetable, start_time)
                if journey is None:
                    # Don't forward the frame if we can't get to the neighbour
                    continue
                out_frame.time = journey.arrival_time
                this_node.udp_socket.sendto(out_frame.to_bytes(), (HOST, port))
                sent_frames += 1
            except KeyError:
                print(
                    f"{this_node.name} failed to find timetable for {name} forwarding frame {out_frame.to_string()}"
                )

    if sent_frames == 0:
        if out_frame.origin == this_node.name:
            # We can't get anywhere, respond to browser
            out_socket = this_node.response_sockets[out_frame.seqno]
            http_lines = [
                f"Arrival time at destination: Couldn't get there",
                f"Next leg of trip: None",
            ]
            http_response = http_string(200, "OK", http_lines)
            out_socket.send(http_response.encode("utf-8"))
            this_node.input_sockets.remove(out_socket)
            out_socket.shutdown(socket.SHUT_RD)
            out_socket.close()

        else:
            # Everyone around us has seen this frame
            response_frame = Frame(
                origin=out_frame.dest,
                dest=out_frame.origin,
                src=out_frame.src,
                seqno=out_frame.seqno,
                time=-1,
                type=FrameType.RESPONSE,
            )
            out_port = get_port_from_name(this_node, out_frame.src[-2])
            this_node.udp_socket.sendto(response_frame.to_bytes(), (HOST, out_port))
    else:
        outstanding_response = Response(
            sent_frames, out_frame.src, out_frame.origin, out_frame.seqno, -1, "",
        )
        this_node.packet_count += sent_frames
        this_node.outstanding_frames.append(outstanding_response)



def process_request_frame(this_node: Node, in_frame: Frame) -> None:
    """Processes request frames.

    If a frame is received that is destined for the current node, a response is
    sent immediately, if the the request is not destined for the current node and
    it hasn't passed through the current node before it is forwarded to the node's
    neighbours, and if it has passed through the current node before a negative
    response is sent to the sender to squash the cycle. 

    Args:
        this_node: instance of the node class representing a given node in the network.
        in_frame: Frame object representing the request frame to be processed.
    Returns:
        None
    """
    print(f"{this_node.name} received request {in_frame.to_string()} from" f"{in_frame.src[-1]}")
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
            type=FrameType.RESPONSE,
        )
        this_node.udp_socket.sendto(response_frame.to_bytes(), (HOST, out_port))
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
            type=FrameType.RESPONSE,
        )
        this_node.udp_socket.sendto(response_frame.to_bytes(), (HOST, out_port))


def process_response_frame(this_node: Node, in_frame: Frame) -> None:
    """Processes response frames.

    Searches through the list of response objects a node has stored to find the 
    frame the response frame pertains to, adjusts its fastest time if a faster route
    has been found, and decrements its count of responses remaining. If no more responses
    are expected a response frame is sent to the sender, or if the sender was the current
    node a response is sent to the browser.

     Args:
        this_node: instance of the node class representing a given node in the network.
        in_frame: Frame object representing the response frame to be processed.
    Returns:
        None

    """
    print(f"{this_node.name} received response {in_frame.to_string()} from" f"{in_frame.src[-1]}")
    src_node = in_frame.src.pop(-1)
    response_obj = None
    for resp in this_node.outstanding_frames:
        match = resp.origin == in_frame.dest and resp.seqno == in_frame.seqno and resp.src == in_frame.src
        if match:
            response_obj = resp
            break

    if response_obj is None:
        print(f"{this_node.name} couldn't find response for frame " f"{in_frame.to_string()}")
        this_node.quit(1)

    if response_obj.time == -1 and in_frame.time > 0:
        # Anything is faster than not getting there at all
        response_obj.stop = src_node
        response_obj.time = in_frame.time
    elif in_frame.time < response_obj.time and in_frame.time > 0:
        # We've found a faster route
        response_obj.stop = src_node
        response_obj.time = in_frame.time
    (response_obj.remaining_responses) = (response_obj.remaining_responses) - 1
    if response_obj.remaining_responses == 0:
        if in_frame.dest == this_node.name:
            print(f"End of the line, let's respond to the TCP socket")
            if response_obj.time < 0:
                # We couldn't get there
                arrival_time = f"Couldn't get there"
                itinerary = "None"
            else:
                timetable = this_node.timetables[response_obj.stop]
                time_obj = time.localtime(int(time.time()))
                start_time = (time_obj.tm_hour * 60) + time_obj.tm_min
                next_journey = find_next_trip(timetable, start_time)
                hours = response_obj.time // 60
                minutes = response_obj.time % 60
                if minutes < 10:
                    minutes = f"0{minutes}"
                arrival_time = f"{hours}:{minutes}"
                itinerary = next_journey.string_rep
            http_lines = [
                f"Arrival time at destination: {arrival_time}",
                f"Next leg of trip: {itinerary}",
            ]
            http_response = http_string(200, "OK", http_lines)
            out_socket = this_node.response_sockets[response_obj.seqno]
            out_socket.send(http_response.encode("utf-8"))
            this_node.input_sockets.remove(out_socket)
            out_socket.shutdown(socket.SHUT_RD)
            out_socket.close()

        else:
            response_frame = Frame(
                origin=in_frame.origin,
                dest=response_obj.origin,
                src=in_frame.src,
                seqno=response_obj.seqno,
                time=response_obj.time,
                type=FrameType.RESPONSE,
            )
            out_port = get_port_from_name(this_node, in_frame.src[-2])
            this_node.udp_socket.sendto(response_frame.to_bytes(), (HOST, out_port))
            print(
                f"{this_node.name} responding to {in_frame.src[-2]} with {response_frame.to_string()}"
            )
        this_node.outstanding_frames.remove(response_obj)
