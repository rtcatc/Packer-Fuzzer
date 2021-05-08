# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,re,sqlite3,json,requests,random
from tqdm import tqdm
from urllib.parse import quote
from lib.common import readConfig
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog


class SqlTest():

    def __init__(self,projectTag,options):
        self.projectTag = projectTag
        self.path = ""
        self.name = ""
        self.option = ""
        self.api_id = ""
        self.from_js = ""
        self.error = 0
        self.boolen = 0
        self.time = 0
        self.options = options
        self.header = ""
        self.log = creatLog().get_logger()
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

    def sqlTest(self):
        whole_list = []
        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        # success=1 的情况是get的情况 success=2的情况是post的情况
        sql = "select * from api_tree where success = 1 or success = 2"
        cursor.execute(sql)
        apiTreeInfo = cursor.fetchall()
        for apiInfo in apiTreeInfo:
            name_list=[]
            api_option = apiInfo[3]
            api_path = apiInfo[1]
            json_strs = json.loads(api_option)
            if json_strs["type"] == "post":
                json_strs = json.loads(api_option)["post"]
            else:
                json_strs = json.loads(api_option)["get"]
            for json_str in json_strs:
                json_default = json_str["default"]
                if json_default.isdigit():
                    for json_str in json_strs:
                        name_list.append(json_str["name"])
                    self.startTest(name_list,api_path,api_option)
                    break

    def startTest(self,name,path,option):
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

        self.name = "".join(name)
        self.path = path
        self.option = option
        self.getIDFromDB()  # 获取对应的id
        # name 应该是参数的名字
        # path api接口地址

        self.errorSQLInjection()
        if self.error == 0:
            self.boolenSQLInjection()
            if self.boolen == 0:
                self.timeSQLInjction()


    def getIDFromDB(self):
        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select id,from_js from api_tree where path=\"" + self.path + "\""
        cursor.execute(sql)
        apiTreeInfo = cursor.fetchall()
        if len(apiTreeInfo) != 0:
            try:
                self.api_id = int(apiTreeInfo[0][0])   # 对应路径的api_id
                self.from_js = int(apiTreeInfo[0][1])  # 对应路径的from_js
            except Exception as e:
                self.log.error("[Err] %s" % e)

    # 报错注入检测模块
    def errorSQLInjection(self):
        sslFlag = int(self.options.ssl_flag)
        # 有待改进
        errors = ["You have an error in your SQL syntax","Oracle Text error","Microsoft SQL Server"]
        datas = json.loads(self.option)
        method = datas['type']
        # get的请求
        if method == "get":
            gets = datas["get"]
            get_datas = []
            # 对options中的参数进行遍历，然后再进行一个组合
            for get in gets:
                get_name = get["name"]
                # 如果参数是传入的参数 对default 进行处理
                if get_name == self.name:
                    # 加入两个引号促使报错
                    get_default = get['default'] + '\'"'
                else:
                    get_default = get["default"]
                get_datas.append(get_name + "=" + get_default)
            # url中加入单引号 导致报错
            url = self.path + "?" + "&".join(get_datas)
            # print(url)
            try:
                if sslFlag == 1:
                    get_resp = requests.get(url,headers=self.header,proxies=self.proxy_data,timeout=10,verify=False)
                else:
                    get_resp = requests.get(url,headers=self.header,proxies=self.proxy_data,timeout=10)
                get_resp_text = get_resp.text

            # 对错误进行一个遍历
                for error in errors:
                    errors.set_description("Processing %s" % error)

                    if error in get_resp_text:
                        #print("目标疑似存在SQL报错注入")
                        self.error = 1
                        try:
                            DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, quote(url),
                                                                          quote(get_resp_text))
                        except Exception as e:
                            self.log.error("[Err] %s" % e)
            except Exception as e:
                self.log.error("[Err] %s" % e)

        if method == "post":
            post_json = {}
            posts = datas["post"]
            post_datas = []
            for post in posts:
                post_name = post["name"]
                if post_name == self.name:
                    post_default = post['default'] + '\'"'
                else:
                    post_default = post['default']
                post_datas.append(post_name + "=" +post_default)
                post_json[post_name] = post_default  # json 类型的数据
            post_data = "&".join(post_datas)
            # print(post_json)
            # print(post_data)
            try:
                if sslFlag == 1:
                    post_resp = requests.post(self.path,headers=self.header,data=post_data,proxies=self.proxy_data,timeout=10,verify=False)
                else:
                    post_resp = requests.post(self.path,headers=self.header,data=post_data,proxies=self.proxy_data,timeout=10)
                post_text = post_resp.text
                post_code = post_resp.status_code
                # json类型
                if post_code == '415':
                    if self.options.cookie != None:
                        header = {
                            'User-Agent': random.choice(self.UserAgent),
                            'Content-Type': 'application/json',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Cookie': self.options.cookie,
                            self.options.head.split(':')[0]: self.options.head.split(':')[1]
                        }
                    else:
                        header = {
                            'User-Agent': random.choice(self.UserAgent),
                            'Content-Type': 'application/json',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            self.options.head.split(':')[0]: self.options.head.split(':')[1]
                        }
                    try:
                        if sslFlag == 1:
                            post_json_resp = requests.post(self.path, data=post_json, headers=header,proxies=self.proxy_data,timeout=10,verify=False)
                        else:
                            post_json_resp = requests.post(self.path, data=post_json, headers=header,proxies=self.proxy_data,timeout=10)
                        post_json_text = post_json_resp.text
                        post_json_code = post_json_resp.status_code
                        if post_json_code == '415':  # 如果状态码还是 415 就不管了 只负责json和普通的data
                            pass
                        else:
                            for error in errors:
                                if error in post_json_text:
                                    #print("疑似存在SQL注入")
                                    self.error = 1
                                    try:
                                        DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id,self.from_js,post_json,post_json_text)
                                    except Exception as e:
                                        self.log.error("[Err] %s" % e)
                    except Exception as e:
                        self.log.error("[Err] %s" % e)

                else:
                    for error in errors:
                        if error in post_text:
                            #print("疑似存在SQL注入")
                            self.error = 1
                            try:
                                DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, post_data,post_text)
                            except Exception as e:
                                self.log.error("[Err] %s" % e)
            except Exception as e:
                self.log.error("[Err] %s" % e)

    def boolenSQLInjection(self):
        sslFlag = int(self.options.ssl_flag)
        datas = json.loads(self.option)
        method = datas['type']
        # get的请求
        if method == "get":
            gets = tqdm(datas["get"])
            get_datas = []
            get_datas1 = []
            get_datas2 = []
            # 对options中的参数进行遍历，然后再进行一个组合
            for get in gets:
                # or 1=1 的 payload
                get_name = get["name"]
                # 如果参数是传入的参数 对default 进行处理
                if get_name == self.name:
                    # 加入两个引号促使报错
                    # 后续可以改成用户自定义
                    get_default = get['default'] + " and 1=1"
                else:
                    get_default = get["default"]
                get_datas.append(get_name + "=" + get_default)

                # or 1=2 的 payload
                get_name1 = get["name"]
                # 如果参数是传入的参数 对default 进行处理
                if get_name1 == self.name:
                    # 加入两个引号促使报错
                    get_default1 = get['default'] + " and 1=2"
                else:
                    get_default1 = get["default"]
                get_datas1.append(get_name1 + "=" + get_default1)

                # 默认 的 payload
                get_name2 = get["name"]
                # 如果参数是传入的参数 对default 进行处理
                if get_name2 ==self.name:
                    # 加入两个引号促使报错
                    get_default2 = get['default']
                else:
                    get_default2 = get["default"]
                get_datas2.append(get_name2 + "=" + get_default2)

            # url中加入单引号 导致报错
            url1 = self.path + "?" + "&".join(get_datas)
            url2 = self.path + "?" + "&".join(get_datas1)
            url_default = self.path + "?" + "&".join(get_datas2)
            # print(url1)  # or 1=1
            # print(url2)  # or 1=2
            # print(url_default)  # default

            # 发送三个get 请求
            try:
                if sslFlag == 1:
                    get_resp1 = requests.get(url1,headers=self.header,proxies=self.proxy_data,timeout=10,verify=False)
                    get_resp2 = requests.get(url2,headers=self.header,proxies=self.proxy_data,timeout=10,verify=False)
                    get_resp_default = requests.get(url_default,headers=self.header,proxies=self.proxy_data,timeout=10,verify=False)
                else:
                    get_resp1 = requests.get(url1,headers=self.header,proxies=self.proxy_data,timeout=10)
                    get_resp2 = requests.get(url2,headers=self.header,proxies=self.proxy_data,timeout=10)
                    get_resp_default = requests.get(url_default,headers=self.header,proxies=self.proxy_data,timeout=10)
                get_resp1_len = len(get_resp1.text)
                get_resp2_len = len(get_resp2.text)
                get_resp_default = len(get_resp_default.text)

                # 首先做一个判断 判断这两者长度是否相投 正常的 和 1=1的
                if (get_resp1_len == get_resp_default) and (get_resp2_len != get_resp_default):
                    #print("疑似存在sql布尔盲注")
                    self.boolen = 1
                    DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, url_default, get_resp1.text)
            except Exception as e:
                self.log.error("[Err] %s" % e)

        if method == "post":
            post_json1 = {}
            post_json2 = {}
            post_json_default = {}

            posts = datas["post"]
            post_datas1 = []
            post_datas2 = []
            post_datas_default = []

            for post in posts:
                # or 1=1
                post_name1 = post["name"]
                if post_name1 ==self.name:
                    post_default = post['default'] + " and 1=1"
                else:
                    post_default = post['default']
                post_datas1.append(post_name1 + "=" + post_default)
                post_json1[post_name1] = post_default  # json 类型的数据

                # or 1=2
                post_name2 = post["name"]
                if post_name2 == self.name:
                    post_default = post['default'] + " and 1=2"
                else:
                    post_default = post['default']
                post_datas2.append(post_name1 + "=" + post_default)
                post_json2[post_name2] = post_default  # json 类型的数据

                # default
                post_name_default = post["name"]
                if post_name_default == self.name:
                    post_default = post['default']
                else:
                    post_default = post['default']
                post_datas_default.append(post_name1 + "=" + post_default)
                post_json_default[post_name_default] = post_default  # json 类型的数据

            post_data1 = "&".join(post_datas1)
            # print(post_data1)
            # print(post_json1) # json数据

            post_data2 = "&".join(post_datas2)
            # print(post_data2)
            # print(post_json2) # json数据

            post_data_default = "&".join(post_datas_default)
            # print(post_data_default)
            # print(post_json_default) # json数据
            try:
                if sslFlag == 1:
                    post_resp = requests.post(self.path,header=self.header,proxies=self.proxy_data,data=post_data1,verify=False)
                else:
                    post_resp = requests.post(self.path,header=self.header,proxies=self.proxy_data,data=post_data1)
                post_code = post_resp.status_code
                # 如果状态吗是 414
                if post_code == '415':

                    if self.options.cookie != None:
                        header = {
                            'User-Agent': random.choice(self.UserAgent),
                            'Content-Type': 'application/json',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Cookie': self.options.cookie,
                            self.options.head.split(':')[0]: self.options.head.split(':')[1]
                        }
                    else:
                        header = {
                            'User-Agent': random.choice(self.UserAgent),
                            'Content-Type': 'application/json',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            self.options.head.split(':')[0]: self.options.head.split(':')[1]
                        }
                    if sslFlag == 1:
                        post_json_len1 = len(requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json1,verify=False).text)
                        post_json_len2 = len(requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json2,verify=False).text)
                        post_json_defaule_len = len(requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json_default,verify=False).text)
                        post_resp_code = requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json1,verify=False).status_code
                        post_resp_text = requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json1,verify=False).text
                    else:
                        post_json_len1 = len(requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json1).text)
                        post_json_len2 = len(requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json2).text)
                        post_json_defaule_len = len(requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json_default).text)
                        post_resp_code = requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json1).status_code
                        post_resp_text = requests.post(self.path,headers=header,proxies=self.proxy_data,data=post_json1).text
                    if post_resp_code == '415':
                        pass
                    else:
                        if (post_json_len1 == post_json_defaule_len) and (post_json_len2 != post_json_defaule_len):
                            #print("疑似存在布尔盲注")
                            self.boolen = 1
                            try:
                                DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, post_json_default,post_resp_text)
                            except Exception as e:
                                self.log.error("[Err] %s" % e)
                else:
                    if sslFlag == 1:
                        post_len1 = len(requests.post(self.path,headers=self.header,data=post_data1,proxies=self.proxy_data,verify=False).text)
                        post_len2 = len(requests.post(self.path,headers=self.header,data=post_data2,proxies=self.proxy_data,verify=False).text)
                        post_len_default = len(requests.post(self.path,headers=self.header,data=post_data_default,proxies=self.proxy_data,verify=False).text)
                    else:
                        post_len1 = len(requests.post(self.path,headers=self.header,data=post_data1,proxies=self.proxy_data).text)
                        post_len2 = len(requests.post(self.path,headers=self.header,data=post_data2,proxies=self.proxy_data).text)
                        post_len_default = len(requests.post(self.path,headers=self.header,data=post_data_default,proxies=self.proxy_data).text)
                    if (post_len1 == post_len_default) and (post_len2 != post_len_default):
                        #print("疑似存在布尔盲注")
                        self.boolen = 1
                        try:
                            DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, post_data_default, post_resp.text)
                        except Exception as e:
                            self.log.error("[Err] %s" % e)

            except Exception as e:
                self.log.error("[Err] %s" % e)

    def timeSQLInjction(self):
        sslFlag = int(self.options.ssl_flag)
        datas = json.loads(self.option)
        method = datas['type']
        if sslFlag == 1:
            default_time = requests.get(self.path, headers=self.header, proxies=self.proxy_data,verify=False).elapsed.seconds
        else:
            default_time = requests.get(self.path, headers=self.header, proxies=self.proxy_data).elapsed.seconds
        # get的请求
        if method == "get":
            gets = datas["get"]
            get_datas = []
            # 对options中的参数进行遍历，然后再进行一个组合
            #print(gets)
            for get in gets:
                get_name = get["name"]
                #print(get_name)
                # 如果参数是传入的参数 对default 进行处理
                if get_name == self.name:
                    # 加入两个引号促使报错
                    get_default = get['default'] + " and sleep(10)"
                else:
                    get_default = get["default"]
                get_datas.append(get_name + "=" + get_default)
            url = self.path + "?" + "&".join(get_datas)  # url
            #print(url)
            # start_time = time.time()
            if sslFlag == 1:
                get_resp = requests.get(url,headers=self.header,proxies=self.proxy_data,verify=False)
            else:
                get_resp = requests.get(url,headers=self.header,proxies=self.proxy_data)
            # 获取响应时间
            sec = get_resp.elapsed.seconds
            #print(sec)
            if (default_time<2) and (sec>=9):
                #print("检测到sql时间盲注")
                self.time =1
                DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, quote(url), get_resp.text)

        if method == "post":
            post_json = {}
            posts = datas["post"]
            post_datas = []
            for post in posts:
                post_name = post["name"]
                if post_name == self.name:
                    post_default = post['default'] + " and sleep(10)"
                else:
                    post_default = post['default']
                post_datas.append(post_name + "=" + post_default)
                post_json[post_name] = post_default  # json 类型的数据
            post_data = "&".join(post_datas)
            #print(post_json)
            #print(post_data)
            try:
                if sslFlag == 1:
                    post_resp = requests.post(self.path,data=post_data,proxies=self.proxy_data,verify=False)
                else:
                    post_resp = requests.post(self.path,data=post_data,proxies=self.proxy_data)
                code = post_resp.status_code
                sec = post_resp.elapsed.seconds

                if code == '415':
                    if self.options.cookie != None:
                        header = {
                            'User-Agent': random.choice(self.UserAgent),
                            'Content-Type': 'application/json',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Cookie': self.options.cookie,
                            self.options.head.split(':')[0]: self.options.head.split(':')[1]
                        }
                    else:
                        header = {
                            'User-Agent': random.choice(self.UserAgent),
                            'Content-Type': 'application/json',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            self.options.head.split(':')[0]: self.options.head.split(':')[1]
                        }
                    if sslFlag == 1:
                        post_json_resp = requests.post(self.path, headers=header, data=post_json, proxies=self.proxy_data, verify=False)
                    else:
                        post_json_resp = requests.post(self.path, headers=header, data=post_json, proxies=self.proxy_data)
                    json_code = post_json_resp.status_code
                    json_sec = post_json_resp.elapsed.seconds
                    if json_code == '415':
                        pass
                    elif default_time<2 and json_sec>9:
                        #print("疑似存在 sql时间盲注")
                        self.time = 1
                        try:
                            DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, post_json, post_json_resp.text)
                        except Exception as e:
                            self.log.error("[Err] %s" % e)

                else:
                    if default_time<2 and sec>9:
                        #print("疑似存在 sql时间盲注")
                        self.time = 1
                        try:
                            DatabaseType(self.projectTag).insertSQLInfoIntoDB(self.api_id, self.from_js, post_data, post_resp.text)
                        except Exception as e:
                            self.log.error("[Err] %s" % e)

            except Exception as e:
                self.log.error("[Err] %s" % e)




# if __name__ == '__main__':
    # test.startTest(name,path,post_option)
    # test.boolenSQLInjection()
    # test.sqlTest()
