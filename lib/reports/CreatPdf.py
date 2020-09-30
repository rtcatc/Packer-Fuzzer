#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
from docx2pdf import convert
from lib.common.CreatLog import creatLog


class CreatPdf():

    def __init__(self,projectTag,namePdf):
        self.new_filepath = "reports" + os.sep + "tmp_" + projectTag + ".docx"
        self.pdf_filepath = namePdf
        self.log = creatLog().get_logger()

    def CreatMe(self):
        try:
            convert(self.new_filepath,self.pdf_filepath)
            self.log.debug("正确获取到pdf转化模块")
        except Exception as e:
            self.log.error("[Err] %s" % e)
