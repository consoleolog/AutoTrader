

class EMA:
    SHORT = "EMA_SHORT"
    MID = "EMA_MID"
    LONG = "EMA_LONG"

    def __init__(
        self,
        short: int = 10,
        mid: int = 20,
        long: int = 40,
    ):
        self.short = short
        self.mid = mid
        self.long = long