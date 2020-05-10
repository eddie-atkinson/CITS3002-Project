from Frame import Frame
from FrameType import FrameType


class Packet:
    frame_bytes: bytes
    port: int
    time: int
    failures: int
    type: FrameType

    def __init__(self, frame_bytes: bytes, port: int,
                 time: int, failures: int, type: FrameType):
        self.frame_bytes = frame_bytes
        self.port = port
        self.time = time
        self.failures = failures
        self.type = type


class DisconnectionError(Exception):
    def __init__(self, msg):
        self.msg = msg
