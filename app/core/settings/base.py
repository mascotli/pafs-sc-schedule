import pathlib
from enum import Enum
from pathlib import PosixPath, Path

from pydantic import BaseSettings


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"
    stg: str = "stg"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.dev
    root: PosixPath = Path(__file__).parent.absolute()

    class Config:
        env_file = f"{pathlib.Path(__file__).resolve().parent.parent.parent.parent}/.env"
