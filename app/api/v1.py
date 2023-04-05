import json

from fastapi import APIRouter

from app.core import config
from app.utils import R

v1 = APIRouter(prefix="/api/v1", tags=["v1"], )


@v1.get("/home")
async def home():
    """
    home
    """
    return R.resp_200(data="welcome pafs sc algorithm")


@v1.get("/info")
async def info():
    """
    获取配置信息
    """
    return R.resp_200(data=json.loads(json.dumps(config.settings, default=lambda o: o.__dict__)))


@v1.get("/settings")
async def settings():
    """
    获取配置信息
    """
    s = config.get_app_settings()
    return R.resp_200(data=json.loads(json.dumps(s, default=lambda o: o.__dict__)))

