from aioredis import Redis
from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings


async def connect_to_redis(app: FastAPI, settings: AppSettings) -> None:
    """
    connect to rds
    """
    logger.info("Connecting to rds")
    # app.state.rds = await redis_pool(settings)
    from app.rds.redis_client import redis_cli
    app.state.redis = redis_cli
    logger.info("rds Connection established")


async def close_redis_connection(app: FastAPI) -> None:
    """
    close rds connection
    """
    logger.info("Closing connection to rds")
    await app.state.redis.close()
    logger.info("rds Connection closed")
