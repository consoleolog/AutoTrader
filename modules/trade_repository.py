from functools import wraps

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import env
from models import MacdInfo, RsiInfo, StochasticInfo, TradeInfo


def catch_db_exception(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except psycopg2.Error as e:
            print(e)
            self.conn.rollback()

    return wrapper


class TradeRepository:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=env.database["host"],
            database=env.database["database"],
            user=env.database["user"],
            password=env.database["password"],
            port=env.database["port"],
        )
        self.engine = create_engine(env.database["url"])

    @catch_db_exception
    def init_trade(self, ticker, service):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO TRADE_INFO(TICKER, SERVICE) VALUES (%s, %s);
            INSERT INTO RSI_INFO(TICKER, SERVICE) VALUES (%s, %s);
            INSERT INTO STOCHASTIC_INFO(TICKER, SERVICE) VALUES (%s, %s);
            INSERT INTO MACD_INFO(TICKER, SERVICE) VALUES (%s, %s);
            """,
            (ticker, service, ticker, service, ticker, service, ticker, service),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def refresh_macd(self, ticker, service):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE MACD_INFO
            SET SHORT_CROSS = NULL,
                MID_CROSS = NULL,
                LONG_CROSS = NULL 
            WHERE MACD_INFO.TICKER = %s
            AND MACD_INFO.SERVICE = %s
            """,
            (ticker, service),
        )
        self.conn.commit()
        cur.close()

    def get_info(self, ticker, service):
        query = """
        SELECT I.SERVICE,
               I.TICKER,
               I.PRICE,
               I.STATUS,
               I.UPDATED_AT,
               I.CREATED_AT
        FROM TRADE_INFO AS I
        WHERE I.SERVICE = %(service)s
        AND I.TICKER = %(ticker)s
        """
        data = pd.read_sql(
            query, self.engine, params={"service": service, "ticker": ticker}
        ).iloc[-1]
        return TradeInfo.from_df(data)

    @catch_db_exception
    def rsi_over(self, rsi_info: RsiInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE RSI_INFO
            SET RSI = %s,
                RSI_OVER = %s,
                OVER_TIME = %s
            WHERE RSI_INFO.TICKER = %s
            AND RSI_INFO.SERVICE = %s
            """,
            (
                rsi_info.rsi,
                rsi_info.rsi_over,
                rsi_info.over_time,
                rsi_info.ticker,
                rsi_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def rsi_cross(self, rsi_info: RsiInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE RSI_INFO 
            SET RSI = %s,
                RSI_CROSS = %s,
                CROSS_TIME = %s
            WHERE RSI_INFO.TICKER = %s
            AND RSI_INFO.SERVICE = %s
            """,
            (
                rsi_info.rsi,
                rsi_info.rsi_cross,
                rsi_info.cross_time,
                rsi_info.ticker,
                rsi_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def macd_short(self, macd_info: MacdInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE MACD_INFO
            SET SHORT_CROSS = %s,
                SHORT_TIME = %s
            WHERE MACD_INFO.TICKER = %s
            AND MACD_INFO.SERVICE = %s
            """,
            (
                macd_info.short_cross,
                macd_info.short_time,
                macd_info.ticker,
                macd_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def macd_mid(self, macd_info: MacdInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE MACD_INFO
            SET MID_CROSS = %s,
                MID_TIME = %s
            WHERE MACD_INFO.TICKER = %s
            AND MACD_INFO.SERVICE = %s
            """,
            (
                macd_info.mid_cross,
                macd_info.mid_time,
                macd_info.ticker,
                macd_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def macd_long(self, macd_info: MacdInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE MACD_INFO
            SET LONG_CROSS = %s,
                LONG_TIME = %s
            WHERE MACD_INFO.TICKER = %s
            AND MACD_INFO.SERVICE = %s
            """,
            (
                macd_info.long_cross,
                macd_info.long_time,
                macd_info.ticker,
                macd_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def stochastic_over(self, stochastic_info: StochasticInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE STOCHASTIC_INFO
            SET K_SLOW = %s,
                D_SLOW = %s,
                STOCHASTIC_OVER = %s,
                OVER_TIME = %s
            WHERE STOCHASTIC_INFO.TICKER = %s
            AND STOCHASTIC_INFO.SERVICE = %s
            """,
            (
                stochastic_info.k_slow,
                stochastic_info.d_slow,
                stochastic_info.stochastic_over,
                stochastic_info.over_time,
                stochastic_info.ticker,
                stochastic_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def stochastic_cross(self, stochastic_info: StochasticInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE STOCHASTIC_INFO
            SET K_SLOW = %s,
                D_SLOW = %s,
                STOCHASTIC_CROSS = %s,
                CROSS_TIME = %s
            WHERE STOCHASTIC_INFO.TICKER = %s
            AND STOCHASTIC_INFO.SERVICE = %s
            """,
            (
                stochastic_info.k_slow,
                stochastic_info.d_slow,
                stochastic_info.stochastic_cross,
                stochastic_info.cross_time,
                stochastic_info.ticker,
                stochastic_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def update_rsi(self, rsi_info: RsiInfo):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE RSI_INFO 
            SET RSI = %s,
                RSI_CROSS = %s,
                CROSS_TIME = %s
            WHERE RSI_INFO.TICKER = %s
            AND RSI_INFO.SERVICE = %s
            """,
            (
                rsi_info.rsi,
                rsi_info.rsi_cross,
                rsi_info.cross_time,
                rsi_info.ticker,
                rsi_info.service,
            ),
        )
        self.conn.commit()
        cur.close()

    def get_rsi(self, ticker, service):
        data = pd.read_sql(
            """
        SELECT R.TICKER,
               R.SERVICE,
               R.RSI,
               R.RSI_OVER,
               R.OVER_TIME,
               R.RSI_CROSS,
               R.CROSS_TIME
        FROM RSI_INFO AS R 
        WHERE R.TICKER = %(ticker)s 
        AND R.SERVICE = %(service)s 
        """,
            self.engine,
            params={"ticker": ticker, "service": service},
        )
        return RsiInfo.from_df(data.iloc[-1])

    def get_stochastic(self, ticker, service):
        data = pd.read_sql(
            """
        SELECT S.TICKER,
               S.SERVICE,
               S.K_SLOW,
               S.D_SLOW,
               S.STOCHASTIC_OVER,
               S.OVER_TIME,
               S.STOCHASTIC_CROSS,
               S.CROSS_TIME
        FROM STOCHASTIC_INFO AS S 
        WHERE S.TICKER = %(ticker)s 
        AND S.SERVICE = %(service)s 
        """,
            self.engine,
            params={"ticker": ticker, "service": service},
        )
        return StochasticInfo.from_df(data.iloc[-1])

    def get_macd(self, ticker, service):
        data = pd.read_sql(
            """
        SELECT M.TICKER,
               M.SERVICE,
               M.SHORT_CROSS,
               M.SHORT_TIME,
               M.MID_CROSS,
               M.MID_TIME,
               M.LONG_CROSS,
               M.LONG_TIME
        FROM MACD_INFO AS M 
        WHERE M.TICKER = %(ticker)s 
        AND M.SERVICE = %(service)s 
        """,
            self.engine,
            params={"ticker": ticker, "service": service},
        )
        return MacdInfo.from_df(data.iloc[-1])

    @catch_db_exception
    def update_trade_info(self, service, ticker, price, status):
        cur = self.conn.cursor()
        cur.execute(
            """
        UPDATE TRADE_INFO
        SET PRICE = %s,
            STATUS = %s,
            UPDATED_AT = NOW()
        WHERE TRADE_INFO.SERVICE = %s
        AND TRADE_INFO.TICKER = %s;
        """,
            (price, status, service, ticker),
        )
        self.conn.commit()
        cur.close()


if __name__ == "__main__":
    repo = TradeRepository()
    rsi = repo.get_rsi("test", "upbit")
    print(rsi.service)
