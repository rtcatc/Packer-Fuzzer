#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,re,sqlite3,random,json,time
from time import sleep
from tqdm import trange
from urllib.parse import urlparse
from lib.common import readConfig
from lib.common.utils import Utils
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog


class FuzzerParam():

    def creatAlpha(self,num):
        H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt

    def creatNum(self,num):
        H = '0123456789'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt

    def __init__(self, projectTag):
        self.projectTag = projectTag
        self.blacklist_param = readConfig.ReadConfig().getValue('FuzzerParam', 'param')[0]
        self.default_judges = readConfig.ReadConfig().getValue('FuzzerParam', 'default')[0]
        self.log = creatLog().get_logger()

    def collect_api_str(self):
        whole_post_str = ""
        whole_get_str = ""
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
            cursor = connect.cursor()
            connect.isolation_level = None
            sql = "select * from api_tree where success = 1 or success = 2"
            cursor.execute(sql)
            api_list = cursor.fetchall()
            for api in api_list:
                api_post_list= ""
                api_get_list = ""
                api_id = "§§§" + str(api[0]) + "§§§\n"
                for filename in filenames:
                    if filename != self.projectTag + ".db":
                        filePath = os.path.join(parent, filename)
                        with open(filePath, "r", encoding="utf-8",errors="ignore") as f:
                            js_strs = f.readlines()
                            count = 0
                            for js_str in js_strs:
                                count = count + 1
                                locationInfo = re.search(api[2], js_str)
                                if locationInfo != None:
                                    startInfoEnds = js_strs[count-5:count+5]
                                    startstring = ""
                                    for startInfoEnd in startInfoEnds:
                                        startstring = startstring + startInfoEnd
                                    if "post" in startstring:
                                        api_post_list = api_post_list + startstring
                                    else:
                                        api_get_list = api_get_list + startstring
                if api_post_list:
                    whole_post_str = whole_post_str + api_post_list + api_id
                if api_get_list:
                    whole_get_str = whole_get_str + api_get_list + api_id
        whole_str = []
        whole_str.append(whole_post_str)
        # with open("post.js","w",encoding="utf-8") as f:
        #    f.write(whole_post_str)
        #    f.close()
        whole_str.append(whole_get_str)
        # with open("get.js","w",encoding="utf-8") as f:
        #    f.write(whole_get_str)
        #    f.close()
        return whole_str

    def FuzzerCollect(self):
        templates_post_str = """
        {
            "type": "post",
            "post": [
{result_post}
            ],
            "get": [
{result_get}
            ]
        }"""
        try:
            whole_str = FuzzerParam(self.projectTag).collect_api_str()
            self.log.debug("collect_api_str模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)
        j = 0
        k = 1
        for i in range(int((len(whole_str[0].split('§§§'))-1)/2)):
            sleep(0.1)
            result_id = whole_str[0].split('§§§')[k]
            result_post = FuzzerParam(self.projectTag).result_method_1(whole_str[0].split('§§§')[j])
            j = j + 2
            k = k + 2
            if result_post[0]:
                replace_str_post = ""
                for c in range(len(result_post[0])):
                    if "\"" not in result_post[1][c]:
                        default_value = FuzzerParam(self.projectTag).creatAlpha(3)
                    else:
                        default_value = result_post[1][c]
                        default_value = default_value.replace("\"","")
                        for default_judge in self.default_judges.split(","):
                            if default_judge in default_value:
                                flag = 1
                                break
                            else:
                                flag = 0
                        if flag:
                            default_value = FuzzerParam(self.projectTag).creatNum(3)
                    str = "\t{\n\t\t\"name\":\"" + result_post[0][c] + "\",\n" + "\t\t\"default\":\"" + default_value + "\"\n\t}\n\t,\n"
                    replace_str_post = replace_str_post + str
                templates_post_str = templates_post_str.replace("{result_post}", replace_str_post[:-2])
                projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                cursor = connect.cursor()
                connect.isolation_level = None
                sql = "UPDATE api_tree set option='%s' where id='%s'"%(templates_post_str,result_id)
                cursor.execute(sql)

        l = 0
        m = 1
        for i in range(int((len(whole_str[1].split('§§§')) - 1) / 2)):
            result_id = whole_str[1].split('§§§')[m]
            try:
                result_get = FuzzerParam(self.projectTag).result_method_1(whole_str[1].split('§§§')[l])
                self.log.debug("result_method_1正常")
            except Exception as e:
                self.log.error("[Err] %s" % e)
            l = l + 2
            m = m + 2
            if result_get[0]:
                replace_str_get = ""
                for c in range(len(result_get[0])):
                    if "\"" not in result_get[1][c]:
                        default_value = FuzzerParam(self.projectTag).creatAlpha(3)
                    else:
                        default_value = result_get[1][c]
                        default_value = default_value.replace("\"","")
                        for default_judge in self.default_judges.split(","):
                            if default_judge in default_value:
                                flag = 1
                                break
                            else:
                                flag = 0
                        if flag:
                            default_value = FuzzerParam(self.projectTag).creatNum(3)
                    str = "\t{\n\t\t\"name\":\"" + result_get[0][c] + "\",\n" + "\t\t\"default\":\"" + default_value + "\"\n\t}\n\t,\n"
                    replace_str_get = replace_str_get + str
                projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                cursor = connect.cursor()
                connect.isolation_level = None
                sql = "select option from api_tree where id='%s'"%(result_id)
                cursor.execute(sql)
                options = cursor.fetchall()
                for option in options:
                    if option[0]:
                        templates_get_str = option[0]
                        templates_get_str = templates_get_str.replace("{result_get}", replace_str_get[:-2])
                        sql = "UPDATE api_tree set option='%s' where id='%s'" % (templates_get_str, result_id)
                    else:
                        templates_get_str = """
        {
            "type": "get",
            "post": [

            ],
            "get": [
{result_get}
            ]
        }"""
                        templates_get_str = templates_get_str.replace("{result_get}", replace_str_get[:-2])
                        sql = "UPDATE api_tree set option='%s' where id='%s'" % (templates_get_str, result_id)
                    cursor.execute(sql)
                else:
                    for option in options:
                        if option[0]:
                            templates_get_str = option[0]
                            templates_get_str = templates_get_str.replace("{result_get}", "")
                            sql = "UPDATE api_tree set option='%s' where id='%s'" % (templates_get_str, result_id)
                    cursor.execute(sql)

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from api_tree where success = 1 or success = 2"
        cursor.execute(sql)
        api_list = cursor.fetchall()
        templates_post_new_str = """
{
    "type": "post",
    "post": [

    ],
    "get": [

    ]
}
"""
        for api in api_list:
            if api[3]:
                option = api[3]
                option = option.replace("{result_get}","")
                sql = "UPDATE api_tree set option='%s' where id='%s'" % (option, api[0])
                cursor.execute(sql)
            else:
                sql = "UPDATE api_tree set option='%s' where id='%s'" % (templates_post_new_str, api[0])
                cursor.execute(sql)

        sql = "select * from api_tree where success = 1 or success = 2"
        cursor.execute(sql)
        api_list = cursor.fetchall()
        sql = "select * from api_tree where option='%s'" %(templates_post_new_str)
        cursor.execute(sql)
        #总共需要暴力提取的数量，可以用这快做进度条
        num_vio = cursor.fetchall()
        # print(len(num_vio))
        num = len(num_vio)

        for n in trange(num):
            time.sleep(1)

        a=0
        for api in api_list:
            option = api[3]
            if option == templates_post_new_str:
                a = a + 1
                templates_post_str = """
        {
            "type": "post",
            "post": [
{result_post}
            ],
            "get": [
{result_get}
            ]
        }"""
                whole_str = FuzzerParam(self.projectTag).collect_api_str()
                j = 0
                k = 1
                for i in range(int((len(whole_str[0].split('§§§')) - 1) / 2)):
                    result_id = int(whole_str[0].split('§§§')[k])
                    try:
                        result_post = FuzzerParam(self.projectTag).violent_method(whole_str[0].split('§§§')[j])
                        self.log.debug("暴力提取模块正常——post")
                    except Exception as e:
                        self.log.error("[Err] %s" % e)
                    j = j + 2
                    k = k + 2
                    if result_id == int(api[0]):
                        if result_post[0]:
                            replace_str_post = ""
                            for j in range(len(result_post[0])):
                                default_value = result_post[1][j]
                                str = "\t{\n\t\t\"name\":\"" + result_post[0][j] + "\",\n" + "\t\t\"default\":\"" + default_value + "\"\n\t}\n\t,\n"
                                replace_str_post = replace_str_post + str
                            templates_post_str = templates_post_str.replace("{result_post}", replace_str_post[:-2])
                            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                            cursor = connect.cursor()
                            connect.isolation_level = None
                            sql = "UPDATE api_tree set option='%s' where id='%s'" % (templates_post_str, result_id)
                            cursor.execute(sql)
                        break
                l = 0
                m = 1
                for i in range(int((len(whole_str[1].split('§§§')) - 1) / 2)):
                    result_id = int(whole_str[1].split('§§§')[m])
                    try:
                        result_get = FuzzerParam(self.projectTag).violent_method(whole_str[1].split('§§§')[l])
                        self.log.debug("暴力提取模块正常——get")
                    except Exception as e:
                        self.log.error("[Err] %s" % e)
                    l = l + 2
                    m = m + 2
                    if result_id == int(api[0]):
                        if result_get[0]:
                            replace_str_get = ""
                            for j in range(len(result_get[0])):
                                default_value = result_get[1][j]
                                str = "\t{\n\t\t\"name\":\"" + result_get[0][j] + "\",\n" + "\t\t\"default\":\"" + default_value + "\"\n\t}\n\t,\n"
                                replace_str_get = replace_str_get + str
                            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                            cursor = connect.cursor()
                            connect.isolation_level = None
                            sql = "select option from api_tree where id='%s'" % (result_id)
                            cursor.execute(sql)
                            options = cursor.fetchall()
                            for option in options:
                                new_str = json.loads(option[0].replace("{result_get}",""))
                                if new_str["post"]:
                                    templates_get_str = option[0]
                                    templates_get_str = templates_get_str.replace("{result_get}", replace_str_get[:-2])
                                    sql = "UPDATE api_tree set option='%s' where id='%s'" % (templates_get_str, result_id)
                                else:
                                    templates_get_str = """
    {
        "type": "get",
        "post": [

        ],
        "get": [
{result_get}
        ]
    }"""
                                    templates_get_str = templates_get_str.replace("{result_get}", replace_str_get[:-2])
                                    sql = "UPDATE api_tree set option='%s' where id='%s'" % (templates_get_str, result_id)
                                cursor.execute(sql)
                        else:
                            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
                            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
                            cursor = connect.cursor()
                            connect.isolation_level = None
                            sql = "select option from api_tree where id='%s'" % (result_id)
                            cursor.execute(sql)
                            options = cursor.fetchall()
                            for option in options:
                                new_str = json.loads(option[0].replace("{result_get}", ""))
                                new_str = json.dumps(new_str).replace("\'","\"")
                                sql = "UPDATE api_tree set option='%s' where id='%s'" % (new_str, result_id)
                                cursor.execute(sql)

                        break

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from api_tree where success = 1 or success = 2"
        cursor.execute(sql)
        api_list = cursor.fetchall()
        for api in api_list:
            option = api[3]
            option = option.replace("{result_get}","").replace("{result_post}","")
            sql = "UPDATE api_tree set option='%s' where id='%s'" % (option, api[0])
            cursor.execute(sql)

    def result_method_1(self,str):
        result_key_list = []
        result_value_list = []
        regxs_1 = r'method\:.*?\,url\:.*?\,data\:({.*?})'
        if re.findall(regxs_1, str, re.S):
            result_json = re.findall(regxs_1, str, re.S)[0].replace(" ", "").replace("\n", "").replace("{", "").replace("\t",                                                                                                         "")
            regx_key = r'(.*?)\:.*?\,|(.*?)\:.*?\}'
            result_keys = re.findall(regx_key, result_json, re.S)
            for result_key in result_keys:
                if result_key[0] != "":
                    result_key_list.append(result_key[0])
                if result_key[1] != "":
                    result_key_list.append(result_key[1])
            regx_value = r'\:(.*?)\,|\:(.*?)\}'
            result_values = re.findall(regx_value, result_json, re.S)
            for para in result_values:
                if para[0] != '':
                    result_value_list.append(para[0])
                if para[1] != '':
                    result_value_list.append(para[1])

        # regxs_2 = r""
        # if re.findall(regxs_2,str,re.S):
        #      result_json =

        result_list = [result_key_list,result_value_list]
        return result_list

    def violent_method(self,str):
        violent_regx = r'(?isu)"([^"]+)'
        results = re.findall(violent_regx, str)
        result_key_list = []
        result_value_list =[]
        for result in results:
            if result.isalpha():
                for black_list in self.blacklist_param.split(","):
                    if result not in black_list:
                        flag = 1
                    else:
                        flag = 0
                        break
                if flag:
                    result_key_list.append(result)
        result_key_list = list(set(result_key_list))
        for i in range(len(result_key_list)):
            result_value_list.append(FuzzerParam(self.projectTag).creatAlpha(3))
        result_list = [result_key_list,result_value_list]
        return result_list
