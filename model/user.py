# coding=utf-8
from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime
from .base import CI


class User(CI):
    __tablename__ = 'user'

    uid = Column(String, unique=True, comment="user unique id")
    email = Column(String(64), nullable=False, unique=True, comment="email address")
    mobile = Column(String(20), nullable=False,
                    unique=True, comment="phone number")
    dept = Column(String, nullable=False, comment="department name")

