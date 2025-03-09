
class StochasticInfo:
    def __init__(
        self,
        service=None,
        ticker=None,
        k_slow=None,
        d_slow=None,
        stochastic_cross=None,
        cross_time=None,
        updated_at=None,
        created_at=None
    ):
        self.service = service
        self.ticker = ticker
        self.k_slow = k_slow
        self.d_slow = d_slow
        self.stochastic_cross = stochastic_cross
        self.cross_time = cross_time
        self.updated_at = updated_at
        self.created_at = created_at

    @classmethod
    def from_df(cls, df):
        return cls(
            service=df["service"],
            ticker=df["ticker"],
            k_slow=df["k_slow"],
            d_slow=df["d_slow"],
            stochastic_cross=df["stochastic_cross"],
            cross_time=df["cross_time"],
            updated_at=df["updated_at"],
            created_at=df["created_at"]
        )