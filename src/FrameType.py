"""Enum to represent frame types intuitively
"""
from enum import Enum


class FrameType(Enum):
    """Simple enum representing types of frames as integers
    """

    NAME_FRAME = 0
    REQUEST = 1
    RESPONSE = 2

    def __str__(self):
        """Simple function to represent enum value when printing frames
        """
        return str(self.value)
