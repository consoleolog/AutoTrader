

class EMA:
    SHORT = "short"
    MID = "mid"
    LONG = "long"

    def __init__(
        self,
        short: int = 10,
        mid: int = 20,
        long: int = 40,
    ):
        self.short = short
        self.mid = mid
        self.long = long