#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys,os


class loadExtensions():

    def __init__(self, projectTag, options):
        self.projectTag = projectTag
        self.options = options

    def runExt(self):
        path = r"ext"
        sys.path.append(path)
        for root, dirs, files in os.walk(r"ext"):
            for file in files:
                if os.path.join(root,file).split(os.sep)[-1].split(".")[-1] == "py" and file != '__init__.py':
                    module_name = os.path.join(root,file).split(os.sep)[-1].split(".")[0]
                    module = __import__(module_name)
                    module.ext(self.projectTag, self.options).start()
