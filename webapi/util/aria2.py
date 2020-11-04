#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/7/15 17:32
# Author  : He
# Github : https://github.com/JustKeepSilence


# 启动aria2的脚本,使用RPC-xml来进行控制，可以很方便的进行配置的控制
# 需要先启动aria2，默认的端口号为6800,可以在配置文件中进行控制


def get_gids(urls, s):

    """获取aria2下载的gids"""

    gids = []
    for url in urls:
        gids.append(s.aria2.addUri([url]))
    return gids
