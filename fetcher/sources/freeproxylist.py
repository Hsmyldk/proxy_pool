# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     freeproxylist.py
   Description :   Free-Proxy-List / SSLProxies代理源
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


class FreeProxyListFetcher(BaseFetcher):
    """Free-Proxy-List 系列免费代理列表 https://free-proxy-list.net/"""

    name = "freeproxylist"
    url = "https://free-proxy-list.net/"

    # 页面内的只读文本框直接给出纯文本 ip:port 列表, 无需解析表格
    listUrls = [
        "https://free-proxy-list.net/",
        "https://www.sslproxies.org/",
    ]

    limit = 200

    def fetch(self):
        proxies = []
        for url in self.listUrls:
            r = WebRequest().get(url, timeout=20, retry_time=1, verify=False)
            proxies.extend(self.parseProxiesFromText(r.text))

        unique = list(dict.fromkeys(proxies))
        for proxy in self.yieldUniqueProxies(self.limitProxies(unique)):
            yield proxy


if __name__ == '__main__':
    for proxy in FreeProxyListFetcher().fetch():
        print(proxy)
