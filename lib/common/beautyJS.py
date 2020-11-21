# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import re,os,re
from urllib.parse import urlparse
from lib.common import readConfig
from lib.common.utils import Utils
from lib.Database import DatabaseType
from lib.common.cmdline import CommandLines


class BeautyJs():

    def __init__(self,projectTag):
        self.projectTag = projectTag

    def beauty_js(self,filePath):
        lines = open(filePath, encoding="utf-8",errors="ignore").read().split(";")
        indent = 0
        formatted = []
        for line in lines:
            newline = []
            for char in line:
                newline.append(char)
                if char == '{':
                    indent += 1
                    newline.append("\n")
                    newline.append("\t" * indent)
                if char == "}":
                    indent -= 1
                    newline.append("\n")
                    newline.append("\t" * indent)
            formatted.append("\t" * indent + "".join(newline))
        open(filePath, "w", encoding="utf-8",errors="ignore").writelines(";\n".join(formatted))

    def rewrite_js(self):
        projectPath = DatabaseType(self.projectTag).getPathfromDB()
        for parent, dirnames, filenames in os.walk(projectPath, followlinks=True):
            for filename in filenames:
                if filename != self.projectTag + ".db":
                    filePath = os.path.join(parent, filename)
                    BeautyJs(self.projectTag).beauty_js(filePath)
