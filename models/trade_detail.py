class TradeDetail:
    def __init__(
        self,
        service=None,
        ticker=None,
        rsi_over=None,
        stochastic_over=None,
        macd_short_over=None,
        macd_mid_over=None,
        macd_long_over=None,
        created_at=None,
        updated_at=None,
    ):
        self.service = service
        self.ticker = ticker
        self.rsi_over = rsi_over
        self.stochastic_over = stochastic_over
        self.macd_short_over = macd_short_over
        self.macd_mid_over = macd_mid_over
        self.macd_long_over = macd_long_over
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_df(cls, df):
        return cls(
            service=df["service"],
            ticker=df["ticker"],
            rsi_over=df["rsi_over"],
            stochastic_over=df["stochastic_over"],
            macd_short_over=df["macd_short_over"],
            macd_mid_over=df["macd_mid_over"],
            macd_long_over=df["macd_long_over"],
            created_at=df["created_at"],
            updated_at=df["updated_at"],
        )

    def to_dict(self):
        return {
            "service": self.service,
            "ticker": self.ticker,
            "rsi_over": self.rsi_over,
            "stochastic_over": self.stochastic_over,
            "macd_short_over": self.macd_short_over,
            "macd_mid_over": self.macd_mid_over,
            "macd_long_over": self.macd_long_over,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
