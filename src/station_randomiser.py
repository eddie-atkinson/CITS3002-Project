#!/usr/bin/python3
import random

with open("startstations.sh", "r") as in_file:
    lines = in_file.readlines()
    new_lines = []
    for line in lines:
        if random.uniform(0, 1) > 0.5:
            line = line.replace("./station", "./station.py")
        new_lines.append(line)

with open("startstations.sh", "w") as out_file:
    for line in new_lines:
        print(line, file=out_file, end="")
