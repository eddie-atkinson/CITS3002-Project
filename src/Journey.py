import time


class Journey:
    string_rep: str
    destination: str
    departure_time: int
    arrival_time: int

    def __init__(
        self,
        string_rep: str,
        destination: str,
        departure_time: str,
        arrival_time: str,
    ):
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
        return (
            f"String rep: {self.string_rep}"
            f"\nDestination: {self.destination}"
            f"\nDeparture Time: {time.strftime('%H:%M', self.departure_time)}"
            f"\nArrival time: {self.arrival_time}"
        )
