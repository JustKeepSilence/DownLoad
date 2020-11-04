#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/7/7 11:01
# Author  : He
# Github : https://github.com/JustKeepSilence


# HttpResponse 配置


from enum import IntEnum


class ResponseCode(IntEnum):
    SUCCESS = 200  # 请求成功
    ERROR = 500  # 请求出错
    RUNNING = 204  # 正在运行


class ResponseResult:

    """返回响应的类"""
