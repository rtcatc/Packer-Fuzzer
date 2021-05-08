# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,re,sqlite3
from lib.common import readConfig
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog


class UnAuthTest():

    def __init__(self, projectTag):
        self.projectTag = projectTag
        self.api_UnAuth_result = []
        self.resultFilters = readConfig.ReadConfig().getValue('vulnTest', 'resultFilter')[0]
        self.unauth_not_sure = readConfig.ReadConfig().getValue('vulnTest', 'unauth_not_sure')[0]
        self.log = creatLog().get_logger()

    def apiUnAuthTest(self):
        try:
            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
            cursor = connect.cursor()
            connect.isolation_level = None
            sql = "select * from api_tree where success = 1 or success = 2"
            cursor.execute(sql)
            apiTreeInfo = cursor.fetchall()
            for apiInfo in apiTreeInfo:
                for resultFilter in self.resultFilters.split(","):
                    try:
                        if resultFilter not in apiInfo[4]:
                            flag = 1
                        else:
                            flag = 0
                            break
                    except:
                        flag = 0
                if flag:
                    # print(apiInfo[4])
                    self.api_UnAuth_result.append(apiInfo[4])
                    sql = "select from_js from api_tree where id=('%s')" % apiInfo[0]
                    cursor.execute(sql)
                    js_id = cursor.fetchone()
                    for unauth_not_sure in self.unauth_not_sure.split(","):
                        if unauth_not_sure not in apiInfo[4]:
                            flag = 1
                        else:
                            flag = 0
                            break
                    if flag:
                        sql = "insert into vuln(api_id,js_id,response_b,sure,type) values ('%s','%s','%s','%s','unAuth')" % (
                            apiInfo[0], js_id[0], apiInfo[4], 1)
                    else:
                        sql = "insert into vuln(api_id,js_id,response_b,sure,type) values ('%s','%s','%s','%s','unAuth')" % (
                            apiInfo[0], js_id[0], apiInfo[4], 2)
                    cursor.execute(sql)

            connect.close()
        except Exception as e:
            self.log.error("[Err] %s" % e)
