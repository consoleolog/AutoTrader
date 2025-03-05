from functools import wraps

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import env
from models import TradeInfo, TradeDetail


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
    def update_trade_detail(self, service, ticker, rsi_over=None, stochastic_over=None):
        cur = self.conn.cursor()
        if rsi_over is not None:
            cur.execute("""
            UPDATE TRADE_DETAIL
            SET RSI_OVER = %s,
                UPDATED_AT = NOW()
            WHERE TICKER = %s
            AND SERVICE = %s
            """,(rsi_over, ticker, service)
                        )
        if stochastic_over is not None:
            cur.execute("""
            UPDATE TRADE_DETAIL
            SET STOCHASTIC_OVER = %s,
                UPDATED_AT = NOW()
            WHERE TICKER = %s
            AND SERVICE = %s
            """,(stochastic_over, ticker, service)
            )
        self.conn.commit()
        cur.close()

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
               D.STOCHASTIC_OVER,
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
