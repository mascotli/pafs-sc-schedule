from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings
from app.job.events import start_job, stop_job
# from app.db.events import close_db_connection, connect_to_db
from app.rds.events import close_redis_connection, connect_to_redis


def create_start_app_handler(
    app: FastAPI,
    settings: AppSettings,
) -> Callable:  # type: ignore
    @logger.catch
    async def start_app() -> None:
        # await connect_to_db(app, settings)
        await connect_to_redis(app, settings)
        await start_job(app, settings)

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    @logger.catch
    async def stop_app() -> None:
        # await close_db_connection(app)
        await close_redis_connection(app)
        await stop_job(app)

    return stop_app
