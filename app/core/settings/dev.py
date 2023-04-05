import logging
import pathlib

from app.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True

    title: str = "Dev FastAPI example application"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = f"{pathlib.Path(__file__).resolve().parent.parent.parent.parent}/.env"
