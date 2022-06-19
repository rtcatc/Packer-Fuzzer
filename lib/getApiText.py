#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import urllib3,requests,random
from lib.common.CreatLog import creatLog
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


class ApiText(object):

    def __init__(self, urls, options):
        self.log = creatLog().get_logger()
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
        self.codes = []
        self.url = []
        self.urls = urls
        self.res = {}
        self.options = options
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}

    def check(self, url):
        urllib3.disable_warnings()  # 禁止跳出来对warning
        if self.options.contenttype != None:
            contenttype = self.options.contenttype
        else:
            contenttype = 'application/x-www-form-urlencoded'
        if self.options.cookie != None:
            headers = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': contenttype,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cookie': self.options.cookie,
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        else:
            headers = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': contenttype,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        s = requests.Session()
        s.keep_alive = False
        sslFlag = int(self.options.ssl_flag)
        try:
            if sslFlag == 1:
                text = str(s.get(url, headers=headers, timeout=6, proxies=self.proxy_data, verify=False).text)  # 正常的返回code是int类型
            else:
                text = str(s.get(url, headers=headers, timeout=6, proxies=self.proxy_data).text)
            self.res[url] = text
            # else:
            # self.res[url] = text
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def run(self):
        # target = (url for url in self.urls)
        pool = ThreadPoolExecutor(20)
        allTask = [pool.submit(self.check, domain) for domain in self.urls]
        wait(allTask, return_when=ALL_COMPLETED)
        # print(self.res)
        return self.res
        # for future in as_completed(allTask):
        #     data = future.result()
        #     print(data)

# if __name__ == '__main__':
#     try:
#         # banner()
#         che = Checkstatus()
#         che.run()
#     except KeyboardInterrupt:
#         print("停止中...")
