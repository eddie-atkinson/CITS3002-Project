from Frame import Frame


class Response:
    # Responses we're waiting on before we can respond
    remaining_responses: int
    frame: Frame
    time: int

    def __init__(self, remaining_responses: int, frame: Frame, time: int):
        self.remaining_responses = remaining_responses
        self.frame = frame
        self.time = time
