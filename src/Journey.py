"""Module containing a class to represent journeys from the timetable files
"""
import time


class Journey:
    """Class representing individual journeys contained within timetable files.

    Used for storing information about journeys between nodes when their timetables
    are parsed.

    Attributes:
        string_rep: string representation of the journey as it appears in the
        timetable file
        destination: name of the node where the trip is going
        departure_time: the time of departure in minutes after midnight
        arrival_time: arrival time at the destination in minutes after midnight
    """

    string_rep: str
    destination: str
    departure_time: int
    arrival_time: int

    def __init__(self, string_rep: str, destination: str, departure_time: str, arrival_time: str):

        """Initialises instance.

        Parses string departure_time and arrival_time to convert them to minutes
        after midnight.
        """
        # Add spaces between the commas to make the str rep nicer
        self.string_rep = ", ".join(string_rep.split(","))
        self.destination = destination
        if departure_time:
            time_split = departure_time.split(":")
            hours = int(time_split[0])
            minutes = int(time_split[1])
            self.departure_time = (hours * 60) + minutes
        if arrival_time:
            time_split = arrival_time.split(":")
            hours = int(time_split[0])
            minutes = int(time_split[1])
            self.arrival_time = (hours * 60) + minutes

    def __str__(self):
        """Returns string representation of journey for easy printing.
        """
        return (
            f"String rep: {self.string_rep}"
            f"\nDestination: {self.destination}"
            f"\nDeparture Time: {time.strftime('%H:%M', self.departure_time)}"
            f"\nArrival time: {self.arrival_time}"
        )
