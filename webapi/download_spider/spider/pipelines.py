# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import re
import json
import random
import asyncio
from datetime import datetime
from itertools import zip_longest

import util.utils as uu
from util import db


def serialize_item(obj: object) -> dict:

    """在序列化json的时候序列化对应的Item类
       也可以直接将dict(Item)就可以使用json序列化,使用json.dumps的default参数即可
       `obj`:任意的object对象
    """

    d = {"__classname__": type(obj).__name__}  # 获取obj的类名
    d.update(vars(obj))  # 获取d的所有属性并更新,也可以使用__dict__获取属性
    return d


class MovieSpiderPipeline:

    def __init__(self):
        self.data = []

    def process_item(self, item, spider):
        self.data.append(item)
        uu.save_parse_item(spider.task_id, spider.logger, json.dumps(item, ensure_ascii=False, default=serialize_item))
        return item  # 交给下一个PipeLine接着处理

    def close_spider(self, spider):
        # 之提取可以解析的下载链接，即以https?|ftp|thunder|flashget|qqdl|fs2you开头的连接
        pattern = re.compile(r"https|ftp|thunder|flashget|qqdl|fs2you")
        for item in self.data:
            # 由于item的download_link可能为None,这样在正则中就没法匹配,所以要先去除那些为None的item
            t = list(filter(lambda k: re.match(pattern, k[0]),
                            filter(lambda k: k[0], zip(item["download_link"], item["download_link_type"]))))
            item["download_link"] = list(dict(t).keys())
            item["download_link_type"] = list(dict(t).values())
        # 将爬取到的数据写入数据库
        if self.data:
            # 如果爬取到的数据不为空
            sql = 'insert into movie_cfg (name, director, score, download_link, download_link_type, movie_type, ' \
                  'synopsis)' \
                  ' values ' + ",".join(f"""('{item["name"]}', '{item["director"]}', '{item["score"]}', 
                  '{json.dumps(item["download_link"]).replace("'", '"')}', 
                  '{json.dumps(item["download_link_type"], ensure_ascii=False).replace("'", '"')}',
                  '{item["movie_type"]}', '{item["synopsis"]}')""" for item in self.data)
            db.change_data_sync(sql)
        else:
            pass


class ProxySpiderPipeline:

    def __init__(self):
        self.data = []
        # self.sqlite = SQLite()  # 连接数据库

    def process_item(self, item, spider):

        # 处理每一个item

        proxies = json.loads(item["proxy"])
        proxies_ip = [item[1] for item in proxies]
        loop = asyncio.get_event_loop()
        checked_result = uu.check_proxy_async(proxies_ip, loop)
        useful_proxies = filter(lambda k: k[1], zip_longest(proxies, checked_result))
        now = format(datetime.now(), "%Y-%m-%d %H:%M:%S")
        for item in useful_proxies:
            self.data.append({"proxy_ip": item[0][1], "proxy_user_name": "", "proxy_user_pwd": "",
                              "proxy_type": item[0][0], "proxy_priority": random.randint(1, 1000),
                              "update_time": now})

    def close_spider(self, spider):
        self.sqlite.insert_multiple_data("proxy_cfg", "proxy_ip, proxy_user_name, proxy_user_pwd,"
                                                      "proxy_type, proxy_priority, update_time",
                                         self.data)
