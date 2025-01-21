import os

from apscheduler.schedulers.background import BackgroundScheduler
import factory
from model.const.timeframe import TimeFrame


def add_job(tickers):
    for ticker in tickers:
        scheduler.add_job(
            func=factory.exchange_service.trade,
            trigger="interval",
            minutes=5,
            kwargs={
                "ticker": ticker,
                "timeframe": TimeFrame.MINUTE_5
            },
            id=f"{ticker}_{TimeFrame.MINUTE_5}",
        )

        scheduler.add_job(
            func=factory.exchange_service.trade,
            trigger="interval",
            minutes=30,
            kwargs={
                "ticker": ticker,
                "timeframe": TimeFrame.HALF_HOUR
            },
            id=f"{ticker}_{TimeFrame.HALF_HOUR}",
        )

        scheduler.add_job(
            func=factory.exchange_service.trade,
            trigger="interval",
            minutes=60,
            kwargs={
                "ticker": ticker,
                "timeframe": TimeFrame.HOUR
            },
            id=f"{ticker}_{TimeFrame.HOUR}",
        )

        scheduler.add_job(
            func=factory.exchange_service.trade,
            trigger="interval",
            minutes=240,
            kwargs={
                "ticker": ticker,
                "timeframe": TimeFrame.HOUR_4
            },
            id=f"{ticker}_{TimeFrame.HOUR_4}",
        )

scheduler = BackgroundScheduler()
tickers = [
    "BTC/KRW",
    "ETH/KRW",
    "BCH/KRW",
    "AAVE/KRW",
    "SOL/KRW",
    "BSV/KRW",
]
add_job(tickers)

