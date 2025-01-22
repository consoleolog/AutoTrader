import os

import pandas as pd
from pandas import DataFrame

from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from model.dto.ticker_info_dto import TickerInfoDTO
from utils import data_utils

class ExchangeModule:
    def __init__(self, exchange):
        self.exchange = exchange
        self.logger = LoggerFactory().get_logger(__class__.__name__)

    def get_ticker_info(self, ticker):
        try:
            params = {"market": ticker}
            info = self.exchange.fetch_ticker(ticker, params)
            return TickerInfoDTO.from_dict(info)
        except Exception as e:
            self.logger.error(f"Error in get_ticker_info: {e}")
            raise

    def get_krw(self):
        balance = self.exchange.fetch_balance()
        return float(balance["KRW"]['free'])

    def create_buy_order(self, ticker, amount):
        self.logger.info(f"""
        {'-'*30}
        매수 
        Ticker : {ticker}
        Amount : {amount}
        {'-'*30}""")
        if os.getenv("ID") == "upbit":
            self.exchange.options['createMarketBuyOrderRequiresPrice'] = False
            return self.exchange.create_market_buy_order(
                symbol=ticker,
                amount=7000,
            )
        return self.exchange.create_market_buy_order(
            symbol=ticker,
            amount=amount
        )

    def create_sell_order(self, ticker, amount):
        self.logger.info(f"""
        {'-'*30}
        매도 
        Ticker : {ticker}
        Amount : {amount}
        {'-'*30}""")
        return self.exchange.create_market_sell_order(
            symbol=ticker,
            amount=amount
        )

    def get_current_price(self, ticker) -> float:
        try:
            ticker_info_dto = self.get_ticker_info(ticker)
            return float(ticker_info_dto.close)
        except KeyError as e:
            self.logger.error(f"Ticker '{ticker}' not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in get_current_price: {e}")
            raise

    def get_avg_price(self, ticker) -> float:
        ticker_info_dto = self.get_ticker_info(ticker)
        return float(ticker_info_dto.average)

    def get_profit(self , ticker) -> float:
        current_price = self.get_current_price(ticker)
        avg_buy_price = self.get_avg_price(ticker)
        return (current_price - avg_buy_price) / avg_buy_price * 100.0

    def get_balance(self, ticker: str) -> float:
        format_ticker = ticker.replace("/KRW", "")
        balances = self.exchange.fetch_balance()
        try:
            balance = balances[format_ticker]
            if balance == 0:
                return 0
            return float(balance['free'])
        except KeyError:
            return 0

    def get_candles(self, ticker, timeframe: TimeFrame) -> DataFrame:
        ohlcv = self.exchange.fetch_ohlcv(symbol=ticker, timeframe=timeframe)
        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        pd_ts = pd.to_datetime(df['datetime'], utc=True, unit='ms')
        pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
        pd_ts = pd_ts.dt.tz_localize(None)
        df.set_index(pd_ts, inplace=True)
        df = df[['datetime','close']]
        data = data_utils.create_sub_data(df)
        return data
