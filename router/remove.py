# coding=utf-8
"""
# @File       : delete.py
# @Time       : 2024/7/30 18:31
# @Author     : forevermessi@foxmail.com
# @Description: 
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import model    # Do not delete it, used in eval()/exec()
from model import get_db
from logger import MyLogger
from router.common import CommonResponse

remove_router = APIRouter()


class RemoveInput(BaseModel):
    model: str = Field(..., alias="Model")
    name: str = Field(..., alias="Name")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "Model": "Item",
                    "Name": "testItem"
                }
            ]
        }
    }


@remove_router.post('/remove', description="delete one cmdb entity", response_model=CommonResponse)
def remove(q: RemoveInput, db: Session = Depends(get_db)):
    try:
        query = f"db.query(model.{q.model}).filter(model.{q.model}.name == \"{q.name}\").first()"
        MyLogger.info(query)
        entity = eval(query)
        if entity:
            MyLogger.info(f"--- {q.model}({q.name}) will be delete")
            db.delete(entity)
            db.commit()
        else:
            return CommonResponse(code=400, message=f"{q.model}: {q.name} not exist", data=[], success=False)
    except Exception as e:
        return CommonResponse(code=500, message=str(e), data=[], success=False)
    return CommonResponse(code=200, message="OK", data=[], success=True)