import uuid


class CandleMACD:
    def __init__(
        self,
        candle_id:str = str(uuid.uuid4()),
        up: float = None,
        mid: float = None,
        low : float = None,
        up_hist: float = None,
        mid_hist: float = None,
        low_hist: float = None,
        up_slope: float = None,
        mid_slope: float = None,
        low_slope: float = None,
        signal: float = None,
    ):
        self.candle_id = candle_id
        self.up = up
        self.mid = mid
        self.low = low
        self.up_hist = up_hist
        self.mid_hist = mid_hist
        self.low_hist = low_hist
        self.up_slope = up_slope
        self.mid_slope = mid_slope
        self.low_slope = low_slope
        self.signal = signal

    def __str__(self):
        return f"""
        CandleMACD(
            candle_id={self.candle_id},
            up={self.up},
            mid={self.mid},
            low={self.low},
            up_hist={self.up_hist},
            mid_hist={self.mid_hist},
            low_hist={self.low_hist},
            up_slope={self.up_slope},
            mid_slope={self.mid_slope},
            low_slope={self.low_slope},
            signal={self.signal}
        )"""