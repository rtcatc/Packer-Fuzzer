# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import requests,sys
from lib.common.utils import Utils
from lib.common.cmdline import CommandLines

def testProxy(options,show):
    try:
        url = "http://ifconfig.me/ip"
        proxy_data = {
            'http': options.proxy,
            'https': options.proxy,
        }
        ipAddr = "127.0.0.1"
        ipAddr = requests.get(url, proxies=proxy_data, timeout=7, verify=False).text.strip()
        if show == 1:
            if options.silent == None:
                print("[+] " + Utils().getMyWord("{connect_s}") + ipAddr)
        return ipAddr
    except:
        if show == 1:
            if options.silent == None:
                print("[!] " + Utils().getMyWord("{connect_f}"))
        return ipAddr
