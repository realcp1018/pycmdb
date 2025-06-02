# coding=utf-8
"""
# @File       : update.py
# @Time       : 2024/7/30 18:31
# @Author     : forevermessi@foxmail.com
# @Description: 
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any
from sqlalchemy.orm import Session
import model    # Do not delete it, used in eval()/exec()
from model import get_db
from logger import MyLogger
from router.common import CommonResponse

update_router = APIRouter()


class UpdateInput(BaseModel):
    model: str = Field(..., alias="Model")
    name: str = Field(..., alias="Name")
    values: Dict[str, Any] = Field(..., alias="Values")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "Model": "Item",
                    "Name": "testItem",
                    "Values": {
                        "notes": "new notes for testItem"
                    }
                }
            ]
        }
    }


@update_router.post('/update', description="update one cmdb entity", response_model=CommonResponse)
def update(q: UpdateInput, db: Session = Depends(get_db)):
    try:
        query = f"db.query(model.{q.model}).filter(model.{q.model}.name == \"{q.name}\").first()"
        MyLogger.info(query)
        entity = eval(query)
        if entity:
            for k, v in q.values.items():
                MyLogger.info(f"--- {q.model}({q.name}) new values: [{k} = {v}]")
                if hasattr(entity, k):
                    setattr(entity, k, v)
                else:
                    raise AttributeError(f"{q.model} has no attribute: {k}")
            db.commit()
        else:
            return CommonResponse(code=400, message=f"{q.model}: {q.name} not exist", data=[], success=False)
    except Exception as e:
        return CommonResponse(code=500, message=str(e), data=[], success=False)
    return CommonResponse(code=200, message="OK", data=[], success=True)