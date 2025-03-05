import numpy as np

import constants as const


class DataGenerator:
    def __init__(self, short_period, mid_period, long_period, rsi_period, timeframe):
        self.s, self.m, self.l = short_period, mid_period, long_period
        self.rsi_p = rsi_period
        self.timeframe = timeframe

    def get_stage(self, data):
        short, mid, long = (
            data[const.EMA.S].iloc[-1],
            data[const.EMA.M].iloc[-1],
            data[const.EMA.L].iloc[-1],
        )

        if short > mid > long:
            return 1
        elif mid > short > long:
            return 2
        elif mid > long > short:
            return 3
        elif long > mid > short:
            return 4
        elif long > short > mid:
            return 5
        elif short > long > mid:
            return 6
        else:
            return 0

    def load(self, ticker, exchange_module=None):
        data = exchange_module.get_candles(ticker, self.timeframe)
        # EMA
        data[const.EMA.S] = EMA(data["close"], self.s)
        data[const.EMA.M] = EMA(data["close"], self.m)
        data[const.EMA.L] = EMA(data["close"], self.l)

        returns = ("val", "signal", "oscillator", "gc", "dc")
        # MACD SHORT
        (
            data[const.MACD.S],
            data[const.MACD.S_S],
            data[const.MACD.S_O],
            data[const.MACD.S_GC],
            data[const.MACD.S_DC],
        ) = MACD(data, self.s, self.m, returns=returns)

        # MACD MIDDLE
        (
            data[const.MACD.M],
            data[const.MACD.M_S],
            data[const.MACD.M_O],
            data[const.MACD.M_GC],
            data[const.MACD.M_DC],
        ) = MACD(data, self.s, self.l, returns=returns)

        # MACD LONG
        (
            data[const.MACD.L],
            data[const.MACD.L_S],
            data[const.MACD.L_O],
            data[const.MACD.L_GC],
            data[const.MACD.L_DC],
        ) = MACD(data, self.m, self.l, returns=returns)

        # RSI
        (
            data[const.RSI.V],
            data[const.RSI.S],
            data[const.RSI.O],
            data[const.RSI.GC],
            data[const.RSI.DC],
        ) = RSI(data, self.rsi_p, returns=returns)

        # Stochastic
        (
            data[const.STOCHASTIC.K_SLOW],
            data[const.STOCHASTIC.D_SLOW],
            data[const.STOCHASTIC.GC],
            data[const.STOCHASTIC.DC],
        ) = Stochastic(data, 14, 3, 3, returns=("k_slow", "d_slow", "gc", "dc"))

        return data


def EMA(data, period):
    return data.ewm(span=period, adjust=False).mean()


def MACD(data, short_period, long_period, signal_period=9, returns=("val",)):
    ShortEMA = EMA(data["close"], short_period)
    LongEMA = EMA(data["close"], long_period)

    val = ShortEMA - LongEMA
    signal = EMA(val, signal_period)
    oscillator = val - signal
    gc = (val.shift(1) < signal.shift(1)) & (val > signal)
    dc = (val.shift(1) > signal.shift(1)) & (val < signal)
    variables = locals()
    return tuple(variables[r] for r in returns)


def RSI(data, period, signal_period=9, returns=("val",)):
    delta = data["close"].diff()
    U = delta.clip(lower=0)
    D = -delta.clip(upper=0)
    AU = U.ewm(com=period - 1, min_periods=1).mean()
    AD = D.ewm(com=period - 1, min_periods=1).mean()

    rs = AU / AD
    rs.replace([np.inf, -np.inf], np.nan, inplace=True)
    rs.fillna(0, inplace=True)

    val = 100 - (100 / (1 + rs))
    signal = EMA(val, signal_period)
    oscillator = val - signal
    gc = (val.shift(1) < signal.shift(1)) & (val > signal)
    dc = (val.shift(1) > signal.shift(1)) & (val < signal)
    variables = locals()
    return tuple(variables[r] for r in returns)


def Stochastic(data, k_len=10, k_smooth=6, d_smooth=6, returns=("k_slow", "d_slow")):
    low_price = data["low"].rolling(window=k_len, min_periods=1).min()
    high_price = data["high"].rolling(window=k_len, min_periods=1).max()
    k_fast = ((data["close"] - low_price) / (high_price - low_price)) * 100.0

    k_slow = k_fast.rolling(window=k_smooth, min_periods=1).mean()
    d_fast = k_fast.rolling(window=k_smooth, min_periods=1).mean()
    d_slow = d_fast.rolling(window=d_smooth, min_periods=1).mean()
    gc = (k_slow.shift(1) < d_slow.shift(1)) & (k_slow > d_slow)
    dc = (k_slow.shift(1) > d_slow.shift(1)) & (k_slow < d_slow)
    variables = locals()
    return tuple(variables[r] for r in returns)
