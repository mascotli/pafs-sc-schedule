import pathlib

from app.core.settings.app import AppSettings


class ProdAppSettings(AppSettings):
    class Config(AppSettings.Config):
        env_file = f"{pathlib.Path(__file__).resolve().parent.parent.parent.parent}/.env.prod"
