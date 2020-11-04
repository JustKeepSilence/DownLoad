# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieSpiderItem(scrapy.Item):
    name = scrapy.Field()  # 电影名称
    director = scrapy.Field()  # 演员
    score = scrapy.Field()  # 电影评分
    download_link = scrapy.Field()  # 电影的链接
    download_link_type = scrapy.Field()  # 链接的类型
    movie_type = scrapy.Field()  # 电影的类型
    synopsis = scrapy.Field()  # 电影简介


class ProxyItem(scrapy.Item):
    proxy = scrapy.Field()  # value为代理列表


class MusicItem(scrapy.Item):

    """音乐Item"""
    name = scrapy.Field()  # 音乐的名称
    singer = scrapy.Field()  # 歌手
    album = scrapy.Field()  # 专辑
    duration = scrapy.Field()  # 时长
    source = scrapy.Field()  # 来源,qq.网易...
    music_link = scrapy.Field()  # 播放链接
    mv_link = scrapy.Field()  # Mv链接
