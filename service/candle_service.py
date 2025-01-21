import uuid
from datetime import datetime

from pandas import DataFrame

from logger import LoggerFactory
from model.const.ema import EMA
from model.const.macd import MACD
from model.entity.candle import Candle
from model.entity.candle_ema import CandleEMA
from model.entity.candle_macd import CandleMACD
from repository.candle_repository import CandleRepository

class CandleService:
    def __init__(self, candle_repository: CandleRepository):
        self.candle_repository = candle_repository
        self.logger = LoggerFactory().get_logger(__class__.__name__)

    def save(self, ticker, timeframe , stage, data: DataFrame, up_slope, mid_slope, low_slope):
        candle_id = str(uuid.uuid4())
        candle = Candle(
            candle_id=candle_id,
            datetime=datetime.now(),
            ticker=ticker,
            close=float(data["close"].iloc[-1]),
            timeframe=timeframe,
        )
        candle_ema = CandleEMA(
            candle_id=candle_id,
            short=float(data[EMA.SHORT].iloc[-1]),
            mid=float(data[EMA.MID].iloc[-1]),
            long=float(data[EMA.LONG].iloc[-1]),
            stage=stage
        )
        candle_macd = CandleMACD(
            candle_id=candle_id,
            up=float(data[MACD.UP].iloc[-1]),
            mid=float(data[MACD.MID].iloc[-1]),
            low=float(data[MACD.LOW].iloc[-1]),
            up_hist=float(data[MACD.UP_HIST].iloc[-1]),
            mid_hist=float(data[MACD.MID_HIST].iloc[-1]),
            low_hist=float(data[MACD.LOW_HIST].iloc[-1]),
            up_slope=float(up_slope),
            mid_slope=float(mid_slope),
            low_slope=float(low_slope),
            signal=float(data[MACD.SIGNAL].iloc[-1]),
        )
        self.candle_repository.insert_many(candle, candle_ema, candle_macd)



