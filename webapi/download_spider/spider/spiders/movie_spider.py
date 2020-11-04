#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/4/23 0:02
# Author  : He
# Github : https://github.com/JustKeepSilence


import re
import json
import time
import asyncio
from lxml import etree
from hashlib import md5
from typing import Union
from concurrent import futures
from itertools import zip_longest

from scrapy import Request
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor

import util.utils as uu
from ..items import *


class MovieSpider(scrapy.Spider):
    """电影爬虫类"""

    name = "movie"  # 爬虫的名称
    custom_settings = {
        "COOKIES_ENABLED": True,  # 开启cookie否则无法爬取该网站
        "DOWNLOAD_TIMEOUT": 20  # 设置下载超时为20s
    }

    def __init__(self, *args, **kwargs):

        """接受从views中传过来的参数进行初始化爬虫"""

        self.key_words = kwargs.get("key_words")  # 获取搜索的关键字
        self.start_urls = [kwargs.get("source_link")]  # 获取初始的url
        self.task_id = kwargs.get("task_id")  # 获取任务的id
        self.allow_domains = [uu.get_domains(self.start_urls[0])]  # 设置允许的爬虫域
        self.q = kwargs.get("q")  # 获取通信的队列
        super().__init__(*args, **kwargs)
        uu.update_task_process(self.task_id, json.dumps({time.strftime("%Y-%m-%d %H:%M:%S"): "Initialize spider "
                                                                                             "successfully"}))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> scrapy.Spider:

        """重写from crawler来支持在twisted中使用ThreadPoolExecutor多进程来开启爬虫"""

        if not args:
            args = [cls.name]  # 如果args为空则获取cls中的爬虫名称
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    @staticmethod
    def get_data_from_response(response: Response, xpath_sentence: str, r_type: str) -> Union[str, list]:

        """从response中根据xpath提取内容
           `response`: scrapy的Response响应对象
           `xpath_sentence`: 提取内容的xpath表达式
           `r_type`: 返回的结果类型,可以是str或者list
        """

        if r_type == "str":
            try:
                return response.xpath(xpath_sentence).extract()[0]
            except IndexError:
                return ""
        elif r_type == "list":
            try:
                return response.xpath(xpath_sentence).extract()
            except IndexError:
                return []
        else:
            raise TypeError("unsupported type %s".format(r_type))

    def parse(self, response: Response, **kwargs):

        """先使用GET拿到页面的CSRF,也可以使用FromRequest直接构造POST请求"""

        csrf = response.xpath("//input[@id='_csrf']/@value").extract()[0]
        data = {
            "keyword": self.key_words,
            "_csrf": csrf
        }
        uu.save_parse_page(self.task_id, self.logger, response.url)  # 更新日志和数据库
        yield scrapy.FormRequest(url=self.start_urls[0],
                                 callback=self.parse_first_page, formdata=data,
                                 dont_filter=True)

    def parse_first_page(self, response: Response):

        """解析搜索结果页面,拿到所有结果的资源页的url"""

        uu.save_parse_page(self.task_id, self.logger, response.url)  # 更新日志和数据库
        source_links = LinkExtractor(
            restrict_xpaths=r"//div[@class='content-wrapper']//a[@target='_blank']")
        links = source_links.extract_links(response)  # 提取response中的链接
        for link in links:
            # 发送请求
            yield scrapy.Request(url=link.url, callback=self.parse_source_page)

    def parse_source_page(self, response: Response):

        """解析最终的界面,拿到各种需要的信息"""

        uu.save_parse_page(self.task_id, self.logger, response.url)  # 更新日志和数据库
        item = MovieSpiderItem()
        movie_name = self.get_data_from_response(
            response, r'//div[@class="section-header col-md-12"]//h2/text()', "str")
        item["name"] = movie_name
        director = self.get_data_from_response(
            response, r'//div[@class="blog-image"]//div[2]//div[3]//div/text()', "str")
        item["director"] = re.search(
            r":(.*)", director).group(1) if director != "" else ""
        item["score"] = self.get_data_from_response(
            response, r'//div[@class="blog-image"]//div[2]//div[6]//a/text()', "str")
        movie_type_name = self.get_data_from_response(
            response, r'//div[@class="blog-image"]//div[2]//div[2]//div/text()', "str")
        item["movie_type"] = re.sub(
            r"\s*",
            "",
            re.search(
                r":(.*)",
                movie_type_name).group(1).replace(
                "/",
                ",") if movie_type_name != "" else "")
        item["synopsis"] = self.get_data_from_response(
            response, r'//span[@id="layout"]/text()', "str").replace("©豆瓣", "")
        item["download_link_type"] = self.get_data_from_response(
            response, r'//span[@class="label label-warning"]/text()', "list")
        rule = LinkExtractor(restrict_xpaths=r'//a[@class="list-group-item"]')
        download_links = rule.extract_links(
            response)[::-1][:len(item["download_link_type"]):]
        urls = [link.url for link in download_links]
        download_url = self.parse_download_page(urls)
        item["download_link"] = download_url
        yield item

    def parse_download_page(self, urls: list) -> list:

        """使用异步和多线程提取下载链接页的所有链接
           urls: 下载链接页的url列表
        """

        download_url = []
        if urls:
            loop = asyncio.get_event_loop()  # 获取事件循环
            html_contents = uu.start_async_request(urls, loop, text_type="text")  # 获取urls列表中所有url的html内容
            if html_contents:
                # html内容不为空时候才提取url
                max_workers = len(html_contents)  # 可能会有多余的线程,但是为了使用filter生成器
                html_contents = filter(lambda item: item != "false", html_contents)  # 返回的是false的不要
                with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    download_url = list(executor.map(self.get_download_url, html_contents))
        return download_url

    @staticmethod
    def get_download_url(html_content: "str") -> Union[str, None]:

        """解析html页面中的下载地址"""

        try:
            content = etree.HTML(html_content)
            return content.xpath(r"//textarea//text()")[0]  # 提取url
        except (AttributeError, IndexError):
            return None  # 返回None来保证item中download_link和download_link_type
        # list的长度是一样的


class XProxySpider(scrapy.Spider):

    """西祠代理爬虫"""

    name = "x_proxy"  # 爬虫名称
    index = 0  # 用于记录urls列表的下标,用于终止爬虫
    custom_settings = {
        "ITEM_PIPELINES": {
            "spider.pipelines.ProxySpiderPipeline": 400  # 管道文件
        },
        "LOG_FILE": rf"log\x_proxy_crawl.log"  # 日志文件
    }

    def __init__(self, name):

        self.start_urls = ["https://www.xicidaili.com/nt/"]
        self.urls = ["https://www.xicidaili.com/nt/2",
                     "https://www.xicidaili.com/nn/", "https://www.xicidaili.com/nn/2"]
        super().__init__()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> scrapy.Spider:

        """重写from crawler来支持在twisted中使用ThreadPoolExecutor多进程来开启爬虫"""

        if not args:
            args = [cls.name]  # 如果args为空则获取cls中的爬虫名称
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def parse(self, response):

        """解析页面"""

        proxy_item = ProxyItem()
        proxy_type = response.xpath(r'//table[@id="ip_list"]//tr//td[6]/text()').extract()  # 代理的类型
        proxy_url = response.xpath(r'//table[@id="ip_list"]//tr//td[2]/text()').extract()  # 代理url
        proxy_port = response.xpath(r'//table[@id="ip_list"]//tr//td[3]/text()').extract()  # 代理端口号
        survival_time = response.xpath(r'//table[@id="ip_list"]//tr//td[9]/text()').extract()  # 存活时间
        filtered_proxy = [(item[0].lower(), f"{item[0].lower()}://{item[1]}:{item[2]}") for item in
                          zip_longest(proxy_type, proxy_url, proxy_port, survival_time)
                          if "秒" not in item[-1] and "分钟" not in item[-1]]  # 只提取存活时间>分钟的代理
        proxy_item["proxy"] = json.dumps(filtered_proxy, ensure_ascii=False)
        yield proxy_item
        if self.index < len(self.urls):
            self.index += 1
            yield scrapy.Request(self.urls[self.index - 1], callback=self.parse, dont_filter=True)


class KProxySpider(scrapy.Spider):

    """快代理爬虫"""

    name = "k_proxy"  # 爬虫名称
    custom_settings = {
        "ITEM_PIPELINES": {
            "spider.pipelines.ProxySpiderPipeline": 400  # 管道文件
        },
        "LOG_FILE": rf"log\k_proxy_crawl.log"  # 日志文件
    }

    def __init__(self, name):
        self.index = 0  # 记录urls的下标用于终止爬虫
        self.urls = ["https://www.kuaidaili.com/free/inha/2/", "https://www.kuaidaili.com/free/intr/",
                     "https://www.kuaidaili.com/free/intr/2/"]
        self.start_urls = ["https://www.kuaidaili.com/free/inha/"]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> scrapy.Spider:

        """重写from crawler来支持在twisted中使用ThreadPoolExecutor多进程来开启爬虫"""

        if not args:
            args = [cls.name]  # 如果args为空则获取cls中的爬虫名称
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def parse(self, response):

        """解析页面"""

        proxy_item = ProxyItem()
        proxy_type = response.xpath(r'//table//tr//td[4]/text()').extract()
        proxy_url = response.xpath(r'//table//tr//td[1]/text()').extract()
        proxy_port = response.xpath(r'//table//tr//td[2]/text()').extract()
        filtered_proxy = [(item[0].lower(), f"{item[0].lower()}://{item[1]}:{item[2]}") for item in
                          zip_longest(proxy_type, proxy_url, proxy_port)]
        proxy_item["proxy"] = json.dumps(filtered_proxy, ensure_ascii=False)
        yield proxy_item
        if self.index < len(self.urls):
            self.index += 1
            yield scrapy.Request(self.urls[self.index - 1], callback=self.parse, dont_filter=True)


class KGMusicSpider(scrapy.Spider):

    """酷狗音乐爬虫"""

    name = "kg_music"

    custom_settings = {
        "COOKIES_ENABLED": True,  # 开启cookie否则无法爬取该网站
        "DEFAULT_REQUEST_HEADERS": {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.122 Safari/537.36',
        ":authority": "music.163.com",
        ":path": "/search/m/",
        ":scheme": "https",
        "upgrade-insecure-requests": 1
    }
    }

    def __init__(self, *args, **kwargs):
        self.keyword = kwargs.get("key_word")  # 获取搜索的关键词
        data = list(range(20))  # 拼接酷狗搜索的md5字符串
        data[0] = "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
        data[1] = "bitrate=0"
        data[2] = "callback=callback123"
        data[3] = "clienttime=1591011074750"
        data[4] = "clientver=2000"
        data[5] = "dfid=-"
        data[6] = "inputtype=0"
        data[7] = "iscorrection=1"
        data[8] = "isfuzzy=0"
        data[9] = f"keyword={self.keyword}"
        data[10] = "mid=1591011074750"
        data[11] = "page=1"
        data[12] = "pagesize=30"
        data[13] = "platform=WebFilter"
        data[14] = "privilege_filter=0"
        data[15] = "srcappid=2919"
        data[16] = "tag=em"
        data[17] = "userid=-1"
        data[18] = "uuid=1591011074750"
        data[19] = "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
        m = md5()
        m.update("".join(data).encode("utf-8"))
        self.signature = m.hexdigest().upper()  # 得到signature字段
        self.start_urls = [f"https://complexsearch.kugou.com/v2/search/song?callback=callback123&keyword={self.keyword}"
                           f"&page=1&pagesize=30&bitrate=0&isfuzzy=0&tag=em&inputtype=0&platform=WebFilter&userid=-1"
                           f"&clientver=2000&iscorrection=1&privilege_filter=0&srcappid=2919&clienttime=1591011074750&"
                           f"mid=1591011074750&uuid=1591011074750&dfid=-&signature={self.signature}"]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> scrapy.Spider:

        """重写from crawler来支持在twisted中使用ThreadPoolExecutor多进程来开启爬虫"""

        if not args:
            args = [cls.name]  # 如果args为空则获取cls中的爬虫名称
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=False, meta={"dont_redirect": False},
                          callback=self.parse,)

    def parse(self, response):

        """拿到搜索结果"""
        pattern = re.compile(r"callback123\((.*)\)", re.DOTALL)  # 利用正则匹配搜索的结果
        song_list = json.loads(re.match(pattern, response.text).group(1))["data"]["lists"]
        for song in song_list:
            item = MusicItem()
            item["name"] = song.get("SongName").replace("<em>", "").replace("</em>", "")  # 歌曲名称
            item["singer"] = song.get("SingerName")  # 歌手名称
            item["album"] = song.get("AlbumName")  # 专辑名称
            item["duration"] = song.get("SQDuration")  # 歌曲时长
            item["source"] = "酷我音乐"  # 歌曲来源
            item["music_link"] = f"https://www.kugou.com/song/#hash={song.get('FileHash')}&album_id=" \
                                 f"{song.get('AlbumID')}"  # 音乐的链接
            yield item


class QQMusicSpider(scrapy.Spider):

    """QQ音乐爬虫"""

    name = "qq_music"

    def __init__(self, *args, **kwargs):
        self.key = kwargs.get("key_word")  # 搜索的关键字
        self.start_urls = ["https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&"
                           "remoteplace=txt.yqq.song&searchid=64565844011673806&t=0&aggr=1&cr=1&catZhida=1&lossless=0&"
                           "flag_qc=0&p=1&n=10&w={}&g_tk_new_20200303=5381&g_tk=5381&loginUin=0&hostUin=0&format=json"
                           "&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0".format(self.key)]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):

        """重写from crawler来支持在twisted中使用ThreadPoolExecutor多进程来开启爬虫"""

        if not args:
            args = [cls.name]  # 如果args为空则获取cls中的爬虫名称
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def parse(self, response):
        song_list = json.loads(response.text)["data"]["song"]["list"]
        for song in song_list:
            item = MusicItem()
            item["name"] = song.get("name").replace("<em>", "").replace("</em>", "")  # 歌曲名称
            item["singer"] = song.get("singer")[0].get("name")  # 歌手名称
            item["album"] = song.get("album").get("title")  # 专辑名称
            # item["duration"] = song.get("SQDuration")  # 歌曲时长
            item["source"] = "QQ音乐"  # 歌曲来源
            item["music_link"] = f"https://y.qq.com/n/yqq/song/{song.get('mid')}.html"  # 音乐的链接
            item["mv_link"] = f"https://y.qq.com/n/yqq/mv/v/{song.get('mv').get('vid')}.html"
            yield item
