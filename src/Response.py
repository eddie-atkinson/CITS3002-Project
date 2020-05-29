"""Module containing a class used to represent requests forwarded by a node
that need to be responded to
"""


class Response:
    """Class storing essential information about a frame that has been forwarded
    to correctly interpret responses and send them to requesters as necessary.

    Attributes:
        remaining_responses: the number of nodes responses are expected from
        src: a list of nodes the frame has passed through in chronological order
        origin: the node the frame originated with
        seqno: the sequence number applied to the frame at its origin
        time: the best time received in response to the request yet received
        stop: the node from which the fastest response originated 
    """

    remaining_responses: int
    src: list
    origin: str
    seqno: int
    time: int
    stop: str

    def __init__(
        self, remaining_responses: int, src: list, origin: str, seqno: int, time: int, stop: str
    ):
        """Initialises instance
        """
        self.remaining_responses = remaining_responses
        self.src = src
        self.origin = origin
        self.seqno = seqno
        self.time = time
        self.stop = stop

    def __str__(self):
        """Returns a string representation for easy printing
        """
        return (
            f"Remaining Responses: {self.remaining_responses}\n"
            f"SRC: {self.src}\n"
            f"Origin: {self.origin}\n"
            f"Seqno: {self.seqno}\n"
            f"Best time: {self.time}\n"
            f"Best stop: {self.stop}\n"
        )
