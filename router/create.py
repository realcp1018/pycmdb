# coding=utf-8
"""
# @File       : create.py
# @Time       : 2024/7/30 18:32
# @Author     : forevermessi@foxmail.com
# @Description: 
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from sqlalchemy.orm import Session
import model    # Do not delete it, used in eval()/exec()
from model import get_db
from logger import MyLogger
from router.common import CommonResponse

create_router = APIRouter()


class CreateInput(BaseModel):
    model: str = Field(..., alias="Model")
    values: Dict[str, Any] = Field(..., alias="Values")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "Model": "Item",
                    "Values": {"name": "testItem",
                               "owner": 1,
                               "department": 1,
                               "notes": "this is a test item"}
                }
            ]
        }
    }


@create_router.post('/createOne', description="create one cmdb entity", response_model=CommonResponse)
def createOne(q: CreateInput, db: Session = Depends(get_db)):
    try:
        entity = eval(f"model.{q.model}(**{q.values})")
        db.add(entity)
        db.commit()
    except Exception as e:
        return CommonResponse(code=500, message=str(e), data=[], success=False)
    return CommonResponse(code=200, message="OK", data=[], success=True)


@create_router.post('/createMany', description="create multiple cmdb entities", response_model=CommonResponse)
def createMany(q: List[CreateInput], db: Session = Depends(get_db)):
    try:
        for obj in q:
            entity = None
            query = f"entity: model.{obj.model} = model.{obj.model}(**{obj.values})\n"
            MyLogger.info(query)
            exec(query)
            db.add(entity)
        db.commit()
    except Exception as e:
        db.rollback()
        return CommonResponse(code=500, message=f"Error: {str(e)}, all {len(q)} records create failed and rollback",
                              data=[], success=False)
    return CommonResponse(code=200, message="OK", data=[], success=True)
