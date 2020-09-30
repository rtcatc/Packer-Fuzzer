#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from lib.common.utils import Utils
from lib.Database import DatabaseType


class ext():

    def __init__(self, projectTag, options):
        self.projectTag = projectTag
        self.options = options
        self.statut = 0   #0 disable  1 enable

    def start(self):
        if self.statut == 1:
            self.run()

    def run(self):
        print(Utils().tellTime() + "Hello Bonjour Hola 你好 こんにちは")
