#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os,sqlite3,time,shutil,json
from docx.shared import RGBColor
from urllib.parse import urlparse
from lib.common.utils import Utils
from lib.TestProxy import testProxy
from lib.Database import DatabaseType
from lib.common.CreatLog import creatLog
from lib.common.cmdline import CommandLines
from lib.reports.CreatWord import Docx_replace


class CreatHtml():

    def __init__(self,projectTag,nameHtml):
        self.projectTag = projectTag
        self.html_filepath = nameHtml
        self.creat_vuln_num = 1
        self.creat_api_num = 1
        self.creat_cors_num = 1
        self.info_num = 1
        self.log = creatLog().get_logger()

    #外面标签条
    def vuln_list(self):
        global creat_vuln_num
        creat_vuln_num = 1
        tr_whole_api_list = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "unAuth" and vuln_info[4] == 1:
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    tr_api_list = """
                    <tr>
                      <td>{vuln_num}</td>
                      <td>{vuln_api_name}</td>
                      <td>{vuln_url}</td>
                      <td>{vuln_url_type}</td>
                      <td>{vuln_risk}</td>
                      <td>{vuln_length}</td>
                      <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                    </tr>"""
                    if api_info[5] == 1:
                        vuln_url_type = Utils().getMyWord("{r_get}")
                    else:
                        vuln_url_type = Utils().getMyWord("{r_post}")
                    tr_api_list = tr_api_list.replace("{vuln_num}", str(self.creat_api_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    try:
                        api_length_info = len(api_info[4])
                    except:
                        api_length_info = 0
                    for js_path in js_paths:
                        tr_api_list = tr_api_list.replace("{vuln_api_name}",api_info[2])
                        tr_api_list = tr_api_list.replace("{vuln_url}", api_info[1])
                        tr_api_list = tr_api_list.replace("{vuln_url_type}", vuln_url_type)
                        tr_api_list = tr_api_list.replace("{vuln_length}", str(api_length_info))
                        tr_api_list = tr_api_list.replace("{vuln_risk}", Utils().getMyWord("{r_l_m}"))
                        tr_api_list = tr_api_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                        self.creat_api_num = self.creat_api_num + 1
                        creat_vuln_num = creat_vuln_num + 1
                        tr_whole_api_list = tr_whole_api_list + tr_api_list
            elif vuln_info[3] == "unAuth" and vuln_info[4] == 2:
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    tr_api_list = """
                    <tr>
                      <td>{vuln_num}</td>
                      <td>{vuln_api_name}</td>
                      <td>{vuln_url}</td>
                      <td>{vuln_url_type}</td>
                      <td>{vuln_risk}</td>
                      <td>{vuln_length}</td>
                      <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                    </tr>"""
                    if api_info[5] == 1:
                        vuln_url_type = Utils().getMyWord("{r_get}")
                    else:
                        vuln_url_type = Utils().getMyWord("{r_post}")
                    tr_api_list = tr_api_list.replace("{vuln_num}", str(self.creat_api_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    try:
                        api_length_info = len(api_info[4])
                    except:
                        api_length_info = 0
                    for js_path in js_paths:
                        tr_api_list = tr_api_list.replace("{vuln_api_name}", api_info[2])
                        tr_api_list = tr_api_list.replace("{vuln_url}", api_info[1])
                        tr_api_list = tr_api_list.replace("{vuln_url_type}", vuln_url_type)
                        tr_api_list = tr_api_list.replace("{vuln_length}", str(api_length_info))
                        tr_api_list = tr_api_list.replace("{vuln_risk}", Utils().getMyWord("{r_l_l}") + "，" + Utils().getMyWord("{r_vuln_maybe}"))
                        tr_api_list = tr_api_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                        self.creat_api_num = self.creat_api_num + 1
                        creat_vuln_num = creat_vuln_num + 1
                        tr_whole_api_list = tr_whole_api_list + tr_api_list
        return tr_whole_api_list


    def info_list(self):
        global creat_vuln_num
        tr_whole_info_list = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "INFO":
                sql = "select * from js_file where id='%s'" % (vuln_info[2])
                cursor.execute(sql)
                js_infos = cursor.fetchall()
                for js_info in js_infos:
                    tr_info_list = """
                    <tr>
                        <td>{vuln_num}</td>
                        <td>{vuln_des}</td>
                        <td>{vuln_url}</td>
                        <td>{vuln_info_less}</td>
                        <td>{vuln_risk}</td>
                        <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                    </tr>"""
                    tr_info_list = tr_info_list.replace("{vuln_num}",str(self.creat_api_num))
                    tr_info_list = tr_info_list.replace("{vuln_des}", vuln_info[8])
                    tr_info_list = tr_info_list.replace("{vuln_risk}", Utils().getMyWord("{r_l_m}"))
                    tr_info_list = tr_info_list.replace("{vuln_url}", js_info[2])
                    tr_info_list = tr_info_list.replace("{vuln_info_less}", vuln_info[6])
                    tr_info_list = tr_info_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                    creat_vuln_num = creat_vuln_num + 1
                    self.creat_api_num = self.creat_api_num + 1
                    tr_whole_info_list = tr_whole_info_list + tr_info_list
        return tr_whole_info_list

    def vuln_list_password(self):
        global creat_vuln_num
        tr_whole_password_list = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "passWord":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    tr_api_list = """
                    <tr>
                      <td>{vuln_num}</td>
                      <td>{vuln_api_name}</td>
                      <td>{vuln_url}</td>
                      <td>{vuln_url_type}</td>
                      <td>{vuln_risk}</td>
                      <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                    </tr>"""
                    option = api_info[3]
                    json_strs = json.loads(option)
                    if json_strs["type"] == "post":
                        vuln_url_type = Utils().getMyWord("{r_post}")
                    else:
                        vuln_url_type = Utils().getMyWord("{r_get}")
                    tr_api_list = tr_api_list.replace("{vuln_num}", str(self.creat_api_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    for js_path in js_paths:
                        tr_api_list = tr_api_list.replace("{vuln_api_name}",api_info[2])
                        tr_api_list = tr_api_list.replace("{vuln_url}", api_info[1])
                        tr_api_list = tr_api_list.replace("{vuln_url_type}", vuln_url_type)
                        tr_api_list = tr_api_list.replace("{vuln_risk}", Utils().getMyWord("{r_l_h}"))
                        tr_api_list = tr_api_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                        self.creat_api_num = self.creat_api_num + 1
                        creat_vuln_num = creat_vuln_num + 1
                        tr_whole_password_list = tr_whole_password_list + tr_api_list
        return tr_whole_password_list

    def cors_list(self):
        global creat_vuln_num
        tr_whole_cors_list = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        sql = "select vaule from info where name='%s'" % ("host")
        cursor.execute(sql)
        infos = cursor.fetchall()
        api_path = infos[0][0]
        tr_cors_list = """
                            <tr>
                              <td>{vuln_api_path}</td>
                              <td>{vuln_payload}</td>
                              <td>{vuln_risk}</td>
                              <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                            </tr>"""
        for vuln_info in vuln_infos:
            if vuln_info[3] == "CORS":
                tr_cors_list = tr_cors_list.replace("{vuln_api_path}",api_path)
                tr_cors_list = tr_cors_list.replace("{vuln_payload}", vuln_info[5])
                tr_cors_list = tr_cors_list.replace("{vuln_risk}",  Utils().getMyWord("{r_l_l}"))
                tr_cors_list = tr_cors_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                self.creat_api_num = self.creat_api_num + 1
                creat_vuln_num = creat_vuln_num + 1
                tr_whole_cors_list = tr_whole_cors_list + tr_cors_list
        return tr_whole_cors_list


    def vuln_bac_list(self):
        global creat_vuln_num
        tr_whole_api_list = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "BAC":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    tr_api_list = """
                    <tr>
                      <td>{vuln_num}</td>
                      <td>{vuln_api_name}</td>
                      <td>{vuln_url}</td>
                      <td>{vuln_url_type}</td>
                      <td>{vuln_risk}</td>
                      <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                    </tr>"""
                    if api_info[5] == 1:
                        vuln_url_type = Utils().getMyWord("{r_get}")
                    else:
                        vuln_url_type = Utils().getMyWord("{r_post}")
                    tr_api_list = tr_api_list.replace("{vuln_num}", str(self.creat_api_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    for js_path in js_paths:
                        tr_api_list = tr_api_list.replace("{vuln_api_name}", api_info[2])
                        tr_api_list = tr_api_list.replace("{vuln_url}", api_info[1])
                        tr_api_list = tr_api_list.replace("{vuln_url_type}", vuln_url_type)
                        tr_api_list = tr_api_list.replace("{vuln_risk}", Utils().getMyWord("{r_l_m}"))
                        tr_api_list = tr_api_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                        self.creat_api_num = self.creat_api_num + 1
                        creat_vuln_num = creat_vuln_num + 1
                        tr_whole_api_list = tr_whole_api_list + tr_api_list
        return tr_whole_api_list

    def vuln_upload_list(self):
        global creat_vuln_num
        tr_whole_api_list = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "upLoad":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    tr_api_list = """
                            <tr>
                              <td>{vuln_num}</td>
                              <td>{vuln_api_name}</td>
                              <td>{vuln_url}</td>
                              <td>{vuln_url_type}</td>
                              <td>{vuln_risk}</td>
                              <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                            </tr>"""
                    if api_info[5] == 1:
                        vuln_url_type = Utils().getMyWord("{r_get}")
                    else:
                        vuln_url_type = Utils().getMyWord("{r_post}")
                    tr_api_list = tr_api_list.replace("{vuln_num}", str(self.creat_api_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    for js_path in js_paths:
                        tr_api_list = tr_api_list.replace("{vuln_api_name}", api_info[2])
                        tr_api_list = tr_api_list.replace("{vuln_url}", api_info[1])
                        tr_api_list = tr_api_list.replace("{vuln_url_type}", "POST")
                        tr_api_list = tr_api_list.replace("{vuln_risk}", Utils().getMyWord("{r_l_h}"))
                        tr_api_list = tr_api_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                        self.creat_api_num = self.creat_api_num + 1
                        creat_vuln_num = creat_vuln_num + 1
                        tr_whole_api_list = tr_whole_api_list + tr_api_list
        return tr_whole_api_list


    def vuln_sql_list(self):
        global creat_vuln_num
        tr_whole_api_list = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "SQL":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    tr_api_list = """
                                    <tr>
                                      <td>{vuln_num}</td>
                                      <td>{vuln_api_name}</td>
                                      <td>{vuln_url}</td>
                                      <td>{vuln_url_type}</td>
                                      <td>{vuln_risk}</td>
                                      <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{vuln_id}">More</button></td>
                                    </tr>"""
                    if api_info[5] == 1:
                        vuln_url_type = Utils().getMyWord("{r_get}")
                    else:
                        vuln_url_type = Utils().getMyWord("{r_post}")
                    tr_api_list = tr_api_list.replace("{vuln_num}", str(self.creat_api_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    for js_path in js_paths:
                        tr_api_list = tr_api_list.replace("{vuln_api_name}", api_info[2])
                        tr_api_list = tr_api_list.replace("{vuln_url}", api_info[1])
                        tr_api_list = tr_api_list.replace("{vuln_url_type}", vuln_url_type)
                        tr_api_list = tr_api_list.replace("{vuln_risk}", Utils().getMyWord("{r_l_h}"))
                        tr_api_list = tr_api_list.replace("{vuln_id}", "vuln_" + str(creat_vuln_num))
                        self.creat_api_num = self.creat_api_num + 1
                        creat_vuln_num = creat_vuln_num + 1
                        tr_whole_api_list = tr_whole_api_list + tr_api_list
        return tr_whole_api_list

    # more里面的内容
    def vuln_detail_html(self):
        whole_html = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "unAuth" and vuln_info[4] == 1:
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    unauth_info_html = """
<div id="{vuln_id}" class="modal fade" role="dialog">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h6 class="modal-title">%s...</h4>
            </div>
            <div class="modal-body">
                <div class="box-body no-padding">
                    <p>
                        %s：%s<br><br>
            %s：{vuln_risk}<br><br>
            %s：<a href="{vuln_url}">{vuln_url}</a><br><br>
            %s {vuln_js}<br><br>
            %s <code>{vuln_res}</code><br>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>"""%(Utils().getMyWord("{vuln_info}"),Utils().getMyWord("{vuln_type}"),Utils().getMyWord("{unauth_vuln}"),Utils().getMyWord("{vuln_level}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_api_js}"),Utils().getMyWord("{r_api_res}"))
                    unauth_info_html = unauth_info_html.replace("{vuln_id}","vuln_" + str(self.creat_vuln_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    for js_path in js_paths:
                        if vuln_info[6] == None:
                            vuln_res = ""
                        else:
                            vuln_res = vuln_info[6]
                        self.creat_vuln_num = self.creat_vuln_num + 1
                        unauth_info_html = unauth_info_html.replace("{vuln_risk}", Utils().getMyWord("{r_l_m}"))
                        unauth_info_html = unauth_info_html.replace("{vuln_url}", api_info[1])
                        unauth_info_html = unauth_info_html.replace("{vuln_js}", js_path[0])
                        unauth_info_html = unauth_info_html.replace("{vuln_res}", vuln_res)
                        whole_html = whole_html + unauth_info_html
            elif vuln_info[3] == "unAuth" and vuln_info[4] == 2:
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    unauth_info_html = """
<div id="{vuln_id}" class="modal fade" role="dialog">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h6 class="modal-title">%s...</h4>
            </div>
            <div class="modal-body">
                <div class="box-body no-padding">
                    <p>
                        %s：%s<br><br>
            %s：{vuln_risk}<br><br>
            %s：<a href="{vuln_url}">{vuln_url}</a><br><br>
            %s {vuln_js}<br><br>
            %s <code>{vuln_res}</code><br>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>"""%(Utils().getMyWord("{vuln_info}"),Utils().getMyWord("{vuln_type}"),Utils().getMyWord("{unauth_vuln}"),Utils().getMyWord("{vuln_level}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_api_js}"),Utils().getMyWord("{r_api_res}"))
                    unauth_info_html = unauth_info_html.replace("{vuln_id}", "vuln_" + str(self.creat_vuln_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    for js_path in js_paths:
                        if vuln_info[6] == None:
                            vuln_res = ""
                        else:
                            vuln_res = vuln_info[6]
                        self.creat_vuln_num = self.creat_vuln_num + 1
                        unauth_info_html = unauth_info_html.replace("{vuln_risk}", Utils().getMyWord("{r_l_l}") + "，" + Utils().getMyWord("{r_vuln_maybe}"))
                        unauth_info_html = unauth_info_html.replace("{vuln_url}", api_info[1])
                        unauth_info_html = unauth_info_html.replace("{vuln_js}", js_path[0])
                        unauth_info_html = unauth_info_html.replace("{vuln_res}", vuln_res)
                        whole_html = whole_html + unauth_info_html
            elif vuln_info[3] == "INFO":
                sql = "select * from js_file where id='%s'" % (vuln_info[2])
                cursor.execute(sql)
                js_infos = cursor.fetchall()
                for js_info in js_infos:
                    info_html = """
<div id="{vuln_id}" class="modal fade" role="dialog">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h6 class="modal-title">%s...</h4>
            </div>
            <div class="modal-body">
                <div class="box-body no-padding">
                    <p>
                        %s：%s<br><br>
            %s：{vuln_risk}<br><br>
            %s {vuln_des}<br><br>
            %s <a href="{vuln_url}">{vuln_url}</a><br><br>
            %s <b>{vuln_info_less}</b><br><br>
            %s： <code>{vuln_info_more}</code><br>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>"""%(Utils().getMyWord("{vuln_info}"),Utils().getMyWord("{vuln_type}"),Utils().getMyWord("{info_vuln}"),Utils().getMyWord("{vuln_level}"),Utils().getMyWord("{r_js_des}"),Utils().getMyWord("{r_api_js}"),Utils().getMyWord("{r_js_detial}"),Utils().getMyWord("{related_frag}"))
                    info_html = info_html.replace("{vuln_id}","vuln_" + str(self.creat_vuln_num))
                    info_html = info_html.replace("{vuln_risk}", Utils().getMyWord("{r_l_m}"))
                    info_html = info_html.replace("{vuln_des}", vuln_info[8])
                    info_html = info_html.replace("{vuln_url}", js_info[2])
                    info_html = info_html.replace("{vuln_info_less}", vuln_info[6])
                    info_html = info_html.replace("{vuln_info_more}", vuln_info[7])
                    self.creat_vuln_num = self.creat_vuln_num + 1
                    whole_html = whole_html + info_html
            elif vuln_info[3] == "passWord":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    passWord_info_html = """
<div id="{vuln_id}" class="modal fade" role="dialog">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h6 class="modal-title">%s...</h4>
            </div>
            <div class="modal-body">
                <div class="box-body no-padding">
                    <p>
                        %s：%s<br><br>
            %s：{vuln_risk}<br><br>
            %s：<a href="{vuln_url}">{vuln_url}</a><br><br>
            %s {vuln_js}<br><br>
            %s <code>{vuln_res2}</code><br><br>
            %s <code>{vuln_res}</code>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>"""%(Utils().getMyWord("{vuln_info}"),Utils().getMyWord("{vuln_type}"),Utils().getMyWord("{passWord_vuln}"),Utils().getMyWord("{vuln_level}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_api_js}"),Utils().getMyWord("{request_info}"),Utils().getMyWord("{r_api_res}"))
                    passWord_info_html = passWord_info_html.replace("{vuln_id}", "vuln_" + str(self.creat_vuln_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    for js_path in js_paths:
                        if vuln_info[6] == None:
                            vuln_res = ""
                        else:
                            vuln_res = vuln_info[6]
                        self.creat_vuln_num = self.creat_vuln_num + 1
                        passWord_info_html = passWord_info_html.replace("{vuln_risk}", Utils().getMyWord(
                            "{r_l_h}"))
                        passWord_info_html = passWord_info_html.replace("{vuln_url}", api_info[1])
                        passWord_info_html = passWord_info_html.replace("{vuln_js}", js_path[0])
                        passWord_info_html = passWord_info_html.replace("{vuln_res}", vuln_res)
                        passWord_info_html = passWord_info_html.replace("{vuln_res2}", vuln_info[5])
                        whole_html = whole_html + passWord_info_html
            elif vuln_info[3] == "CORS":
                sql = "select vaule from info where name='%s'" % ("host")
                cursor.execute(sql)
                infos = cursor.fetchall()
                api_path = infos[0][0]
                cors_info_html="""
                <div id="{vuln_id}" class="modal fade" role="dialog">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h6 class="modal-title">%s...</h4>
            </div>
            <div class="modal-body">
                <div class="box-body no-padding">
                    <p>
                        %s：%s<br><br>
            %s：{vuln_risk}<br><br>
            %s：<a href="{vuln_url}">{vuln_url}</a><br><br>
            %s： <code>{vuln_res2}</code><br><br>
            %s： <code>{vuln_res}</code>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>"""%(Utils().getMyWord("{vuln_info}"),Utils().getMyWord("{vuln_type}"),Utils().getMyWord("{CORS_vuln}"),Utils().getMyWord("{vuln_level}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{request_head}"),Utils().getMyWord("{response_head}"))
                cors_info_html = cors_info_html.replace("{vuln_id}", "vuln_" + str(self.creat_vuln_num))
                self.creat_vuln_num = self.creat_vuln_num + 1
                cors_info_html = cors_info_html.replace("{vuln_url}", api_path)
                cors_info_html = cors_info_html.replace("{vuln_risk}", Utils().getMyWord("{r_l_l}"))
                cors_info_html = cors_info_html.replace("{vuln_res}", vuln_info[7])
                cors_info_html = cors_info_html.replace("{vuln_res2}", vuln_info[5])
                whole_html = whole_html + cors_info_html
            elif vuln_info[3] == "BAC":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    BAC_info_html = """
                <div id="{vuln_id}" class="modal fade" role="dialog">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h6 class="modal-title">%s...</h4>
                            </div>
                            <div class="modal-body">
                                <div class="box-body no-padding">
                                    <p>
                                        %s：%s<br><br>
                            %s：{vuln_risk}<br><br>
                            %s：<a href="{vuln_url}">{vuln_url}</a><br><br>
                            %s：{vuln_js}<br><br>
                            %s1： <code>{vuln_res1}</code><br><br>
                            %s1： <code>{vuln_res3}</code><br><br>
                            %s2： <code>{vuln_res2}</code><br><br>
                            %s2： <code>{vuln_res4}</code><br><br>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>""" % (Utils().getMyWord("{vuln_info}"), Utils().getMyWord("{vuln_type}"),
                             Utils().getMyWord("{BAC_vuln}"), Utils().getMyWord("{vuln_level}"),
                             Utils().getMyWord("{vuln_path}"), Utils().getMyWord("{r_api_js}"),
                             Utils().getMyWord("{request_info}"),Utils().getMyWord("{respons_info}"),Utils().getMyWord("{request_info}"),Utils().getMyWord("{respons_info}"))
                    BAC_info_html = BAC_info_html.replace("{vuln_id}", "vuln_" + str(self.creat_vuln_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    vuln_res1 = vuln_info[5].split("§§§")[0]
                    vuln_res2 = vuln_info[5].split("§§§")[1]
                    vuln_res3 = vuln_info[6].split("§§§")[0]
                    vuln_res4 = vuln_info[6].split("§§§")[1]
                    self.creat_vuln_num = self.creat_vuln_num + 1
                    BAC_info_html = BAC_info_html.replace("{vuln_risk}", Utils().getMyWord("{r_l_m}"))
                    BAC_info_html = BAC_info_html.replace("{vuln_url}", api_info[1])
                    BAC_info_html = BAC_info_html.replace("{vuln_js}", js_path[0])
                    BAC_info_html = BAC_info_html.replace("{vuln_res1}", vuln_res1)
                    BAC_info_html = BAC_info_html.replace("{vuln_res2}", vuln_res2)
                    BAC_info_html = BAC_info_html.replace("{vuln_res3}", vuln_res3)
                    BAC_info_html = BAC_info_html.replace("{vuln_res4}", vuln_res4)
                    whole_html = whole_html + BAC_info_html
            elif vuln_info[3] == "upLoad":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    upload_info_html = """
                <div id="{vuln_id}" class="modal fade" role="dialog">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h6 class="modal-title">%s...</h4>
                            </div>
                            <div class="modal-body">
                                <div class="box-body no-padding">
                                    <p>
                                        %s：%s<br><br>
                            %s：{vuln_risk}<br><br>
                            %s：<a href="{vuln_url}">{vuln_url}</a><br><br>
                            %s：{vuln_js}<br><br>
                            %s： <code>{vuln_res1}</code><br><br>
                            %s： <code>{vuln_res2}</code><br><br>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>""" % (Utils().getMyWord("{vuln_info}"), Utils().getMyWord("{vuln_type}"),
                             Utils().getMyWord("{upload_vuln}"), Utils().getMyWord("{vuln_level}"),
                             Utils().getMyWord("{vuln_path}"), Utils().getMyWord("{r_api_js}"),
                             Utils().getMyWord("{request_info}"),Utils().getMyWord("{respons_info}"))
                    upload_info_html = upload_info_html.replace("{vuln_id}", "vuln_" + str(self.creat_vuln_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    self.creat_vuln_num = self.creat_vuln_num + 1
                    upload_info_html = upload_info_html.replace("{vuln_risk}", Utils().getMyWord("{r_l_h}"))
                    upload_info_html = upload_info_html.replace("{vuln_url}", api_info[1])
                    upload_info_html = upload_info_html.replace("{vuln_js}", js_path[0])
                    upload_info_html = upload_info_html.replace("{vuln_res1}", vuln_info[5])
                    upload_info_html = upload_info_html.replace("{vuln_res2}", vuln_info[6])
                    whole_html = whole_html + upload_info_html
            elif vuln_info[3] == "SQL":
                sql = "select * from api_tree where id='%s'" % (vuln_info[1])
                cursor.execute(sql)
                api_infos = cursor.fetchall()
                for api_info in api_infos:
                    upload_info_html = """
                <div id="{vuln_id}" class="modal fade" role="dialog">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h6 class="modal-title">%s...</h4>
                            </div>
                            <div class="modal-body">
                                <div class="box-body no-padding">
                                    <p>
                                        %s：%s<br><br>
                            %s：{vuln_risk}<br><br>
                            %s：<a href="{vuln_url}">{vuln_url}</a><br><br>
                            %s：{vuln_js}<br><br>
                            %s： <code>{vuln_res1}</code><br><br>
                            %s： <code>{vuln_res2}</code><br><br>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>""" % (Utils().getMyWord("{vuln_info}"), Utils().getMyWord("{vuln_type}"),
                             Utils().getMyWord("{sql_vuln}"), Utils().getMyWord("{vuln_level}"),
                             Utils().getMyWord("{vuln_path}"), Utils().getMyWord("{r_api_js}"),
                             Utils().getMyWord("{request_info}"),Utils().getMyWord("{respons_info}"))
                    upload_info_html = upload_info_html.replace("{vuln_id}", "vuln_" + str(self.creat_vuln_num))
                    sql = "select path from js_file where id='%s'" % (vuln_info[2])
                    cursor.execute(sql)
                    js_paths = cursor.fetchall()
                    self.creat_vuln_num = self.creat_vuln_num + 1
                    upload_info_html = upload_info_html.replace("{vuln_risk}", Utils().getMyWord("{r_l_h}"))
                    upload_info_html = upload_info_html.replace("{vuln_url}", api_info[1])
                    upload_info_html = upload_info_html.replace("{vuln_js}", js_path[0])
                    upload_info_html = upload_info_html.replace("{vuln_res1}", vuln_info[5])
                    upload_info_html = upload_info_html.replace("{vuln_res2}", vuln_info[6])
                    whole_html = whole_html + upload_info_html

        return whole_html
    # elif vuln_info[3] == "sql"
    def api_list_html(self):
        vuln_whole_list = ""

        api_list_str = """
<a id="vuln_unauth" class="anchor"></a>
              <h6>◆ %s</h6>
                 <table class="table table-hover">
                  <thead class="ant-table-thead">
                  <tr>
                     <th style="width:6%%">ID</th>
                     <th style="width:16%%">%s</th>
                     <th>%s</th>
                     <th style="width:15%%">%s</th>
                     <th style="width:10%%">%s</th>
                     <th style="width:5%%">%s</th>
                     <th style="width:6%%"></th>
                  </tr>
                  </thead><tbody class="ant-table-tbody">
                    {tr_unAuth_list}
                </tbody>
                </table><hr>"""%(Utils().getMyWord("{unauth_vuln}"),Utils().getMyWord("{api_name}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_type}"),Utils().getMyWord("{vuln_level}"),Utils().getMyWord("{api_length}"))

        info_list_str = """
<a id="vuln_info" class="anchor"></a>
                <h6>◆ %s</h6>
                   <table class="table table-hover">
                    <thead class="ant-table-thead">
                    <tr>
                       <th style="width:6%%">ID</th>
                       <th style="width:16%%">%s</th>
                       <th>%s</th>
                       <th style="width:17%%">%s</th>
                       <th style="width:10%%">%s</th>
                       <th style="width:6%%"></th>
                    </tr>
                    </thead><tbody class="ant-table-tbody">
                      {tr_info_vuln}
                  </tbody>
                  </table><hr>"""%(Utils().getMyWord("{info_vuln}"),Utils().getMyWord("{info_vuln_type}"),Utils().getMyWord("{r_api_js}"),Utils().getMyWord("{r_js_detial}"),Utils().getMyWord("{vuln_level}"))

        passWord_list_str = """
        <a id="vuln_password" class="anchor"></a>
                      <h6>◆ %s</h6>
                         <table class="table table-hover">
                          <thead class="ant-table-thead">
                          <tr>
                             <th style="width:6%%">ID</th>
                             <th style="width:16%%">%s</th>
                             <th>%s</th>
                             <th style="width:15%%">%s</th>
                             <th style="width:10%%">%s</th>
                             <th style="width:6%%"></th>
                          </tr>
                          </thead><tbody class="ant-table-tbody">
                            {tr_passWord_list}
                        </tbody>
                        </table><hr>""" % (
        Utils().getMyWord("{passWord_vuln}"), Utils().getMyWord("{api_name}"), Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_type}"), Utils().getMyWord("{vuln_level}"))

        cors_list_str = """
        <a id="vuln_cors" class="anchor"></a>
                      <h6>◆ %s</h6>
                         <table class="table table-hover">
                          <thead class="ant-table-thead">
                          <tr>
                             <th style="width:29%%">%s</th>
                             <th style="width:55%%">%s</th>
                             <th style="width:10%%">%s</th>
                             <th style="width:6%%"></th>
                          </tr>
                          </thead><tbody class="ant-table-tbody">
                            {tr_cors_list}
                        </tbody>
                        </table><hr>""" % (
        Utils().getMyWord("{CORS_vuln}"), Utils().getMyWord("{web_addr}"), "Payload",Utils().getMyWord("{vuln_level}"))

        bac_list_str = """
<a id="vuln_bac" class="anchor"></a>
              <h6>◆ %s</h6>
                 <table class="table table-hover">
                  <thead class="ant-table-thead">
                  <tr>
                     <th style="width:6%%">ID</th>
                     <th style="width:16%%">%s</th>
                     <th>%s</th>
                     <th style="width:15%%">%s</th>
                     <th style="width:10%%">%s</th>
                     <th style="width:6%%"></th>
                  </tr>
                  </thead><tbody class="ant-table-tbody">
                    {tr_bac_list}
                </tbody>
                </table><hr>"""%(Utils().getMyWord("{BAC_vuln}"),Utils().getMyWord("{api_name}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_type}"),Utils().getMyWord("{vuln_level}"))

        upload_list_str = """
<a id="vuln_upload" class="anchor"></a>
              <h6>◆ %s</h6>
                 <table class="table table-hover">
                  <thead class="ant-table-thead">
                  <tr>
                     <th style="width:6%%">ID</th>
                     <th style="width:16%%">%s</th>
                     <th>%s</th>
                     <th style="width:15%%">%s</th>
                     <th style="width:10%%">%s</th>
                     <th style="width:6%%"></th>
                  </tr>
                  </thead><tbody class="ant-table-tbody">
                    {tr_upload_list}
                </tbody>
                </table><hr>"""%(Utils().getMyWord("{upload_vuln}"),Utils().getMyWord("{api_name}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_type}"),Utils().getMyWord("{vuln_level}"))

        sql_list_str = """
<a id="vuln_sql" class="anchor"></a>
              <h6>◆ %s</h6>
                 <table class="table table-hover">
                  <thead class="ant-table-thead">
                  <tr>
                     <th style="width:6%%">ID</th>
                     <th style="width:16%%">%s</th>
                     <th>%s</th>
                     <th style="width:15%%">%s</th>
                     <th style="width:10%%">%s</th>
                     <th style="width:6%%"></th>
                  </tr>
                  </thead><tbody class="ant-table-tbody">
                    {tr_sql_list}
                </tbody>
                </table><hr>"""%(Utils().getMyWord("{sql_vuln}"),Utils().getMyWord("{api_name}"),Utils().getMyWord("{vuln_path}"),Utils().getMyWord("{r_type}"),Utils().getMyWord("{vuln_level}"))
        try:
            api_list = CreatHtml(self.projectTag,self.html_filepath).vuln_list()
            info_list = CreatHtml(self.projectTag,self.html_filepath).info_list()
            passWord_list = CreatHtml(self.projectTag,self.html_filepath).vuln_list_password()
            cors_list = CreatHtml(self.projectTag, self.html_filepath).cors_list()
            bac_list = CreatHtml(self.projectTag,self.html_filepath).vuln_bac_list()
            upload_list = CreatHtml(self.projectTag,self.html_filepath).vuln_upload_list()
            sql_list = CreatHtml(self.projectTag,self.html_filepath).vuln_sql_list()
            self.log.debug("vuln列表替换正常")
        except Exception as e:
            self.log.error("[Err] %s" % e)

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        flag7 = flag6 = flag5 = flag4 = flag3=flag2=flag1=0
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "unAuth":
                flag1 = 1
            elif vuln_info[3] == "INFO":
                flag2 = 1
            elif vuln_info[3] == "passWord":
                flag3 = 1
            elif vuln_info[3] == "CORS":
                flag4 = 1
            elif vuln_info[3] == "BAC":
                flag5 = 1
            elif vuln_info[3] == "upLoad":
                flag6 = 1
            elif vuln_info[3] == "SQL":
                flag7 = 1

        if flag1:
            api_list_str = api_list_str.replace("{tr_unAuth_list}", api_list)
            vuln_whole_list = vuln_whole_list + api_list_str
        if flag2:
            info_list_str = info_list_str.replace("{tr_info_vuln}", info_list)
            vuln_whole_list = vuln_whole_list + info_list_str
        if flag3:
            passWord_list_str = passWord_list_str.replace("{tr_passWord_list}", passWord_list)
            vuln_whole_list = vuln_whole_list + passWord_list_str
        if flag4:
            cors_list_str = cors_list_str.replace("{tr_cors_list}",cors_list)
            vuln_whole_list = vuln_whole_list + cors_list_str
        if flag5:
            bac_list_str = bac_list_str.replace("{tr_bac_list}", bac_list)
            vuln_whole_list = vuln_whole_list + bac_list_str
        if flag6:
            upload_list_str = upload_list_str.replace("{tr_upload_list}",upload_list)
            vuln_whole_list = vuln_whole_list + upload_list_str
        if flag7:
            sql_list_str = sql_list_str.replace("{tr_sql_list}", sql_list)
            vuln_whole_list = vuln_whole_list + sql_list_str
        return vuln_whole_list


    def vuln_nav_html(self):
        vuln_nav_str = ""
        vuln_unauth_str = """
            <li class="nav-item">
                <a href="#vuln_unauth" class="nav-link">
                  <i class="fab fa-searchengin nav-icon"></i>
                  <p>%s</p>
                </a>
            </li>"""%(Utils().getMyWord("{unauth_vuln}"))
        vuln_info_str = """
            <li class="nav-item">
                <a href="#vuln_info" class="nav-link">
                  <i class="fab fa-searchengin nav-icon"></i>
                  <p>%s</p>
                </a>
            </li>"""%(Utils().getMyWord("{info_vuln}"))
        vuln_passWord_str = """
                    <li class="nav-item">
                        <a href="#vuln_password" class="nav-link">
                          <i class="fab fa-searchengin nav-icon"></i>
                          <p>%s</p>
                        </a>
                    </li>""" % (Utils().getMyWord("{passWord_vuln}"))
        vuln_cors_str = """
                <li class="nav-item">
                        <a href="#vuln_cors" class="nav-link">
                          <i class="fab fa-searchengin nav-icon"></i>
                          <p>%s</p>
                        </a>
                    </li>""" % (Utils().getMyWord("{CORS_vuln}"))
        vuln_bac_str = """
                <li class="nav-item">
                        <a href="#vuln_bac" class="nav-link">
                          <i class="fab fa-searchengin nav-icon"></i>
                          <p>%s</p>
                        </a>
                    </li>""" % (Utils().getMyWord("{BAC_vuln}"))
        vuln_upload_str = """
                        <li class="nav-item">
                                <a href="#vuln_upload" class="nav-link">
                                  <i class="fab fa-searchengin nav-icon"></i>
                                  <p>%s</p>
                                </a>
                            </li>""" % (Utils().getMyWord("{upload_vuln}"))

        vuln_sql_str = """
                                <li class="nav-item">
                                        <a href="#vuln_sql" class="nav-link">
                                          <i class="fab fa-searchengin nav-icon"></i>
                                          <p>%s</p>
                                        </a>
                                    </li>""" % (Utils().getMyWord("{sql_vuln}"))

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        flag1=flag2=flag3=flag4=flag5=flag6=flag7=0
        for vuln_info in vuln_infos:
            if vuln_info[3] == "unAuth":
                flag1=1
            elif vuln_info[3] == "INFO":
                flag2=1
            elif vuln_info[3] == "passWord":
                flag3=1
            elif vuln_info[3] == "CORS":
                flag4=1
            elif vuln_info[3] == "BAC":
                flag5=1
            elif vuln_info[3] == "upLoad":
                flag6=1
            elif vuln_info[3] == "SQL":
                flag7=1

        if flag1:
            vuln_nav_str = vuln_nav_str + vuln_unauth_str
        if flag2:
            vuln_nav_str = vuln_nav_str + vuln_info_str
        if flag3:
            vuln_nav_str = vuln_nav_str + vuln_passWord_str
        if flag4:
            vuln_nav_str = vuln_nav_str + vuln_cors_str
        if flag5:
            vuln_nav_str = vuln_nav_str + vuln_bac_str
        if flag6:
            vuln_nav_str = vuln_nav_str + vuln_upload_str
        if flag7:
            vuln_nav_str = vuln_nav_str + vuln_sql_str
        return vuln_nav_str

    def js_list_html(self):
        js_id = 1
        js_whole_html=""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select id from js_file"
        cursor.execute(sql)
        ids = cursor.fetchall()
        for id in ids:
            js_list_str = """
                    <tr>
                        <td>{js_id}</td>
                        <td>{js_path}</td>
                        <td>{js_split}</td>
                    </tr>"""
            sql = "select * from js_file where id=%s"%(id[0])
            cursor.execute(sql)
            js_infos = cursor.fetchall()
            for js_info in js_infos:
                if js_info[5] == None:
                    js_split = Utils().getMyWord("{js_split_n}")
                elif js_info[5] == 999:
                    js_split = Utils().getMyWord("{js_split_b}")
                elif js_info[5] == 000:
                    js_split = "IN-HTML"
                else:
                    js_split = Utils().getMyWord("{js_split_s}")
                js_list_str = js_list_str.replace("{js_id}",str(js_id))
                js_list_str = js_list_str.replace("{js_path}", js_info[2])
                js_list_str = js_list_str.replace("{js_split}", str(js_split))
                js_id = js_id + 1
                js_whole_html = js_whole_html + js_list_str
        return js_whole_html

    def api_list_table(self):
        api_id = 1
        api_whole_html=""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select id from api_tree where success = 1 or success = 2"
        cursor.execute(sql)
        ids = cursor.fetchall()
        for id in ids:
            api_list_str = """
                     <tr>
                       <td>{api_id}</td>
                       <td>{api_name}</td>
                       <td>{api_path}</td>
                       <td>{api_length}</td>
                       <td>{api_type}</td>
                       <td><button type="button" class="btn btn-primary" data-toggle="modal" data-target="#api_{api_id}">More</button></td>
                     </tr>"""
            sql = "select * from api_tree where id=%s"%(id[0])
            cursor.execute(sql)
            api_infos = cursor.fetchall()
            for api_info in api_infos:
                try:
                    api_length_info = len(api_info[4])
                except:
                    api_length_info = 0
                if api_info[5] == 2:
                    api_type = Utils().getMyWord("{r_post}")
                else:
                    api_type = Utils().getMyWord("{r_get}")
                api_list_str = api_list_str.replace("{api_id}", str(api_id))
                api_list_str = api_list_str.replace("{api_name}", api_info[2])
                api_list_str = api_list_str.replace("{api_path}", api_info[1])
                api_list_str = api_list_str.replace("{api_length}", str(api_length_info))
                api_list_str = api_list_str.replace("{api_type}", str(api_type))
                api_id = api_id + 1
                api_whole_html = api_whole_html + api_list_str
        return api_whole_html

    def api_detail_html(self):
        api_id = 1
        whole_html = ""

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from api_tree where success = 1 or success = 2"
        cursor.execute(sql)
        api_infos = cursor.fetchall()
        for api_info in api_infos:
            api_info_html = """<div id="api_{api_id}" class="modal fade" role="dialog">
            	<div class="modal-dialog">
            		<div class="modal-content">
            			<div class="modal-header">
            				<h6 class="modal-title">%s...</h4>
            			</div>
            			<div class="modal-body">
            				<div class="box-body no-padding">
            					<p>
            						%s：{api_name}<br><br>
                        %s：{api_type}<br><br>
                        %s <a href="{api_path}">{api_path}</a><br><br>
                        %s {api_js}<br><br>
                        %s <code>{api_res}</code><br>
            					</p>
            				</div>
            			</div>
            		</div>
            	</div>
            </div>"""%(Utils().getMyWord("{api_detail}"),Utils().getMyWord("{api_name}"),Utils().getMyWord("{r_type}"),Utils().getMyWord("{r_api_addr}"),Utils().getMyWord("{r_api_js}"),Utils().getMyWord("{r_api_res}"))
            sql = "select path from js_file where id='%s'" % (api_info[6])
            cursor.execute(sql)
            js_path = cursor.fetchone()
            if api_info[5] == 2:
                api_type = Utils().getMyWord("{r_post}")
            else:
                api_type = Utils().getMyWord("{r_get}")
            if api_info[4] == None:
                api_res = ""
            else:
                api_res = api_info[4]
            api_info_html = api_info_html.replace("{api_id}", str(api_id))
            api_info_html = api_info_html.replace("{api_type}", str(api_type))
            api_info_html = api_info_html.replace("{api_name}", api_info[2])
            api_info_html = api_info_html.replace("{api_path}", api_info[1])
            api_info_html = api_info_html.replace("{api_js}", js_path[0])
            api_info_html = api_info_html.replace("{api_res}", api_res)
            api_id = api_id + 1
            whole_html = whole_html + api_info_html
        return whole_html

    def report_html(self):
        reports_str = """
                    <div class="right-info">
                      <div class="left-info">
                        %s：{target_host}<br><br>
                        %s：{target_url}<br><br>
                        %s{scan_type}%s {scan_time} %s<br><br>
                        %s {scan_ip} %s
                      </div>
                      <div class="right-info">
                        %s {api_num} %s<br><br>
                        %s {js_num} %s<br><br>
                        %s {vuln_num} %s<br><br>
                        %s {vuln_h_num} %s、%s {vuln_m_num} %s、%s {vuln_l_num} %s。
                      </div>
                    </div>
                    <br><br>
                      <div>
                        <div class="left-info2">
                          <ul>
                            <li>%s：{extra_cookie}</li><br>
                            <li>%s：{extra_head}</li>
                          </ul>
                        </div>
                        <div class="right-info2 box-info">
                          <strong>%s：</strong><h5 style="color:{sec_lv_color}";>{sec_lv}</h5>
                        </div>
                      </div>"""%(Utils().getMyWord("{scaned_plat}"),Utils().getMyWord("{para_value}"),Utils().getMyWord("{scan_method}"),Utils().getMyWord("{scan_time}"),Utils().getMyWord("{s}"),Utils().getMyWord("{use}"),Utils().getMyWord("{ip_address}"),Utils().getMyWord("{co_discovery}"),Utils().getMyWord("{effective_api}"),Utils().getMyWord("{co_discovery}"),Utils().getMyWord("{effective_js}"),Utils().getMyWord("{co_discovery}"),Utils().getMyWord("{effective_vuln}"),Utils().getMyWord("{r_l_h}"),Utils().getMyWord("{ge}"),Utils().getMyWord("{r_l_m}"),Utils().getMyWord("{ge}"),Utils().getMyWord("{r_l_l}"),Utils().getMyWord("{ge}"),Utils().getMyWord("{extra_cookies}"),Utils().getMyWord("{extra_head}"),Utils().getMyWord("{vuln_total_level}"))
        cmd = CommandLines().cmd()
        ipAddr = testProxy(cmd,0)
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        report_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        main_url = DatabaseType(self.projectTag).getURLfromDB()
        parse_url = urlparse(main_url)
        host = parse_url.netloc

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select id from js_file"
        cursor.execute(sql)
        js_all_files = cursor.fetchall()
        js_num = len(js_all_files)
        sql = "select path from js_file"
        cursor.execute(sql)
        jsfilelist = cursor.fetchall()
        js_paths=''
        for js in jsfilelist:
            jspath = "◆ " + js[0] + "\n"
            js_paths = js_paths + jspath
        sql ="select id from api_tree where success = 1 or success = 2"
        cursor.execute(sql)
        api_list = cursor.fetchall()
        api_num = len(api_list)
        vuln_infos = Docx_replace(self.projectTag).vuln_judge()
        vuln_h_num = vuln_infos[1]
        vuln_m_num = vuln_infos[2]
        vuln_l_num = vuln_infos[3]
        vuln_num = vuln_h_num + vuln_m_num + vuln_l_num
        vuln_score = vuln_infos[0]
        if vuln_score >= 18:
            sec_lv = Utils().getMyWord("{risk_h}")
        elif vuln_score < 18 and vuln_score >= 10:
            sec_lv = Utils().getMyWord("{risk_m}")
        elif vuln_score < 10 and vuln_score >= 5:
            sec_lv = Utils().getMyWord("{risk_l}")
        else:
            sec_lv = Utils().getMyWord("{risk_n}")
        sql = "select vaule from info where name='time'"
        cursor.execute(sql)
        time_in_info = cursor.fetchone()
        timeArray = time.localtime(int(time_in_info[0]))
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        type = CommandLines().cmd().type
        if type == "simple":
            scan_type = Utils().getMyWord("{mode_simple}")
        else:
            scan_type = Utils().getMyWord("{mode_adv}")
        scan_min = int(end_time.split(":")[-2]) - int(start_time.split(":")[-2])
        if int(scan_min) >= 1:
            end_time_one = int(end_time.split(":")[-1]) + int(scan_min) * 60
            scan_time = int(end_time_one) - int(start_time.split(":")[-1])
        else:
            scan_time = int(end_time.split(":")[-1]) - int(start_time.split(":")[-1])
        vuln_list = ''
        sql = "select id from vuln where type='unAuth'"
        cursor.execute(sql)
        num_auth = cursor.fetchall()
        if len(num_auth) != 0:
            vuln_list = vuln_list + "◆ " + Utils().getMyWord("{vuln_unauth_num}") + str(len(num_auth)) + Utils().getMyWord("{ge}") + "\n"
        sql = "select id from vuln where type='CORS'"
        cursor.execute(sql)
        num_cors = cursor.fetchall()
        if len(num_cors) != 0:
            vuln_list = vuln_list + "◆ " + Utils().getMyWord("{vuln_cors_num}") + str(len(num_cors)) + Utils().getMyWord("{ge}") + "\n"
        sql = "select id from vuln where type='INFO'"
        cursor.execute(sql)
        num_info = cursor.fetchall()
        if len(num_info) != 0:
            vuln_list = vuln_list + "◆ " + Utils().getMyWord("{vuln_info_num}") + str(len(num_info)) + Utils().getMyWord("{ge}") + "\n"
        sql = "select id from vuln where type='passWord'"
        cursor.execute(sql)
        num_passWord = cursor.fetchall()
        if len(num_passWord) != 0:
            vuln_list = vuln_list + "◆ " + Utils().getMyWord("{vuln_passWord_num}") + str(len(num_passWord)) + Utils().getMyWord("{ge}") + "\n"
        sql = "select id from vuln where type='BAC'"
        cursor.execute(sql)
        num_BAC = cursor.fetchall()
        if len(num_BAC) != 0:
            vuln_list = vuln_list + "◆ " + Utils().getMyWord("{vuln_BAC_num}") + str(len(num_BAC)) + Utils().getMyWord("{ge}") + "\n"
        sql = "select id from vuln where type='upLoad'"
        cursor.execute(sql)
        num_upload = cursor.fetchall()
        if len(num_upload) != 0:
            vuln_list = vuln_list + "◆ " + Utils().getMyWord("{vuln_upload_num}") + str(len(num_upload)) + Utils().getMyWord("{ge}") + "\n"
        sql = "select id from vuln where type='SQL'"
        cursor.execute(sql)
        num_sql = cursor.fetchall()
        if len(num_sql) != 0:
            vuln_list = vuln_list + "◆ " + Utils().getMyWord("{vuln_sql_num}") + str(
                len(num_sql)) + Utils().getMyWord("{ge}") + "\n"

        cookies = CommandLines().cmd().cookie
        if cookies:
            extra_cookies = cookies
        else:
            extra_cookies = Utils().getMyWord("{no_extra_cookies}")
        head = CommandLines().cmd().head
        if head != "Cache-Control:no-cache":
             extra_head = head
        else:
             extra_head = Utils().getMyWord("{no_extra_head}")
        if sec_lv == Utils().getMyWord("{risk_n}"):
            sec_lv_color = "gray"
        elif sec_lv == Utils().getMyWord("{risk_l}"):
            sec_lv_color = "green"
        elif sec_lv == Utils().getMyWord("{risk_m}"):
            sec_lv_color = "orange"
        elif sec_lv == Utils().getMyWord("{risk_h}"):
            sec_lv_color = "red"

        reports_str = reports_str.replace("{target_host}", host)
        reports_str = reports_str.replace("{vuln_list}", vuln_list)
        reports_str = reports_str.replace("{target_url}", main_url)
        reports_str = reports_str.replace("{scan_type}", scan_type)
        reports_str = reports_str.replace("{scan_time}", str(scan_time))
        reports_str = reports_str.replace("{scan_ip}", str(ipAddr))
        reports_str = reports_str.replace("{api_num}", str(api_num))
        reports_str = reports_str.replace("{js_num}", str(js_num))
        reports_str = reports_str.replace("{vuln_num}", str(vuln_num))
        reports_str = reports_str.replace("{vuln_h_num}", str(vuln_h_num))
        reports_str = reports_str.replace("{vuln_m_num}", str(vuln_m_num))
        reports_str = reports_str.replace("{vuln_l_num}", str(vuln_l_num))
        reports_str = reports_str.replace("{extra_cookie}", extra_cookies)
        reports_str = reports_str.replace("{extra_head}", extra_head)
        reports_str = reports_str.replace("{sec_lv_color}", sec_lv_color)
        reports_str = reports_str.replace("{sec_lv}", sec_lv)

        return reports_str

    def vuln_pie_html(self):
        vuln_pie_str = ""
        vuln_cors_num = vuln_bac_num=vuln_sql_num=vuln_info_num = vuln_unauth_num = vuln_passWord_num= vuln_upload_num = 0

        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        for vuln_info in vuln_infos:
            if vuln_info[3] == "INFO":
                vuln_info_num = vuln_info_num + 1
            if vuln_info[3] == "unAuth":
                vuln_unauth_num = vuln_unauth_num + 1
            if vuln_info[3] == "passWord":
                vuln_passWord_num = vuln_passWord_num + 1
            if vuln_info[3] == "CORS":
                vuln_cors_num = vuln_cors_num + 1
            if vuln_info[3] == "BAC":
                vuln_bac_num = vuln_bac_num + 1
            if vuln_info[3] == "upLoad":
                vuln_upload_num = vuln_upload_num + 1
            if vuln_info[3] == "SQL":
                vuln_sql_num = vuln_sql_num + 1
        vuln_pie_unauth_str = "{name: '%s', value: {vuln_unauth_num}}," % (Utils().getMyWord("{unauth_vuln}"))
        vuln_pie_info_str = "{name: '%s', value: {vuln_info_num} }"  % (Utils().getMyWord("{info_vuln}"))
        vuln_pie_passWord_str = "{name: '%s', value: {vuln_passWord_num} }" % (Utils().getMyWord("{password_vuln}"))
        vuln_pie_cors_str = "{name: '%s', value: {vuln_cors_num} }" % (Utils().getMyWord("{CORS_vuln}"))
        vuln_pie_bac_str = "{name: '%s', value: {vuln_BAC_num} }" % (Utils().getMyWord("{BAC_vuln}"))
        vuln_pie_upload_str = "{name: '%s', value: {vuln_upload_num} }" % (Utils().getMyWord("{upload_vuln}"))
        vuln_pie_sql_str = "{name: '%s', value: {vuln_sql_num} }" % (Utils().getMyWord("{sql_vuln}"))
        no_vuln_str = "{name: '%s', value: 1 }"% (Utils().getMyWord("{no_vuln}"))
        if vuln_unauth_num:
            vuln_pie_unauth_str = vuln_pie_unauth_str.replace("{vuln_unauth_num}",str(vuln_unauth_num))
            vuln_pie_str = vuln_pie_str + vuln_pie_unauth_str
        if vuln_info_num:
            vuln_pie_info_str = vuln_pie_info_str.replace("{vuln_info_num}",str(vuln_info_num))
            vuln_pie_str = vuln_pie_str + vuln_pie_info_str
        if vuln_passWord_num:
            vuln_pie_passWord_str = vuln_pie_passWord_str.replace("{vuln_passWord_num}",str(vuln_passWord_num))
            vuln_pie_str = vuln_pie_str + vuln_pie_passWord_str
        if vuln_cors_num:
            vuln_pie_cors_str = vuln_pie_cors_str.replace("{vuln_cors_num}", str(vuln_cors_num))
            vuln_pie_str = vuln_pie_str + vuln_pie_cors_str
        if vuln_bac_num:
            vuln_pie_bac_str = vuln_pie_bac_str.replace("{vuln_BAC_num}", str(vuln_bac_num))
            vuln_pie_str = vuln_pie_str + vuln_pie_bac_str
        if vuln_upload_num:
            vuln_pie_upload_str = vuln_pie_upload_str.replace("{vuln_upload_num}", str(vuln_upload_num))
            vuln_pie_str = vuln_pie_str + vuln_pie_upload_str
        if vuln_sql_num:
            vuln_pie_sql_str = vuln_pie_sql_str.replace("{vuln_sql_num}", str(vuln_sql_num))
            vuln_pie_str = vuln_pie_str + vuln_pie_sql_str
        if vuln_unauth_num == 0 and vuln_info_num == 0 and vuln_passWord_num == 0 and vuln_cors_num == 0 and vuln_bac_num == 0 and vuln_upload_num == 0 and vuln_sql_num == 0:
            vuln_pie_str = vuln_pie_str + no_vuln_str
        return vuln_pie_str

    def suggest_html(self):
        suggest_html_str = ""
        suggest_html_nav_str = ""


        projectDBPath = DatabaseType(self.projectTag).getPathfromDB() + self.projectTag + ".db"
        connect = sqlite3.connect(os.sep.join(projectDBPath.split('/')))
        cursor = connect.cursor()
        connect.isolation_level = None
        sql = "select * from vuln"
        cursor.execute(sql)
        vuln_infos = cursor.fetchall()
        flag1 = flag2 = flag3 = flag4 = flag5 = flag6 = flag7 = 0
        for vuln_info in vuln_infos:
            if vuln_info[3] == "unAuth":
                flag1 = 1
            elif vuln_info[3] == "INFO":
                flag2 = 1
            elif vuln_info[3] == "CORS":
                flag3 = 1
            elif vuln_info[3] == "SQL":
                flag4 = 1
            elif vuln_info[3] == "upLoad":
                flag5 = 1
            elif vuln_info[3] == "passWord":
                flag6 = 1
            elif vuln_info[3] == "BAC":
                flag7 = 1
        unauth_str = """
<a id="sug_unauth" class="anchor"></a>
<li><h5>%s</h5></li>
1. %s<br>
2. %s<br><br>"""%(Utils().getMyWord("{r_sug_unauth_1}"),Utils().getMyWord("{r_sug_unauth_2}"),Utils().getMyWord("{r_sug_unauth_3}"))
        info_str = """
<a id="sug_info" class="anchor"></a>
<li><h5>%s</h5></li>
1. %s<br><br>
        """%(Utils().getMyWord("{r_sug_info_1}"),Utils().getMyWord("{r_sug_info_2}"))
        cors_str = """
<a id="sug_cors" class="anchor"></a>
<li><h5>%s</h5></li>
1. %s<br><br>
        """%(Utils().getMyWord("{r_sug_cors_1}"),Utils().getMyWord("{r_sug_cors_2}"))
        sql_str = """
<a id="sug_sql" class="anchor"></a>
<li><h5>%s</h5></li>
1. %s<br>
2. %s<br><br>
        """%(Utils().getMyWord("{r_sug_sqli_1}"),Utils().getMyWord("{r_sug_sqli_2}"),Utils().getMyWord("{r_sug_sqli_3}"))
        upload_str = """
<a id="sug_upload" class="anchor"></a>
<li><h5>%s</h5></li>
1. %s<br>
2. %s<br>
3. %s<br><br>
        """%(Utils().getMyWord("{r_sug_upload_1}"),Utils().getMyWord("{r_sug_upload_2}"),Utils().getMyWord("{r_sug_upload_3}"),Utils().getMyWord("{r_sug_upload_4}"))
        password_str = """
<a id="sug_password" class="anchor"></a>
<li><h5>%s</h5></li>
1. %s<br>
2. %s<br><br>
        """%(Utils().getMyWord("{r_sug_password_1}"),Utils().getMyWord("{r_sug_password_2}"),Utils().getMyWord("{r_sug_password_3}"))
        bac_str = """
<a id="sug_bac" class="anchor"></a>
<li><h5>%s</h5></li>
1.%s<br>
2. %s<br><br>
        """%(Utils().getMyWord("{r_sug_bac_1}"),Utils().getMyWord("{r_sug_bac_2}"),Utils().getMyWord("{r_sug_bac_3}"))
        whole_str = """
<a id="sug_total" class="anchor"></a>
<li><h5>%s</h5></li>
1. %s<br>
2. %s<br>
3. %s<br>
4. %s<br>
5. %s
        """%(Utils().getMyWord("{r_sug_g_1}"),Utils().getMyWord("{r_sug_g_2}"),Utils().getMyWord("{r_sug_g_3}"),Utils().getMyWord("{r_sug_g_4}"),Utils().getMyWord("{r_sug_g_5}"),Utils().getMyWord("{r_sug_g_6}"))
        unauth_nav_str = """
<li class="nav-item">
  <a href="#sug_unauth" class="nav-link">
    <i class="fas fa-paste nav-icon"></i>
    <p>%s</p>
  </a>
</li>
        """%(Utils().getMyWord("{r_sug_unauth_1}")[:-1])
        info_nav_str = """
<li class="nav-item">
  <a href="#sug_info" class="nav-link">
    <i class="fas fa-globe nav-icon"></i>
    <p>%s</p>
  </a>
</li>
    """%(Utils().getMyWord("{r_sug_info_1}")[:-1])
        cors_nav_str = """
<li class="nav-item">
  <a href="#sug_cors" class="nav-link">
    <i class="fas fa-globe nav-icon"></i>
    <p>%s</p>
  </a>
</li>
        """%(Utils().getMyWord("{r_sug_cors_1}")[:-1])
        sql_nav_str = """
<li class="nav-item">
  <a href="#sug_sql" class="nav-link">
    <i class="fas fa-globe nav-icon"></i>
    <p>%s</p>
  </a>
</li>
    """%(Utils().getMyWord("{r_sug_sqli_1}")[:-1])
        upload_nav_str = """
<li class="nav-item">
  <a href="#sug_upload" class="nav-link">
    <i class="fas fa-globe nav-icon"></i>
    <p>%s</p>
  </a>
</li>
        """%(Utils().getMyWord("{r_sug_upload_1}")[:-1])
        password_nav_str = """
<li class="nav-item">
  <a href="#sug_password" class="nav-link">
    <i class="fas fa-globe nav-icon"></i>
    <p>%s</p>
  </a>
</li>
        """%(Utils().getMyWord("{r_sug_password_1}")[:-1])
        bac_nav_str = """
<li class="nav-item">
  <a href="#sug_bac" class="nav-link">
    <i class="fas fa-globe nav-icon"></i>
    <p>%s</p>
  </a>
</li>
        """%(Utils().getMyWord("{r_sug_bac_1}")[:-1])
        whole_nav_str = """
<li class="nav-item">
  <a href="#sug_total" class="nav-link">
    <i class="fas fa-globe nav-icon"></i>
    <p>%s</p>
  </a>
</li>
        """%(Utils().getMyWord("{r_sug_g_1}")[:-1])
        if flag1:
            sug_unauth_num = "1"
            unauth_str = unauth_str.replace("sug_unauth",sug_unauth_num)
            unauth_nav_str = unauth_nav_str.replace("sug_unauth", sug_unauth_num)
            suggest_html_str = suggest_html_str + unauth_str
            suggest_html_nav_str = suggest_html_nav_str + unauth_nav_str
        if flag2:
            sug_info_num = "2"
            info_str = info_str.replace("sug_info",sug_info_num)
            info_nav_str = info_nav_str.replace("sug_info", sug_info_num)
            suggest_html_str = suggest_html_str + info_str
            suggest_html_nav_str = suggest_html_nav_str + info_nav_str
        if flag3:
            sug_cors_num = "3"
            cors_str = cors_str.replace("sug_cors",sug_cors_num)
            cors_nav_str = cors_nav_str.replace("sug_cors", sug_cors_num)
            suggest_html_str = suggest_html_str + cors_str
            suggest_html_nav_str = suggest_html_nav_str + cors_nav_str
        if flag4:
            sug_sql_num = "4"
            sql_str = sql_str.replace("sug_sql",sug_sql_num)
            sql_nav_str = sql_nav_str.replace("sug_sql", sug_sql_num)
            suggest_html_str = suggest_html_str + sql_str
            suggest_html_nav_str = suggest_html_nav_str + sql_nav_str
        if flag5:
            sug_upload_num = "5"
            upload_str = upload_str.replace("sug_upload",sug_upload_num)
            upload_nav_str = upload_nav_str.replace("sug_upload", sug_upload_num)
            suggest_html_str = suggest_html_str + upload_str
            suggest_html_nav_str = suggest_html_nav_str + upload_nav_str
        if flag6:
            sug_password_num = "6"
            password_str = password_str.replace("sug_password",sug_password_num)
            password_nav_str = password_nav_str.replace("sug_password", sug_password_num)
            suggest_html_str = suggest_html_str + password_str
            suggest_html_nav_str = suggest_html_nav_str + password_nav_str
        if flag7:
            sug_bac_num = "7"
            bac_str = bac_str.replace("sug_bac",sug_bac_num)
            bac_nav_str = bac_nav_str.replace("sug_bac", sug_bac_num)
            suggest_html_str = suggest_html_str + bac_str
            suggest_html_nav_str = suggest_html_nav_str + bac_nav_str
        sug_total_num = "8"
        whole_str = whole_str.replace("sug_total",sug_total_num)
        whole_nav_str = whole_nav_str.replace("sug_total",sug_total_num)
        suggest_html_str = suggest_html_str + whole_str
        suggest_html_nav_str = suggest_html_nav_str + whole_nav_str

        suggest_html = []
        suggest_html.append(suggest_html_str)
        suggest_html.append(suggest_html_nav_str)

        return suggest_html


    def HtmlReplace(self,HtmlStr):
        html_str = HtmlStr
        try:
            vuln_detail = CreatHtml(self.projectTag, self.html_filepath).vuln_detail_html()
            vuln_list = CreatHtml(self.projectTag, self.html_filepath).api_list_html()
            vuln_nav = CreatHtml(self.projectTag, self.html_filepath).vuln_nav_html()
            vuln_js = CreatHtml(self.projectTag, self.html_filepath).js_list_html()
            api_list = CreatHtml(self.projectTag, self.html_filepath).api_list_table()
            api_detial = CreatHtml(self.projectTag, self.html_filepath).api_detail_html()
            sum_of_reports = CreatHtml(self.projectTag, self.html_filepath).report_html()
            vuln_pie = CreatHtml(self.projectTag, self.html_filepath).vuln_pie_html()
            suggest_whole =  CreatHtml(self.projectTag, self.html_filepath).suggest_html()
            self.log.debug("html所有替换模块正常")
            vuln_list = vuln_list[:-4]
        except Exception as e:
            self.log.error("[Err] %s" % e)

        html_str = html_str.replace("{vuln_detial}", vuln_detail)
        html_str = html_str.replace("{vuln_list}", vuln_list)
        html_str = html_str.replace("{vuln_nav}", vuln_nav)
        html_str = html_str.replace("{js_list}", vuln_js)
        html_str = html_str.replace("{api_list}", api_list)
        html_str = html_str.replace("{api_detial}", api_detial)
        html_str = html_str.replace("{sum_of_reports}", sum_of_reports)
        html_str = html_str.replace("{vuln_pie}", vuln_pie)
        html_str = html_str.replace("{suggest_foryou}", suggest_whole[0])
        html_str = html_str.replace("{suggest_nav}", suggest_whole[1])
        return html_str

    def CreatMe(self):
        docLang = Utils().getMyWord("{lang}")
        with open("doc" + os.sep + "template" + os.sep + "html"  + os.sep + docLang + ".html","r",encoding="utf-8",errors="ignore") as html:
            html_str = html.read()
            new_html_str = CreatHtml(self.projectTag, self.html_filepath).HtmlReplace(html_str)
            with open(self.html_filepath,"w",encoding="utf-8",errors="ignore") as new_html:
                new_html.write(new_html_str)
                new_html.close()
            html.close()
