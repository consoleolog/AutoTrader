from functools import wraps

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import env
from models import TradeInfo


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
