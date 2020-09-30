# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

from lib.ParseJs import ParseJs
from lib.vulnTest import vulnTest
from lib.common.utils import Utils
from lib.getApiText import ApiText
from lib.ApiCollect import Apicollect
from lib.Database import DatabaseType
from lib.FuzzParam import FuzzerParam
from lib.PostApiText import PostApiText
from lib.common.beautyJS import BeautyJs
from lib.common.CreatLog import creatLog
from lib.Recoverspilt import RecoverSpilt
from lib.CreateReport import CreateReport
from lib.getApiResponse import ApiResponse
from lib.LoadExtensions import loadExtensions


class Project():

    def __init__(self, url, options):
        self.url = url
        self.codes = {}
        self.options = options

    def parseStart(self):
        projectTag = Utils().creatTag(6)
        DatabaseType(projectTag).createDatabase()
        ParseJs(projectTag, self.url, self.options).parseJsStart()
        RecoverSpilt(projectTag,self.options).recoverStart()
        Apicollect(projectTag).apireCoverStart()
        apis = DatabaseType(projectTag).apiPathFromDB()  # 从数据库中提取出来的api
        self.codes = ApiResponse(apis,self.options).run()
        DatabaseType(projectTag).insertResultFrom(self.codes)
        getPaths = DatabaseType(projectTag).sucesssPathFromDB()   # 获取get请求的path
        getTexts = ApiText(getPaths,self.options).run()    # 对get请求进行一个获取返回包
        postMethod = DatabaseType(projectTag).wrongMethodFromDB()  # 获取post请求的path
        if len(postMethod) != 0:
            postText = PostApiText(postMethod,self.options).run()
            DatabaseType(projectTag).insertTextFromDB(postText)
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
        CreateReport(projectTag).create_repoter()
        creatLog().get_logger().info("[-] " + Utils().getMyWord("{all_end}"))
