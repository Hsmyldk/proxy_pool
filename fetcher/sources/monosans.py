# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     monosans.py
   Description :   Monosans代理源
   Author :        JHao
   date：          2026/10/14
-------------------------------------------------
   Change Activity:
                   2026/10/14: 新增
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class MonosansFetcher(BaseFetcher):
    """Monosans 免费代理列表 https://github.com/monosans/proxy-list"""

    name = "monosans"
    url = "https://github.com/monosans/proxy-list"

    # 上游每小时复检一次并按响应速度排序, 是免费源里质量最高的一个
    listUrl = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"

    # 列表本身仅300余条且质量高, 基本全量入队
    limit = 300

    def fetch(self):
        r = WebRequest().get(self.listUrl, timeout=15, retry_time=1)
        proxies = self.limitProxies(self.parseProxiesFromText(r.text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in MonosansFetcher().fetch():
        print(proxy)
