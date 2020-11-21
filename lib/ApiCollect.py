#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,re
from urllib.parse import urlparse
from lib.common import readConfig
from lib.common.utils import Utils
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog
from lib.common.cmdline import CommandLines


class Apicollect():

    def __init__(self, projectTag):
        self.projectTag = projectTag
        self.regxs = [r'\w\.get\(\"(.*?)\"\,',
                      r'\w\.post\(\"(.*?)\"\,',
                      r'\w\.post\(\"(.*?)\"',
                      r'\w\.get\(\"(.*?)\"',
                      r'\w\+\"(.*?)\"\,']
        self.baseUrlRegxs = [r'url.?\s?\:\s?\"(.*?)\"',
                             r'url.?\s?\+\s?\"(.*?)\"',
                             r'url.?\s?\=\s?\"(.*?)\"',
                             r'host\s?\:\s?\"(.*?)\"', ]
        self.baseUrlPaths = []
        self.apiPaths = []
        self.completeUrls = []
        self.apiExts = readConfig.ReadConfig().getValue('blacklist', 'apiExts')[0]
        self.log = creatLog().get_logger()

    def apiCollect(self, filePath):
        with open(filePath, "r", encoding="utf-8",errors="ignore") as jsPath:
            apiStr = jsPath.read()
            for regx in self.regxs:
                apiLists = re.findall(regx, apiStr)
                for apiPath in apiLists:
                    if apiPath != '' and '/' in apiPath:
                        for apiExt in self.apiExts.split(","):
                            if apiExt not in apiPath:
                                flag = 1
                            else:
                                flag = 0
                                break
                        if flag:
                            if "?" in apiPath:
                                apiPath = apiPath.split("?")[0]
                                self.apiPaths.append(apiPath + "§§§" + filePath)
                            else:
                                self.apiPaths.append(apiPath + "§§§" + filePath)
                        else:
                            try:
                                self.apiTwiceCollect(apiPath, filePath)
                                self.log.debug("api二次提取模块正常")
                            except Exception as e:
                                self.log.error("[Err] %s" % e)

    def apiViolentCollect(self, filePath):
        violentRe = r'(?isu)"([^"]+)'
        with open(filePath, "r", encoding="utf-8",errors="ignore") as jsPath:
            print(Utils().tellTime() + Utils().getMyWord("{api_violent_file}") + Utils().getFilename(filePath))
            apiStr = jsPath.read()
            apiLists = re.findall(violentRe, apiStr)
            for apiPath in apiLists:
                if apiPath != '' and '/' in apiPath and apiPath != "/":
                    for apiExt in self.apiExts.split(","):
                        if apiExt not in apiPath:
                            flag = 1
                        else:
                            flag = 0
                            break
                    if flag:
                        if "?" in apiPath:
                            apiPath = apiPath.split("?")[0]
                            self.apiPaths.append(apiPath + "§§§" + filePath)
                        else:
                            self.apiPaths.append(apiPath + "§§§" + filePath)

    def apiTwiceCollect(self, api_str, filePath):
        for regx in self.regxs:
            apiLists = re.findall(regx, api_str)
            for apiPath in apiLists:
                apiPaths = []
                if apiPath != '' and '/' in apiPath:
                    for api_ext in self.apiExts.split(","):
                        if api_ext not in apiPath:
                            flag = 1
                        else:
                            flag = 0
                            break
                    if flag:
                        self.apiPaths.append(apiPath + "§§§" + filePath)

    def getBaseurl(self, filePath):
        baseURL = CommandLines().cmd().baseurl
        if baseURL == None:
            self.baseUrlPaths.append("/")  # 加入一个默认的
            with open(filePath, "r", encoding="utf-8",errors="ignore") as js_path:
                baseUrlStr = js_path.read()
                for baseurlRegx in self.baseUrlRegxs:
                    baseurLists = re.findall(baseurlRegx, baseUrlStr)
                    for baseurlPath in baseurLists:
                        if baseurlPath != '' and '/' in baseurlPath and baseurlPath != "/" and len(baseurlPath) > 3 and len(
                                baseurlPath) < 20:
                            for apiExt in self.apiExts.split(","):
                                if apiExt not in baseurlPath:
                                    flag = 1
                                else:
                                    flag = 0
                                    break
                            if flag:
                                if baseurlPath[0] == "/":
                                    baseurlPath = baseurlPath[1:]
                                if "?" in baseurlPath:
                                    baseurlPath = baseurlPath.split("?")[0]
                                    self.baseUrlPaths.append(baseurlPath)
                                else:
                                    self.baseUrlPaths.append(baseurlPath)
        else:
            baseURLs = baseURL.split(',')
            self.baseUrlPaths = baseURLs

    def apiComplete(self):
        self.baseUrlPaths = list(set(self.baseUrlPaths))  # list去重
        self.apiPaths = list(set(self.apiPaths))
        url = DatabaseType(self.projectTag).getURLfromDB()
        if "#" in url:  # 帮我检测下此处逻辑
            url = url.split("#")[0]
        res = urlparse(url)
        tmpUrl = res.path.split("/")
        if "." in tmpUrl[-1]:
            del tmpUrl[-1]
        hostURL = res.scheme + "://" + res.netloc + "/"
        url = res.scheme + "://" + res.netloc + "/".join(tmpUrl)
        if url[-1:] != "/":
            url = url + "/"
        for baseurl in self.baseUrlPaths:
            for apiPath in self.apiPaths:
                if baseurl == "/":
                    completeUrl1 = url + apiPath
                    completeUrl2 = hostURL + apiPath
                    self.completeUrls.append(completeUrl1)
                    self.completeUrls.append(completeUrl2)
                else:
                    completeUrl1 = url + baseurl + apiPath
                    completeUrl2 = hostURL + baseurl + apiPath
                    self.completeUrls.append(completeUrl1)
                    self.completeUrls.append(completeUrl2)
        self.completeUrls = list(set(self.completeUrls))
        for completeUrl in self.completeUrls:
            if "//" in completeUrl.split("//", 1)[1]:
                completeUrl = completeUrl.split("//", 1)[0] + "//" + completeUrl.split("//", 1)[1].replace("//", "/")
            completeApiPath = completeUrl.split("§§§")[0]
            filePath = completeUrl.split("§§§")[1]
            DatabaseType(self.projectTag).apiRecordToDB(filePath, completeApiPath)
        self.log.info(Utils().tellTime() + Utils().getMyWord("{total_api_num}") + str(len(self.completeUrls)))

    def apireCoverStart(self):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        # projectPath = "tmp/_/"
        for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
            for filename in filenames:
                if filename != self.projectTag + ".db":
                    filePath = os.path.join(parent, filename)
                    try:
                        self.apiCollect(filePath)
                        self.getBaseurl(filePath)
                        self.log.debug("api收集和baseurl提取成功")
                    except Exception as e:
                        self.log.error("[Err] %s" % e)
        if len(self.apiPaths) < 30:  # 提取结果过少时暴力破解
            self.log.info(Utils().tellTime() + Utils().getMyWord("{total_api_auto}"))
            for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
                for filename in filenames:
                    if filename != self.projectTag + ".db":
                        filePath = os.path.join(parent, filename)
                        try:
                            self.apiViolentCollect(filePath)
                            self.log.debug("自动api暴力提取模块正常")
                        except Exception as e:
                            self.log.error("[Err] %s" % e)
        else:
            self.log.info(Utils().tellTime() + Utils().getMyWord("{total_api_1}") + str(len(self.apiPaths)) + Utils().getMyWord("{total_api_2}"))
            open_violent = input(Utils().tellTime() + Utils().getMyWord("{open_violent_input}"))
            if open_violent == "Y" or open_violent == "y":
                for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
                    for filename in filenames:
                        if filename != self.projectTag + ".db":
                            filePath = os.path.join(parent, filename)
                            try:
                                self.apiViolentCollect(filePath)
                                self.log.debug("手动api暴力提取模块正常")
                            except Exception as e:
                                self.log.error("[Err] %s" % e)
        self.apiComplete()
