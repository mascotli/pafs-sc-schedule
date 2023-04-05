import logging
import os
import sys
import time
from typing import Any, Dict, List, Tuple

from loguru import logger
# from pydantic import PostgresDsn, SecretStr

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    env_id: str = "not found"
    PROJECT_NAME: str = "pafs-sc-algorithm"

    # doc
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FastAPI example application"
    version: str = "0.0.0"

    # database
    # database_url: PostgresDsn
    # max_connection_count: int = 10
    # min_connection_count: int = 10

    # secret_key: SecretStr

    # fastapi
    api_prefix: str = "/api"
    jwt_token_prefix: str = "Token"
    allowed_hosts: List[str] = ["*"]

    # logger
    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    # rds
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DATABASE: int

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]

        # 接管所有日志
        logger_name_list = [name for name in logging.root.manager.loggerDict]
        # logger_name_list = [name for name in logging.root.manager.loggerDict if '.' not in name]

        for logger_name in logger_name_list:
            logging.getLogger(logger_name).setLevel(10)
            logging.getLogger(logger_name).handlers = []
            if '.' not in logger_name:
                logging.getLogger(logger_name).addHandler(InterceptHandler())

        # logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])

        # 日志的路径
        log_path = os.path.join(os.path.join(os.getcwd(), os.pardir), 'logs')
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        # 日志输出的文件格式
        from uuid import uuid4
        uid = uuid4()
        log_path_out = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}/out_{uid}.log')
        log_path_error = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}/error_{uid}.log')
        log_path_info = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}/info_{uid}.log')
        log_path_debug = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}/debug_{uid}.log')

        logger.add(log_path_out, rotation="00:00", retention="5 days", enqueue=True, encoding="utf-8")
        logger.add(log_path_info, rotation="00:00", retention="5 days", enqueue=True, encoding="utf-8", level="INFO")
        logger.add(log_path_error, rotation="00:00", retention="5 days", enqueue=True, encoding="utf-8", level="ERROR")
        logger.add(log_path_debug, rotation="00:00", retention="5 days", enqueue=True, encoding="utf-8", level="DEBUG")
