# coding=utf-8
"""
# @File       : base.py
# @Time       : 2024/6/7 10:05
# @Author     : forevermessi@foxmail.com
# @Description: orm base model && CI model
"""
import os
from sqlalchemy import create_engine, Column, String, BigInteger, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base

PYCMDB_CONFIG = {
    'host': os.getenv('PYCMDB_HOST', default="127.0.0.1"),
    'port': os.getenv('PYCMDB_PORT', default=3306),
    'user': os.getenv('PYCMDB_USER', default="cmdb_user"),
    'password': os.getenv('PYCMDB_PASSWORD', default="cmdb_password"),
    'database': os.getenv('PYCMDB_DATABASE', default="cmdb")
}

PYCMDB_DB_URL = (
    "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(**PYCMDB_CONFIG))

engine = create_engine(
    PYCMDB_DB_URL,
    connect_args={"charset": "utf8mb4"},
    pool_size=25,         # Initial pool size
    max_overflow=25,      # Max overflow beyond pool_size
    pool_recycle=900,     # Recycle connections every 15 min, this is an alive-check mechanism
    pool_timeout=30,      # Timeout value of retrieving a new connection from the pool
    pool_pre_ping=True    # Enable pre-ping to detect dead connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CI this mode can not be auto-generated, we must define it manually
class CI(Base):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    create_time = Column(DateTime, index=True, default=func.now())
    update_time = Column(DateTime, index=True,
                         default=func.now(), onupdate=func.now())
    status = Column(String(10), nullable=False, default="online")
    notes = Column(String)


if __name__ == '__main__':
    print(PYCMDB_DB_URL)
