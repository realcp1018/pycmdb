# coding=utf-8
from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime
from .base import CI


class MySQLCluster(CI):
    __tablename__ = 'mysqlcluster'

    port = Column(Integer, default=3306, comment="cluster port")
    item = Column(BigInteger, comment="cluster item")
    rw_domain = Column(String(50), comment="cluster read-write domain")
    ro_domain = Column(String(50), comment="cluster read-only domain")
    rw_domain_ip = Column(String(50), comment="cluster read-write domain bound IP")
    ro_domain_ip = Column(String(50), comment="cluster read-only domain bound IP")
    version = Column(Integer, comment="cluster version")
    env = Column(String(10), nullable=False, default="prd",
                 comment="cluster env:prd,stg,uat,dev")
    ha_type = Column(String(50), nullable=False,
                     comment="cluster ha type: standalone,master-slave,master-master,mha,orchestrator")
