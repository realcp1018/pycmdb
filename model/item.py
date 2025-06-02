# coding=utf-8
from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime
from .base import CI


class Item(CI):
    __tablename__ = 'item'

    uid = Column(String, unique=True, comment="item unique id")
    owner = Column(BigInteger, nullable=False, index=True, comment="item owner")
    members = Column(String, comment="item member list")
    level = Column(String(10), nullable=False, default="P1",
                   comment="item level: P1, P2, P3, P4, P5")
