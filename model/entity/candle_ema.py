import uuid


class CandleEMA:
    def __init__(
            self,
            candle_id: str = str(uuid.uuid4()),
            short: float = None,
            mid: float = None,
            long: float = None,
            stage: int = None
    ):
        self.candle_id = candle_id
        self.short = short
        self.mid = mid
        self.long = long
        self.stage = stage

    def __str__(self):
        return f"""
        CandleEMA(
            candle_id={self.candle_id},
            short={self.short},
            mid={self.mid},
            long={self.long},
            stage={self.stage}
        )"""