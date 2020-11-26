# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests, sqlite3, warnings, os
from lib.common.utils import Utils
from lib.Database import DatabaseType


class CheckPacker():

    def __init__(self, projectTag, url, options):
        warnings.filterwarnings('ignore') #不显示警告，后期可以优化为全局的
        self.fingerprint_html = ['<noscript','webpackJsonp','<script id=\"__NEXT_DATA__','webpack-','<style id=\"gatsby-inlined-css','<div id=\"___gatsby','<meta name=\"generator\" content=\"phoenix','<meta name=\"generator\" content=\"Gatsby','<meta name=\"generator\" content=\"Docusaurus'];
        self.fingerprint_js = ['webpackJsonp','gulp'];
        self.url = url
        self.projectTag = projectTag
        self.options = options
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}
        if self.options.cookie != None:
            self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
                           "Cookie":options.cookie,
                           self.options.head.split(':')[0]: self.options.head.split(':')[1],
                           }
        else:
            self.header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }

    def checkJS(self):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        flag = 0
        for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
            for filename in filenames:
                if filename != self.projectTag + ".db":
                    filePath = os.path.join(parent, filename)
                    jsOpen = open(filePath, 'r', encoding='UTF-8',errors="ignore")  # 防编码报错
                    jsFile = jsOpen.readlines()
                    jsFile = str(jsFile)  # 二次转换防报错
                    if any(i in jsFile for i in self.fingerprint_js):
                        flag = 1
                        break
        return flag

    def checkHTML(self):
        headers = self.header
        url = self.url
        sslFlag = int(self.options.ssl_flag)
        if sslFlag == 1:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data,verify=False).text
        else:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data).text
        return 1 if any(i in demo for i in self.fingerprint_html) else 0

    def checkStart(self):
        try:
            flag = self.checkHTML()
            if flag != 1:
                flag = self.checkJS()
        except:
            flag = 777
        return flag
