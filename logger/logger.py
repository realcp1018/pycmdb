# coding=utf-8
"""
# @File       : logger.py
# @Time       : 2024/5/28 16:47
# @Author     : forevermessi@foxmail.com
# @Description:

"""
import logging
import logging.handlers


class FileLogger(logging.Logger):
    def __init__(self, filename=None, log_level=logging.INFO):
        logging.Logger.__init__(self, name="default", level=log_level)
        self.__handler = logging.handlers.RotatingFileHandler(filename=filename, maxBytes=512**3, backupCount=30)
        self.__formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s]: %(message)s")
        self.__handler.setFormatter(self.__formatter)
        self.addHandler(self.__handler)


class StreamLogger(logging.Logger):
    def __init__(self, log_level=logging.INFO):
        logging.Logger.__init__(self, name="default", level=log_level)
        self.__handler = logging.StreamHandler()
        self.__formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s]: %(message)s")
        self.__handler.setFormatter(self.__formatter)
        self.addHandler(self.__handler)