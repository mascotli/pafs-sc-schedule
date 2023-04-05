import json

from fastapi import APIRouter

from app.rds.redis_client import redis_cli
from app.utils import R

redis_router = APIRouter(prefix="/api/redis", tags=["rds"], )


@redis_router.get("/get")
async def get(key: str):
    """
    home
    """
    if not key:
        return R.resp_200(data="key is empty")
    if not redis_cli.exists(key):
        return R.resp_200(data="key is not exist")
    return R.resp_200(data=redis_cli.get(key))
