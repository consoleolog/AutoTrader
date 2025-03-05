class TradeInfo:
    def __init__(
        self,
        service=None,
        ticker=None,
        price=None,
        status=None,
        updated_at=None,
        created_at=None,
    ):
        self.service = service
        self.ticker = ticker
        self.price = price
        self.status = status
        self.updated_at = updated_at
        self.created_at = created_at

    @classmethod
    def from_df(cls, df):
        return cls(
            service=df["service"],
            ticker=df["ticker"],
            price=df["price"],
            status=df["status"],
            updated_at=df["updated_at"],
            created_at=df["created_at"],
        )

    def to_dict(self):
        return {
            "service": self.service,
            "ticker": self.ticker,
            "price": self.price,
            "status": self.status,
            "updated_at": self.updated_at,
            "created_at": self.created_at,
        }
