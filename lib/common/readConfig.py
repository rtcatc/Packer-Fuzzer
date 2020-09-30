# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from configparser import ConfigParser


class ReadConfig(object):

    def __init__(self):
        self.path = os.getcwd() + os.sep + "config.ini"  # 配置文件地址
        self.langPath = os.getcwd() + os.sep + "doc/lang.ini"  # 配置文件地址
        self.config = ConfigParser()
        self.res = []

    def getValue(self, sections, key):
        self.config.read(self.path, encoding="utf-8")
        options = self.config[sections][key]
        self.res.append(options)
        return self.res

    def getLang(self, sections, key):
        self.config.read(self.langPath, encoding="utf-8")
        options = self.config[sections][key]
        self.res.append(options)
        return self.res
