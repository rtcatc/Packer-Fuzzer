# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,sqlite3,json,urllib3,random
from urllib.parse import quote
from collections import Counter
from lib.getApiText import ApiText
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog
from lib.PostDataText import PostsDataText


class BacTest():
    
    def __init__(self,projectTag,options):
        self.projectTag = projectTag
        self.get_results = []
        self.post_data_results = []
        self.post_json_results = []
        self.options = options
        self.path = ""
        self.log = creatLog().get_logger()

    def bacTest(self):
        try:
            whole_list = []
            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
            cursor = connect.cursor()
            connect.isolation_level = None
            sql = "select * from api_tree where success = 1 or success = 2"
            cursor.execute(sql)
            apiTreeInfo = cursor.fetchall()
            for apiInfo in apiTreeInfo:
                name_list=[]
                api_option = apiInfo[3]
                api_path = apiInfo[1]
                if api_option:
                    json_strs = json.loads(api_option)
                    if json_strs["type"] == "post":
                        json_strs = json.loads(api_option)["post"]
                    else:
                        json_strs = json.loads(api_option)["get"]
                    # 循环遍历
                    for json_str in json_strs:
                        json_default = json_str["default"]  # 获取default参数的数值
                        # 如果是数字
                        if json_default.isdigit():
                            # for json_str in json_strs:
                            #     print(json_str["name"])
                            name_list.append(json_str["name"])
                            # BacTest(self.projectTag).startTest(name_list,api_path,api_option)
                            self.startTest(name_list,api_path,api_option)
                            break
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def startTest(self,name,path,option):
        try:
            self.path = path
            # 数据库读取
            name = "".join(name)
            # 处理完成后的get请求
            get_param = []
            get_burp = []  # 爆破参数集合
            # {"type":"get","get":[{"name":"id","default":"1"}]}
            datas = json.loads(option)
            method = datas["type"]
            data = datas[method]
            # get 请求部分参数
            if method == "get":
                domain = self.path.split("?")[0] # 获取主域名
                for value in data:
                    get_name = value["name"]   # get 请求的参数
                    get_default = value["default"]   # get 请求的参数值
                    if get_name == name:              # 如果参数等于name
                        for value in range(1,6):
                            get_req = str("".join(name)) + "=" + str(value)   # 进行拼姐
                            get_burp.append(get_req)    # 遍历后的参数
                    # 筛选出来 只有一个还是说 有多个
                    elif get_name!=None:
                        param = get_name + "=" + get_default
                        get_param.append(param)

                if len(get_param) == 0:
                    for value in get_burp:
                        get_result = domain + "?" + value
                        self.get_results.append(get_result)
                else:
                    for value in get_burp:
                        get_result = domain + "?" + value +"&"+ "&".join(get_param)
                        self.get_results.append(get_result)
                # 返回数据包比较大小功能

                """
                数据库
                """
                # get 请求 测试
                get_resp_lens = {}
                try:
                    get_obj = ApiText(self.get_results,self.options)
                    get_obj.run()
                    get_texts = get_obj.res
                except Exception as e:
                    self.log.error("[Err] %s" % e)
                # 遍历字典中的元素
                for req,resp in get_texts.items():
                    # 返回数据大小
                    resp_body = len(resp)
                    get_resp_lens[req] = resp_body
                # 筛选
                get_select_list = set()
                get_all_list = []
                for value in get_resp_lens.values():
                    get_select_list.add(int(value))
                    get_all_list.append(value)

                get_resp_data1 = ""
                get_resp_data2 = ""
                get_req_data1 = ""
                get_req_data2 = ""

                # 页面返回包数据 {10496, 7588, 7246，7738}
                # 只要有三个不同
                # get_select_list = list(get_select_list)
                get_repeat_nums = dict(Counter(get_all_list))
                get_repeat_num = int("".join([str(key) for key, value in get_repeat_nums.items() if value > 1]))  # 获取到我们重复的数据

                if len(get_select_list) >=3:
                    # 需要写入到数据库中
                    for key,value in get_resp_lens.items():
                        value = int(value)
                        # if value in get_select_list:   # 如果数值在set中说明是不同的
                        if value != get_repeat_num:
                            get_resp_data1 = get_texts[key]
                            get_req_data1 = str(key)
                        # if value not in get_select_list:
                        if value == get_repeat_num:
                            get_resp_data2 = get_texts[key]
                            get_req_data2 = str(key)

                    # 写入数据库的data
                    get_data = str(get_resp_data1) + "§§§" + str(get_resp_data2)
                    get_req = get_req_data1 + "§§§" + get_req_data2
                    # 写入数据库

                    # 数据库连接
                    projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                    connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                    cursor = connect.cursor()
                    connect.isolation_level = None
                    sql = "select id,from_js from api_tree where path=\"" + self.path + "\""
                    cursor.execute(sql)
                    apiTreeInfo = cursor.fetchall()
                    if len(apiTreeInfo) != 0:
                        api_id = int(apiTreeInfo[0][0])  # 对应路径的api_id
                        from_js = int(apiTreeInfo[0][1])  # 对应路径的from_js
                    # 数据库连接
                        try:
                            DatabaseType(self.projectTag).insertBacInfoIntoDB(api_id,from_js,get_req,quote(get_data))
                        except Exception as e:
                            self.log.error("[Err] %s" % e)

            post_json_burp = []
            post_json_prama = {}
            post_json = {}
            post_burp = []
            post_param = []
            # post 请求参数部分
            if method == "post":
                for value in data:
                    post_name = value["name"]  # post 请求的参数
                    post_default = value["default"]  # post 请求的参数值
                    if post_name == name:
                        post_num = int(post_default)
                        # 对参数做一个循环遍历
                        for value in range(1,6):
                            post_json[name] = value
                            post_req = str("".join(name)) + "=" + str(value)
                            post_burp.append(post_req)
                            # json加入列表需要使用copy方法
                            post_json_burp.append(post_json.copy())
                    else:
                        param = post_name + "=" + post_default
                        post_param.append(param)
                        # 存储json类型
                        post_json_prama[post_name] = post_default

                for data in post_json_burp:
                    for key,value in data.items():
                        post_json_prama[key] = value
                        self.post_json_results.append(post_json_prama.copy())

                for value in post_burp:
                    post_result = value + "&" + "&".join(post_param)
                    self.post_data_results.append(post_result)


                # post请求测试
                post_resp_data1 = ""
                post_resp_data2 = ""
                post_req_data1 = ""
                post_req_data2 = ""
                post_resp_lens = {}
                try:
                    post_obj = PostsDataText(self.path,self.options)
                    post_obj.run(self.post_data_results,self.post_json_results)
                    post_texts = post_obj.res
                except Exception as e:
                    self.log.error("[Err] %s" % e)
                # key对应的是传输过去的data value 对应的是返回数值
                # 获取 返回数据包的五个数值
                for req_data,resp in post_texts.items():
                    resp_body = len(resp)
                    # 存入字典 建立键值对
                    post_resp_lens[req_data] = resp_body


                post_select_list = set()
                post_all_list = []
                for value in post_resp_lens.values():
                    post_select_list.add(int(value))
                    post_all_list.append(value)

                post_repeat_nums = dict(Counter(post_all_list))
                post_repeat_num = int("".join([str(key) for key, value in post_repeat_nums.items() if value > 1]))  # 获取到我们重复的数据

                if len(post_select_list) >= 3:
                    # 需要写入到数据库中
                    for key,value in post_resp_lens.items():
                        value = int(value)
                        if value != post_repeat_num:
                            post_resp_data1 = post_texts[key]
                            post_req_data1 = str(key)
                        if value == post_repeat_num:
                            post_resp_data2 = post_texts[key]
                            post_req_data2 = str(key)

                    # 写入数据库的data
                    post_data = str(post_resp_data1) + "§§§" + str(post_resp_data2)
                    post_req = post_req_data1 + "§§§" + post_req_data2

                    projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                    connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                    cursor = connect.cursor()
                    connect.isolation_level = None
                    sql = "select id,from_js from api_tree where path=\"" + self.path + "\""
                    cursor.execute(sql)
                    apiTreeInfo = cursor.fetchall()
                    if len(apiTreeInfo) != 0:
                        api_id = int(apiTreeInfo[0][0])  # 对应路径的api_id
                        from_js = int(apiTreeInfo[0][1])  # 对应路径的from_js
                        try:
                            DatabaseType(self.projectTag).insertBacInfoIntoDB(api_id,from_js,post_req,post_data)
                        except Exception as e:
                            self.log.error("[Err] %s" % e)
        except Exception as e:
            self.log.error("[Err] %s" % e)

# if __name__ == '__main__':
#     options = CommandLines().cmd()
#     test = Bactest("rMirrz","options")
#     test.bacTest()
#     print(test.get_results)
#
