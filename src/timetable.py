import time 
import os
import sys
from Journey import Journey
from Node import Node
from constants import SECONDS_IN_DAY

# def check_timetable(this_node: Node) -> None:
# 	file_name = f"tt-{this_node.name}"
# 	try:
# 		stat_info = os.stat(file_name)
# 		if stat_info.st_mtime > this_node.last_timetable_check:
# 			this_node.last_timetable_check = int(time.time())
# 			this_node.timetables.clear()

# 			with open(file_name, "r") as in_file:
# 				lines = in_file.readlines()[1:]
# 				for line in lines:
# 					line = line.strip("\n")
# 					info = line.split(",")
# 					journey = Journey(
# 						line,
# 						line[-1],
# 						line[0],
# 						line[-2]
# 					)
# 					if journey.destination not in this_node.timetables.keys():
# 						this_node.timetables[journey.destination] = []

# 					this_node.timetables[journey.destination].append(journey)
# 					for timetable in this_node.timetables.values():
# 						timetable.sort(key=lambda x: x.departure_time)
# 	except FileNotFoundError:
# 		print(f"{file_name} for node {this_node.name} not found, exiting")
# 		sys.exit(0)

def check_timetable(this_node: Node) -> None:
    file_name = f"tt-{this_node.name}"
    try:
        stat_info = os.stat(file_name)
        if stat_info.st_mtime > this_node.last_timetable_check:
            print(f"{this_node.name} Refreshing timetable")
            last_check = int(time.time())
            # Clear all the old entries
            this_node.timetables.clear()

            with open(file_name, "r") as in_file:
                # We are not interested in the header info
                lines = in_file.readlines()[1:]
                for line in lines:
                    line = line.strip("\n")
                    info = line.split(",")
                    journey = Journey(line, info[-1], info[0], info[-2])
                    if journey.destination not in this_node.timetables.keys():
                        this_node.timetables[journey.destination] = []
                    this_node.timetables[journey.destination].append(journey)

        # Just in case the timetables were not in chronological order
        for timetable in this_node.timetables.values():
            timetable.sort(key=lambda x: x.departure_time)

    except FileNotFoundError:
        print(f"{file_name} for node {this_node.name} not found, exiting")
        sys.exit(0)


def normalise_time(time_struct: time.struct_time) -> time.struct_time:
    string_rep = f"{time_struct[3]}:{time_struct[4]}"
    return time.strptime(string_rep, "%H:%M")

def find_next_trip(timetable: list, start_time: int) -> Journey:
    local_time = time.localtime(start_time)
    time_obj = normalise_time(local_time)
    # In case there isn't another journey till tomorrow
    next_journey = timetable[0]
    for journey in timetable:
        if journey.departure_time > time_obj:
            next_journey = journey
            break
    return next_journey


def calc_arrival_time(timetable: list, start_time: int) -> int:
    local_time = time.localtime(start_time)
    time_obj = normalise_time(local_time)
    next_journey = find_next_trip(timetable, start_time)
    wait_time = int(
        time.mktime(next_journey.departure_time) - time.mktime(time_obj)
    )
    if wait_time < 0:
        # Next journey is tomorrow
        leaving_time = start_time + (SECONDS_IN_DAY + wait_time)
    else:
        leaving_time = start_time + wait_time
	
    arrival_time = leaving_time + next_journey.duration_in_secs 

    return arrival_time
