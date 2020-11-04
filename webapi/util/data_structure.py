#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/6/30 21:48
# Author  : He
# Github : https://github.com/JustKeepSilence


from collections import namedtuple


# 用户的数据结构
User = namedtuple("User", "id, username, password, role_name, role_description,"
                          "user_avatar, usertoken, role_id, updated_time")
WebSite = namedtuple("WebSite", "web_site_name")
SearchHistory = namedtuple("SearchHistory", "keyword")
Movie = namedtuple("Movie", "id, name, director, score, download_link, download_link_type, movie_type, synopsis,"
                            "insert_time, is_collect, is_delete")
CrawlLog = namedtuple("CrawlLog", "id, abbreviated_log, detailed_log, search_keyword, insert_time,is_success")
ProjectLog = namedtuple("ProjectLog", "id, updated_content, executor, insert_time")
Executor = namedtuple("Executor", "executor")
Count = namedtuple("Count", "count")
Download = namedtuple("Download", "id, download_url, download_file_name, download_file_path, download_gid, insert_time,"
                                  "is_success, process, type_name")
UserRole = namedtuple("UserRole", "username, role_name")
