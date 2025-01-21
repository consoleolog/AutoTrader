import os

from logger import LoggerFactory
from model.const.macd import MACD
from model.const.stage import Stage
from model.const.timeframe import TimeFrame
from module.exchange_module import ExchangeModule
from service.candle_service import CandleService
from utils import data_utils

class ExchangeController:
    def __init__(
            self,
            exchange_module: ExchangeModule,
            candle_service : CandleService,
    ):
        self.exchange_module = exchange_module
        self.candle_service = candle_service
        self.logger = LoggerFactory().get_logger(__class__.__name__)
        self.price_keys = {
            "BTC/KRW": 0.00005,
            "ETH/KRW": 0.0015,
            "BCH/KRW": 0.011,
            "AAVE/KRW": 0.015,
            "SOL/KRW": 0.02,
            "BSV/KRW": 0.1,
        }


    def _print_report(self, ticker, up, mid, low, stage):
        self.logger.info(f"""
        {'-' * 50}
        Ticker : {ticker}
        Stage  : {stage}
        Up Slope  : {data_utils.get_slope(up.tolist()[-6:])}
        Mid Slope : {data_utils.get_slope(mid.tolist()[-6:])}
        Low Slope : {data_utils.get_slope(low.tolist()[-6:])}
        {'-' * 50}
        """)

    def _print_buy_report(self, ticker, up, mid, low, stage):
        self.logger.info(f"""
        {'-' * 50}
        매수 검토
        Ticker : {ticker}
        Stage  : {stage}
        Up Slope  : {data_utils.get_slope(up.tolist()[-6:])}
        Mid Slope : {data_utils.get_slope(mid.tolist()[-6:])}
        Low Slope : {data_utils.get_slope(low.tolist()[-6:])}
        {'-' * 50}
        """)

    def _print_sell_report(self, ticker, up, mid, low, stage):
        self.logger.info(f"""
        {'-' * 50}
        매도 검토
        Ticker : {ticker}
        Stage  : {stage}
        Up Slope  : {data_utils.get_slope(up.tolist()[-6:])}
        Mid Slope : {data_utils.get_slope(mid.tolist()[-6:])}
        Low Slope : {data_utils.get_slope(low.tolist()[-6:])}
        {'-' * 50}
        """)

    def _print_profit(self, ticker, profit):
        self.logger.info(f"""
        {'-' * 30}
        이익 검토
        Ticker : {ticker}
        Profit : {profit}
        {'-' * 30}
        """)

    def trade(self, ticker: str, timeframe: TimeFrame):
        data = self.exchange_module.get_candles(ticker, timeframe)
        stage = data_utils.get_stage(data)

        volume =  self.exchange_module.get_balance(ticker)

        up, mid, low = data[MACD.UP], data[MACD.MID], data[MACD.LOW]
        up_hist, mid_hist, low_hist = data[MACD.UP_HIST], data[MACD.MID_HIST], data[MACD.LOW_HIST]
        up_slope, mid_slope, low_slope = data_utils.get_slope(up.tolist()[-6:]), data_utils.get_slope(mid.tolist()[-6:]), data_utils.get_slope(low.tolist()[-6:])
        if os.getenv("ID") == "bithumb":
            self.candle_service.save(ticker, timeframe, stage, data, up_slope, mid_slope, low_slope)

        # 매수 검토
        if volume == 0 and self.exchange_module.get_balance("KRW") > 8000:
            # 4, 5, 6 스테이지 일 때 피크아웃 확인
            if stage == Stage.STABLE_DECREASE or stage == Stage.END_OF_DECREASE or stage == Stage.START_OF_INCREASE:
                peekout = all(
                    [up_hist[-10:].min() < 0, up_hist.iloc[-1] < 0, mid_hist[-10:].min() < 0, mid_hist.iloc[-1] < 0,
                     low_hist[-10:].min() < 0, low_hist.iloc[-1] < 0,
                     up_hist[-6:].min() < up_hist.iloc[-1], mid_hist[-6:].min() < mid_hist.iloc[-1],
                     low_hist[-6:].min() < low_hist.iloc[-1]])

                self._print_buy_report(ticker, up, mid, low, stage)
                if peekout and up_slope > low_slope > 30 :
                    res = self.exchange_module.create_buy_order(ticker, self.price_keys[ticker])
                    self.logger.info(res)
                else:
                    return
            else:
                return
        # 매도 검토
        else:
            # 1, 2, 3 스테이지 일 때 기울기 확인
            if stage == Stage.STABLE_INCREASE or stage == Stage.END_OF_INCREASE or stage == Stage.START_OF_DECREASE:
                decrease = all([
                    data_utils.get_slope(up.tolist()[-3:]) < 0,
                    data_utils.get_slope(mid.tolist()[-3:]) < 0
                ])
                self._print_sell_report(ticker, up, mid, low, stage)
                if decrease or (data_utils.get_slope(up.tolist()[-3:]) < data_utils.get_slope(low.tolist()[-3:])):
                    profit = self.exchange_module.get_profit(ticker)
                    self._print_profit(ticker, profit)
                    if profit > 0.1:
                        res = self.exchange_module.create_sell_order(ticker, self.exchange_module.get_balance(ticker))
                        self.logger.info(res)
                    else:
                        return
                else:
                    return
            else:
                return

