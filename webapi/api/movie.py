#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/9/19 17:15
# Author  : He
# Github : https://github.com/JustKeepSilence

# 电影搜索界面的后台函数

import os
import asyncio
from multiprocessing import Process
from typing import Union, AsyncGenerator, Optional

import aiofiles
from aiohttp import web

from util.config import sio
from util import db, log, config
from download_spider.main import *
from util.decorator import method_dec
from util.data_structure import WebSite, SearchHistory, Movie


@method_dec("/get_website_list")
async def get_website_list(request):

    """获取爬虫website列表
       `type_name`: 类型名称
       `return`: dict{code: int, data: dict{msg: str, result: list[str]}}
    """

    request_data = await request.json()
    web_site_type = request_data.get("type_name")
    if web_site_type:
        # 如果可以获取到web_site
        try:
            query_data = [item.web_site_name for item in
                          [WebSite(*item) async for item in await db.get_data(
                              f"select web_site_name from web_site_cfg where type_name='{web_site_type}'")]]
        except AttributeError:
            return web.json_response({"code": 500, "data": {"msg": "failed", "error_msg": "incorrect type"}})
        else:
            return web.json_response({"code": 200, "data": {"msg": "success", "result": query_data}})
    else:
        return web.json_response({"code": 500, "data": {"msg": "failed", "error_msg": "incorrect type"}})

@method_dec("/get_search_history_list")
async def get_search_history_list(request):

    """获取搜索历史
       `type_name`: 类型名称
       `return`: dict{code: int, data: dict{msg: str, result: list[str]}}
    """

    request_data = await request.json()
    type_name = request_data.get("type_name")
    if type_name:
        query_data = await db.get_data(f"select distinct keyword from search_history_cfg where type_name='{type_name}'")
        if query_data:
            # 如果查询的结果不为空
            response_data = [{"value": item.keyword} for item in [SearchHistory(*item) async for item in query_data]]
        else:
            response_data = [{"value": "搜索历史为空"}]
        return web.json_response({"code": 200, "data": {"msg": "success", "result": response_data}})
    else:
        return web.json_response({"code": 500, "data": {"msg": "failed", "error_msg": "incorrect type"}})

@sio.event(namespace="/")
async def search_movie(sid, request_data):

    """根据用户输入的关键字和选择的网站来获取电影信息
       如果电影信息在数据库中已经存在,则直接获取数据库中的数据
       如果数据库中不存在则启动爬虫进行爬取，目前只支持模糊搜索
       后面需要加上配置，让用户在选择搜索方式的时候可以选择模糊或者是精确搜索
       `state`: websocket的连接状态,为None则是连接，否则是断开
       `func`: 待执行的函数,为delete_item则是删除某条记录,否则是获取记录
       `keyword`: 搜索的关键字
       `web_site_id`: 爬虫爬取得网站的id
       `page`: 前台表格中当前的页码
       `limit`: 前台表格中每一页的条数
       `return`: dict{code: int, data: dict{msg: str, total: int, result: list[dict{id, item_id, name,
       director, score, download_link, download_link_type, movie_type, synopsis, is_collected}]}}
    """

    keyword = request_data.get("keyword")
    search_keyword = request_data.get("search_keyword")
    web_site_id = request_data.get("web_site_id")
    page = request_data.get("page")
    limit = request_data.get("limit")
    if search_keyword:
        # 有搜索框输入
        query_data = [item async for item in await db.get_data(
            f"select * from movie_cfg where (name like '%{keyword}%' or director like '%{keyword}%') "
            f"and (name like '%{search_keyword}%' or director like '%{search_keyword}%') order by id")]
    else:
        query_data = [item async for item in await db.get_data(
            f"select * from movie_cfg where name like '%{keyword}%' or director like '%{keyword}%' "
            f"order by id")]
    if query_data or search_keyword:
        # 如果查询到的结果不为空 或者是表格内搜索框有输入但是查询出来的结果为空
        if query_data:
            # 查询到了结果
            response_data, total = await get_movie(page, limit, query_data)
        else:
            # 表格内搜索结果为空
            response_data, total = [], 0
        await sio.emit("movie", {"code": 200, "data": {"msg": "success", "result": response_data, "total": total}})
    else:
        root = os.getcwd()  # 获取当前的工作路径
        try:
            url = [item[0] async for item in
                   await db.get_data(f"select web_site_url from web_site_cfg where id={web_site_id}")][0]
            crawl_process = Process(target=start_crawl, args=("movie", ),
                                    kwargs={"source_link": url, "key_words": keyword, "task_id": 1})
            crawl_process.start()  # 启动爬虫进程
            os.chdir(root)  # 切换回当前的工作路径
            await sio.emit({"code": 204, "data": {"msg": "running", "result": []}})
            while crawl_process.is_alive():
                async with aiofiles.open(rf"{config.ROOT_PATH}\download_spider\log\movie_crawl.log",
                                         encoding="utf-8") as f:
                    response_data = await f.readlines()
                await asyncio.sleep(2)
                await sio.emit("movie", {"code": 204, "data": {"msg": "running", "result": response_data, "total": 0}})
            else:
                # 更新爬虫日志
                crawl_result = await log.update_crawl_log("movie", keyword)  # 更新爬虫日志到数据库,并获取爬虫结果
                log.clean_log("movie")  # 清空原来的爬虫日志文件
                if crawl_result:
                    # 如果爬取成功
                    response_data, total = await get_movie(page, limit, sql_command=f"select * from movie_cfg "
                                                                                    f"where name like "
                                                                                    f"'%{keyword}%' or director "
                                                                                    f"like '%{keyword}%' "
                                                                                    f"order by id")
                    await sio.emit("movie", {"code": 200, "data": {"msg": "success", "result": response_data,
                                                                   "total": total}})
                else:
                    await sio.emit("movie", {"code": 500, "data": {"msg": "failure", "result": [], "total": 0}})
        except IndexError:
            await sio.emit("movie", {"code": 200, "data": {"msg": "success", "result": [], "total": 0}})


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
    # 如果评分为空在页面上显示为暂无,这样既方便显示也方便前台按照评分来进行排序
    return [{"id": index, "item_id": item.id, "name": item.name, "director": item.director,
             "score": "暂无" if not item.score else item.score,
             "download_link": item.download_link,
             "download_link_type": item.download_link_type,
             "movie_type": item.movie_type, "synopsis": item.synopsis, "is_collected": item.is_collect}
            for index, item in enumerate(query_data[start: stop], start=1)], total

@sio.event(namespace='/')
async def update_movie_item_collection_status(sid, request_data):
    """
    更新电影表格中的某一行数据的收藏状态
    `id`: 该行数据在数据库中的id
    """
    movie_id = request_data.get("movie_id")  # 该行数据在数据库中的index
    table_id = request_data.get("table_id")  # 该行数据在表格中的index,前台需要根据这个index去更新表格中的数据
    is_collect = 1 if request_data.get("is_collected") else 0  # 判断该行写入数据库的数据
    await db.change_data(f'update movie_cfg set {is_collect=} where id={movie_id}')
    await sio.emit("update_movie_item_collection_status", {"code": 200, "data": {"msg": "success", "table_id": table_id,
                                                                                 "is_collected": is_collect}})

@method_dec('/delete_movie_item')
async def delete_movie_item(request):
    """删除电影表格中的某一行数据
       `movie_id`: 数据库中数据的index
       `return`:
    """
    request_data = await request.json()  # 获取请求数据
    movie_id = request_data.get("movie_id")
    await db.change_data(f"delete from movie_cfg where id={movie_id}")  # 删除数据
    return web.json_response({"code": 200, "data": {"msg": "success"}})


@method_dec("/get_all_movie_data")
async def get_all_movie_data(request):
    """获取所有的电影数据
       `keyword`: 搜索的关键字
       `search_keyword`: 表格搜索输入框的关键字
       `return`: dict{code: int, data: dict{msg: str, total: int, result: list[dict{id, item_id, name,
       director, score, download_link, download_link_type, movie_type, synopsis, is_collected}]}}
    """

    try:
        request_data = await request.json()  # 获取请求数据
        keyword = request_data.get("keyword")  # 获取搜索的关键字
        search_keyword = request_data.get("search_keyword")  # 获取表格内搜索关键字
        if search_keyword:
            # 有搜索框输入
            query_data = [item async for item in await db.get_data(
                f"select * from movie_cfg where (name like '%{keyword}%' or director like '%{keyword}%') "
                f"and (name like '%{search_keyword}%' or director like '%{search_keyword}%') order by id")]
        else:
            query_data = [item async for item in await db.get_data(
                f"select * from movie_cfg where name like '%{keyword}%' or director like '%{keyword}%' "
                f"order by id")]
        response_data, total = await get_movie(0, 0, query_data)
        return web.json_response({"code": 200, "data": {"msg": "success", "result": response_data, "total": total}})
    except Exception as e:
        return web.json_response({"code": 500, "data": {"msg": "error", "result": str(e), "total": 0}})
