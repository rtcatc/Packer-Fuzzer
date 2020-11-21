#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from docx2txt import process
from lib.common.CreatLog import creatLog


class CreatTxt():

    def __init__(self,projectTag,nameTxt):
        self.new_filepath = "reports" + os.sep + "tmp_" + projectTag + ".docx"
        self.txt_filepath = nameTxt
        self.log = creatLog().get_logger()

    def CreatMe(self):
        try:
            text = process(self.new_filepath)
            self.log.debug("正确获取到process模块")
        except Exception as e:
            self.log.error("[Err] %s" % e)
        if "\n\n\n\n\n" in text:
            text1 = text.replace("\n\n\n\n\n", "\n")
        with open(self.txt_filepath, "w", encoding="utf-8",errors="ignore") as f:
            f.write(text1)
            f.close()
