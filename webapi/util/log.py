#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/7/5 12:59
# Author  : He
# Github : https://github.com/JustKeepSilence


"""日志文件的操作"""

import re
import json

import pymysql

from . import db
from .utils import get_root_path


async def update_crawl_log(log_type_name: str, search_keyword: str) -> bool:

    """更新crawl log表,会将爬取的stats数据以及详细的日志全部写入数据库
       `log_type_name`:爬取的类型,movie,music,image...
       `search_keyword`: 搜索关键字
    """

    log_path = rf"{get_root_path()}\download_spider\log\{log_type_name}_crawl.log"  # 日志文件的路径
    with open(log_path, "r", encoding="utf-8") as f:
        detailed_log = f.read()  # 爬取日志
        pattern = re.compile(r"Dumping Scrapy stats:(.*)}", re.DOTALL)  # 开启跨行匹配
        try:
            match_result = "%s}" % re.search(pattern, detailed_log).group(1).replace("'", '"')  # 提取最后的{}中的内容
            abbreviated_log = match_result.replace("\n", "")
            stats = json.loads(abbreviated_log)  # 将爬取结果反序列化
            try:
                is_success = 1 if stats.get("item_scraped_count") else 0  # 是否爬取成功
            except KeyError:
                is_success = 0  # 爬取失败
        except AttributeError:
            # 正则匹配错误
            is_success = 0
            abbreviated_log = json.dumps({"错误信息": "正则匹配出错"}, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            # 反序列化json出错
            is_success = 1
        finally:
            detailed_log = detailed_log.replace("'", '"')  # 为了写入SQL需要将'替换成"
            await db.change_data(f"insert into crawl_log_cfg (abbreviated_log, detailed_log, type_name, search_keyword,"
                                 f"is_lately_insert, is_success) values ('{abbreviated_log}','{detailed_log}',"
                                 f"'{log_type_name}', '{search_keyword}', 1, '{is_success}')")  # 将爬虫日志写入数据库
            if is_success == 1:
                # 如果爬取成功则将此次搜索关键字写入数据库的搜索历史表中
                try:
                    await db.change_data(f"insert into search_history_cfg (keyword, type_name) values "
                                         f"('{search_keyword}', '{log_type_name}')")
                except pymysql.IntegrityError:
                    pass  # 该搜索关键字已经存在
    return True if is_success == 1 else False  # 是否爬取成功

def clean_log(log_type_name: str) -> None:

    """清空爬虫日志文件
       `log_type_name`:爬取的类型,movie,music,image...
    """

    log_path = rf"{get_root_path()}\download_spider\log\{log_type_name}_crawl.log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.truncate()


def update_project_log(content: str) -> None:

    """更新项目进度日志
       `content`: 要更新的内容
    """

    # sqlite = SQLite()
    # now = format(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    # sqlite.insert("project_log", "update_log, update_time", f"'{content}', '{now}'")
    # sqlite.close_db()


