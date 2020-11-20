# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import random,requests
from urllib.parse import urlparse
from lib.common.CreatLog import creatLog


class CorsTest(object):

    def __init__(self, url, options):
        self.UserAgent = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
                          "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
                          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                          "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
                          "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
                          "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
                          "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
                          "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
                          "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0",
                          "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
                          "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"]
        self.url = url
        self.log = creatLog().get_logger()
        self.baseurl = urlparse(self.url)
        self.expUrl = "https://" + self.baseurl.netloc + ".example.org" + "/" + self.baseurl.netloc
        self.options = options
        if self.options.cookie != None:
            self.header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Origin': self.expUrl,
                'Cookie': options.cookie,
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        else:
            self.header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Origin': self.expUrl,
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        self.res = {}
        self.flag = 0

    def testStart(self):
        try:
            sslFlag = int(self.options.ssl_flag)
            if sslFlag == 1:
                text = requests.get(self.url, headers=self.header, timeout=6, allow_redirects=False,verify=False).headers
            else:
                text = requests.get(self.url, headers=self.header, timeout=6, allow_redirects=False).headers
            self.res = text
            if 'example.org' in text['Access-Control-Allow-Origin'] and text[
                 'Access-Control-Allow-Credentials'] == 'true':
                #print("已检测到cors漏洞")
                self.flag = 1
        except Exception as e:
            self.log.debug("Access-Control-Allow-Origin头不存在")