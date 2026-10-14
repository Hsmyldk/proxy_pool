# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     openproxylist.py
   Description :   OpenProxyList代理源
   Author :        JHao
   date：          2026/10/12
-------------------------------------------------
   Change Activity:
                   2026/10/12: 新增OpenProxyList HTTPS代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class OpenProxyListFetcher(BaseFetcher):
    """OpenProxyList HTTPS代理列表 https://openproxylist.com"""

    name = "openproxylist"
    url = "https://openproxylist.com"
    enabled = True

    # GitHub raw 上的HTTPS代理列表(纯文本, 代理行形如 "🇹🇭 1.2.3.4:8080 374ms TH [ISP]")
    listUrl = "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS.txt"

    def fetch(self):
        r = WebRequest().get(self.listUrl, timeout=15, retry_time=1)
        for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
            yield proxy


if __name__ == '__main__':
    for proxy in OpenProxyListFetcher().fetch():
        print(proxy)
