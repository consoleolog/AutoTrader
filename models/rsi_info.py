class RsiInfo:
    def __init__(
        self,
        ticker=None,
        service=None,
        rsi=None,
        rsi_over=None,
        over_time=None,
        rsi_cross=None,
        cross_time=None,
    ):
        self.ticker = ticker
        self.service = service
        self.rsi = rsi
        self.rsi_over = rsi_over
        self.over_time = over_time
        self.rsi_cross = rsi_cross
        self.cross_time = cross_time

    @classmethod
    def from_df(cls, df):
        return cls(
            ticker=df["ticker"],
            service=df["service"],
            rsi=float(df["rsi"]),
            rsi_over=df["rsi_over"],
            over_time=df["over_time"],
            rsi_cross=df["rsi_cross"],
            cross_time=df["cross_time"],
        )
