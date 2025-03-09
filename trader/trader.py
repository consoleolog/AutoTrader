from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import constants as const
from modules import DataGenerator, Exchange, TradeRepository
from utils import MetricTracker, isin


class Trader:
    def __init__(
        self,
        config,
        exchange: Exchange,
        data_generator: DataGenerator,
        trade_repository: TradeRepository,
    ):
        self.logger = config.get_logger("trader", config["trader"]["verbosity"])
        self.config = config
        self.exchange = exchange
        self.service = exchange.service
        self.data_generator = data_generator
        self.trade_repository = trade_repository

    def check_peekout(self, ticker, data, stage):
        trade_detail = self.trade_repository.get_detail(self.service, ticker)
        short, mid, long = data[const.MACD.S_O], data[const.MACD.M_O], data[const.MACD.L_O]
        if stage in [4, 5, 6]:
            return all([
                short.iloc[-1] < 0,
                mid.iloc[-1] < 0,
                long.iloc[-1] < 0,
                short.iloc[-1] > data.query(f"datetime >= {trade_detail.macd_short_time}")[const.MACD.S_O].min(),
                mid.iloc[-1] > data.query(f"datetime >= {trade_detail.macd_mid_time}")[const.MACD.M_O].min(),
                long.iloc[-1] > data.query(f"datetime >= {trade_detail.macd_long_time}")[const.MACD.L_O].min(),
            ])
        else:
            return all([
                short.iloc[-1] > 0,
                mid.iloc[-1] > 0,
                long.iloc[-1] > 0,
                short.iloc[-1] < data.query(f"datetime >= {trade_detail.macd_short_time}")[const.MACD.S_O].max(),
                mid.iloc[-1] < data.query(f"datetime >= {trade_detail.macd_mid_time}")[const.MACD.M_O].max(),
                long.iloc[-1] < data.query(f"datetime >= {trade_detail.macd_long_time}")[const.MACD.L_O].max(),
            ])

    def update_args(self, ticker, data):
        timestamp = data["datetime"].iloc[-1]
        rsi = data[const.RSI.V].iloc[-1]
        if rsi < 30:
            self.trade_repository.update_trade_info(self.service, ticker, ("rsi", True, timestamp))
        elif rsi > 70:
            self.trade_repository.update_trade_detail(self.service, ticker, ("rsi", False, timestamp))

        k, d = data[const.STOCHASTIC.K_SLOW].iloc[-1], data[const.STOCHASTIC.D_SLOW].iloc[-1]
        if k < 30 and d < 30:
            self.trade_repository.update_trade_detail(self.service, ticker ,("stochastic", True, timestamp))
        elif k > 70 and d > 70:
            self.trade_repository.update_trade_detail(self.service, ticker, ("stochastic", False, timestamp))
            self.trade_repository.refresh_rsi(self.service, ticker)

        short_gc, mid_gc, long_gc = data[const.MACD.S_GC].iloc[-1], data[const.MACD.M_GC].iloc[-1], data[const.MACD.L_GC].iloc[-1]
        if short_gc:
            self.trade_repository.update_trade_detail(self.service, ticker, ("macd_short", True, timestamp))
        if mid_gc:
            self.trade_repository.update_trade_detail(self.service, ticker, ("macd_mid", True, timestamp))
        if long_gc:
            self.trade_repository.update_trade_detail(self.service, ticker, ("macd_long", True, timestamp))

        short_dc, mid_dc, long_dc = data[const.MACD.S_DC].iloc[-1], data[const.MACD.M_DC].iloc[-1], data[const.MACD.L_DC].iloc[-1]
        if short_dc:
            self.trade_repository.update_trade_detail(self.service, ticker, ("macd_short", False, timestamp))
        if mid_dc:
            self.trade_repository.update_trade_detail(self.service, ticker, ("macd_mid", False, timestamp))
        if long_dc:
            self.trade_repository.update_trade_detail(self.service, ticker, ("macd_long", False, timestamp))

        return float(rsi), float(k), float(d)

    def trading(self, ticker):
        result = {}
        data = self.data_generator.load(ticker, self.exchange)
        stage = self.data_generator.get_stage(data)
        result["info"] = f"{ticker.upper()} | {stage}"
        result["rsi"], result["k_slow"], result["d_slow"] = self.update_args(
            ticker, data
        )

        trade_detail = self.trade_repository.get_detail(self.service, ticker)
        golden_cross = all(
            [
                trade_detail.macd_short_over == True,
                trade_detail.macd_mid_over == True,
                trade_detail.macd_long_over == True,
            ]
        )
        trade_into = self.trade_repository.get_info(self.service, ticker)

        # 처음 매수는 rsi 와 stochastic 의 과매도를 확인
        if trade_into.status != "bid":
            if (
                self.check_peekout(ticker, data, stage)
                and golden_cross
                and trade_detail.rsi_over
                and trade_detail.stochastic_over
                and self.exchange.get_krw() > 30000
            ):
                self.buy_and_update(ticker)
                return result
        else:
        # 추가 매수는 stochastic 의 과매도를 확인
            if (
                self.check_peekout(ticker, data, stage)
                and golden_cross
                and trade_detail.stochastic_over
                and self.exchange.get_krw() > 30000
            ):
                self.buy_and_update(ticker)
                return result

        balance = self.exchange.get_balance(ticker)
        if balance != 0:
            profit = self.get_profit(ticker)
            result["profit"] = profit
            stochastic_dc = isin(data[const.STOCHASTIC.DC], True)
            peekout = all(
                [trade_detail.stochastic_over == False, trade_detail.rsi_over == False]
            )
            dead_cross = all(
                [
                    trade_detail.macd_short_over == False,
                    trade_detail.macd_mid_over == False,
                    trade_detail.macd_long_over == False,
                ]
            )
            # -*- 손절 -*-
            if profit < 0 and (stochastic_dc or dead_cross) and stage == 1:
                self.sell_and_update(ticker, balance)
                return result
            # -*- 손절 -*-

            # -*- 익절 -*-
            if peekout and stage == 1:
                self.sell_and_update(ticker, balance)
                return result
            if (
                profit > 0.1
                and (stochastic_dc or dead_cross)
                and stage in [2, 3, 4, 5, 6]
            ):
                self.sell_and_update(ticker, balance)
                return result
            # -*- 익절 -*-
        return result

    def sell_and_update(self, ticker, balance):
        # update price
        self.trade_repository.update_trade_info(
            self.service, ticker, self.exchange.get_current_price(ticker), "ask"
        )
        # refresh macd
        self.trade_repository.refresh()
        self.exchange.create_sell_order(ticker, balance)

    def buy_and_update(self, ticker):
        trade_info = self.trade_repository.get_info(self.service, ticker)

        # 이미 매수 했으면 매수 평균가를 구해서 업데이트
        if trade_info.status == "bid":
            price = (
                float(trade_info.price) + self.exchange.get_current_price(ticker)
            ) / 2
            self.trade_repository.update_trade_info(self.service, ticker, price, "bid")
        else:
            self.trade_repository.update_trade_info(
                self.service, ticker, self.exchange.get_current_price(ticker), "bid"
            )
        self.trade_repository.refresh()

        if self.service == "upbit":
            price = self.config["trader"]["price"]
            self.exchange.create_buy_order(ticker, price)
        elif self.service == "bithumb":
            price_keys = self.config["trader"]["price_key"]
            self.exchange.create_buy_order(ticker, price_keys[ticker])

    def loop(self, tickers):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.trading, t) for t in tickers]
        [pprint(f.result()) for f in futures]

    def get_profit(self, ticker):
        trade_info = self.trade_repository.get_info(self.service, ticker)
        buy_price = float(trade_info.price)
        curr_price = self.exchange.get_current_price(ticker)
        return ((curr_price - buy_price) / buy_price) * 100.0

    def init_trade_info(self, tickers):
        if len(tickers) == 1:
            self.trade_repository.init_trade_info(self.service, tickers[0])
            self.trade_repository.init_trade_detail(self.service, tickers[0])
        else:
            for ticker in tickers:
                self.trade_repository.init_trade_detail(self.service, ticker)
                self.trade_repository.init_trade_info(self.service, ticker)
