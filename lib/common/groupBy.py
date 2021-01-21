# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests,random,tqdm,time,sys
from tqdm._tqdm import trange
from lib.common.CreatLog import creatLog
from lib.common.webRequest import WebRequest


class GroupBy(object):

    def __init__(self, urls, options):
        self.log = creatLog().get_logger()
        self.urls = urls
        self.divide = [self.urls[i:i + 20] for i in range(0, len(self.urls), 20)]
        self.res = []
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
        self.options = options
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}

        if self.options.cookie != None:
            self.header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cookie':options.cookie,
                self.options.head.split(':')[0]: self.options.head.split(':')[1]

            }
        else:
            self.header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                self.options.head.split(':')[0]: self.options.head.split(':')[1]

            }

    def stat(self):
        # bar = tqdm(self.urls)
        for _ in trange(len(self.urls) // 20):
            time.sleep(0.01)

    def start(self):
        for group in self.divide:
            try:
                flag = 0
                obj = WebRequest(1, group, self.options)
                obj.forceBrute()
                for url, code in obj.codes.items():
                    # 如果请求返回码是415 再请求三
                    sslFlag = int(self.options.ssl_flag)
                    if sslFlag == 1:
                        text = requests.head(url, headers=self.header, timeout=6, proxies=self.proxy_data, allow_redirects=False, verify=False)
                    else:
                        text = requests.head(url, headers=self.header, timeout=6, proxies=self.proxy_data, allow_redirects=False)
                    # 错误代码415
                    if "text/html" not in text.headers['Content-Type']:
                        #print(url)
                        flag = 1
                        self.res.append(url)
                if (flag == 0):
                    break
            except Exception as e:
                self.log.error("[Err] %s" % e)

        return self.res


if __name__ == '__main__':
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    data = {1: 1}
    # code = requests.post("xxx",headers=header,data=data,timeout=6).status_code
