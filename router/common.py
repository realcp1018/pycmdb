# coding=utf-8
"""
# @File       : reponse.py
# @Time       : 2024/12/6 14:58
# @Author     : forevermessi@foxmail.com
# @Description: 
"""
from pydantic import BaseModel, Field
from typing import List, Any


class CommonResponse(BaseModel):
    code: int = Field(...)
    message: str = Field(...)
    data: List[Any] = Field(...)
    success: bool = Field(...)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": 200,
                    "message": "OK",
                    "data": [],
                    "success": True,
                },
            ]
        }
    }
