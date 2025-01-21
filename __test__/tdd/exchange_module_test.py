import os
import unittest

import ccxt
import pandas as pd

from logger import LoggerFactory
from model.dto.ticker_info_dto import TickerInfoDTO
from module.exchange_module import ExchangeModule

KEY_PATH = f"{os.getcwd()}/../../bithumb.key"

class ExchangeModuleTest(unittest.TestCase):
    def setUp(self):
        with open(KEY_PATH) as f:
            lines = f.readlines()
            api_key = lines[0].strip()
            api_secret = lines[1].strip()
            self.exchange = getattr(ccxt, "bithumb")({
                'apiKey': api_key,  # API Key
                'secret': api_secret  # API Secret
            })
            # self.exchange = ccxt.bithumb(config={
            #     'apiKey': api_key,
            #     'secret': api_secret,
            #     'enableRateLimit': True
            # })
        self.logger = LoggerFactory().get_logger(__class__.__name__)
        self.exchange_module = ExchangeModule(self.exchange)

    def test_get_tickers(self):
        tickers = self.exchange.fetch_tickers()
        symbols = tickers.keys()
        krw_symbols = [x for x in symbols if x.endswith('KRW')]
        print(krw_symbols)
        print(len(krw_symbols))

    def test_get_profit(self):
        balances = self.exchange.fetch_balance()
        self.logger.info(balances)
        ticker = "BTC/KRW"
        profit = self.exchange_module.get_profit(ticker)
        self.logger.debug(profit)

    def test_get_current_price(self):
        ticker = "ETH/KRW"
        tickers = self.exchange.fetch_tickers()
        info = tickers[ticker]
        ticker_info_dto = TickerInfoDTO.from_dict(info)
        self.logger.info(ticker_info_dto.__str__())
        self.logger.info(ticker_info_dto.close)
        self.logger.info(type(ticker_info_dto.close))

    def test_get_candles(self):
        ohlcv = self.exchange.fetch_ohlcv(symbol="BTC/KRW", timeframe='4h')

        df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        pd_ts = pd.to_datetime(df['datetime'], utc=True, unit='ms')
        pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
        pd_ts = pd_ts.dt.tz_localize(None)
        df.set_index(pd_ts, inplace=True)
        df = df[['datetime','close']]
        self.logger.info(df)
        self.logger.info(df['close'])
        self.logger.info(type(df))

    def test_get_balances(self):
        balances = self.exchange.fetch_balance()
        self.logger.info(type(balances))
        self.logger.info(balances)
        self.logger.info(balances["BTC"])
        self.logger.info(balances["BTC"]['free'])

    def test_create_buy_order(self):
        ticker = "BSV/KRW"
        response = self.exchange.create_market_buy_order(
            symbol=ticker,
            amount=0.09
        )
        self.logger.info(response)

    def test_create_sell_order(self):
        ticker = "BSV/KRW"

        response = self.exchange.create_market_sell_order(
            symbol=ticker,
            amount=self.exchange_module.get_balance(ticker.replace("/KRW", ""))
        )
        self.logger.info(response)
