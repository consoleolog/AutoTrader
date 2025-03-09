import time
import unittest

from modules import DataGenerator, Exchange


class DataGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.data_generator = DataGenerator(5, 8, 13, 9, "15m")
        self.exchange = Exchange("upbit")

    def testLoad(self):
        ticker = "BTC/KRW"
        data = self.data_generator.load(ticker, self.exchange)
        # print(data["datetime"])
        print(int(time.time()) * 1000)
        data["datetime"].apply(lambda x: x // 1000)
        print(data.query("datetime >= 1741479300000"))
        print(data.query("datetime >= 1741479300000")["MACD_SHORT"].iloc[-1])
        # 1741496197000
        # 1741479300000
