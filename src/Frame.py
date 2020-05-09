"""
Frame class to represent a UDP frame.

#TODO Add full pep8 docs
"""


class Frame:
    size: int = 0
    origin: str = ""
    dest: str = ""
    src: str = ""
    seqno: int = -1
    time: int = -1
    type: int = -1

    def __init__(self, origin, dest, seqno, src, time, type):
        self.origin = origin
        self.dest = dest
        self.src = src
        self.seqno = seqno
        self.time = time
        self.type = type

    def to_string(self):
        return(
            f"size:{self.size},"
            f"origin:{self.origin},"
            f"dest:{self.dest},"
            f"src:{self.src},"
            f"seqno:{self.seqno},"
            f"time:{self.time},"
            f"type:{self.type}"
        )

    def to_bytes(self):
        return(self.to_string().encode("utf-8"))
