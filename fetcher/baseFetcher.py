# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     baseFetcher.py
   Description :   代理源基类
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
                    2026/10/14: 新增limit属性与limitProxies采样方法, 限制超大源单轮入队量
-------------------------------------------------
"""
__author__ = 'JHao'

import random
import re


class BaseFetcher(object):
    """代理源基类"""

    # ---- 子类必须声明 ----
    name = ""        # 唯一标识，如 "zdaye"
    url = ""         # 源网站首页 URL

    # ---- 子类可覆盖 ----
    enabled = True   # 是否启用，设为 False 可禁用该源
    limit = 0        # 单轮最多产出条数(超出时随机采样)，0 表示不限制

    def fetch(self):
        """爬取代理，yield "host:port" 字符串"""
        raise NotImplementedError

    def limitProxies(self, proxies):
        """
        按 limit 随机采样，限制单轮入队量

        超大源(数万条)全量入队会让单轮校验耗时数小时，故只随机取 limit 条慢慢消化，
        未入选的代理在后续轮次仍有概率被采到，保证入池的都是校验通过的代理。
        """
        if self.limit and len(proxies) > self.limit:
            return random.sample(proxies, self.limit)
        return proxies

    @staticmethod
    def parseProxiesFromText(text):
        """从文本中用正则提取 ip:port"""
        if not text:
            return []
        proxy_pattern = re.compile(
            r'(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?:\s*:\s*|\s+)(\d{2,5})(?!\d)')
        return ["%s:%s" % proxy for proxy in proxy_pattern.findall(text)]

    @staticmethod
    def yieldUniqueProxies(proxies):
        """去重 yield"""
        seen = set()
        for proxy in proxies:
            if proxy not in seen:
                seen.add(proxy)
                yield proxy