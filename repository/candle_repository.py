from model.entity.candle import Candle
from model.entity.candle_ema import CandleEMA
from model.entity.candle_macd import CandleMACD

class CandleRepository:
    def __init__(self, connection):
        self.connection = connection

    def insert_candle(self, candle: Candle):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            INSERT INTO CANDLE(
                CANDLE_ID,
                DATETIME,
                TICKER,
                CLOSE,
                TIMEFRAME
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,(candle.candle_id,
                 candle.datetime,
                 candle.ticker,
                 candle.close,
                 candle.timeframe))
        self.connection.commit()

    def insert_candle_ema(self, candle_ema: CandleEMA):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            INSERT INTO CANDLE_EMA(
                CANDLE_ID, 
                SHORT, 
                MID, 
                LONG, 
                STAGE
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,(candle_ema.candle_id,
                 candle_ema.short,
                 candle_ema.mid,
                 candle_ema.long,
                 candle_ema.stage))
        self.connection.commit()

    def insert_candle_macd(self, candle_macd: CandleMACD):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
            INSERT INTO CANDLE_MACD(
                CANDLE_ID, 
                UP, 
                MID,
                LOW, 
                UP_HIST, 
                MID_HIST, 
                LOW_HIST, 
                UP_SLOPE, 
                MID_SLOPE, 
                LOW_SLOPE, 
                SIGNAL
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """, (
                candle_macd.candle_id,
                candle_macd.up,
                candle_macd.mid,
                candle_macd.low,
                candle_macd.up_hist,
                candle_macd.mid_hist,
                candle_macd.low_hist,
                candle_macd.up_slope,
                candle_macd.mid_slope,
                candle_macd.low_slope,
                candle_macd.signal
            ))
        self.connection.commit()