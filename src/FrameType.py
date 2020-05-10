from enum import Enum


class FrameType(Enum):
    NAME_FRAME = 0
    ACK = 1
    NACK = 2
    DATA = 3

    def __str__(self):
        return(str(self.value))
