#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/9/30 10:40
# Author  : He
# Github : https://github.com/JustKeepSilence

# 和下载有关的后台函数的接口

from itertools import repeat
import xmlrpc.client as xc

from aiohttp import web

from util import db
from util.decorator import method_dec

@method_dec("/add_download_items")
async def add_download_items(request):

    """向aria2中添加下载链接
       `download_urls`: 下载的链接
       `return`: dict{code: int, data: dict{msg: str, result: list}}
    """

    request_data = await request.json()  # 获取请求的数据
    download_urls = request_data.get("download_urls")  # 获取下载的链接
    # 获取所有已经存在的下载链接
    download_lists = [item[0] async for item in await db.get_data("select download_url from download_cfg")]
    exist_urls = set(download_lists) & set(download_urls)  # 获取已经存在的链接
    if exist_urls != set():
        # 有下载链接已经被加入到aria2中
        download_urls = list(set(download_urls) - set(download_lists))  # 下载链接为两者的差集
    exist_urls = list(exist_urls)
    if download_urls:
        # 最终的下载链接不为空,说明此时可以向
        # 如果前台有传进来file_name,则使用filename,否则使用url作为filename
        download_filenames = download_urls if not request_data.get("filename") else request_data.get("filename")
        filepath = request_data.get("filepath")  # 获取文件的下载路径
        download_filepath = list(repeat(r"F:\aria2", len(download_urls))) if not filepath else filepath
        typename = list(repeat(request_data.get("typename"), len(download_urls)))  # 下载的类型
        server = xc.ServerProxy("http://localhost:6800/rpc")  # 启动aria2的脚本,使用RPC-xml来进行控制,默认的端口号是6800
        gids = []  # 所有下载任务的gids
        for download_url in download_urls:
            gids.append(server.aria2.addUri([download_url]))  # 将下载链接加入到aria2下载器中,需要注意的是加入的必须是list
        command = f"insert into download_cfg (download_url, download_file_name,download_file_path,download_gid,type_name)" \
                  f" values " + \
                  ",".join(f"""('{item[0]}', '{item[1]}', '{item[2]}',  '{item[3]}', '{item[4]}')"""
                           for item in zip(download_urls, download_filenames, download_filepath, gids, typename))
        await db.change_data(command=command)
        return web.json_response({"code": 200, "data": {"msg": "success", "result": gids}})
    else:
        # 所有的下载链接都已经存在
        return web.json_response({"code": 200, "data": {"msg": "success", "result": []}})