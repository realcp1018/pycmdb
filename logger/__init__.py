# coding=utf-8
"""
# @File       : __init__.py.py
# @Time       : 2024/8/20 17:17
# @Author     : forevermessi@foxmail.com
# @Description: 
"""
from .logger import FileLogger, StreamLogger

MyLogger = FileLogger(filename="log/cmdb.log")