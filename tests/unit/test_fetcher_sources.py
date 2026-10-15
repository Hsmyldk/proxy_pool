# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources.py
   Description :   各代理源 fetcher 测试
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from unittest.mock import patch, MagicMock

from lxml import etree

from fetcher.baseFetcher import BaseFetcher


# --------------- 辅助工具 ---------------

def _make_response(text="", tree=None, json_data=None):
    """构造 mock 的 WebRequest 返回对象"""
    resp = MagicMock()
    resp.text = text
    resp.tree = tree
    resp.json = json_data if json_data is not None else {}
    return resp


def _html_table(rows, has_header=False):
    """快速生成 HTML table 字符串"""
    html = "<table>"
    if has_header:
        html += "<tr><th>IP</th><th>Port</th></tr>"
    for ip, port in rows:
        html += "<tr><td>%s</td><td>%s</td></tr>" % (ip, port)
    html += "</table>"
    return html


def _assert_valid_proxies(proxies):
    """验证所有 proxy 符合 ip:port 格式"""
    pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$')
    for p in proxies:
        assert pattern.match(p), f"Invalid proxy format: {p}"


# --------------- 接口约定测试 ---------------

class TestFetcherInterface(object):
    """所有 fetcher 的接口约定"""

    FETCHER_CLASSES = [
        ("fetcher.sources.kxdaili", "KxdailiFetcher"),
        ("fetcher.sources.ip3366", "Ip3366Fetcher"),
        ("fetcher.sources.ip89", "Ip89Fetcher"),
        ("fetcher.sources.docip", "DocipFetcher"),
        ("fetcher.sources.goodips", "GoodipsFetcher"),
        ("fetcher.sources.geonode", "GeonodeFetcher"),

        ("fetcher.sources.kuaidaili", "KuaidailiFetcher"),
        ("fetcher.sources.freevpnnode", "FreeVPNNodeFetcher"),
        ("fetcher.sources.scdn", "ScdnFetcher"),
        ("fetcher.sources.zdaye", "ZdayeFetcher"),
        ("fetcher.sources.ihuan", "IhuanFetcher"),
        ("fetcher.sources.proxifly", "ProxiFlyFetcher"),
        ("fetcher.sources.daili66", "DaiLi66Fetcher"),
        ("fetcher.sources.roundproxies", "RoundProxiesFetcher"),
        ("fetcher.sources.openproxylist", "OpenProxyListFetcher"),
        ("fetcher.sources.scdntext", "ScdnTextFetcher"),
        ("fetcher.sources.monosans", "MonosansFetcher"),
        ("fetcher.sources.thespeedx", "TheSpeedXFetcher"),
        ("fetcher.sources.proxyscrape", "ProxyScrapeFetcher"),
        ("fetcher.sources.spysme", "SpysMeFetcher"),
        ("fetcher.sources.freeproxylist", "FreeProxyListFetcher"),
        ("fetcher.sources.hproxy", "HproxyFetcher"),
    ]

    def test_all_fetchers_have_name_url_enabled(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.name, f"{class_name} missing name"
            assert cls.url, f"{class_name} missing url"
            assert hasattr(cls, 'enabled'), f"{class_name} missing enabled"

    def test_all_fetchers_subclass_base(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert issubclass(cls, BaseFetcher), f"{class_name} not subclass of BaseFetcher"

    def test_all_fetchers_have_fetch_method(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert hasattr(cls, 'fetch'), f"{class_name} missing fetch method"


# --------------- 各 fetcher 逻辑测试 ---------------

class TestKxdailiFetcher(object):

    @patch("fetcher.sources.kxdaili.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.kxdaili import KxdailiFetcher
        html = '<table class="active"><tr><th>IP</th><th>Port</th></tr>' \
               '<tr><td>1.2.3.4</td><td>8080</td></tr></table>'
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(KxdailiFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestIp3366Fetcher(object):

    @patch("fetcher.sources.ip3366.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.ip3366 import Ip3366Fetcher
        html = '<td>1.2.3.4</td><td>8080</td><td>5.6.7.8</td><td>3128</td>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(Ip3366Fetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result


class TestIp89Fetcher(object):

    @patch("fetcher.sources.ip89.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.ip89 import Ip89Fetcher
        html = '<td>1.2.3.4</td><td>8080</td>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(Ip89Fetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestDocipFetcher(object):

    @patch("fetcher.sources.docip.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.docip import DocipFetcher
        json_data = {"data": [{"ip": "1.2.3.4:8080"}, {"ip": "5.6.7.8:3128"}]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(DocipFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result


class TestGoodipsFetcher(object):

    @patch("fetcher.sources.goodips.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.goodips import GoodipsFetcher
        html = '<div class="table-list"><ul><li>1.2.3.4</li><li>8080</li></ul></div>'
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(GoodipsFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestGeonodeFetcher(object):

    @patch("fetcher.sources.geonode.WebRequest")
    def test_fetch_json(self, mock_wr):
        from fetcher.sources.geonode import GeonodeFetcher
        json_data = {"data": [{"ip": "1.2.3.4", "port": "8080"}]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GeonodeFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.geonode.WebRequest")
    def test_fetch_text_fallback(self, mock_wr):
        from fetcher.sources.geonode import GeonodeFetcher
        mock_wr.return_value.get.return_value = _make_response(
            json_data={}, text="1.2.3.4:8080")
        result = list(GeonodeFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.geonode.WebRequest")
    def test_fetch_filters_socks_proxies(self, mock_wr):
        """只保留http/https协议, socks代理应被过滤掉"""
        from fetcher.sources.geonode import GeonodeFetcher
        json_data = {"data": [
            {"ip": "1.2.3.4", "port": "8080", "protocols": ["http"]},
            {"ip": "5.6.7.8", "port": "1080", "protocols": ["socks5"]},
            {"ip": "9.9.9.9", "port": "3128", "protocols": ["https"]},
        ]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GeonodeFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "9.9.9.9:3128" in result
        assert "5.6.7.8:1080" not in result


class TestKuaidailiFetcher(object):

    @patch("fetcher.sources.kuaidaili.WebRequest")
    @patch("fetcher.sources.kuaidaili.sleep", return_value=None)
    def test_fetch(self, mock_sleep, mock_wr):
        from fetcher.sources.kuaidaili import KuaidailiFetcher
        # kuaidaili 使用 proxy_list[1:] 跳过第一行
        html = _html_table([("IP", "Port"), ("1.2.3.4", "8080")])
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(KuaidailiFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestFreeVPNNodeFetcher(object):

    @patch("fetcher.sources.freevpnnode.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.freevpnnode import FreeVPNNodeFetcher
        html = _html_table([("1.2.3.4", "8080")])
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(
            tree=tree, text="1.2.3.4:8080 5.6.7.8:3128")
        result = list(FreeVPNNodeFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result


class TestScdnFetcher(object):

    @patch("fetcher.sources.scdn.WebRequest")
    def test_fetch_json(self, mock_wr):
        from fetcher.sources.scdn import ScdnFetcher
        json_data = {"data": [{"ip": "1.2.3.4", "port": "8080"}]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ScdnFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.scdn.WebRequest")
    def test_fetch_table_html(self, mock_wr):
        from fetcher.sources.scdn import ScdnFetcher
        table_html = '<tr><td>1.2.3.4</td><td>8080</td></tr>'
        json_data = {"table_html": table_html}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ScdnFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestZdayeFetcher(object):

    @patch("fetcher.sources.zdaye.WebRequest")
    @patch("fetcher.sources.zdaye.sleep", return_value=None)
    @patch("fetcher.sources.zdaye.datetime")
    def test_fetch_recent(self, mock_dt, mock_sleep, mock_wr):
        from fetcher.sources.zdaye import ZdayeFetcher
        from datetime import datetime as real_datetime
        # 模拟最新帖子时间在5分钟内
        mock_dt.now.return_value = real_datetime(2026, 5, 31, 12, 0, 0)
        mock_dt.strptime.return_value = real_datetime(2026, 5, 31, 11, 58, 0)

        index_tree = etree.HTML(
            '<span class="thread_time_info">2026/05/31 11:58:00</span>'
            '<h3 class="thread_title"><a href="/detail/1">test</a></h3>')
        detail_tree = etree.HTML(_html_table([("1.2.3.4", "8080")]))

        def side_effect(url, **kwargs):
            resp = MagicMock()
            if "free" in url:
                resp.tree = index_tree
            else:
                resp.tree = detail_tree
            return resp

        mock_wr.return_value.get.side_effect = side_effect
        result = list(ZdayeFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.zdaye.WebRequest")
    @patch("fetcher.sources.zdaye.datetime")
    def test_fetch_old_returns_empty(self, mock_dt, mock_wr):
        from fetcher.sources.zdaye import ZdayeFetcher
        from datetime import datetime as real_datetime
        # 模拟最新帖子时间超过5分钟
        mock_dt.now.return_value = real_datetime(2026, 5, 31, 12, 0, 0)
        mock_dt.strptime.return_value = real_datetime(2026, 5, 31, 10, 0, 0)

        index_tree = etree.HTML(
            '<span class="thread_time_info">2026/05/31 10:00:00</span>'
            '<h3 class="thread_title"><a href="/detail/1">test</a></h3>')
        mock_wr.return_value.get.return_value = _make_response(tree=index_tree)
        result = list(ZdayeFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.zdaye.WebRequest")
    @patch("fetcher.sources.zdaye.datetime")
    def test_fetch_old_cross_day_returns_empty(self, mock_dt, mock_wr):
        """跨天帖子应判定为过期（total_seconds 而非 seconds）"""
        from fetcher.sources.zdaye import ZdayeFetcher
        from datetime import datetime as real_datetime
        # 帖子是昨天 23:59，当前是今天 00:01（差 2 分钟，但跨天）
        mock_dt.now.return_value = real_datetime(2026, 5, 31, 0, 1, 0)
        mock_dt.strptime.return_value = real_datetime(2026, 5, 30, 23, 59, 0)

        index_tree = etree.HTML(
            '<span class="thread_time_info">2026/05/30 23:59:00</span>'
            '<h3 class="thread_title"><a href="/detail/1">test</a></h3>')
        mock_wr.return_value.get.return_value = _make_response(tree=index_tree)
        result = list(ZdayeFetcher().fetch())
        assert result == []


class TestIhuanFetcher(object):

    @patch("fetcher.sources.ihuan.requests")
    def test_fetch(self, mock_requests):
        from fetcher.sources.ihuan import IhuanFetcher
        html = (
            '<table class="table table-hover table-bordered">'
            '<tr><td>1.2.3.4</td><td>8080</td></tr>'
            '<tr><td>5.6.7.8</td><td>3128</td></tr>'
            '</table>'
        )
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = html
        # 第一次 get 获取 cookie，第二次 get 返回数据
        mock_session.get.return_value = mock_resp
        mock_requests.session.return_value = mock_session

        result = list(IhuanFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert mock_session.get.call_count == 2

    @patch("fetcher.sources.ihuan.requests")
    def test_fetch_empty_table_returns_empty(self, mock_requests):
        from fetcher.sources.ihuan import IhuanFetcher
        html = '<table class="table table-hover table-bordered"></table>'
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_session.get.return_value = mock_resp
        mock_requests.session.return_value = mock_session

        result = list(IhuanFetcher().fetch())
        assert result == []


class TestProxiFlyFetcher(object):

    @patch("fetcher.sources.proxifly.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.proxifly import ProxiFlyFetcher
        json_data = [
            {"proxy": "1.2.3.4:8080", "protocol": "http", "geolocation": {"country": "CN"}},
            {"proxy": "5.6.7.8:3128", "protocol": "http", "geolocation": {"country": "CN"}},
        ]
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ProxiFlyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxifly.WebRequest")
    def test_fetch_filters_non_cn(self, mock_wr):
        from fetcher.sources.proxifly import ProxiFlyFetcher
        json_data = [
            {"proxy": "1.2.3.4:8080", "protocol": "http", "geolocation": {"country": "CN"}},
            {"proxy": "9.9.9.9:8080", "protocol": "http", "geolocation": {"country": "US"}},
        ]
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ProxiFlyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "9.9.9.9:8080" not in result

    @patch("fetcher.sources.proxifly.WebRequest")
    def test_fetch_filters_non_http(self, mock_wr):
        from fetcher.sources.proxifly import ProxiFlyFetcher
        json_data = [
            {"proxy": "1.2.3.4:8080", "protocol": "http", "geolocation": {"country": "CN"}},
            {"proxy": "9.9.9.9:8080", "protocol": "https", "geolocation": {"country": "CN"}},
        ]
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ProxiFlyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "9.9.9.9:8080" not in result


class TestDaiLi66Fetcher(object):

    @patch("fetcher.sources.daili66.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.daili66 import DaiLi66Fetcher
        json_data = {
            "data": [
                {"ip": "1.2.3.4", "port": "8080"},
                {"ip": "5.6.7.8", "port": "3128"},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(DaiLi66Fetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.daili66.WebRequest")
    def test_fetch_empty_data_returns_empty(self, mock_wr):
        from fetcher.sources.daili66 import DaiLi66Fetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        result = list(DaiLi66Fetcher().fetch())
        assert result == []


class TestRoundProxiesFetcher(object):

    @patch("fetcher.sources.roundproxies.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.roundproxies import RoundProxiesFetcher
        json_data = {
            "data": [
                {"ip": "1.2.3.4", "port": "8080"},
                {"ip": "5.6.7.8", "port": "3128"},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(RoundProxiesFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.roundproxies.WebRequest")
    def test_fetch_empty_data_returns_empty(self, mock_wr):
        from fetcher.sources.roundproxies import RoundProxiesFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        result = list(RoundProxiesFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.roundproxies.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.roundproxies import RoundProxiesFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data=None)
        result = list(RoundProxiesFetcher().fetch())
        assert result == []


class TestOpenProxyListFetcher(object):

    @patch("fetcher.sources.openproxylist.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.openproxylist import OpenProxyListFetcher
        text = ("HTTP(S) Proxy list updated at 2026-10-12 14:00:03 GMT+7\n"
                "Website=https://openproxylist.com\n"
                "183.88.219.206:41564 374ms TH [Triple T Internet Company Limited]\n"
                "104.128.228.69:8118 139ms US [HostUS Solutions LLC]\n")
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(OpenProxyListFetcher().fetch())
        assert "183.88.219.206:41564" in result
        assert "104.128.228.69:8118" in result

    @patch("fetcher.sources.openproxylist.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.openproxylist import OpenProxyListFetcher
        text = "1.2.3.4:8080\n1.2.3.4:8080\n5.6.7.8:3128\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(OpenProxyListFetcher().fetch())
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.openproxylist.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.openproxylist import OpenProxyListFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(OpenProxyListFetcher().fetch()) == []


class TestScdnTextFetcher(object):

    @patch("fetcher.sources.scdntext.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.scdntext import ScdnTextFetcher
        text = "210.61.216.63:60808\n154.64.211.145:999\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ScdnTextFetcher().fetch())
        assert result == ["210.61.216.63:60808", "154.64.211.145:999"]

    @patch("fetcher.sources.scdntext.WebRequest")
    def test_fetch_limit_applied(self, mock_wr):
        """条数超过limit时随机采样到limit条"""
        from fetcher.sources.scdntext import ScdnTextFetcher
        text = "\n".join("10.0.%d.%d:8080" % (i // 250, i % 250 + 1) for i in range(400))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ScdnTextFetcher().fetch())
        assert len(result) == ScdnTextFetcher.limit == 300

    @patch("fetcher.sources.scdntext.WebRequest")
    def test_fetch_limit_zero_keeps_all(self, mock_wr):
        """limit=0 -> 不限制条数"""
        from fetcher.sources.scdntext import ScdnTextFetcher
        text = "\n".join("10.0.%d.%d:8080" % (i // 250, i % 250 + 1) for i in range(400))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        with patch.object(ScdnTextFetcher, "limit", 0):
            result = list(ScdnTextFetcher().fetch())
        assert len(result) == 400

    @patch("fetcher.sources.scdntext.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.scdntext import ScdnTextFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ScdnTextFetcher().fetch()) == []


class TestMonosansFetcher(object):

    @patch("fetcher.sources.monosans.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.monosans import MonosansFetcher
        text = "1.2.3.4:8080\n5.6.7.8:3128\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(MonosansFetcher().fetch())
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.monosans.WebRequest")
    def test_fetch_limit_applied(self, mock_wr):
        from fetcher.sources.monosans import MonosansFetcher
        text = "\n".join("10.0.%d.%d:8080" % (i // 250, i % 250 + 1) for i in range(400))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(MonosansFetcher().fetch())
        assert len(result) == MonosansFetcher.limit == 300

    @patch("fetcher.sources.monosans.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.monosans import MonosansFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(MonosansFetcher().fetch()) == []


class TestTheSpeedXFetcher(object):

    @patch("fetcher.sources.thespeedx.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.thespeedx import TheSpeedXFetcher
        text = "1.2.3.4:8080\n5.6.7.8:3128\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(TheSpeedXFetcher().fetch())
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.thespeedx.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.thespeedx import TheSpeedXFetcher
        text = "1.2.3.4:8080\n1.2.3.4:8080\n5.6.7.8:3128\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(TheSpeedXFetcher().fetch())
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.thespeedx.WebRequest")
    def test_fetch_limit_applied(self, mock_wr):
        from fetcher.sources.thespeedx import TheSpeedXFetcher
        text = "\n".join("10.0.%d.%d:8080" % (i // 250, i % 250 + 1) for i in range(500))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(TheSpeedXFetcher().fetch())
        assert len(result) == TheSpeedXFetcher.limit == 200


class TestProxyScrapeFetcher(object):

    @patch("fetcher.sources.proxyscrape.WebRequest")
    def test_fetch_merges_both_protocols(self, mock_wr):
        """http与https两个接口的结果合并去重"""
        from fetcher.sources.proxyscrape import ProxyScrapeFetcher
        http_resp = _make_response(text="1.2.3.4:8080\n5.6.7.8:8080\n")
        https_resp = _make_response(text="5.6.7.8:8080\n9.9.9.9:3128\n")
        mock_wr.return_value.get.side_effect = [http_resp, https_resp]

        result = list(ProxyScrapeFetcher().fetch())

        assert mock_wr.return_value.get.call_count == len(ProxyScrapeFetcher.listUrls) == 2
        assert result == ["1.2.3.4:8080", "5.6.7.8:8080", "9.9.9.9:3128"]

    @patch("fetcher.sources.proxyscrape.WebRequest")
    def test_fetch_limit_applied(self, mock_wr):
        from fetcher.sources.proxyscrape import ProxyScrapeFetcher
        text = "\n".join("10.0.%d.%d:8080" % (i // 250, i % 250 + 1) for i in range(300))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxyScrapeFetcher().fetch())
        assert len(result) == ProxyScrapeFetcher.limit == 200

    @patch("fetcher.sources.proxyscrape.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.proxyscrape import ProxyScrapeFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ProxyScrapeFetcher().fetch()) == []


class TestSpysMeFetcher(object):

    @patch("fetcher.sources.spysme.WebRequest")
    def test_fetch_with_country_suffix(self, mock_wr):
        """行格式为 ip:port 国家码-匿名度"""
        from fetcher.sources.spysme import SpysMeFetcher
        text = ("1.2.3.4:8080 TH-H\n"
                "5.6.7.8:3128 US-N\n")
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(SpysMeFetcher().fetch())
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.spysme.WebRequest")
    def test_fetch_limit_applied(self, mock_wr):
        from fetcher.sources.spysme import SpysMeFetcher
        text = "\n".join("10.0.%d.%d:8080" % (i // 250, i % 250 + 1) for i in range(400))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(SpysMeFetcher().fetch())
        assert len(result) == SpysMeFetcher.limit == 200

    @patch("fetcher.sources.spysme.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.spysme import SpysMeFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(SpysMeFetcher().fetch()) == []


class TestFreeProxyListFetcher(object):

    @patch("fetcher.sources.freeproxylist.WebRequest")
    def test_fetch_parses_textarea_content(self, mock_wr):
        """页面内只读文本框中的纯文本列表"""
        from fetcher.sources.freeproxylist import FreeProxyListFetcher
        html = ('<textarea class="form-control" readonly="readonly">'
                'Free proxies from free-proxy-list.net\n'
                '1.2.3.4:8080\n5.6.7.8:3128</textarea>')
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(FreeProxyListFetcher().fetch())
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.freeproxylist.WebRequest")
    def test_fetch_merges_pages_dedup(self, mock_wr):
        from fetcher.sources.freeproxylist import FreeProxyListFetcher
        page1 = _make_response(text="1.2.3.4:8080\n5.6.7.8:3128\n")
        page2 = _make_response(text="5.6.7.8:3128\n9.9.9.9:8080\n")
        mock_wr.return_value.get.side_effect = [page1, page2]

        result = list(FreeProxyListFetcher().fetch())

        assert mock_wr.return_value.get.call_count == len(FreeProxyListFetcher.listUrls)
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128", "9.9.9.9:8080"]

    @patch("fetcher.sources.freeproxylist.WebRequest")
    def test_fetch_limit_applied(self, mock_wr):
        from fetcher.sources.freeproxylist import FreeProxyListFetcher
        text = "\n".join("10.0.%d.%d:8080" % (i // 250, i % 250 + 1) for i in range(400))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(FreeProxyListFetcher().fetch())
        assert len(result) == FreeProxyListFetcher.limit == 200

    @patch("fetcher.sources.freeproxylist.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.freeproxylist import FreeProxyListFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(FreeProxyListFetcher().fetch()) == []
