import time
class Journey:
    string_rep: str
    destination: str
    departure_time: time.struct_time
    arrival_time: time.struct_time

    def __init__(self, string_rep: str, destination: str,
                 departure_time: str, arrival_time: str):

        self.string_rep = string_rep
        self.destination = destination
        self.departure_time = time.strptime(departure_time, "%H:%M") 
        self.arrival_time = time.strptime(arrival_time, "%H:%M")

    def __str__(self):
        return (f"String rep: {self.string_rep}\
                \nDestination: {self.destination}\
                \nDeparture Time: {time.strftime('%H:%M', self.departure_time)}\
                \nArrival Time: {time.strftime('%H:%M', self.arrival_time)}")
