from concurrent.futures import ThreadPoolExecutor
from pprint import pprint

import constants as const
from models import MacdInfo, RsiInfo, StochasticInfo
from modules import DataGenerator, Exchange, TradeRepository


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
        self.stochastic = config["trader"]["stochastic"]
        self.rsi = config["trader"]["rsi"]

        self.price = config["trader"]["price"]

    def update_stochastic(self, ticker, data):
        k_slow, d_slow = (
            float(data[const.STOCHASTIC.K_SLOW].iloc[-1]),
            float(data[const.STOCHASTIC.D_SLOW].iloc[-1]),
        )
        datetime = int(data["datetime"].iloc[-1])
        if (
            k_slow < self.stochastic["over_sold"]
            and d_slow < self.stochastic["over_sold"]
        ):
            stochastic_info = StochasticInfo(
                ticker=ticker,
                k_slow=k_slow,
                d_slow=d_slow,
                service=self.service,
                stochastic_over=const.over_sold,
                over_time=datetime,
            )
            self.trade_repository.stochastic_over(stochastic_info)
        elif (
            k_slow > self.stochastic["over_bought"]
            and d_slow > self.stochastic["over_bought"]
        ):
            stochastic_info = StochasticInfo(
                ticker=ticker,
                service=self.service,
                k_slow=k_slow,
                d_slow=d_slow,
                stochastic_over=const.over_bought,
                over_time=datetime,
            )
            self.trade_repository.stochastic_over(stochastic_info)
        golden_cross, dead_cross = (
            data[const.STOCHASTIC.GC].iloc[-1],
            data[const.STOCHASTIC.DC].iloc[-1],
        )
        if golden_cross:
            stochastic_info = StochasticInfo(
                ticker=ticker,
                service=self.service,
                k_slow=k_slow,
                d_slow=d_slow,
                stochastic_cross=const.golden_cross,
                cross_time=datetime,
            )
            self.trade_repository.stochastic_cross(stochastic_info)
        elif dead_cross:
            stochastic_info = StochasticInfo(
                ticker=ticker,
                service=self.service,
                k_slow=k_slow,
                d_slow=d_slow,
                stochastic_cross=const.dead_cross,
                cross_time=datetime,
            )
            self.trade_repository.stochastic_cross(stochastic_info)
        return k_slow, d_slow

    def update_rsi(self, ticker, data):
        rsi = float(data[const.RSI.V].iloc[-1])
        rsi_gc = data[const.RSI.GC].iloc[-1]
        rsi_dc = data[const.RSI.DC].iloc[-1]
        datetime = int(data["datetime"].iloc[-1])
        if rsi < self.rsi["over_sold"]:
            rsi_info = RsiInfo(
                ticker=ticker,
                service=self.service,
                rsi=rsi,
                rsi_over=const.over_sold,
                over_time=datetime,
            )
            self.trade_repository.rsi_over(rsi_info)
        if rsi > self.rsi["over_bought"]:
            rsi_info = RsiInfo(
                ticker=ticker,
                service=self.service,
                rsi=rsi,
                rsi_over=const.over_bought,
                over_time=datetime,
            )
            self.trade_repository.rsi_over(rsi_info)
        if rsi_gc:
            rsi_info = RsiInfo(
                ticker=ticker,
                service=self.service,
                rsi=rsi,
                rsi_cross=const.golden_cross,
                cross_time=datetime,
            )
            self.trade_repository.rsi_cross(rsi_info)
        if rsi_dc:
            rsi_info = RsiInfo(
                ticker=ticker,
                service=self.service,
                rsi=rsi,
                rsi_cross=const.dead_cross,
                cross_time=datetime,
            )
            self.trade_repository.rsi_cross(rsi_info)
        return rsi

    def update_macd(self, ticker, data):
        short_golden, mid_golden, long_golden = (
            data[const.MACD.S_GC].iloc[-1],
            data[const.MACD.M_GC].iloc[-1],
            data[const.MACD.L_GC].iloc[-1],
        )
        short_dead, mid_dead, long_dead = (
            data[const.MACD.S_DC].iloc[-1],
            data[const.MACD.M_DC].iloc[-1],
            data[const.MACD.L_DC].iloc[-1],
        )
        datetime = int(data["datetime"].iloc[-1])

        if short_dead and mid_dead and long_dead:
            self.trade_repository.refresh_rsi(ticker, self.service)
            self.trade_repository.refresh_stochastic(ticker, self.service)

        # MACD Short
        if short_golden:
            macd_info = MacdInfo(
                ticker=ticker,
                service=self.service,
                short_cross=const.golden_cross,
                short_time=datetime,
            )
            self.trade_repository.macd_short(macd_info)
        elif short_dead:
            macd_info = MacdInfo(
                ticker=ticker,
                service=self.service,
                short_cross=const.dead_cross,
                short_time=datetime,
            )
            self.trade_repository.macd_short(macd_info)

        # MACD Mid
        if mid_golden:
            macd_info = MacdInfo(
                ticker=ticker,
                service=self.service,
                mid_cross=const.golden_cross,
                mid_time=datetime,
            )
            self.trade_repository.macd_mid(macd_info)
        elif mid_dead:
            macd_info = MacdInfo(
                ticker=ticker,
                service=self.service,
                mid_cross=const.dead_cross,
                mid_time=datetime,
            )
            self.trade_repository.macd_mid(macd_info)

        # MACD Long
        if long_golden:
            macd_info = MacdInfo(
                ticker=ticker,
                service=self.service,
                long_cross=const.golden_cross,
                long_time=datetime,
            )
            self.trade_repository.macd_long(macd_info)
        elif long_dead:
            macd_info = MacdInfo(
                ticker=ticker,
                service=self.service,
                long_cross=const.dead_cross,
                long_time=datetime,
            )
            self.trade_repository.macd_long(macd_info)

    def update_args(self, ticker, data):
        rsi = self.update_rsi(ticker, data)
        k_slow, d_slow = self.update_stochastic(ticker, data)
        self.update_macd(ticker, data)
        return rsi, k_slow, d_slow

    def trading(self, ticker):
        result = {}
        data = self.data_generator.load(ticker, exchange_module=self.exchange)
        stage = self.data_generator.get_stage(data)
        result["ticker"], result["stage"] = ticker, stage
        result["rsi"], result["k_slow"], result["d_slow"] = self.update_args(
            ticker, data
        )

        rsi_info = self.trade_repository.get_rsi(ticker, self.service)
        stochastic_info = self.trade_repository.get_stochastic(ticker, self.service)
        macd_info = self.trade_repository.get_macd(ticker, self.service)

        trade_info = self.trade_repository.get_info(ticker, self.service)
        if trade_info.status == "bid":
            buy_condition = all(
                [
                    rsi_info.rsi_over == const.golden_cross,
                    stochastic_info.stochastic_over == const.over_sold,
                    stochastic_info.stochastic_over == const.golden_cross,
                    macd_info.short_cross == const.golden_cross,
                    macd_info.mid_cross == const.golden_cross,
                    macd_info.long_cross == const.golden_cross,
                ]
            )
            if buy_condition:
                self.buy_and_update(ticker)
                return result
        else:
            buy_condition = all(
                [
                    rsi_info.rsi_over == const.over_sold,
                    rsi_info.rsi_cross == const.golden_cross,
                    stochastic_info.stochastic_over == const.over_sold,
                    stochastic_info.stochastic_cross == const.golden_cross,
                    macd_info.short_cross == const.golden_cross,
                    macd_info.mid_cross == const.golden_cross,
                    macd_info.long_cross == const.golden_cross,
                ]
            )
            if buy_condition :
                self.buy_and_update(ticker)
                return result

        balance = self.exchange.get_balance(ticker)
        if balance != 0:
            profit = self.get_profit(ticker)
            result["profit"] = profit

            root_sell_condition = all(
                [
                    stochastic_info.stochastic_over == const.over_bought,
                    rsi_info.rsi_over == const.over_bought,
                ]
            )
            if root_sell_condition and stage == 1:
                self.sell_and_update(ticker, balance)
                return result

            if profit < 0 and stage == 1 and all([
                stochastic_info.stochastic_over == const.over_bought,
                stochastic_info.stochastic_cross == const.dead_cross,
            ]):
                self.sell_and_update(ticker, profit)
                return result

            if profit > 0.1 and any([
                stochastic_info.stochastic_over == const.over_bought,
                stochastic_info.stochastic_cross == const.dead_cross,
            ]):
                self.sell_and_update(ticker, balance)
                return result
        return result

    def sell_and_update(self, ticker, balance):
        self.trade_repository.update_trade_info(
            self.service, ticker, self.exchange.get_current_price(ticker), "ask"
        )
        self.trade_repository.refresh(ticker, self.service)
        self.exchange.create_sell_order(ticker, balance)

    def buy_and_update(self, ticker):
        trade_info = self.trade_repository.get_info(ticker, self.service)
        self.trade_repository.refresh(ticker, self.service)
        # 추가 매수라면 매수 가격의 평균으로 업데이트
        if trade_info.status == "bid":
            self.trade_repository.update_trade_info(
                self.service,
                ticker,
                (float(trade_info.price) + self.exchange.get_current_price(ticker)) / 2,
                "bid",
            )
            if self.service == "upbit":
                price = self.config["trader"]["price"] * 1.5
            else:
                price = self.config["trader"]["price_key"][ticker] * 1.5
        else:
            self.trade_repository.update_trade_info(
                self.service, ticker, self.exchange.get_current_price(ticker), "bid"
            )
            if self.service == "upbit":
                price = self.config["trader"]["price"]
            else:
                price = self.config["trader"]["price_key"][ticker]

        krw = self.exchange.get_krw()
        if self.service == "upbit" and krw > price:
            self.exchange.create_buy_order(ticker, price)
        elif self.service == "bithumb" and krw > price:
            self.exchange.create_buy_order(ticker, price)

    def loop(self, tickers):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.trading, t) for t in tickers]
        [pprint(f.result()) for f in futures]

    def get_profit(self, ticker):
        trade_info = self.trade_repository.get_info(ticker, self.service)
        buy_price = float(trade_info.price)
        curr_price = self.exchange.get_current_price(ticker)
        return ((curr_price - buy_price) / buy_price) * 100.0

    def init_trade_info(self, tickers):
        if len(tickers) == 1:
            self.trade_repository.init_trade(tickers[0], self.service)
        else:
            for ticker in tickers:
                self.trade_repository.init_trade(ticker, self.service)
