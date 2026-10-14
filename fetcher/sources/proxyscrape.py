# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyscrape.py
   Description :   ProxyScrape代理源
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


class ProxyScrapeFetcher(BaseFetcher):
    """ProxyScrape 免费代理接口 https://www.proxyscrape.com/free-proxy-list"""

    name = "proxyscrape"
    url = "https://www.proxyscrape.com/free-proxy-list"

    # 官方v4接口, 分别取http转发与https(CONNECT)代理, 每个协议返回上千条
    listUrls = [
        "https://api.proxyscrape.com/v4/free-proxy-list/get"
        "?request=display_proxies&protocol=http&proxy_format=ipport&format=text&timeout=5000",
        "https://api.proxyscrape.com/v4/free-proxy-list/get"
        "?request=display_proxies&protocol=https&proxy_format=ipport&format=text&timeout=5000",
    ]

    # 接口数据量大且时效性一般, 单轮只随机取limit条
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
    for proxy in ProxyScrapeFetcher().fetch():
        print(proxy)
