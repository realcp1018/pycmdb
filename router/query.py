# coding=utf-8
"""
# @File       : select.py
# @Time       : 2024/7/30 18:31
# @Author     : forevermessi@foxmail.com
# @Description:
"""
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import Row
from model import get_db
import model  # Do not delete it, used in eval()/exec()
from parser import Request
from typing import List, Dict, Any
from logger import MyLogger

query_router = APIRouter()


class QueryInput(BaseModel):
    models: str = Field(..., alias="Models")
    relations: str = Field(..., alias="Relations")
    fields: str = Field(..., alias="Fields")
    limit: str = Field(None, alias="Limit")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "Models": "i: Item(name=\"testItem\"), u: User",
                    "Relations": "i.owner->u",
                    "Fields": "i.name, u.name, u.status",
                    "Limit": "0,10"
                }
            ]
        }
    }


class QueryResponse(BaseModel):
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
                    "data": [
                        {
                            "i.name": "testItem",
                            "u.name": "leo",
                            "u.status": "online",
                        }
                    ],
                    "success": True,
                }
            ]
        }
    }


@query_router.post('/query', description="query cmdb entities", response_model=QueryResponse)
def query(q: QueryInput, db: Session = Depends(get_db)):
    try:
        request: Request = Request.from_request_body({
            "Models": q.models,
            "Relations": q.relations,
            "Fields": q.fields,
            "Limit": q.limit,
        })
    except Exception as e:
        return QueryResponse(code=500, message=str(e), data=[], success=False)
    query = request.to_orm_query()
    MyLogger.info(query)
    try:
        rows: List[Row] = eval(query)
    except Exception as e:
        return QueryResponse(code=500, message=str(e), data=[], success=False)
    records: List[Dict[str, Any]] = list()
    if len(rows) == 0:
        QueryResponse(code=200, message="no records matched", data=[], success=True)
    for row in rows:
        # the first n=len(request.models) element are ids of models, remove them before return
        records.append(dict(zip(request.fields, row[len(request.models):])))
    return QueryResponse(code=200, message="OK", data=jsonable_encoder(records), success=True)
