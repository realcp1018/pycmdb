# coding=utf-8
from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime
from .base import CI


class MySQLInstance(CI):
    __tablename__ = 'mysqlinstance'

    machine = Column(Integer, nullable=False, comment="instance machine")
    port = Column(Integer, default=3306, comment="instance port")
    cluster = Column(BigInteger, nullable=False, comment="cluster")
    role = Column(String(10), comment="instance role: Master/Slave/StandAlone/Mixed/Unknown")
    config_path = Column(String(50), comment="path of my.cnf")
