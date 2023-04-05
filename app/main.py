from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.redis import redis_router
from app.api.v1 import v1
from app.core.config import settings
from app.core.events import create_stop_app_handler, create_start_app_handler


def get_application():
    # 初始化
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.allowed_hosts],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 初始化相关
    _app.add_event_handler(
        "startup",
        create_start_app_handler(_app, settings),
    )
    _app.add_event_handler(
        "shutdown",
        create_stop_app_handler(_app),
    )

    # 全剧异常捕捉
    # _app.add_exception_handler(HTTPException, http_error_handler)
    # _app.add_exception_handler(RequestValidationError, http422_error_handler)

    # 添加路由
    _app.include_router(v1)
    _app.include_router(redis_router)

    # 初始化监听线程执行任务

    return _app


# 日志配置
settings.configure_logging()


# fastapi app
app = get_application()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
