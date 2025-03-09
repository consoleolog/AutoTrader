
class MacdInfo:
    def __init__(
            self,
            service=None,
            ticker=None,
            short_cross=None,
            short_cross_time=None,
            mid_cross=None,
            mid_cross_time=None,
            long_cross=None,
            long_cross_time=None,
            updated_at=None,
            created_at=None
    ):
        self.service = service
        self.ticker = ticker
        self.short_cross = short_cross
        self.short_cross_time = short_cross_time
        self.mid_cross = mid_cross
        self.mid_cross_time = mid_cross_time
        self.long_cross = long_cross
        self.long_cross_time = long_cross_time
        self.updated_at = updated_at
        self.created_at = created_at

    @classmethod
    def from_df(cls, df):
        return cls(
            service=df['service'],
            ticker=df['ticker'],
            short_cross=df['short_cross'],
            short_cross_time=df['short_cross_time'],
            mid_cross=df['mid_cross'],
            mid_cross_time=df['mid_cross_time'],
            long_cross=df['long_cross'],
            long_cross_time=df['long_cross_time'],
            updated_at=df['updated_at'],
            created_at=df['created_at'],
        )