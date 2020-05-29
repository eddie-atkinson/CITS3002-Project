"""Class to store the essential information needed for a UDP frame
"""
from FrameType import FrameType


class Frame:
    """Class to represent a UDP frame.

    Contains the essential components of a UDP frame for communication between stations
    as well methods to convert between string format, byte format and to initiliase an
    instance from a string representation.
    Attributes:
        origin: the name of the origin node for the frame
        dest: the name of the node which is the final destination of the frame
        src: a list containing the names of the nodes the frame has passed through,
        ordered chronologically
        seqno: the sequence number of the frame applied by the origin
        time: the time, in minutes after midnight that the previous sender can arrive
        at the node it is sent to
        type: an enum representing the frames type
    """

    origin: str = ""
    dest: str = ""
    src: list
    seqno: int = -1
    time: int = -1
    type: FrameType

    def __init__(self, origin="", dest="", src=[], seqno=-1, time=-1, type=-1):
        """Inits Frame object
        """
        self.origin = origin
        self.dest = dest
        self.src = src
        self.seqno = seqno
        self.time = time
        self.type = type

    def to_string(self):
        """Returns string representation of frame object for printing and conversion
        to bytes.
        """
        return (
            f"origin:{self.origin},"
            f"dest:{self.dest},"
            f"src:{'.'.join(self.src)},"
            f"seqno:{self.seqno},"
            f"time:{self.time},"
            f"type:{self.type}"
        )

    def to_bytes(self):
        """Returns a byte array representing the frame for sending over the network
        """
        return self.to_string().encode("utf-8")

    def from_string(self, in_str: str):
        """Parses the string representation of a frame (that has possibly arrived
        over the network) and fills the fields with the information it contains.
        """
        fields = {}
        pairs = in_str.split(",")
        for pair in pairs:
            split_pair = pair.split(":")
            fields[split_pair[0]] = split_pair[1]

        self.origin = fields["origin"]
        self.dest = fields["dest"]
        self.src = fields["src"].split(".")
        self.seqno = int(fields["seqno"])
        self.time = int(fields["time"])
        self.type = FrameType(int(fields["type"]))
