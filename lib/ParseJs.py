# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import re,requests,warnings,sqlite3,os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from lib.common.utils import Utils
from lib.Database import DatabaseType
from lib.DownloadJs import DownloadJs
from lib.common.CreatLog import creatLog
from lib.common.cmdline import CommandLines


class ParseJs():  # 获取js进行提取

    def __init__(self, projectTag, url, options):
        warnings.filterwarnings('ignore') #不显示警告，后期可以优化为全局的
        self.url = url
        self.jsPaths = []
        self.jsRealPaths = []
        self.jsPathList = []
        self.projectTag = projectTag
        self.options = options
        self.proxy_data = {'http': self.options.proxy,'https': self.options.proxy}
        if self.options.cookie != None:
            self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
                           "Cookie":options.cookie,
                           self.options.head.split(':')[0]: self.options.head.split(':')[1],
                           }
        else:
            self.header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
                self.options.head.split(':')[0]: self.options.head.split(':')[1]
            }
        DatabaseType(self.projectTag).createProjectDatabase(self.url, 1, "0")
        self.log = creatLog().get_logger()

    def requestUrl(self):
        headers = self.header
        url = self.url
        self.log.info(Utils().tellTime() + Utils().getMyWord("{target_url}") + url)
        self.log.info(Utils().tellTime() + Utils().getMyWord("{pares_js}"))
        sslFlag = int(self.options.ssl_flag)
        if sslFlag == 1:
            demo = requests.get(url=url, headers=headers, proxies=self.proxy_data,verify=False).text
        else:
            demo = requests.get(url=url, headers=headers,proxies=self.proxy_data).text
        demo = demo.replace("<!--", "").replace("-->", "")  # 删去html注释
        soup = BeautifulSoup(demo, "html.parser")
        for item in soup.find_all("script"):
            jsPath = item.get("src")
            if jsPath:  # 处理src空情况
                self.jsPaths.append(jsPath)
            jsPathInScript = item.text #处理script标签里面的js内容
            jsPathInScript = jsPathInScript.encode()
            if jsPathInScript:
                #self.jsPathInScripts.append(jsPathInScript)
                jsTag = Utils().creatTag(6)
                res = urlparse(self.url)
                domain = res.netloc
                if ":" in domain:
                    domain = str(domain).replace(":", "_")
                PATH = "tmp/" + self.projectTag + "_" + domain +'/' + self.projectTag + ".db"

                conn = sqlite3.connect(os.sep.join(PATH.split('/')))
                cursor = conn.cursor()
                conn.isolation_level = None
                if "#" in self.url:
                    inurl = self.url.split("#")[0] + "/§§§"
                else:
                    inurl = self.url + "/§§§"
                sql = "insert into js_file(name,path,local) values('%s','%s','%s')" % (jsTag + ".js" , inurl , jsTag + ".js")
                cursor.execute(sql)
                with open("tmp" + os.sep + self.projectTag + "_" + domain + os.sep + jsTag + ".js", "wb") as js_file:
                    js_file.write(jsPathInScript)
                    js_file.close()
                    cursor.execute("UPDATE js_file SET success = 1 WHERE local='%s';" % (jsTag + ".js"))
                    conn.commit()
                conn.close()
        for item in soup.find_all("link"):  # 防止使用link标签情况
            jsPath = item.get("href")
            try:
                if jsPath[-2:] == "js":  # 防止提取css
                    self.jsPaths.append(jsPath)
            except:
                pass
        try:
            jsInScript = self.scriptCrawling(demo)
            self.log.debug("scriptCrawling模块正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)
        for jsPath in jsInScript:
            self.jsPaths.append(jsPath)
        try:
            self.dealJs(self.jsPaths)
            self.log.debug("dealjs函数正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)

    def dealJs(self, js_paths):  # 生成js绝对路径
        res = urlparse(self.url)  # 处理url多余部分
        if res.path == "":
            baseUrl = res.scheme + "://" + res.netloc + "/"
        else:
            baseUrl = res.scheme + "://" + res.netloc + res.path
            if res.path[-1:] != "/":  # 文件夹没"/",若输入的是文件也会被加上，但是影响不大
                baseUrl = baseUrl + "/"
        if self.url[-1:] != "/":  # 有文件的url
            tmpPath = res.path.split('/')
            tmpPath = tmpPath[:]  # 防止解析报错
            del tmpPath[-1]
            baseUrl = res.scheme + "://" + res.netloc + "/".join(tmpPath) + "/"
        for jsPath in js_paths:  # 路径处理多种情况./ ../ / http
            if jsPath[:2] == "./":
                jsPath = jsPath.replace("./", "")
                jsRealPath = baseUrl + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:3] == "../":
                dirCount = jsPath.count('../')
                tmpCount = 1
                jsPath = jsPath.replace("../", "")
                new_tmpPath = tmpPath[:]  # 防止解析报错
                while tmpCount <= dirCount:
                    del new_tmpPath[-1]
                    tmpCount = tmpCount + 1
                baseUrl = res.scheme + "://" + res.netloc + "/".join(new_tmpPath) + "/"
                jsRealPath = baseUrl + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:2] == "//":  # 自适应域名js
                jsRealPath = res.scheme + ":" + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:1] == "/":
                jsRealPath = res.scheme + "://" + res.netloc + jsPath
                self.jsRealPaths.append(jsRealPath)
            elif jsPath[:4] == "http":
                jsRealPath = jsPath
                self.jsRealPaths.append(jsRealPath)
            else:
                #jsRealPath = res.scheme + "://" + res.netloc + "/" + jsPath
                jsRealPath = baseUrl + jsPath #我感觉我原来的逻辑写错了
                self.jsRealPaths.append(jsRealPath)
        self.log.info(Utils().tellTime() + Utils().getMyWord("{pares_js_fini_1}") + str(len(self.jsRealPaths)) + Utils().getMyWord("{pares_js_fini_2}"))
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":", "_") #处理端口号
        DownloadJs(self.jsRealPaths,self.options).downloadJs(self.projectTag, domain, 0)
        extJS = CommandLines().cmd().js
        if extJS != None:
            extJSs = extJS.split(',')
            DownloadJs(extJSs,self.options).downloadJs(self.projectTag, domain, 0)

    def scriptCrawling(self, demo):  # 处理动态生成的js内容及html内的script
        res = urlparse(self.url)  # 处理url多余部分
        domain = res.netloc
        if ":" in domain:
            domain = str(domain).replace(":", "_") #处理端口号
        scriptInside = "" #初始为空
        soup = BeautifulSoup(demo, "html.parser")
        for item in soup.find_all("script"):
            scriptString = str(item.string)  # 防止特殊情况报错
            listSrc = re.findall(r'src=\"(.*?)\.js', scriptString)
            if not listSrc == []:
                for jsPath in listSrc:
                    self.jsPathList.append(jsPath)
            if scriptString != "None": #None被转成字符串了
                scriptInside = scriptInside + scriptString
        if scriptInside != "":
            DownloadJs(self.jsRealPaths,self.options).creatInsideJs(self.projectTag, domain, scriptInside, self.url)
        return self.jsPathList

    def parseJsStart(self):
        # unique_tag = DatabaseType().createProjectDatabase(self.url, 1, "0")
        # print(self.url)
        self.requestUrl()
