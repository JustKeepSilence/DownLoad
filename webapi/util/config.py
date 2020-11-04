#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/9/20 9:57
# Author  : He
# Github : https://github.com/JustKeepSilence

# 整个项目的配置文件，可以被所有python文件所访问

import os
import socket
import socketio

__all__ = ('PARAM_LIST', 'IP', 'PORT', 'ROOT_PATH', 'sio')

def get_root_path() -> str:

    """获取整个项目的根目录,即web.py文件所在的目录"""

    *file_path, _ = os.path.dirname(os.path.abspath(__file__)).split("\\")
    return "\\".join(file_path)

def get_ip():

    """获取本机的IP"""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


PARAM_LIST = []  # 后台接口函数的参数列表
IP = get_ip()  # 后台接口的IP地址
PORT = 8082  # 后台接口的端口号
ROOT_PATH = get_root_path()  # 整个项目的根路径
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins="*")  # socket IO


