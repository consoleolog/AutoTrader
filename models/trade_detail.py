class TradeDetail:
    def __init__(
        self,
        service=None,
        ticker=None,
        rsi_over=None,
        rsi_time=None,
        stochastic_over=None,
        stochastic_time=None,
        macd_short_over=None,
        macd_short_time=None,
        macd_mid_over=None,
        macd_mid_time=None,
        macd_long_over=None,
        macd_long_time=None,
        created_at=None,
        updated_at=None,
    ):
        self.service = service
        self.ticker = ticker
        self.rsi_over = rsi_over
        self.rsi_time = rsi_time
        self.stochastic_over = stochastic_over
        self.stochastic_time = stochastic_time
        self.macd_short_over = macd_short_over
        self.macd_short_time = macd_short_time
        self.macd_mid_over = macd_mid_over
        self.macd_mid_time = macd_mid_time
        self.macd_long_over = macd_long_over
        self.macd_long_time = macd_long_time
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_df(cls, df):
        return cls(
            service=df["service"],
            ticker=df["ticker"],
            rsi_over=df["rsi_over"],
            rsi_time=df["rsi_time"],
            stochastic_over=df["stochastic_over"],
            stochastic_time=df["stochastic_time"],
            macd_short_over=df["macd_short_over"],
            macd_short_time=df["macd_short_time"],
            macd_mid_over=df["macd_mid_over"],
            macd_mid_time=df["macd_mid_time"],
            macd_long_over=df["macd_long_over"],
            macd_long_time=df["macd_long_time"],
            created_at=df["created_at"],
            updated_at=df["updated_at"],
        )

    def to_dict(self):
        return {
            "service": self.service,
            "ticker": self.ticker,
            "rsi_over": self.rsi_over,
            "rsi_time": self.rsi_time,
            "stochastic_over": self.stochastic_over,
            "stochastic_time": self.stochastic_time,
            "macd_short_over": self.macd_short_over,
            "macd_short_time": self.macd_short_time,
            "macd_mid_over": self.macd_mid_over,
            "macd_mid_time": self.macd_mid_time,
            "macd_long_over": self.macd_long_over,
            "macd_long_time": self.macd_long_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
