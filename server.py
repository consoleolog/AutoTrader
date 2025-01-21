from contextlib import asynccontextmanager

from fastapi import FastAPI

from scheduler import scheduler
from logger import LoggerFactory

logger = LoggerFactory().get_logger("server")

@asynccontextmanager
async def lifespan(app):
    logger.info("========================")
    logger.info("        START UP        ")
    logger.info("========================")
    scheduler.start()
    yield
app = FastAPI(lifespan=lifespan)


