"""
Frame class to represent a UDP frame.

#TODO Add full pep8 docs

"""
from FrameType import FrameType


class Frame:
    origin: str = ""
    dest: str = ""
    src: list
    seqno: int = -1
    time: int = -1
    type: FrameType

    def __init__(
        self, origin="", dest="", src=[], seqno=-1, time=-1, type=-1,
    ):
        self.origin = origin
        self.dest = dest
        self.src = src
        self.seqno = seqno
        self.time = time
        self.type = type

    def to_string(self):
        return (
            f"origin:{self.origin},"
            f"dest:{self.dest},"
            f"src:{'.'.join(self.src)},"
            f"seqno:{self.seqno},"
            f"time:{self.time},"
            f"type:{self.type}"
        )

    def to_bytes(self):
        """
        Convert the message to a string, calculate its length, convert the
        string to bytes and concatenate the length as a 32 bit integer on the
        front
        """
        return self.to_string().encode("utf-8")

    def from_string(self, input: str):
        fields = {}
        pairs = input.split(",")
        for pair in pairs:
            split_pair = pair.split(":")
            fields[split_pair[0]] = split_pair[1]

        self.origin = fields["origin"]
        self.dest = fields["dest"]
        self.src = fields["src"].split(".")
        self.seqno = int(fields["seqno"])
        self.time = int(fields["time"])
        self.type = FrameType(int(fields["type"]))
