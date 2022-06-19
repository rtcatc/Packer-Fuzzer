# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from lib.ParseJs import ParseJs
from lib.vulnTest import vulnTest
from lib.common.utils import Utils
from lib.getApiText import ApiText
from lib.ApiCollect import Apicollect
from lib.Database import DatabaseType
from lib.FuzzParam import FuzzerParam
from lib.CheckPacker import CheckPacker
from lib.PostApiText import PostApiText
from lib.common.beautyJS import BeautyJs
from lib.Recoverspilt import RecoverSpilt
from lib.CreateReport import CreateReport
from lib.getApiResponse import ApiResponse
from lib.LoadExtensions import loadExtensions
from lib.reports.CreatWord import Docx_replace
from lib.common.CreatLog import creatLog,log_name,logs


class Project():

    def __init__(self, url, options):
        self.url = url
        self.codes = {}
        self.options = options

    def parseStart(self):
        projectTag = logs
        if self.options.silent != None:
            print("[TAG]" + projectTag)
        DatabaseType(projectTag).createDatabase()
        ParseJs(projectTag, self.url, self.options).parseJsStart()
        path_log = os.path.abspath(log_name)
        path_db = os.path.abspath(DatabaseType(projectTag).getPathfromDB() + projectTag + ".db")
        creatLog().get_logger().info("[!] " + Utils().getMyWord("{db_path}") + path_db)  #显示数据库文件路径
        creatLog().get_logger().info("[!] " + Utils().getMyWord("{log_path}") + path_log) #显示log文件路径
        checkResult = CheckPacker(projectTag, self.url, self.options).checkStart()
        if checkResult == 1 or checkResult == 777: #打包器检测模块
            if checkResult != 777: #确保检测报错也能运行
                creatLog().get_logger().info("[!] " + Utils().getMyWord("{check_pack_s}"))
            RecoverSpilt(projectTag, self.options).recoverStart()
        else:
            creatLog().get_logger().info("[!] " + Utils().getMyWord("{check_pack_f}"))
        Apicollect(projectTag, self.options).apireCoverStart()
        apis = DatabaseType(projectTag).apiPathFromDB()  # 从数据库中提取出来的api
        self.codes = ApiResponse(apis,self.options).run()
        DatabaseType(projectTag).insertResultFrom(self.codes)
        if self.options.sendtype == "GET" or self.options.sendtype == "get":
            allPaths = DatabaseType(projectTag).allPathFromDB()
            getTexts = ApiText(allPaths,self.options).run()    # 对get请求进行一个获取返回包
            DatabaseType(projectTag).updatePathsMethod(1)
            DatabaseType(projectTag).insertTextFromDB(getTexts)
        elif self.options.sendtype == "POST" or self.options.sendtype == "post":
            allPaths = DatabaseType(projectTag).allPathFromDB()
            postTexts = PostApiText(allPaths,self.options).run()
            DatabaseType(projectTag).updatePathsMethod(2)
            DatabaseType(projectTag).insertTextFromDB(postTexts)
        else:
            getPaths = DatabaseType(projectTag).sucesssPathFromDB()   # 获取get请求的path
            getTexts = ApiText(getPaths,self.options).run()    # 对get请求进行一个获取返回包
            postPaths = DatabaseType(projectTag).wrongMethodFromDB()  # 获取post请求的path
            if len(postPaths) != 0:
                postTexts = PostApiText(postPaths,self.options).run()
                DatabaseType(projectTag).insertTextFromDB(postTexts)
            DatabaseType(projectTag).insertTextFromDB(getTexts)
        if self.options.type == "adv":
            creatLog().get_logger().info("[!] " + Utils().getMyWord("{adv_start}"))
            creatLog().get_logger().info(Utils().tellTime() + Utils().getMyWord("{beauty_js}"))
            BeautyJs(projectTag).rewrite_js()
            creatLog().get_logger().info(Utils().tellTime() + Utils().getMyWord("{fuzzer_param}"))
            FuzzerParam(projectTag).FuzzerCollect()
        creatLog().get_logger().info(Utils().tellTime() + Utils().getMyWord("{response_end}"))
        vulnTest(projectTag,self.options).testStart(self.url)
        if self.options.type == "adv":
            vulnTest(projectTag,self.options).advtestStart(self.options)
        if self.options.ext == "on":
            creatLog().get_logger().info("[+] " + Utils().getMyWord("{ext_start}"))
            loadExtensions(projectTag,self.options).runExt()
            creatLog().get_logger().info("[-] " + Utils().getMyWord("{ext_end}"))
        vuln_num = Docx_replace(projectTag).vuln_judge()
        co_vuln_num = vuln_num[1] + vuln_num[2] + vuln_num[3]
        creatLog().get_logger().info("[!] " + Utils().getMyWord("{co_discovery}") + str(co_vuln_num) + Utils().getMyWord("{effective_vuln}") + ": " + Utils().getMyWord("{r_l_h}") + str(vuln_num[1]) + Utils().getMyWord("{ge}") + ", " + Utils().getMyWord("{r_l_m}") + str(vuln_num[2]) + Utils().getMyWord("{ge}") + ", " + Utils().getMyWord("{r_l_l}") + str(vuln_num[3]) + Utils().getMyWord("{ge}"))
        CreateReport(projectTag).create_repoter()
        creatLog().get_logger().info("[-] " + Utils().getMyWord("{all_end}"))
