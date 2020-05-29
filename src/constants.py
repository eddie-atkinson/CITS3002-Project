"""Module containing constants relied upon by the program
"""
# Keep the seqnos bounded to 32 bits for our C friends
MAX_INT = 4294967295  # 2^32 -1
MAX_PACKET_LEN = 1024
HOST = "127.0.0.1"
KILL_FILE = "killfile"
# Add some colours for pretty printing
ANSI_COLOR_RED = "\x1b[31m"
ANSI_COLOR_GREEN = "\x1b[32m"
ANSI_COLOR_YELLOW = "\x1b[33m"
ANSI_COLOR_BLUE = "\x1b[34m"
ANSI_COLOR_MAGENTA = "\x1b[35m"
ANSI_COLOR_CYAN = "\x1b[36m"
ANSI_COLOR_RESET = "\x1b[0m"
