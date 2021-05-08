# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os, re, sqlite3
from lib.common import readConfig
from lib.common.utils import Utils
from lib.vuln.SqlTest import SqlTest
from lib.vuln.BacTest import BacTest
from lib.Database import DatabaseType
from lib.vuln.InfoTest import InfoTest
from lib.vuln.CorsTest import CorsTest
from lib.common.CreatLog import creatLog
from lib.vuln.UploadTest import UploadTest
from lib.vuln.UnauthTest import UnAuthTest
from lib.vuln.PasswordTest import PasswordTest


class vulnTest():

    def __init__(self, projectTag,options):
        self.projectTag = projectTag
        self.options = options
        self.log = creatLog().get_logger()

    def testStart(self, url):
        self.log.info(Utils().tellTime() + Utils().getMyWord("{unauth_test}"))
        try:
            UnAuthTest(self.projectTag).apiUnAuthTest()
            self.log.debug("UnAuthTest模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)
        self.log.info(Utils().tellTime() + Utils().getMyWord("{info_test}"))
        try:
            InfoTest(self.projectTag).startInfoTest()
            self.log.debug("InfoTest模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)
        self.log.info(Utils().tellTime() + Utils().getMyWord("{cors_test}"))
        try:
            cors = CorsTest(url,self.options)
            cors.testStart()
            if cors.flag == 1:
                DatabaseType(self.projectTag).insertCorsInfoIntoDB(cors.header, cors.res)
            self.log.debug("CorsTest模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def advtestStart(self,options):
        try:
            self.log.info(Utils().tellTime() + Utils().getMyWord("{password_test}"))
            passwordtest = PasswordTest(self.projectTag)
            passwordtest.passwordTest()
            passwordtest.vulntestStart(options)
            self.log.debug("passwordTest模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)


        # 水平越权  ok
        try:
            self.log.info(Utils().tellTime() + Utils().getMyWord("{bac_test}"))
            bactest = BacTest(self.projectTag,self.options)
            bactest.bacTest()
            self.log.debug("BacTest模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)

        # 文件上传 fuzz 检测模块
        try:
            self.log.info(Utils().tellTime() + Utils().getMyWord("{upload_test}"))
            uploadtest = UploadTest(self.projectTag,self.options)
            uploadtest.uploadTest()
            self.log.debug("UploadTest模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)

        # sql注入检测模块
        try:
            self.log.info(Utils().tellTime() + Utils().getMyWord("{sql_test}"))
            sqltest = SqlTest(self.projectTag,self.options)
            sqltest.sqlTest()
            self.log.debug("SqlTest模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)
