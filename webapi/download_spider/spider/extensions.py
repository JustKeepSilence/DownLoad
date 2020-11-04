#!/usr/bin/python3.6.5
# -*- coding: utf-8 -*-
# Time     : 2020/5/23 14:47
# Author  : He
# Github : https://github.com/JustKeepSilence


"""自定义的爬虫扩展件"""


import time
import datetime


from scrapy.extensions.corestats import CoreStats


class StatsCollectorExtensions(CoreStats):

    """重新定义StatsCollector中的日志起始时间和终止时间的格式
       原来的格式不利于json解析以及信息的提取
       datetime.utcnow() -> 北京标准时间
    """

    def spider_opened(self, spider):
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.stats.set_value('start_time', self.start_time, spider=spider)

    def spider_closed(self, spider, reason):
        finish_time = time.strftime("%Y-%m-%d %H:%M:%S")
        elapsed_time = datetime.datetime.strptime(finish_time,
                                                  "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(self.start_time,
                                                                                                    "%Y-%m-%d %H:%M:%S")
        elapsed_time_seconds = elapsed_time.seconds
        self.stats.set_value('elapsed_time_seconds', elapsed_time_seconds, spider=spider)
        self.stats.set_value('finish_time', finish_time, spider=spider)
        self.stats.set_value('finish_reason', reason, spider=spider)
