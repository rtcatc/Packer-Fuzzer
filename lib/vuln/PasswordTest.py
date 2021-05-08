# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,re,sqlite3,json,requests
from lib.common import readConfig
from lib.getApiText import ApiText
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog
from lib.PostDataText import PostsDataText
from concurrent.futures import ThreadPoolExecutor,ALL_COMPLETED,wait


class PasswordTest():

    def __init__(self,projectTag):
        self.projectTag = projectTag
        self.passwordtest_list = readConfig.ReadConfig().getValue('vuln', 'passwordtest_list')[0]
        self.passworduser_list = readConfig.ReadConfig().getValue('vuln', 'passworduser_list')[0]
        self.passwordpass_list = readConfig.ReadConfig().getValue('vuln', 'passwordpass_list')[0]
        self.postdatas = []
        self.getdatas = []
        self.jsonposts = []
        self.log = creatLog().get_logger()
        self.path = ""

    def passwordTest(self):
        for passwordtests in self.passwordtest_list.split(","):
            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
            cursor = connect.cursor()
            connect.isolation_level = None
            sql = "select * from api_tree where name = '%s'"%(passwordtests)
            cursor.execute(sql)
            apiTreeInfo = cursor.fetchall()
            for apiInfo in apiTreeInfo:
                pass_list = []
                api_path = apiInfo[1]
                pass_list.append(api_path)
                api_option = apiInfo[3]
                if api_option:
                    pass_list.append(api_option)
                    for passwordusers in self.passworduser_list.split(","):
                        if passwordusers in api_option:
                            pass_list.append(passwordusers)
                            flag = 1
                            break
                        else:
                            flag = 0
                            pass_list.append("none")

                    if flag:
                        for passwordpass in self.passwordpass_list.split(","):
                            if passwordpass in api_option:
                                pass_list.append(passwordpass)
                                flag = 1
                                break
                            else:
                                flag = 0
                                pass_list.append("none")
                    # PasswordTest(self.projectTag).startTest(pass_list[0],pass_list[1],pass_list[2],pass_list[3])
                    if  (pass_list[3] != "none") and (pass_list[2] != "none"):
                        self.startTest(pass_list[0],pass_list[1],pass_list[2],pass_list[3])
            # print(self.postdatas)

    #  数据处理没有参与线程池
    def startTest(self,path,option,username,password):
        self.path = path
        dict_username = []
        dict_password = []
        jsonpost = {}  # json类型的数据
        userdictpath = os.getcwd() + os.sep + "doc" + os.sep +"dict" + os.sep + "username.dic"
        passwddictpath = os.getcwd()  + os.sep + "doc" + os.sep +"dict" + os.sep + "password.dic"

        with open(userdictpath, "r+") as file:
            for value in file.readlines():
                value = value.strip("\n")
                dict_username.append(value)

        with open(passwddictpath, "r+") as file:
            for value in file.readlines():
                value = value.strip("\n")
                dict_password.append(value)

        datas = json.loads(option)
        method = datas['type']
        if method == "post":
            posts = datas['post']
            post_datas = []
            for value in posts:
                name = value['name']
                if name == username:
                    default = "$username$"
                elif name == password:
                    default = "$password$"
                else:
                    default = value['default']
                post_datas.append(name+ "=" +default)
                jsonpost[name] = default
            post_data = "&".join(post_datas)
            if ("$username$" in post_data) and ("$password$" in post_data):
                for user in dict_username:
                    post1 = post_data.replace("$username$",user)
                    for passwd in dict_password:
                        post2 = post1.replace("$password$",passwd)
                        self.postdatas.append(post2)

            # 为了应对数据是json的类型
            for user in dict_username:
                jsonpost[username] = user
                for passwd in dict_password:
                    jsonpost[password] = passwd
                    # print(type(jsonpost))
                    # 将字典存入到列表中需要利用copy的方法
                    self.jsonposts.append(jsonpost.copy())
            # print(self.jsonposts)
            # print(self.jsonposts)

        if method == "get":
            gets = datas['get']
            get_datas = []
            for value in gets:
                name = value['name']
                if name == username :
                    default = "$username$"
                elif name == password:
                    default = "$password$"
                else:
                    default = value['default']
                get_datas.append(name + "=" + default)
            get_data = "?" + "&".join(get_datas)
            if ("$username$" in get_data) and ("password" in get_data):
                for user in dict_username:
                    get1 = get_data.replace("$username$",user)
                    for passwd in dict_password:
                        get2 = get1.replace("$password$",passwd)
                        self.getdatas.append(path + get2)
            # for value in self.getdatas:
            #     print(value)
            # return  self.getdatas

    # 测试模块，对数据进行处理整合
    def vulntestStart(self,options):
        # 获取from_js 和api_id
        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select id,from_js from api_tree where path=\"" + self.path + "\""
        cursor.execute(sql)
        apiTreeInfo = cursor.fetchall()
        if len(apiTreeInfo) != 0:
            api_id = int(apiTreeInfo[0][0])   # 对应路径的api_id
            from_js = int(apiTreeInfo[0][1])  # 对应路径的from_js

            message = str(readConfig.ReadConfig().getValue('vulnTest', 'login')[0]).split(',')
            # get类型返回的数据列表
            getdatas = self.getdatas
            # post类型返回的数据列表
            postdatas = self.postdatas
            jsonpostdata = self.jsonposts

            # post请求
            if len(getdatas) == 0:
                postobj = PostsDataText(self.path, options)
                # 传入post的数据和json的数据 线程池跑
                # postobj.res.items 是返回的结果
                postobj.run(postdatas, jsonpostdata)
                for key, value in postobj.res.items():
                    #print(key + ": " + value)
                    for flag in message:
                        if flag in str(value):
                            # 进行数据裤的插入
                            try:
                                DatabaseType(self.projectTag).insertWeakPassInfoIntoDB(api_id,from_js,str(key), str(value))
                            except Exception as e:
                                self.log.error("[Err] %s" % e)

            # get请求
            if len(postdatas) == 0:
                getobj = ApiText(getdatas, options)
                getobj.run()
                for key, value in getobj.res.items():
                    for flag in message:
                        if flag in str(value):
                            # 进行数据裤的插入
                            try:
                                DatabaseType(self.projectTag).insertWeakPassInfoIntoDB(api_id,from_js,str(key), str(value))
                            except Exception as e:
                                self.log.error("[Err] %s" % e)
