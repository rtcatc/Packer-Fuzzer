# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import random,time,os,sqlite3,requests
from tqdm import tqdm,trange
from urllib.parse import quote
from lib.common import readConfig
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog


class getoutofloop(Exception): pass

class UploadTest():

    def __init__(self,projectTag,options):
        self.projectTag = projectTag
        self.uploadtest_list = readConfig.ReadConfig().getValue('vuln', 'uploadtest_list')[0]
        self.upload_fail = readConfig.ReadConfig().getValue('vuln', 'upload_fail')[0]
        self.upload_success = readConfig.ReadConfig().getValue('vuln', 'upload_success')[0]
        self.options = options
        self.log = creatLog().get_logger()
        self.header = ""
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}
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
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}

    def uploadTest(self):
        try:
            for uploadtest in self.uploadtest_list.split(","):
                projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                cursor = connect.cursor()
                connect.isolation_level = None
                sql = "select * from api_tree where name = '%s'"%(uploadtest)
                cursor.execute(sql)
                apiTreeInfo = cursor.fetchall()
                for apiInfo in apiTreeInfo:
                    up_list = []
                    api_path = apiInfo[1]
                    up_list.append(api_path)
                    #print(up_list[0])
                    self.startTest(up_list[0])
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def startTest(self,path):

        if self.options.cookie != None:
            self.header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Cookie': self.options.cookie,
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        else:
            self.header = {
                'User-Agent': random.choice(self.UserAgent),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }

        data = "".join(str(time.time()).split("."))
        rands =  bytes().fromhex(data[:12])
        ext_fuzz = ['asp;.jpg', 'asp.jpg', 'asp;jpg', 'asp/1.jpg', 'asp{}.jpg'.format(quote('%00')), 'asp .jpg',
                    'asp_.jpg', 'asa', 'cer', 'cdx', 'ashx', 'asmx', 'xml', 'htr', 'asax', 'asaspp', 'asp;+2.jpg',
                    'asp;.jpg', 'asp.jpg', 'asp;jpg', 'asp/1.jpg', 'asp{}.jpg'.format(quote('%00')), 'asp .jpg',
                    'asp_.jpg', 'asa', 'cer', 'cdx', 'ashx', 'asmx', 'xml', 'htr', 'asax', 'asaspp', 'asp;+2.jpg',
                    'asPx',
                    'aspx .jpg', 'aspx_.jpg', 'aspx;+2.jpg', 'asaspxpx', 'php1', 'php2', 'php3', 'php4', 'php5', 'pHp',
                    'php .jpg', 'php_.jpg', 'php.jpg', 'php.  .jpg',
                    'jpg/.php', 'php.123', 'jpg/php', 'jpg/1.php', 'jpg{}.php'.format(quote('%00')),
                    'php{}.jpg'.format(quote('%00')),
                    'php:1.jpg', 'php::$DATA', 'php::$DATA......', 'ph\np', '.jsp.jpg.jsp', 'jspa', 'jsps', 'jspx',
                    'jspf',
                    'jsp .jpg', 'jsp_.jpg']
        flag = 0

        for _ in trange(22):
            time.sleep(0.1)
        try:
            # python3 随机生成字符串
            sslFlag = int(self.options.ssl_flag)
            for ext in ext_fuzz:
                # 进度条
                files = {"file": (
                    "{}.{}".format(random.randint(1,100), ext), (b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\xD7"+rands))}
                if sslFlag == 1:
                    resp = requests.post(path, files=files, headers=self.header, proxies=self.proxy_data,verify=False)
                else:
                    resp = requests.post(path, files=files, headers=self.header, proxies=self.proxy_data)
                # 如果上传失败了就继续上传
                # 全部走一遍报错
                for fail in str(self.upload_fail).split(","):
                    # 如果返回的信息有失败的
                    if fail in resp.text:
                        flag = 1

                if flag == 0:
                    for success in str(self.upload_success).split(","):
                        if success in resp.text:
                            req_body = resp.request.body
                            resp_text = resp.text
                            # 写入数据库
                            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                            cursor = connect.cursor()
                            connect.isolation_level = None
                            sql = "select id,from_js from api_tree where path=\"" + path + "\""
                            cursor.execute(sql)
                            apiTreeInfo = cursor.fetchall()
                            if len(apiTreeInfo) != 0:
                                #print(apiTreeInfo)
                                try:
                                    api_id = int(apiTreeInfo[0][0])  # 对应路径的api_id
                                    from_js = int(apiTreeInfo[0][1])  # 对应路径的from_js
                                # 数据库连接
                                    DatabaseType(self.projectTag).insertUploadInfoIntoDB(api_id, from_js, quote(req_body),quote(resp_text))
                                except Exception as e:
                                    self.log.error("[Err] %s" % e)
                                raise getoutofloop()
        except getoutofloop:
                pass

if __name__ == '__main__':
    pbar = tqdm(["a", "b", "c", "d"])
    for char in pbar:
        print(char)
        pbar.set_description("Processing %s" % char)
