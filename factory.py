import os
import ccxt
from dotenv import load_dotenv

from database import connection
from module.exchange_module import ExchangeModule
from repository.candle_repository import CandleRepository
from service.candle_service import CandleService
from controller.exchange_controller import ExchangeController

load_dotenv()
exchange = getattr(ccxt, os.getenv("ID"))({
    'apiKey': os.getenv("ACCESS_KEY"),
    'secret': os.getenv("SECRET_KEY")
})
candle_repository = CandleRepository(connection)
candle_service = CandleService(candle_repository)
exchange_module = ExchangeModule(exchange)
exchange_service = ExchangeController(
    exchange_module,
    candle_service
)