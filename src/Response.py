from Frame import Frame


class Response:
    # Responses we're waiting on before we can respond
    remaining_responses: int
    frame: Frame
    time: int
    stop: str

    def __init__(
        self,
        remaining_responses: int,
        frame: Frame,
        time: int,
        stop: str
    ):
        self.remaining_responses = remaining_responses
        self.frame = frame
        self.time = time
        self.stop = stop
