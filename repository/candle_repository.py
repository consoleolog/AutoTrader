from psycopg2 import DatabaseError

from logger import LoggerFactory
from model.entity.candle import Candle
from model.entity.candle_ema import CandleEMA
from model.entity.candle_macd import CandleMACD
import psycopg2

class CandleRepository:
    def __init__(self, connection):
        self.connection = connection
        self.logger = LoggerFactory().get_logger(__class__.__name__)

    def insert_many(self, candle: Candle, candle_ema: CandleEMA, candle_macd: CandleMACD):
        try:
            with self.connection.cursor() as cursor:
                # 각 테이블에 데이터 삽입
                cursor.execute("""
                    INSERT INTO CANDLE (
                        CANDLE_ID, DATETIME, TICKER, CLOSE, TIMEFRAME
                    ) VALUES (%s, %s, %s, %s, %s);
                    """, (
                    candle.candle_id,
                    candle.datetime,
                    candle.ticker,
                    candle.close,
                    candle.timeframe
                ))

                cursor.execute("""
                    INSERT INTO CANDLE_EMA (
                        CANDLE_ID, SHORT, MID, LONG, STAGE
                    ) VALUES (%s, %s, %s, %s, %s);
                    """, (
                    candle_ema.candle_id,
                    candle_ema.short,
                    candle_ema.mid,
                    candle_ema.long,
                    candle_ema.stage
                ))

                cursor.execute("""
                    INSERT INTO CANDLE_MACD (
                        CANDLE_ID, UP, MID, LOW, UP_HIST, MID_HIST, LOW_HIST, 
                        UP_SLOPE, MID_SLOPE, LOW_SLOPE, SIGNAL
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
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
        except DatabaseError as e:
            self.connection.rollback()  # 트랜잭션 롤백
            self.logger.error(f"Transaction failed and rolled back: {str(e)}")
        except Exception as e:
            self.connection.rollback()  # 일반적인 에러에도 롤백
            self.logger.error(f"Unexpected error: {str(e)}")

    def insert_candle(self, candle: Candle):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
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
                """, (
                    candle.candle_id,
                    candle.datetime,
                    candle.ticker,
                    candle.close,
                    candle.timeframe
                ))
            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()  # 트랜잭션 롤백
            print(f"Error inserting into CANDLE: {e}")
            raise

    def insert_candle_ema(self, candle_ema: CandleEMA):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
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
                """, (
                    candle_ema.candle_id,
                    candle_ema.short,
                    candle_ema.mid,
                    candle_ema.long,
                    candle_ema.stage
                ))
            self.connection.commit()
        except psycopg2.Error as e:
            self.connection.rollback()  # 트랜잭션 롤백
            print(f"Error inserting into CANDLE_EMA: {e}")
            raise

    def insert_candle_macd(self, candle_macd: CandleMACD):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
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
        except psycopg2.Error as e:
            self.connection.rollback()  # 트랜잭션 롤백
            print(f"Error inserting into CANDLE_MACD: {e}")
            raise
