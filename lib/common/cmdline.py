# !/usr/bin/env python3
# -*- encoding: utf-8 -*-

import optparse,sys


class CommandLines():

    def cmd(self):
        parse = optparse.OptionParser()
        parse.add_option('-u', '--url', dest='url', help='Please Enter the Target Site')
        parse.add_option('-c', '--cookie', dest='cookie', help='Please Enter the Site Cookies')
        parse.add_option('-d', '--head', dest='head', default='Cache-Control:no-cache', help='Please Enter the extra HTTP head')
        parse.add_option('-l', '--lang', dest='language', help='Please Select Language')
        parse.add_option('-t', '--type', dest='type', default='simple', help='Please Select Scan Mode')
        parse.add_option('-p', '--proxy', dest='proxy', type=str, help='Please Enter your own Proxy Address')
        parse.add_option('-j', '--js', dest='js', type=str, help='Extra JS Files')
        parse.add_option('-b', '--base', dest='baseurl', type=str, help='Please Enter the baseurl')
        parse.add_option('-r', '--report', dest='report', default='html,doc', type=str, help='Choose your report\'s type')
        parse.add_option('-e', '--ext', dest='ext', default='off', type=str, help='Enable Extensions')
        parse.add_option('-f', '--flag', dest='ssl_flag', default='0', type=str, help='SSL SEC FLAG')
        parse.add_option('-s', '--silent', dest='silent', type=str, help='Silent Mode (Custom Report Name)')
        (options, args) = parse.parse_args()
        if options.url == None:
            parse.print_help()
            sys.exit(0)
        return options


if __name__ == '__main__':
    print(CommandLines().cmd().cookie)
