# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     thespeedx.py
   Description :   TheSpeedX代理源
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


class TheSpeedXFetcher(BaseFetcher):
    """TheSpeedX PROXY-List https://github.com/TheSpeedX/PROXY-List"""

    name = "thespeedx"
    url = "https://github.com/TheSpeedX/PROXY-List"

    # 每日更新的纯文本列表, 仅取http协议(项目不支持socks)
    listUrl = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"

    # 源内数千条, 单轮只随机取limit条慢慢校验
    limit = 200

    def fetch(self):
        r = WebRequest().get(self.listUrl, timeout=15, retry_time=1)
        proxies = self.limitProxies(self.parseProxiesFromText(r.text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in TheSpeedXFetcher().fetch():
        print(proxy)
