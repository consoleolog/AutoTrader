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

    def trading(self, ticker):
        result = {}
        data = self.data_generator.load(ticker, self.exchange)
        stage = self.data_generator.get_stage(data)
        result["info"] = f"{ticker.upper()} | {stage}"
        golden_cross = all(
            [
                isin(data[const.MACD.S_GC], True),
                isin(data[const.MACD.M_GC], True),
                isin(data[const.MACD.L_GC], True),
            ]
        )
        rsi, prev_rsi = data[const.RSI.V].iloc[-1], data[const.RSI.V].iloc[-2]
        if rsi < 30:
            self.trade_repository.update_trade_detail(
                self.service, ticker, rsi_over=True
            )
        elif rsi > 70:
            self.trade_repository.update_trade_detail(
                self.service, ticker, rsi_over=False
            )

        k_slow, d_slow = (
            data[const.STOCHASTIC.K_SLOW].iloc[-1],
            data[const.STOCHASTIC.D_SLOW].iloc[-2],
        )
        if k_slow < 30 and d_slow < 30:
            self.trade_repository.update_trade_detail(
                self.service, ticker, stochastic_over=True
            )
        elif k_slow > 70 and d_slow > 70:
            self.trade_repository.update_trade_detail(
                self.service, ticker, stochastic_over=False
            )

        result["GOLDEN_CROSS"], result["RSI"], result["K_SLOW"], result["D_SLOW"] = (
            golden_cross,
            float(rsi),
            float(k_slow),
            float(d_slow),
        )
        trade_detail = self.trade_repository.get_detail(self.service, ticker)
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
            macd_dc = all(
                [
                    isin(data[const.MACD.S_DC], True),
                    isin(data[const.MACD.M_DC], True),
                    isin(data[const.MACD.L_DC], True),
                ]
            )
            if profit < 0 and stage == 1 and (stochastic_dc and macd_dc):
                self.sell_and_update(ticker, balance)
                return result
            if profit > 0.1 and stochastic_dc and stage in [1, 2, 3]:
                self.sell_and_update(ticker, balance)
                return result
            if profit > 0.1 and (stochastic_dc or macd_dc):
                self.sell_and_update(ticker, balance)
                return result
        return result

    def sell_and_update(self, ticker, balance):
        self.trade_repository.update_trade_info(
            self.service, ticker, self.exchange.get_current_price(ticker), "ask"
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
        if self.service == "upbit":
            price = self.config["trader"]["price"]
            self.exchange.create_buy_order(ticker, price)
        elif self.service == "bithumb":
            price_keys = self.config["trader"]["price_keys"]
            self.exchange.create_buy_order(ticker, price_keys[ticker])

    def loop(self, tickers):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.trading, t) for t in tickers]
        result = [pprint(f.result()) for f in futures]
        self.logger.info(result)

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
