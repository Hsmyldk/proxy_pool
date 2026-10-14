# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     spysme.py
   Description :   Spys.me代理源
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


class SpysMeFetcher(BaseFetcher):
    """Spys.me 免费代理列表 https://spys.me/"""

    name = "spysme"
    url = "https://spys.me/"

    # 纯文本, 每行形如 "1.2.3.4:8080 TH-H"(国家码-匿名度)
    listUrl = "https://spys.me/proxy.txt"

    limit = 200

    def fetch(self):
        r = WebRequest().get(self.listUrl, timeout=15, retry_time=1, verify=False)
        proxies = self.limitProxies(self.parseProxiesFromText(r.text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in SpysMeFetcher().fetch():
        print(proxy)
