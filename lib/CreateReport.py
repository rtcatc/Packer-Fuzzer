# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,re,sqlite3,time
from docx import Document   #用来建立一个word对象
from docx.shared import Pt  #用来设置字体的大小
from urllib.parse import urlparse
from lib.common.utils import Utils
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog
from lib.reports.CreatPdf import CreatPdf
from lib.reports.CreatTxt import CreatTxt
from lib.reports.CreatHtml import CreatHtml
from lib.common.cmdline import CommandLines
from lib.reports.CreatWord import Docx_replace


class CreateReport():

    def __init__(self,projectTag):
        self.projectTag = projectTag
        self.log = creatLog().get_logger()

    def create_repoter(self):
        main_url = DatabaseType(self.projectTag).getURLfromDB()
        parse_url = urlparse(main_url)
        host = parse_url.netloc.replace(':', '_') #win can not deal : in filename
        reportType = CommandLines().cmd().report
        reportTypes = reportType.split(',')
        if "doc" in reportTypes or "pdf" in reportTypes or "txt" in reportTypes or "html" in reportTypes:
            self.log.info(Utils().tellTime() + Utils().getMyWord("{report_creat}"))
        if "html" in reportTypes:
            if CommandLines().cmd().silent != None:
                nameHtml = "reports" + os.sep + CommandLines().cmd().silent + ".html"
            else:
                nameHtml = "reports" + os.sep + host + "-" + self.projectTag + ".html"
            if os.path.exists("reports" + os.sep + "res"):
                pass
            else:
                Utils().copyPath("doc" + os.sep + "template" + os.sep + "html" + os.sep + "res","reports")
            try:
                CreatHtml(self.projectTag,nameHtml).CreatMe()
                self.log.debug("html模板正常")
            except Exception as e:
                self.log.error("[Err] %s" % e)
        if "doc" in reportTypes or "pdf" in reportTypes or "txt" in reportTypes:
            Docx_replace(self.projectTag).mainReplace()
            if "doc" in reportTypes:
                if CommandLines().cmd().silent != None:
                    nameDoc = "reports" + os.sep + CommandLines().cmd().silent + ".docx"
                else:
                    nameDoc = "reports" + os.sep + host + "-" + self.projectTag + ".docx"
                Docx_replace(self.projectTag).docMove(nameDoc)
            if "txt" in reportTypes:
                if CommandLines().cmd().silent != None:
                    nameTxt = "reports" + os.sep + CommandLines().cmd().silent + ".txt"
                else:
                    nameTxt = "reports" + os.sep + host + "-" + self.projectTag + ".txt"
                CreatTxt(self.projectTag,nameTxt).CreatMe()
            if "pdf" in reportTypes:
                if CommandLines().cmd().silent != None:
                    namePdf =  "reports" + os.sep + CommandLines().cmd().silent + ".pdf"
                else:
                    namePdf = "reports" + os.sep + host + "-" + self.projectTag + ".pdf"
                CreatPdf(self.projectTag,namePdf).CreatMe()
            Docx_replace(self.projectTag).docDel()
        if "doc" in reportTypes or "pdf" in reportTypes or "txt" in reportTypes or "html" in reportTypes:
            time.sleep(2) #waiting
            self.log.info(Utils().tellTime() + Utils().getMyWord("{report_fini}"))
