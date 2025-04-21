import argparse
import collections
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

import modules.data_generator as data_arch
import modules.exchange as exchange_arch
import modules.trade_repository as trade_repo_arch
from config import ConfigParser
from trader import Trader


def main(config):
    logger = config.get_logger("server", config["server"]["verbosity"])
    tickers = config["tickers"]

    exchange = config.init_obj("exchange", exchange_arch)
    data_generator = config.init_obj("data_generator", data_arch)
    trade_repository = config.init_obj("trade_repository", trade_repo_arch)
    trader = Trader(
        config=config,
        exchange=exchange,
        data_generator=data_generator,
        trade_repository=trade_repository,
    )

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=trader.loop,
        trigger="interval",
        minutes=config["server"]["interval"],
        kwargs={"tickers": tickers},
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("START UP")
        trader.init_trade_info(tickers)
        scheduler.start()
        yield
        scheduler.shutdown()
        logger.info("SHUT DOWN")

    app = FastAPI(lifespan=lifespan)
    uvicorn.run(app, host=config["host"], port=config["port"])


if __name__ == "__main__":
    args = argparse.ArgumentParser(description="AutoTrader")
    args.add_argument(
        "-c",
        "--config",
        default=None,
        type=str,
        help="config file path (default: None)",
    )
    args.add_argument("-p", "--port", default=8000, type=int, help="Port of Server")
    args.add_argument("--host", default="0.0.0.0", type=str, help="host of fast api")
    CustomArgs = collections.namedtuple("CustomArgs", "flags type target")
    options = [
        CustomArgs(
            ["--sp", "--short_period"],
            type=int,
            target="data_generator;args;short_period",
        ),
        CustomArgs(
            ["--mp", "--middle_period"],
            type=int,
            target="data_generator;args;mid_period",
        ),
        CustomArgs(
            ["--lp", "--long_period"],
            type=int,
            target="data_generator;args;long_period",
        ),
        CustomArgs(
            ["--rp", "--rsi_period"], type=int, target="data_generator;args;rsi_period"
        ),
        CustomArgs(["--kl", "--k_len"], type=int, target="data_generator;args;k_len"),
        CustomArgs(
            ["--ks", "--k_smooth"], type=int, target="data_generator;args;k_smooth"
        ),
        CustomArgs(
            ["--ds", "--d_smooth"], type=int, target="data_generator;args;d_smooth"
        ),
        CustomArgs(
            ["--t", "--timeframe"], type=str, target="data_generator;args;timeframe"
        ),
        CustomArgs(["--s", "--service"], type=str, target="exchange;args;service"),
    ]
    config = ConfigParser.from_args(args, options)
    main(config)
