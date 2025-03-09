import time
from functools import wraps

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import env
from models import TradeDetail, TradeInfo


def catch_db_exception(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except psycopg2.Error as e:
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
    def init_trade_info(self, service, ticker):
        cur = self.conn.cursor()
        cur.execute(
            """
        INSERT INTO TRADE_INFO(SERVICE, TICKER)
        VALUES(%s, %s);
        """,
            (service, ticker),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def init_trade_detail(self, service, ticker):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO TRADE_DETAIL(SERVICE, TICKER)
            VALUES(%s, %s);
            """,
            (service, ticker),
        )
        self.conn.commit()
        cur.close()

    @catch_db_exception
    def update_trade_detail(self, service, ticker, data=None):
        cur = self.conn.cursor()
        if data is not None:
            col, val, time = data
            cur.execute(
                f"""
            UPDATE TRADE_DETAIL 
            SET {col.upper()}_OVER = %s,
                {col.upper()}_TIME = %s,
                UPDATED_AT = NOW()
            WHERE TRADE_DETAIL.TICKER = %s 
            AND TRADE_DETAIL.SERVICE = %s 
            """,
                (val, time, ticker, service),
            )
            self.conn.commit()
            cur.close()

    @catch_db_exception
    def refresh_macd(self, service, ticker, timestamp=int(time.time() * 1000)):
        self.update_trade_detail(service, ticker, ("macd_short", None, timestamp))
        self.update_trade_detail(service, ticker, ("macd_mid", None, timestamp))
        self.update_trade_detail(service, ticker, ("macd_long", None, timestamp))

    @catch_db_exception
    def refresh_rsi(self, service, ticker, timestamp=int(time.time() * 1000)):
        self.update_trade_detail(service, ticker, ("rsi", None, timestamp))

    @catch_db_exception
    def refresh_stochastic(self, service, ticker, timestamp=int(time.time() * 1000)):
        self.update_trade_detail(service, ticker, ("stochastic", None, timestamp))

    @catch_db_exception
    def refresh(self, service, ticker, timestamp=int(time.time() * 1000)):
        self.refresh_macd(service, ticker, timestamp)
        self.refresh_rsi(service, ticker, timestamp)
        self.refresh_stochastic(service, ticker, timestamp)

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

    def get_info(self, service, ticker):
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

    def get_detail(self, service, ticker):
        query = """
        SELECT D.SERVICE,
               D.TICKER,
               D.RSI_OVER,
               D.RSI_TIME,
               D.STOCHASTIC_OVER,
               D.STOCHASTIC_TIME,
               D.MACD_SHORT_OVER,
               D.MACD_SHORT_TIME,
               D.MACD_MID_OVER,
               D.MACD_MID_TIME,
               D.MACD_LONG_OVER,
               D.MACD_LONG_TIME, 
               D.CREATED_AT,
               D.UPDATED_AT
        FROM TRADE_DETAIL AS D
        WHERE D.SERVICE = %(service)s
        AND D.TICKER = %(ticker)s
        """
        data = pd.read_sql(
            query, self.engine, params={"service": service, "ticker": ticker}
        ).iloc[-1]
        return TradeDetail.from_df(data)


if __name__ == "__main__":
    repo = TradeRepository()
    repo.update_trade_detail("upbit", "ETH/KRW", ("macd_short_over", True))
