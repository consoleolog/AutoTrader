from typing import Optional

from pandas import DataFrame
from scipy.stats import linregress

from model.const.ema import EMA
from model.const.macd import MACD
from model.const.stage import Stage

def get_stage(data: DataFrame):
    try:
        ema_short,ema_middle,ema_long  = data.iloc[-1][EMA.SHORT], data.iloc[-1][EMA.MID] , data.iloc[-1][EMA.LONG]
        if ema_short > ema_middle > ema_long:
            return Stage.STABLE_INCREASE
        elif ema_middle > ema_short > ema_long:
            return Stage.END_OF_INCREASE
        elif ema_middle > ema_long > ema_short:
            return Stage.START_OF_DECREASE
        elif ema_long > ema_middle > ema_short:
            return Stage.STABLE_DECREASE
        elif ema_long > ema_short > ema_middle:
            return Stage.END_OF_DECREASE
        elif ema_short > ema_long > ema_middle:
            return Stage.START_OF_INCREASE
        else:
            return 0
    except IndexError as err:
        print(err)
        return 0

def get_slope(data) -> Optional[float]:
    if len(data) < 2:
        return None
    x = list(range(len(data)))
    slope, _, _, _, _ = linregress(x, data)
    return slope

def create_sub_data(data: DataFrame) -> DataFrame:
    data[EMA.SHORT] = data["close"].ewm(span=10).mean()
    data[EMA.MID] = data["close"].ewm(span=20).mean()
    data[EMA.LONG] = data["close"].ewm(span=60).mean()

    data[MACD.UP] = data[EMA.SHORT] - data[EMA.MID]
    data[MACD.MID] = data[EMA.SHORT] - data[EMA.LONG]
    data[MACD.LOW] = data[EMA.MID] - data[EMA.LONG]

    data[MACD.SIGNAL] = data["close"].ewm(span=9).mean()
    data[MACD.UP_HIST] = data[MACD.UP] - data[MACD.SIGNAL]
    data[MACD.MID_HIST] = data[MACD.MID] - data[MACD.SIGNAL]
    data[MACD.LOW_HIST] = data[MACD.LOW] - data[MACD.SIGNAL]
    return data