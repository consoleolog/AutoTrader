class MacdInfo:
    def __init__(
        self,
        ticker=None,
        service=None,
        short_cross=None,
        short_time=None,
        mid_cross=None,
        mid_time=None,
        long_cross=None,
        long_time=None,
    ):
        self.ticker = ticker
        self.service = service
        self.short_cross = short_cross
        self.short_time = short_time
        self.mid_cross = mid_cross
        self.mid_time = mid_time
        self.long_cross = long_cross
        self.long_time = long_time

    @classmethod
    def from_df(cls, df):
        return cls(
            ticker=df["ticker"],
            service=df["service"],
            short_cross=df["short_cross"],
            short_time=df["short_time"],
            mid_cross=df["mid_cross"],
            mid_time=df["mid_time"],
            long_cross=df["long_cross"],
            long_time=df["long_time"],
        )
