import os
import unittest

import ccxt

from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from module.exchange_module import ExchangeModule

KEY_PATH = f"{os.getcwd()}/../../bithumb.key"

class IntegrationExchangeModuleTest(unittest.TestCase):
    def setUp(self):
        with open(KEY_PATH) as f:
            lines = f.readlines()
            api_key = lines[0].strip()
            api_secret = lines[1].strip()
            print(api_key, api_secret)

            self.exchange = ccxt.bithumb(config={
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True
            })
        self.logger = LoggerFactory().get_logger(__class__.__name__)
        self.exchange_module = ExchangeModule(self.exchange)

    def test_get_balance(self):
        ticker = "BTC"
        b= self.exchange_module.get_balance(ticker)
        self.logger.info(b)
        ticker = "KRW-AAVE"
        self.logger.info(ticker.replace("KRW-", ""))
        self.logger.debug(self.exchange_module.get_balance("BCH"))

    def test_get_candles(self):
        ticker = "ETH/KRW"
        timeframe = TimeFrame.MINUTE_5
        data = self.exchange_module.get_candles(ticker=ticker, timeframe=timeframe)
        self.logger.info(data)