#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/4/28 17:33
# Author  : He
# Github : https://github.com/JustKeepSilence


"""一些共公函数"""


import re
import os
import sys
import time
import json
import base64
import random
import asyncio
import socket
from typing import Optional, Union, AsyncGenerator
from urllib.request import _parse_proxy

import requests
import pyperclip
import aiohttp.client_exceptions as ac
from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector
from scrapy.utils.log import logger
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

from . import db
from .data_structure import *


# 项目配置的相关函数


def get_root_path() -> str:

    """获取整个项目的根目录,即manage.py文件所在的目录"""

    *file_path, _ = os.path.dirname(os.path.abspath(__file__)).split("\\")
    return "\\".join(file_path)


def get_scrapy_settings(name: str) -> str:

    """获取指定名称的设置的value,
       `name`:要获取的变量的名称,只针对value值为str,dict, list有效
       在scrapy启动之后可以直接使用get_project_settings获得,这里
       只是为了在其他模块中便于直接获得需要的设置信息.
    """

    file_path = rf"{get_root_path()}\download_spider\spider\settings.py"  # 获取设置文件的路径
    pattern = re.compile(r"""%s\s*=\s*(?P<f>["'\[{a-zA-Z0-9]).*?(?P=f)""" % name, flags=re.DOTALL)
    pattern_value = re.compile(r".*?\s*=\s*(.*)", flags=re.DOTALL)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(pattern, content.replace("}", "{").replace("]", "["))
        value = re.search(pattern_value, match.group()).group(1)[::-1].replace("{", "}", 1).replace("[", "]", 1)[::-1]\
            .replace("#", "")
    return value


# 代理操作的相关函数
def get_proxy_from_database() -> list:

    """从数据库中获取代理"""

    # sqlite = SQLite()
    # query_data = sqlite.get_data("proxy_cfg", "proxy_ip, proxy_priority, proxy_user_name, proxy_user_pwd, "
    #                                           "proxy_type", "is_useful=1 and is_current_used=1")
    # return [{"proxy_ip": item.proxy_ip, "proxy_scheme": item.proxy_type, "username": item.proxy_user_name,
    #          "password": item.proxy_user_pwd} for item in [SpiderProxy(*item) for item in query_data]]


def parse_proxy(proxy_ip: str) -> str:

    """解析代理,获取代理的scheme
       `proxy_ip`: 代理ip
    """

    proxy_type, *_ = _parse_proxy(proxy_ip)
    return proxy_type


def check_proxy(proxy_ip: str, proxy_user_name: str, proxy_pwd: str) -> bool:

    """检查代理是否可用,request同步,适用于单个代理
       `proxy_ip`: 代理IP
       `proxy_user_name`: 用户名
       `proxy_pwd`: 密码
    """

    try:
        url = "http://httpbin.org/ip"
        headers = json.loads(get_scrapy_settings("DEFAULT_REQUEST_HEADERS").replace(r"'", '"'))
        proxy_type, username, password, proxy_port = _parse_proxy(proxy_ip)
        if not username and not password:
            proxy = {proxy_type: proxy_ip}  # 用户名和密码都已经包含在了proxy_ip中
        else:
            proxy = {proxy_type: f"{proxy_type}://{proxy_user_name}:{proxy_pwd}@{proxy_port}"}  # 重新组proxy
        response = requests.get(url, headers=headers, proxies=proxy).text
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout):
        return False
    else:
        if json.loads(response).get("origin") == re.search(r"(.*):", proxy_port).group(1):
            return True
        else:
            return False


def check_proxy_async(proxies: list, loop: asyncio.BaseEventLoop) -> list:

    """异步检查代理是否可用
       `proxies`: 代理列表
       `loop`: 事件循环
    """

    tasks = []
    url = "http://httpbin.org/ip"
    for proxy in proxies:
        task = asyncio.ensure_future(send_request(url=url, method="get", proxy=proxy))
        tasks.append(task)
    result = loop.run_until_complete(asyncio.gather(*tasks))
    check_result = [True if item["origin"] != "false" else False for item in result]
    return check_result


def check_proxy_websockets(proxy_id: list, proxies: list) -> None:

    """检查代理是否可用,将检查的结果写入数据库
       用于websocket调用
       `proxy_id`: proxy_cfg表中的代理id
       `proxies`: 与proxy_id对应的代理列表
    """

    # loop = asyncio.get_event_loop()
    # checked_result = zip(check_proxy_async(proxies, loop), proxy_id)
    # updated_id = [item[1] for item in checked_result if not item[0]]
    # sqlite = SQLite()
    # condition = " or ".join(f"id={item}" for item in updated_id)
    # sqlite.update_data("proxy_cfg", "is_useful", "0", condition)
    # sqlite.close_db()


class RandomHttpProxy(HttpProxyMiddleware):

    """选择随机代理的中间件"""

    def process_request(self, request: Request, spider: Spider):

        """给每个请求加上随机代理"""

        proxies = [item["proxy_ip"] for item in get_proxy_from_database()]
        # 从数据库获取可用的代理
        proxy = random.choice(proxies)
        creds, proxy_url = self._get_proxy(proxy, "")  # 获取代理中的用户名密码和url
        request.meta["proxy"] = proxy_url  # 设置request的meta的proxy字段
        if creds and not request.headers.get('Proxy-Authorization'):
            # 如果有用户名和密码则设置对应的头部
            request.headers['Proxy-Authorization'] = b'Basic ' + creds
        return


# 网络请求的相关函数


async def send_request(url: str, method: Optional[str] = "get", text_type: Optional[str] = "json",
                       encoding: Optional[str] = "utf-8", max_cor: Optional[int] = 200, **kwargs) -> str:

    """异步发送请求
       `method`: 请求的方法
       `url`: 请求的url
       `text_type`: 返回的响应文本的格式,有文本,二进制以及json
       `encoding`: 文本的编码
       `max_cor`: 最大并发数
    """

    proxy = kwargs.get("proxy")
    try:
        connector = ProxyConnector.from_url(proxy)  # 使用ProxyConnector来让aiohttp支持https代理
    except (ValueError, TypeError):
        connector = None  # 如果代理有问题则设置connector为None
    sem = asyncio.Semaphore(max_cor)  # 设置最大并发数为200
    headers = json.loads(get_scrapy_settings("DEFAULT_REQUEST_HEADERS").replace(r"'", '"'))
    if method == "get":
        # get 请求
        try:
            async with sem:
                async with ClientSession(connector=connector) as session:
                    async with session.get(url, headers=headers, timeout=5, verify_ssl=False, allow_redirects=False) \
                            as response:
                        if text_type == "json":
                            return await response.json()  # json
                        elif text_type == "text":
                            return await response.text(encoding=encoding)  # 文本
                        else:
                            return await response.read()  # 二进制
        except (ac.ServerConnectionError, asyncio.TimeoutError, ac.ClientProxyConnectionError,
                ac.ClientOSError, ac.ContentTypeError):
            if text_type == "json":
                return {"origin": "false"}
            elif text_type == "text":
                return "false"
            else:
                return b"false"
    else:
        # post请求
        data = kwargs.get("data")
        try:
            async with ClientSession(connector=connector) as session:
                async with session.post(url, headers=headers, data=data, timeout=5, allow_redirects=False) \
                        as response:
                    if text_type == "json":
                        return await response.json()  # json
                    elif text_type == "text":
                        return await response.text(encoding=encoding)  # 文本
                    else:
                        return await response.read()  # 二进制
        except (ac.ServerConnectionError, asyncio.TimeoutError, ac.ClientProxyConnectionError):
            if text_type == "json":
                return {"origin": "false"}
            elif text_type == "text":
                return "false"
            else:
                return b"false"


def start_async_request(urls: list, loop: asyncio.BaseEventLoop, method: Optional[str] = "get",
                        text_type: Optional[str] = "json") -> list:

    """调用异步请求同时发送多条请求并返回请求的响应
       `urls`: url列表
       `loop`: 事件循环
       `method`: http请求的方法,默认为get,支持post
       `text_type`: 返回的响应的格式,默认的为json,支持text,binary
    """

    tasks = []
    for url in urls:
        task = asyncio.ensure_future(send_request(url, method, text_type=text_type))
        tasks.append(task)
    result = loop.run_until_complete(asyncio.gather(*tasks))
    return result


# 与task相关的函数


def insert_task(task_name: str, task_type_name: str) -> int:

    """向数据库中新增任务
       `task_name`: 任务名称
       `task_type_name`: 任务类型名称
    """

    # row_fmt = "'{}','{}','{}'"
    # sqlite = SQLite()
    # row_id = sqlite.insert("task_cfg", "task_name, task_type_name, start_time",
    #                        row_fmt.format(task_name, task_type_name, time.strftime("%Y-%m-%d %H:%M:%S")), True)
    # sqlite.close_db()
    # return row_id


def update_task_status(task_id: int, finished_reason: Optional[str] = "finished") -> None:

    """更新任务的状态
       `task_id`: 任务id
       `finished_reason`: 任务结束的原因,默认为正常结束
    """

    # sqlite = SQLite()
    # sqlite.update_data("task_cfg", "task_status, finish_reason, end_time",
    #                    f"1, {finished_reason}, {time.strftime('%Y-%m-%d %H:%M:%S')}",
    #                    f"id={task_id}")
    # sqlite.close_db()


def update_task_process(task_id: int, task_process: str) -> None:

    """更新任务进度
       `task_id`:任务的id
       `task_process`:更新的任务的内容:{"2020-5-20 22:17:10": "爬虫启动..."}
    """

    # sqlite = SQLite()
    # sqlite.update_data("task_cfg", "task_process", [task_process], f"id={task_id}")
    # sqlite.close_db()


def get_current_task() -> list:

    """获取当前正在执行的所有任务"""

    # sqlite = SQLite()
    # query_data = sqlite.get_data("task_cfg", "task_name, task_type_name", "task_status=0")
    # return query_data


# 其他函数


def start_thunder(urls: list, file_path: str) -> None:

    """启动迅雷下载
       `urls`: 链接列表
       `file_path`: 迅雷启动程序的路径
    """

    os.chdir(file_path)
    d_url = ""
    for url in urls:
        if "thunder" in url:
            d_url = d_url + url + "\n"
        else:
            d_url = d_url + ("thunder://".encode("utf-8")+base64.b64encode(('AA'+url+'ZZ').
                                                                           encode("utf-8"))).decode("utf-8") + "\n"
    os.system(f"Thunder.exe -StartType:DesktopIcon {d_url}")
    pyperclip.copy(d_url)


def get_domains(url: str) -> str:

    """获取指定url的域,例如输入的是https://www.example.com/1.html
       则最终返回的是example.com
       `url`: 链接
    """
    try:
        pattern = re.compile(r"http|https://(.*)?/")
        domains = re.match(pattern, url).group(1)
    except AttributeError:
        raise TypeError("%s must begin with http or https" % url)
    else:
        return domains


def save_parse_page(task_id: int, log: logger, page_url: str) -> None:

    """将正在解析的页面url写入log文件和task_cfg
       `logger`: scrapy中的logger对象
    """

    log.info("parseUrl: %s" % page_url)
    update_task_process(task_id, json.dumps({time.strftime("%Y-%m-%d %H:%M:%S"): "parseUrl: %s" % page_url}))


def save_parse_item(task_id: int, log: logger, parse_item: str) -> None:

    """将正在解析的item写入数据库的日志"""

    log.info("parseItem: %s" % parse_item)
    update_task_process(task_id, json.dumps({time.strftime("%Y-%m-%d %H:%M:%S"): "parseItem: %s" % parse_item},
                                            ensure_ascii=False).replace("'", " "))
    # 将'替换掉,防止写入SQL的时候出错


def replace_apostrophe(dest_lists: list, sign: str) -> list:

    """替换list中的每一个单引号"""

    for item in dest_lists:
        if item:
            item = sign + item + sign
        else:
            item = sign + "" + sign
        yield item


async def get_movie(page: int, limit: int, movie_data: Union[list, AsyncGenerator] = None,
                    sql_command: Optional[str] = None,) -> tuple:

    """获取movie_cfg中的电影信息并返回
       如果给定了movie_data,则直接重组数据返回
       如果没有给定movie_data,则根据command从数据库获取
    """
    if not movie_data:
        movie_data = await db.get_data(sql_command)
    try:
        query_data = [Movie(*item) async for item in movie_data]
    except TypeError:
        query_data = [Movie(*item) for item in movie_data]
    total = len(query_data)
    if limit == 0:
        # 不需要进行分页
        start = 0
        stop = total
    else:
        start = (page - 1) * limit  # 起始
        stop = page * limit
    return [{"id": index, "item_id": item.id, "name": item.name, "director": item.director, "score": item.score,
             "download_link": item.download_link,
             "download_link_type": item.download_link_type,
             "movie_type": item.movie_type, "synopsis": item.synopsis, "is_collected": item.is_collect}
            for index, item in enumerate(query_data[start: stop], start=1)], total


async def get_log(page: int, limit: int, type_name: str, log_data: AsyncGenerator = None,
                  item_id: Optional[str] = None) -> tuple:

    """获取crawl_log_cfg中的信息并返回"""

    if item_id:
        # 如果给定item id
        sql_command = f"select id, abbreviated_log, detailed_log, search_keyword, insert_time, is_success" \
                      f" from crawl_log_cfg where type_name='{type_name}' and id={item_id}"
    else:
        sql_command = f"select id, abbreviated_log, detailed_log, search_keyword, insert_time, is_success" \
                      f" from crawl_log_cfg where type_name='{type_name}'"
    if not log_data:
        log_data = await db.get_data(sql_command)  # 如果没有给定log data则从数据库中获取数据
    query_data = [CrawlLog(*item) async for item in log_data]
    total = len(query_data)  # 数据的数目
    if limit == 0:
        # 不需要进行分页则返回全部的数据
        start = 0
        stop = total
    else:
        start = (page - 1) * limit
        stop = page * limit
    data = [{"id": index, "item_id": item.id, "keyword": item.search_keyword, "is_success": item.is_success,
             "insert_time": str(item.insert_time), "detail": item.detailed_log,
             "abbreviation": item.abbreviated_log.replace(",", "\n")}
            for index, item in enumerate(query_data[start: stop], start=1)]
    return data, total  # 返回数据和总的数据数目


async def get_project_log(keyword: str, executor: str, start_time: str, end_time: str) -> list:

    """获取项目的更新日志"""

    if executor != "all":
        command = f"select * from project_cfg where updated_content like '%{keyword}%' and executor='{executor}' and " \
                  f"insert_time > '{start_time}' and insert_time < '{end_time}'"
    else:
        command = f"select * from project_cfg where updated_content like '%{keyword}%' and " \
                  f"insert_time > '{start_time}' and insert_time < '{end_time}'"
    query_data = await db.get_data(command)
    return [{"id": item.id, "content": item.updated_content.replace("\r", "").replace("\n", "\n\n"),
             "executor": item.executor,
             "insert_time": str(item.insert_time), "insert_date": format(item.insert_time, "%Y-%m-%d")}
            for item in [ProjectLog(*item) async for item in query_data]]


def get_ip():

    """获取本机的IP"""

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_python_version() -> float:

    """获取当前解释器的python版本"""

    return float("%s,%s" % (sys.version_info.major, sys.version_info.minor))


if __name__ == "__main__":
    update_content = """
    2020-5-23更新内容：
    1.添加代理界面是需要将代理全部展示出来，将该界面移动到系统配置中
    2.代理界面更新代理的时候清楚没用的代理,增加和清除按钮删除,
    3.当前任务的联动,涉及线程(进程)之间的通信问题
    4.自定义日志格式,优化爬虫日志的写入
    5.提取电影资源url的优化,以前是request+硬编码xpath提取-->异步aiohttp+多线程xpath提取
    6.函数注解与代码的规范化
    下一步工作:
    1.在爬虫爬取的时候会默认先筛选代理
    2.搜索历史框的联动有问题
    3.爬虫日志是否需要移动到用户中心下,加下拉框实现切换功能
    4.代理与任务的联动
    5.随机代理的优化
    6.多任务运行
    """
    update_project_log(update_content)
