from enum import Enum


class FrameType(Enum):
    NAME_FRAME = 0
    REQUEST = 1
    RESPONSE = 2

    def __str__(self):
        return str(self.value)
