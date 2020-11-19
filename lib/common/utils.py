# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,random,locale,time,shutil
from lib.common import readConfig
from lib.common.cmdline import CommandLines


class Utils():

    def creatTag(self, num):  # 生成随机tag
        H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        salt = ''
        for i in range(num):
            salt += random.choice(H)
        return salt

    def getFilename(self, url):
        filename = url.split('/')[-1]
        filename = filename.split('?')[0]
        return filename

    def creatSometing(self, choice, path):  # choice1文件夹，2文件
        # 返回0已经存在，返回1创建文件夹成功，返回2创建文件夹失败
        if choice == 1:
            path = path.split('/')  # 输入统一用 /
            path = os.sep.join(path)
            path = os.getcwd() + os.sep + path
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                    return 1
            except:
                return 2
            return 0
        if choice == 2:
            path = path.split('/')
            del path[-1]
            path = os.sep.join(path)    #
            path = os.getcwd() + os.sep + path
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                    return 1
            except:
                return 2
            return 0

    def getMiddleStr(self, content, startStr, endStr):  # 获取中间字符串通用函数
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.index(endStr)
        return content[startIndex:endIndex]

    def getMyWord(self, someWord):
        lang = CommandLines().cmd().language
        if lang:
            localLang = lang
        else:
            try:
                localLang = locale.getdefaultlocale()[0][0:2]
            except:
                localLang = 'en' #默认英语
        try:
            myWord = readConfig.ReadConfig().getLang(localLang,someWord)[0]
        except:
            myWord = readConfig.ReadConfig().getLang('en',someWord)[0] #默认英语
        return myWord

    def tellTime(self): #时间输出
        localtime = "[" + str(time.strftime('%H:%M:%S',time.localtime(time.time()))) + "] "
        return localtime

    def getMD5(self,file_path):
        files_md5 = os.popen('md5 %s' % file_path).read().strip()
        file_md5 = files_md5.replace('MD5 (%s) = ' % file_path, '')
        return file_md5

    def copyPath(self,path,out):
        out = out + os.sep + path.split(os.sep)[-1]
        os.mkdir(out)
        for files in os.listdir(path):
            name = os.path.join(path, files)
            back_name = os.path.join(out, files)
            if os.path.isfile(name):
                if os.path.isfile(back_name):
                    if self.getMD5(name) != self.getMD5(back_name):
                        shutil.copy(name,back_name)
                else:
                    shutil.copy(name, back_name)
            else:
                if not os.path.isdir(back_name):
                    os.makedirs(back_name)
                self.main(name, back_name)
