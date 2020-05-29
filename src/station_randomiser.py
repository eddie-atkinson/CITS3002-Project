#!/usr/bin/python3
"""Simple script for replacing every second line of startstations.sh script
with python servers.

Probably wouldn't have been better implemented in bash, but I hate it.
"""

with open("startstations.sh", "r") as in_file:
    lines = in_file.readlines()
    new_lines = []
    count = 0
    for line in lines:
        if count % 2 == 0:
            line = line.replace("./station", "./station.py")
        count += 1
        new_lines.append(line)

with open("startstations.sh", "w") as out_file:
    for line in new_lines:
        print(line, file=out_file, end="")
