import time 
import os
import sys
from Journey import Journey
from Node import Node

def check_timetable(this_node: Node) -> None:
    file_name = f"tt-{this_node.name}"
    try:
        stat_info = os.stat(file_name)
        if stat_info.st_mtime > this_node.last_timetable_check:
            print(f"{this_node.name} refreshing timetable")
            last_check = int(time.time())
            # Clear all the old entries
            this_node.timetables.clear()

            with open(file_name, "r") as in_file:
                # We are not interested in the header info
                lines = in_file.readlines()[1:]
                for line in lines:
                    if line.startswith("#"):
                        continue
                    line = line.strip("\n")
                    info = line.split(",")
                    journey = Journey(line, info[-1], info[0], info[-2])
                    if journey.destination not in this_node.timetables.keys():
                        this_node.timetables[journey.destination] = []
                    this_node.timetables[journey.destination].append(journey)
            this_node.last_timetable_check = int(time.time())

        # Just in case the timetables were not in chronological order
        for timetable in this_node.timetables.values():
            timetable.sort(key=lambda x: x.departure_time)

    except FileNotFoundError:
        print(f"{file_name} for node {this_node.name} not found, exiting")
        sys.exit(0)

def find_next_trip(timetable: list, start_time: int) -> Journey:
    next_journey = None
    for journey in timetable:
        if journey.departure_time > start_time:
            next_journey = journey
            break
    return next_journey

