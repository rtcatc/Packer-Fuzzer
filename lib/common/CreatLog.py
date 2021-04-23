#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import logging,time,os
from lib.common.utils import Utils
from lib.common.cmdline import CommandLines


"""
1.from lib.common.CreatLog import creatLog
2._init_()里加入self.log = creatLog().get_logger()
3.self.log.debug("这里输入日志信息如api接口正常这样的")
4.self.log.info("这里输入print信息")
例如：
try:
    self.log.debug("正常输出信息")
except Exception as e:
    self.log.error("[Err] %s" %e)
需要使用日志记录的地方大致有一下几处：
    输入输出处，无论是从文件输入还是从网络等其他地方输入
    执行命令处
    调用函数处
"""

global log_name,logs #全局变量引用
logs = Utils().creatTag(6)
log_name = "logs" + os.sep + Utils().creatTag(6) + ".log"

class creatLog():

    def __init__(self , logger=None):
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.NOTSET)
        self.log_time = time.strftime("%Y_%m_%d_")

    def info(self, message):
        self.fontColor('\033[0;34m%s\033[0m')
        self.logger.info(message)

    def set_logger(self):
        if not self.logger.handlers:
            self.fh = logging.FileHandler(log_name, "w" ,encoding="utf-8")
            self.fh.setLevel(logging.DEBUG)
            self.chd = logging.StreamHandler()
            if CommandLines().cmd().silent != None:
                self.chd.setLevel(logging.ERROR)  # 设置为notset，可以打印debug、info、warning、error、critical的日志级别
            else: #静默模式不显示INFO
                self.chd.setLevel(logging.INFO)
            self.formatter = logging.Formatter(
                "[%(levelname)s]--%(asctime)s-%(filename)s->%(funcName)s line:%(lineno)d: %(message)s\n")
            self.formatter_info = logging.Formatter()
            self.chd.setFormatter(self.formatter_info)
            self.fh.setFormatter(self.formatter)
            self.logger.addHandler(self.fh)
            self.logger.addHandler(self.chd)

    def get_logger(self):
        creatLog.set_logger(self)
        return self.logger

    def remove_log_handler(self):
        self.logger.removeHandler(self.fh)
        self.logger.removeHandler(self.chd)
        self.fh.close()
        self.chd.close()
