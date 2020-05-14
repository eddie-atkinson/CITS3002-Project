import time


class Journey:
    string_rep: str
    destination: str
    departure_time: time.struct_time
    arrival_time: time.struct_time

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
            self.departure_time = time.strptime(departure_time, "%H:%M")
        if arrival_time:
            self.arrival_time = time.strptime(arrival_time, "%H:%M")

    def __str__(self):
        return (
            f"String rep: {self.string_rep}"
            f"\nDestination: {self.destination}"
            f"\nDeparture Time: {time.strftime('%H:%M', self.departure_time)}"
            f"\nArrival Time: {time.strftime('%H:%M', self.arrival_time)}"
        )
