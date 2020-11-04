#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/4/23 10:44
# Author  : He
# Github : https://github.com/JustKeepSilence


"""启动爬虫的main函数"""


import os
import sys
from typing import Union

from concurrent import futures
from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings


__all__ = ("start_crawl", "start_spiders")


def start_crawl(spider_name: str, **kwargs) -> None:

    """启动爬虫,适用于websocket调用,单一带有命令参数的爬虫
       `spider_name`: 爬虫名称
    """

    args = [f"-a {k}={v}" for k, v in kwargs.items()]  # 拼接命令行参数
    sys.path[0] = os.path.dirname(os.path.abspath(__file__))  # 将当前目录添加到python模块列表中
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 切换工作路径
    cmd = rf"scrapy crawl {spider_name} {' '.join(args)} -s LOG_FILE=log\{spider_name}_crawl.log"  # -s 配置log文件的路径
    execute(cmd.split())


def start_spider(spider_name: str) -> None:

    """启动爬虫,适用于ThreadPoolExecutor调用,不带有命令参数的启动
       此时相关的参数应该已经在spider中使用custom_settings设置完毕
       `spider_name`: 爬虫名称
    """

    sys.path[0] = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 切换工作路径
    cmd = rf"scrapy crawl {spider_name}"
    execute(cmd.split(), get_project_settings())  # get_project_settings()可以省略
    # 如果为None,execute会重新使用该函数进行获取


def start_spiders(spider_names: Union[str, list]) -> None:

    """使用ThreadPoolExecutor启动多个代理爬虫
       `spider_names`: 多个爬虫的名称,可以是以逗号分隔的字符串或者是列表
    """
    try:
        spider_names = spider_names.split(",")
    except AttributeError:
        pass
    with futures.ProcessPoolExecutor() as executor:
        executor.map(start_spider, spider_names)


if __name__ == "__main__":
    # param = {
    #     "callback": "callback123",
    #     "keyword": "周杰伦",
    #     "page": 1,
    #     "pagesize": 30,
    #     "bitrate": 0,
    #     "isfuzzy": 0,
    #     "tag": "em",
    #     "inputtype": 0,
    #     "platform": "WebFilter",
    #     "userid": -1,
    #     "clientver": 2000,
    #     "iscorrection": 1,
    #     "privilege_filter": 0,
    #     "srcappid": 2919,
    #     "clienttime": 1591011074750,
    #     "mid": 1591011074750,
    #     "uuid": 1591011074750,
    #     "dfid": "-"
    # }
    # m = md5()
    # m.update(''.join(f"{k}={v}" for k, v in param.items()).encode("utf-8"))
    # param["signature"] = m.hexdigest().upper()
    # start_crawl_dict("kg_music", param)
    start_crawl("qq_music", key_word="lemon")
