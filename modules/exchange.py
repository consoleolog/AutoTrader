import os 
import ccxt
import pandas as pd
import pyupbit

from config import env
from models import TickerInfo


class Exchange:
    def __init__(self, service):
        self.service = service
        os.environ["ID"] = service
        msg_no_service = "unavailable of this service '{}'".format(service)
        assert service in ["bithumb", "upbit"], msg_no_service
        if service == "upbit":
            self.exchange = ccxt.upbit(
                config={
                    "apiKey": env.accessKey,
                    "secret": env.secretKey,
                    "enableRateLimit": True,
                }
            )
            self.exchange.options["createMarketBuyOrderRequiresPrice"] = False
        elif service == "bithumb":
            self.exchange = ccxt.bithumb(
                config={
                    "apiKey": env.accessKey,
                    "secret": env.secretKey,
                    "enableRateLimit": True,
                }
            )

    def get_ticker_info(self, ticker):
        tickers = self.exchange.fetch_tickers()
        info = tickers[ticker]
        return TickerInfo.from_dict(info)

    def get_krw(self):
        balances = self.exchange.fetch_balance()
        krw = balances["KRW"]
        return float(krw["free"])

    def create_buy_order(self, ticker, amount):
        if self.service == "upbit":
            self.exchange.options["createMarketBuyOrderRequiresPrice"] = False
        return self.exchange.create_market_buy_order(symbol=ticker, amount=amount)

    def create_sell_order(self, ticker, amount):
        return self.exchange.create_market_sell_order(symbol=ticker, amount=amount)

    def get_current_price(self, ticker):
        if self.service == "upbit":
            return pyupbit.get_current_price(_format_ticker(ticker))
        else:
            ticker_info = self.get_ticker_info(ticker)
            return ticker_info.close

    def get_balance(self, ticker):
        try:
            f_ticker = ticker.replace("/KRW", "")
            balances = self.exchange.fetch_balance()
            balance = balances[f_ticker]
            return float(balance["free"])
        except Exception:
            return float(0)

    def get_candles(self, ticker, timeframe):
        ohlcv = self.exchange.fetch_ohlcv(symbol=ticker, timeframe=str(timeframe))
        df = pd.DataFrame(
            ohlcv, columns=["datetime", "open", "high", "low", "close", "volume"]
        )
        pd_ts = pd.to_datetime(df["datetime"], utc=True, unit="ms")
        pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
        pd_ts = pd_ts.dt.tz_localize(None)
        df.set_index(pd_ts, inplace=True)
        df = df[["datetime", "open", "high", "low", "close", "volume"]]
        return df


def _format_ticker(ticker):
    symbol, payment = ticker.split("/")
    return f"{payment}-{symbol}"
