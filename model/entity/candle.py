import uuid
from datetime import datetime

class Candle:
    def __init__(
        self,
        candle_id: str = str(uuid.uuid4()),
        datetime: datetime = datetime.now(),
        ticker: str = None,
        close: float = None,
        timeframe: str = None,
    ):
        self.candle_id = candle_id
        self.datetime = datetime
        self.ticker = ticker
        self.close = close
        self.timeframe = timeframe

    def __str__(self):
        return f"""
        Candle(
            candle_id={self.candle_id},
            datetime={self.datetime},
            ticker={self.ticker},
            close={self.close},
            timeframe={self.timeframe}
        )"""