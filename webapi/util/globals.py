#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/9/17 8:29
# Author  : He
# Github : https://github.com/JustKeepSilence

# 整个后台接口的全局变量,可以被所有的文件所共享

from util import utils as uu

__all__ = ('param_list', 'IP', 'PORT')

param_list = []  # 后台接口函数的参数列表
IP = uu.get_ip()  # 后台接口的IP地址
PORT = 8082  # 后台接口的端口号
