#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import node_vm2, os, re, sqlite3
from urllib.parse import urlparse
from lib.common.utils import Utils
from lib.Database import DatabaseType
from lib.DownloadJs import DownloadJs
from lib.common.groupBy import GroupBy
from lib.common.CreatLog import creatLog


class RecoverSpilt():

    def __init__(self, projectTag, options):
        self.name_list = []
        self.remotePaths = []
        self.jsFileNames = []
        self.localFileNames = []
        self.remoteFileURLs = []
        self.js_compile_results = []
        self.projectTag = projectTag
        self.options = options
        self.log = creatLog().get_logger()

    def jsCodeCompile(self, jsCode, jsFilePath):
        try:
            self.log.info(Utils().tellTime() + Utils().getMyWord("{get_codesplit}"))
            variable = re.findall(r'\[.*?\]', jsCode)
            if "[" and "]" in variable[0]:
                variable = variable[0].replace("[", "").replace("]", "")
            jsCodeFunc = "function js_compile(%s){js_url=" % (variable) + jsCode + "\nreturn js_url}"
            pattern_jscode = re.compile(r"\(\{\}\[(.*?)\]\|\|.\)", re.DOTALL)
            flag_code = pattern_jscode.findall(jsCodeFunc)
            if flag_code:
                jsCodeFunc = jsCodeFunc.replace("({}[%s]||%s)" % (flag_code[0], flag_code[0]), flag_code[0])
            pattern1 = re.compile(r"\{(.*?)\:")
            pattern2 = re.compile(r"\,(.*?)\:")
            nameList1 = pattern1.findall(jsCode)
            nameList2 = pattern2.findall(jsCode)
            nameList = nameList1 + nameList2
            nameList = list(set(nameList))
            projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
            connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
            cursor = connect.cursor()
            connect.isolation_level = None
            localFile = jsFilePath.split(os.sep)[-1]
            sql = "insert into js_split_tree(jsCode,js_name) values('%s','%s')" % (jsCode, localFile)
            cursor.execute(sql)
            connect.commit()
            cursor.execute("select id from js_split_tree where js_name='%s'" % (localFile))
            jsSplitId = cursor.fetchone()[0]
            cursor.execute("select path from js_file where local='%s'" % (localFile))
            jsUrlPath = cursor.fetchone()[0]
            connect.close()
            with node_vm2.VM() as vm:
                vm.run(jsCodeFunc)
                for name in nameList:
                    if "\"" in name:
                        name = name.replace("\"", "")
                    if "undefined" not in vm.call("js_compile", name):
                        jsFileName = vm.call("js_compile", name)
                        self.jsFileNames.append(jsFileName)
            self.log.info(Utils().tellTime() + Utils().getMyWord("{run_codesplit_s}") + str(len(self.jsFileNames)))
            self.getRealFilePath(jsSplitId, self.jsFileNames, jsUrlPath)
            self.log.debug("jscodecomplie模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)  # 这块有问题，逻辑要改进
            return 0

    def checkCodeSpilting(self, jsFilePath):
        jsOpen = open(jsFilePath, 'r', encoding='UTF-8',errors="ignore")  # 防编码报错
        jsFile = jsOpen.readlines()
        jsFile = str(jsFile)  # 二次转换防报错
        if "document.createElement(\"script\");" in jsFile:
            self.log.info(
                Utils().tellTime() + Utils().getMyWord("{maybe_have_codesplit}") + Utils().getFilename(jsFilePath))
            pattern = re.compile(r"\w\.p\+\"(.*?)\.js", re.DOTALL)
            if pattern:
                jsCodeList = pattern.findall(jsFile)
                for jsCode in jsCodeList:
                    if len(jsCode) < 30000:
                        jsCode = "\"" + jsCode + ".js\""
                        self.jsCodeCompile(jsCode, jsFilePath)

    def getRealFilePath(self, jsSplitId, jsFileNames, jsUrlpath):
        # 我是没见过webpack异步加载的js和放异步的js不在同一个目录下的，这版先不管不同目录的情况吧
        jsRealPaths = []
        res = urlparse(jsUrlpath)
        if "§§§" in jsUrlpath:  # html中script情況
            jsUrlpath = jsUrlpath.split('§§§')[0]
            tmpUrl = jsUrlpath.split("/")
            if "." in tmpUrl[-1]:
                del tmpUrl[-1]
            base_url = "/".join(tmpUrl)
            for jsFileName in jsFileNames:
                jsFileName = base_url + jsFileName
                jsRealPaths.append(jsFileName)
        else:
            tmpUrl = jsUrlpath.split("/")
            del tmpUrl[-1]
            base_url = "/".join(tmpUrl) + "/"
            for jsFileName in jsFileNames:
                jsFileName = Utils().getFilename(jsFileName)  # 获取js名称
                jsFileName = base_url + jsFileName
                jsRealPaths.append(jsFileName)
        try:
            domain = res.netloc
            if ":" in domain:
                domain = str(domain).replace(":", "_") #处理端口号
            DownloadJs(jsRealPaths,self.options).downloadJs(self.projectTag, domain, jsSplitId)
            self.log.debug("downjs功能正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def checkSpiltingTwice(self, projectPath):
        self.log.info(Utils().tellTime() + Utils().getMyWord("{check_codesplit_twice}"))
        for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
            for filename in filenames:
                if filename != self.projectTag + ".db":
                    tmpName = filename.split(".")
                    if len(tmpName) == 4:
                        localFileName = "." + tmpName[-2] + ".js"
                        self.localFileNames.append(localFileName)
                        remotePath = DatabaseType(self.projectTag).getJsUrlFromDB(filename, projectPath)
                        tmpRemotePath = remotePath.split("/")
                        del tmpRemotePath[-1]
                        newRemotePath = "/".join(tmpRemotePath) + "/"
                        self.remotePaths.append(newRemotePath)
        self.remotePaths = list(set(self.remotePaths))
        if len(self.localFileNames) > 3:  # 一切随缘
            localFileName = self.localFileNames[0]
            for baseurl in self.remotePaths:
                tmpRemoteFileURLs = []
                res = urlparse(baseurl)
                i = 0
                while i < 500:
                    remoteFileURL = baseurl + str(i) + localFileName
                    i = i + 1
                    tmpRemoteFileURLs.append(remoteFileURL)
                GroupBy(tmpRemoteFileURLs,self.options).stat()
                tmpRemoteFileURLs = GroupBy(tmpRemoteFileURLs,self.options).start()
                for remoteFileURL in tmpRemoteFileURLs:
                    self.remoteFileURLs.append(remoteFileURL)
        else:
            for localFileName in self.localFileNames:
                for baseurl in self.remotePaths:
                    tmpRemoteFileURLs = []
                    res = urlparse(baseurl)
                    i = 0
                    while i < 500:
                        remoteFileURL = baseurl + str(i) + localFileName
                        i = i + 1
                        tmpRemoteFileURLs.append(remoteFileURL)
                    GroupBy(tmpRemoteFileURLs,self.options).stat()
                    tmpRemoteFileURLs = GroupBy(tmpRemoteFileURLs,self.options).start()
                    for remoteFileURL in tmpRemoteFileURLs:
                        self.remoteFileURLs.append(remoteFileURL)
        if self.remoteFileURLs != []:
            domain = res.netloc
            if ":" in domain:
                domain = str(domain).replace(":", "_") #处理端口号
            self.remoteFileURLs = list(set(self.remoteFileURLs))  # 其实不会重复
            self.log.info(Utils().tellTime() + Utils().getMyWord("{check_codesplit_twice_fini_1}") + str(len(self.remoteFileURLs)) + Utils().getMyWord("{check_codesplit_twice_fini_2}"))
            DownloadJs(self.remoteFileURLs,self.options).downloadJs(self.projectTag, domain, 999)  # 999表示爆破

    def recoverStart(self):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
            for filename in filenames:
                if filename != self.projectTag + ".db":
                    filePath = os.path.join(parent, filename)
                    self.checkCodeSpilting(filePath)
        try:
            self.checkSpiltingTwice(projectPath)
            self.log.debug("checkSpiltingTwice模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)
        self.log.info(Utils().tellTime() + Utils().getMyWord("{check_js_fini}"))
