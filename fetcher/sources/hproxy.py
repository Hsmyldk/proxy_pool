# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hproxy.py
   Description :   HProxy代理源
   Author :        JHao
   date：          2026/10/15
-------------------------------------------------
   Change Activity:
                   2026/10/15: 新增HProxy免费代理API源, 仅采集非透明HTTP/HTTPS代理
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class HproxyFetcher(BaseFetcher):
    """HProxy免费代理列表 https://hproxy.com/docs/free-proxy-list"""

    name = "hproxy"
    url = "https://hproxy.com/docs/free-proxy-list"
    enabled = True

    # API无需key: http与https合并查询, 排除transparent, 仅取按uptime排序的前100条
    # min_uptime_pct用于避开完全不可用的代理; anonymity参数保证透明代理不进入采集结果
    listUrl = (
        "https://hproxy.com/api/proxy-list"
        "?format=txt&protocol=http,https&anonymity=elite,anonymous"
        "&min_uptime_pct=20&sort=uptime&limit=100"
    )

    # 上游已带uptime与匿名度过滤, 单轮100条与项目30分钟采集间隔及校验吞吐匹配
    limit = 100

    def fetch(self):
        r = WebRequest().get(self.listUrl, timeout=20, retry_time=1)
        for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
            yield proxy


if __name__ == '__main__':
    for proxy in HproxyFetcher().fetch():
        print(proxy)
