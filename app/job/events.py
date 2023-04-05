from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings


async def start_job(app: FastAPI, settings: AppSettings) -> None:
    """
    start job
    """
    logger.info("start job schedule")
    # app.state.rds = await redis_pool(settings)
    from app.job.scheduler import job_scheduler
    app.state.job_scheduler = job_scheduler
    await job_scheduler.start()
    logger.info("started job schedule")


async def stop_job(app: FastAPI) -> None:
    """
    stop job
    """
    logger.info("stop job schedule")
    await app.state.job_scheduler.stop()
    logger.info("stopped job schedule")
