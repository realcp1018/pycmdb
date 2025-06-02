# coding=utf-8
from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime
from .base import CI


class Machine(CI):
    __tablename__ = 'machine'

    uid = Column(String, unique=True, comment="machine unique id")
    ip = Column(String(20), nullable=False, unique=True, comment="machine ip address")
    is_physical = Column(Boolean, default=False, comment="physical machine or virtual machine")
    cpu = Column(Integer, comment="cpu core number")
    memory = Column(Integer, comment="memory(GB)")
    disk = Column(Integer, comment="disk size(GB)")
    is_ssd = Column(Boolean, default=False, comment="is ssd")
