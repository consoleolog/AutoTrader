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

    def update_args(self, ticker, data):
        rsi, prev_rsi = data[const.RSI.V].iloc[-1], data[const.RSI.V].iloc[-2]
        if rsi < 30:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("rsi_over", True)
            )
        if rsi > 70:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("rsi_over", False)
            )
        k_slow, d_slow = (
            data[const.STOCHASTIC.K_SLOW].iloc[-1],
            data[const.STOCHASTIC.D_SLOW].iloc[-1],
        )
        if k_slow < 30 and d_slow < 30:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("stochastic_over", True)
            )
        if k_slow > 70 and d_slow > 70:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("stochastic_over", False)
            )
        macd_sgc, macd_mgc, macd_lgc = (
            data[const.MACD.S_GC].iloc[-1],
            data[const.MACD.M_GC].iloc[-1],
            data[const.MACD.L_GC].iloc[-1],
        )
        if macd_sgc:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("macd_short_over", True)
            )
        if macd_mgc:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("macd_mid_over", True)
            )
        if macd_lgc:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("macd_long_over", True)
            )
        macd_sdc, macd_mdc, macd_ldc = (
            data[const.MACD.S_DC].iloc[-1],
            data[const.MACD.M_DC].iloc[-1],
            data[const.MACD.L_DC].iloc[-1],
        )
        if macd_sdc:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("macd_short_over", False)
            )
        if macd_mdc:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("macd_mid_over", False)
            )
        if macd_ldc:
            self.trade_repository.update_trade_detail(
                self.service, ticker, ("macd_long_over", False)
            )
        return rsi, k_slow, d_slow

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
        if (
            golden_cross
            and trade_detail.stochastic_over
            and self.exchange.get_krw() > 30000
            and stage in [4, 5, 6]
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
            if profit < 0 and dead_cross and stage not in [1, 2, 3]:
                self.sell_and_update(ticker, balance)
                return result
            # -*- 손절 -*-

            # -*- 익절 -*-
            if profit > 0.1 and peekout and stage == 1:
                self.sell_and_update(ticker, balance)
                return result
            if profit > 0.1 and stochastic_dc and stage in [2, 3, 4, 5, 6]:
                self.sell_and_update(ticker, balance)
                return result
            # -*- 익절 -*-
        return result

    def sell_and_update(self, ticker, balance):
        self.trade_repository.update_trade_info(
            self.service, ticker, self.exchange.get_current_price(ticker), "ask"
        )
        self.trade_repository.update_trade_detail(
            self.service, ticker, ("macd_short_over", None)
        )
        self.trade_repository.update_trade_detail(
            self.service, ticker, ("macd_mid_over", None)
        )
        self.trade_repository.update_trade_detail(
            self.service, ticker, ("macd_long_over", None)
        )
        self.exchange.create_sell_order(ticker, balance)

    def buy_and_update(self, ticker):
        trade_info = self.trade_repository.get_info(self.service, ticker)
        if trade_info.status == "bid":
            price = (
                float(trade_info.price) + self.exchange.get_current_price(ticker)
            ) / 2
            self.trade_repository.update_trade_info(self.service, ticker, price, "bid")
        else:
            self.trade_repository.update_trade_info(
                self.service, ticker, self.exchange.get_current_price(ticker), "bid"
            )
        self.trade_repository.update_trade_detail(
            self.service, ticker, ("macd_short_over", None)
        )
        self.trade_repository.update_trade_detail(
            self.service, ticker, ("macd_mid_over", None)
        )
        self.trade_repository.update_trade_detail(
            self.service, ticker, ("macd_long_over", None)
        )
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
