# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     scdntext.py
   Description :   SCDN纯文本代理源
   Author :        JHao
   date：          2026/10/12
-------------------------------------------------
   Change Activity:
                   2026/10/12: 新增SCDN纯文本代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class ScdnTextFetcher(BaseFetcher):
    """SCDN 纯文本代理接口 https://proxy.scdn.io/text.php"""

    name = "scdntext"
    url = "https://proxy.scdn.io/"
    enabled = True

    listUrl = "https://proxy.scdn.io/text.php"

    # 该接口一次返回数万条(实测28603条), 全量入队会让单轮校验耗时数小时, 故随机采样limit条;
    # 设为0表示不限制(全量)
    limit = 300

    def fetch(self):
        r = WebRequest().get(self.listUrl, timeout=20, retry_time=1, verify=False)
        proxies = self.limitProxies(self.parseProxiesFromText(r.text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ScdnTextFetcher().fetch():
        print(proxy)
