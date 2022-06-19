# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sqlite3,os,time
from urllib.parse import quote
from urllib.parse import urlparse
from lib.common.utils import Utils
from lib.common.CreatLog import creatLog
from lib.common.readConfig import ReadConfig


class DatabaseType():

    def __init__(self, project_tag):
        self.projectTag = project_tag
        self.log = creatLog().get_logger()

    def createDatabase(self):
        path = os.getcwd() + os.sep + "main.db"
        try:
            if not os.path.exists(path):
                connect = sqlite3.connect(path)
                cursor = connect.cursor()
                connect.isolation_level = None
                cursor.execute('''CREATE TABLE if not exists project(
                             id         INTEGER PRIMARY KEY     autoincrement,
                             tag        TEXT                    NOT NULL,
                             host       TEXT                            ,
                             time       INT                             ,
                             process    TEXT                            ,
                             finish     INT                             );''')
                connect.commit()
                connect.close()
            self.log.debug("主数据库创建成功")
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def createProjectDatabase(self, url, type, cloneTag):
        if type == 1:
            typeValue = "simple"
        else:
            typeValue = "adv"
        unixTime = int(time.time())
        res = urlparse(url)
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":","_")
        PATH = "tmp/" + self.projectTag + "_" + domain + '/' + self.projectTag + ".db"
        try:
            if Utils().creatSometing(2, PATH) == 1:
                connect = sqlite3.connect(os.sep.join(PATH.split('/')))
                cursor = connect.cursor()
                connect.isolation_level = None
                cursor.execute('''CREATE TABLE if not exists info(
                             name       TEXT    PRIMARY KEY     NOT NULL,
                             vaule      TEXT                            );''')
                cursor.execute('''CREATE TABLE if not exists js_file(
                             id         INTEGER PRIMARY KEY     autoincrement,
                             name       TEXT                    NOT NULL,
                             path       TEXT                            ,
                             local      TEXT                            ,
                             success    INT                             ,
                             spilt      INT                             );''')
                cursor.execute('''CREATE TABLE if not exists js_split_tree(
                             id         INTEGER PRIMARY KEY     autoincrement,
                             jsCode    TEXT                            ,
                             js_name    TEXT                            ,
                             js_result  TEXT                            ,
                             success    INT                             );''')
                cursor.execute('''CREATE TABLE if not exists api_tree(
                             id         INTEGER PRIMARY KEY     autoincrement,
                             path       TEXT                            ,
                             name       TEXT                    NOT NULL,
                             option     TEXT                            ,
                             result     TEXT                            ,
                             success    INT                             ,
                             from_js    INT                             );''')
                cursor.execute('''CREATE TABLE if not exists vuln(
                             id         INTEGER PRIMARY KEY     autoincrement,
                             api_id     INT                     NOT NULL,
                             js_id      INT                     NOT NULL,
                             type       TEXT                            ,
                             sure       INT                             ,
                             request_b  TEXT                            ,
                             response_b TEXT                            ,
                             response_h TEXT                            ,
                             des        TEXT                            );''')
            cursor.execute("insert into info values('time', '%s')" % (unixTime))
            cursor.execute("insert into info values('url', '%s')" % (url))
            cursor.execute("insert into info values('host','%s')" % (domain))
            cursor.execute("insert into info values('type', '%s')" % (typeValue))
            cursor.execute("insert into info values('tag', '%s')" % (self.projectTag))
            cursor.execute("insert into info (name) VALUES ('clone')")
            connect.commit()
            connect.close()
            conn2 = sqlite3.connect(os.getcwd() + os.sep + "main.db")
            cursor2 = conn2.cursor()
            conn2.isolation_level = None
            sql = "INSERT into project (tag,host,time) VALUES ('" + self.projectTag + "', '" + domain + "', " + str(
                unixTime) + ")"
            cursor2.execute(sql)
            conn2.commit()
            conn2.close()
            self.log.debug("数据库创建成功")
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def getPathfromDB(self):
        path = os.getcwd() + os.sep + "main.db"
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select host from project where tag = '" + self.projectTag + "'")
        host = cursor.fetchone()[0]  # 第一个即可
        conn.close()
        projectPath = "tmp" + os.sep + self.projectTag + "_" + host + os.sep
        return projectPath

    def getJsUrlFromDB(self, localFileName, projectPath):
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select path from js_file where local = '" + localFileName + "'")
        remotePath = cursor.fetchone()[0]  # 第一个即可
        conn.close()
        return remotePath

    def getJsIDFromDB(self, localFileName, projectPath):
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select id from js_file where local = '" + localFileName + "'")
        jsFileID = cursor.fetchone()[0]  # 第一个即可
        conn.close()
        return jsFileID

    def apiRecordToDB(self, js_path, api_path):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        localFileName = js_path.split(os.sep)[-1]
        jsFileID = DatabaseType(self.projectTag).getJsIDFromDB(localFileName, projectPath)
        connect.isolation_level = None
        sql = "insert into api_tree(path,name,from_js) values(\"" + api_path + "\",\"" + api_path.split("/")[
            -1] + "\"," + str(jsFileID) + ")"
        cursor.execute(sql)
        connect.commit()
        connect.close()

    # 获取数据库里面的path
    def apiPathFromDB(self):
        apis = []
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select path from api_tree")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            # print("".join(row))
            api = "".join(row)
            apis.append(api)
        return apis

    def insertResultFrom(self, res):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        for path, suc in res.items():
            # print(path, suc)
            sql = "UPDATE api_tree SET success=" + str(suc) + " WHERE path=\"" + path + '\"'
            cursor.execute(sql)
            # conn.commit()
        conn.close()

    def getURLfromDB(self):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select vaule from info where name = 'url'")
        url = cursor.fetchone()[0]  # 第一个即可
        conn.close()
        return url

    # 获取success为1的路径
    def sucesssPathFromDB(self):
        paths = []
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select path from api_tree where success=1")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            api = "".join(row)
            paths.append(api)
        return paths

    # 获取sucess为2的路径 post请求
    def wrongMethodFromDB(self):
        paths = []
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select path from api_tree where success=2")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            api = "".join(row)
            paths.append(api)
        return paths

    # 获取sucess为1和2的所有存在路径
    def allPathFromDB(self):
        paths = []
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        cursor.execute("select path from api_tree where success=1 or success=2")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            api = "".join(row)
            paths.append(api)
        return paths

    #更新请求类型 POST或GET
    def updatePathsMethod(self,code):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        if code == 1:
            sql = "UPDATE api_tree SET success = 1 WHERE success = 2"
        else:
            sql = "UPDATE api_tree SET success = 2 WHERE success = 1"
        cursor.execute(sql)
        conn.close()

    # 将结果写入数据库
    def insertTextFromDB(self, res):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        for url, text in res.items():
            blacks = ReadConfig()
            blacks.getValue("blacklist", "apiExts")
            black_ext = "".join(blacks.res).split(",")
            try:
                for ext in black_ext:
                    if ("<html" not in text) and ("PNG" not in text) and (len(text) != 0) and (url.split("/")[-1] != "favicon.ico")\
                            and (("." + str(url.split("/")[-1].split(".")[-1])) != ext):
                        sql = "UPDATE api_tree SET result=\'" + text + "\' WHERE path=\"" + url + '\"'
                    else:
                        sql = "UPDATE api_tree SET success=0 WHERE path=\"" + url + '\"'
                cursor.execute(sql)
                self.log.debug("数据库插入成功")
            except Exception as e:
                self.log.debug("插入时有些例外")
        conn.close()

    def insertCorsInfoIntoDB(self, request_b, response_h):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        request_b = "Origin: " + request_b['Origin']
        # response_h = "Access-Control-Allow-Origin: " + response_h['Access-Control-Allow-Origin'] +", Access-Control-Allow-Methods: " + response_h['Access-Control-Allow-Methods'] + ", Access-Control-Allow-Credentials: " + response_h['Access-Control-Allow-Credentials']
        response_h = "Access-Control-Allow-Origin: " + response_h['Access-Control-Allow-Origin']  + ", Access-Control-Allow-Credentials: " + response_h['Access-Control-Allow-Credentials']

        sql = "insert into vuln(sure,api_id,js_id,type,request_b,response_h) VALUES(1,7777777,7777777,'CORS',\"" + request_b + "\",\'" + response_h + "\');"
        cursor.execute(sql)
        conn.close()

    # 将弱口令成功的写入数据库
    def insertWeakPassInfoIntoDB(self, api_id,js_id,request_b, response_h):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        sql = "insert into vuln(api_id,js_id,request_b,response_b,type,sure) values ('%d','%d','%s','%s','passWord',1)" % (
                        api_id, js_id, request_b, response_h)
        cursor.execute(sql)
        conn.close()


    def insertBacInfoIntoDB(self, api_id,js_id,request_b, response_h):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        sql = "insert into vuln(api_id,js_id,request_b,response_b,type,sure) values ('%d','%d','%s','%s','BAC',1)" % (
                        api_id, js_id, request_b, response_h)
        cursor.execute(sql)
        conn.close()

    def insertUploadInfoIntoDB(self, api_id,js_id,request_b, response_h):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        sql = "insert into vuln(api_id,js_id,request_b,response_b,type,sure) values ('%d','%d','%s','%s','upLoad',1)" % (
                        api_id, js_id, request_b, response_h)
        cursor.execute(sql)
        conn.close()

    def insertSQLInfoIntoDB(self, api_id, js_id, request_b, response_h):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        projectDBPath = projectPath + self.projectTag + ".db"
        conn = sqlite3.connect(projectDBPath)
        cursor = conn.cursor()
        conn.isolation_level = None
        sql = "insert into vuln(api_id,js_id,request_b,response_b,type,sure) values ('%d','%d','%s','%s','SQL',1)" % (
            api_id, js_id, request_b, response_h)
        cursor.execute(sql)
        conn.close()
