
class RsiInfo:
    def __init__(
        self,
        service=None,
        ticker=None,
        rsi=None,
        rsi_cross=None,
        cross_time=None,
        updated_at=None,
        created_at=None,
    ):
        self.service = service
        self.ticker = ticker
        self.rsi = rsi
        self.rsi_cross = rsi_cross
        self.cross_time = cross_time
        self.updated_at = updated_at
        self.created_at = created_at

    @classmethod
    def from_df(cls, df):
        return cls(
            service=df["service"],
            ticker=df["ticker"],
            rsi=df["rsi"],
            rsi_cross=df["rsi_cross"],
            cross_time=df["cross_time"],
            updated_at=df["updated_at"],
            created_at=df["created_at"],
        )
