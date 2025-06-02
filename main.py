# coding=utf-8
"""
# @File       : main.py
# @Time       : 2024/6/13 10:37
# @Author     : forevermessi@foxmail.com
# @Description: 
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import router


if __name__ == '__main__':
    app = FastAPI()
    app.add_middleware(CORSMiddleware,
                       allow_origins=["*"],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"],
                       )
    app.include_router(router.create_router, prefix="/v1/cmdb")
    app.include_router(router.query_router,  prefix="/v1/cmdb")
    app.include_router(router.update_router, prefix="/v1/cmdb")
    app.include_router(router.remove_router, prefix="/v1/cmdb")

    # Define a custom uvicorn logging config
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s,%(msecs)03d] [%(levelname)s] [%(filename)s:%(lineno)s]: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=LOGGING_CONFIG)
