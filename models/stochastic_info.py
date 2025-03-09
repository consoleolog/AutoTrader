
class StochasticInfo:
    def __init__(self,
                 ticker=None,
                 service=None,
                 k_slow=None,
                 d_slow=None,
                 stochastic_over=None,
                 over_time=None,
                 stochastic_cross=None,
                 cross_time=None):
        self.ticker = ticker
        self.service = service
        self.k_slow = k_slow
        self.d_slow = d_slow
        self.stochastic_over = stochastic_over
        self.over_time = over_time
        self.stochastic_cross = stochastic_cross
        self.cross_time = cross_time

    @classmethod
    def from_df(cls, df):
        return cls(
            ticker=df['ticker'],
            service=df['service'],
            k_slow=df['k_slow'],
            d_slow=df['d_slow'],
            stochastic_over=df['stochastic_over'],
            over_time=df['over_time'],
            stochastic_cross=df['stochastic_cross'],
            cross_time=df['cross_time'],
        )
