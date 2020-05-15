import time

class Journey:
    string_rep: str
    destination: str
    departure_time: time.struct_time
    duration_in_secs: int

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
            arrival_time_obj = time.strptime(arrival_time, "%H:%M")
        self.duration_in_secs = int(
            time.mktime(arrival_time_obj) - time.mktime(self.departure_time)
        )

    def __str__(self):
        return (
            f"String rep: {self.string_rep}"
            f"\nDestination: {self.destination}"
            f"\nDeparture Time: {time.strftime('%H:%M', self.departure_time)}"
            f"\nDuration in secs: {self.duration_in_secs}"
        )
