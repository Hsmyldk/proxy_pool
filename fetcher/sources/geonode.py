# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     geonode.py
   Description :   Geonode代理源
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
                   2026/10/14: 移除失效的filterLastChecked参数, 并过滤掉socks代理
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class GeonodeFetcher(BaseFetcher):
    """Geonode Free Proxy https://geonode.com/"""

    name = "geonode"
    url = "https://geonode.com/"

    def fetch(self):
        # filterLastChecked 参数已失效(带上它接口恒返回空), 故不再使用
        url = ("https://proxylist.geonode.com/api/proxy-list?"
               "page=1&limit=100&sort_by=lastChecked&sort_type=desc")
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        try:
            proxies = []
            for item in r.json.get("data", []):
                ip = item.get("ip", "")
                port = item.get("port", "")
                protocols = [str(p).lower() for p in (item.get("protocols") or [])]
                # 只保留http/https代理(项目不支持socks); 无protocols字段时不作过滤
                if ip and port and (not protocols
                                    or any(p in ("http", "https") for p in protocols)):
                    proxies.append("%s:%s" % (ip, port))
            if not proxies:
                proxies = self.parseProxiesFromText(r.text)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - geonode: %s" % e)


if __name__ == '__main__':
    for proxy in GeonodeFetcher().fetch():
        print(proxy)