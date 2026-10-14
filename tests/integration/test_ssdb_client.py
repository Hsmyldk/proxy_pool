# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testSsdbClient.py
   Description :   SsdbClient集成测试
   Author :        JHao
   date：          2026/5/28
-------------------------------------------------
   Change Activity:
                   2026/05/28:
-------------------------------------------------
"""
__author__ = 'JHao'

import json
import pytest
from unittest.mock import patch
from db.ssdbClient import SsdbClient
from helper.proxy import Proxy


@pytest.fixture
def ssdb_client(fake_redis):
    """SsdbClient 实例，内部连接替换为 fakeredis"""
    with patch("db.ssdbClient.BlockingConnectionPool"):
        with patch("db.ssdbClient.Redis", return_value=fake_redis):
            client = SsdbClient(host="localhost", port=8888,
                                username=None, password=None)
            client.changeTable("test_proxy")
            return client


def _make_proxy(proxy_str, https=False, source="test"):
    return Proxy(proxy_str, source=https and "https_test" or "http_test",
                 https=https)


class TestSsdbPutGet:

    def test_put_and_get(self, ssdb_client):
        proxy = _make_proxy("1.2.3.4:8080")
        ssdb_client.put(proxy)
        result = ssdb_client.get(https=False)
        assert result is not None
        data = json.loads(result)
        assert data["proxy"] == "1.2.3.4:8080"

    def test_get_https(self, ssdb_client):
        proxy = _make_proxy("5.6.7.8:443", https=True)
        ssdb_client.put(proxy)
        result = ssdb_client.get(https=True)
        assert result is not None
        data = json.loads(result)
        assert data["https"] is True

    def test_get_https_excludes_http(self, ssdb_client):
        proxy = _make_proxy("1.2.3.4:8080", https=False)
        ssdb_client.put(proxy)
        result = ssdb_client.get(https=True)
        assert result is None

    def test_get_empty_returns_none(self, ssdb_client):
        result = ssdb_client.get(https=False)
        assert result is None


class TestSsdbGetFilter:
    """region / anonymous 筛选测试"""

    @staticmethod
    def _proxy(proxy_str, region="", anonymous="", https=False):
        p = Proxy(proxy_str, source="test", https=https)
        p.region = region
        p.anonymous = anonymous
        return p

    def test_get_by_region(self, ssdb_client):
        ssdb_client.put(self._proxy("1.2.3.4:8080", region="广东省深圳市"))
        ssdb_client.put(self._proxy("5.6.7.8:8080", region="美国"))

        result = ssdb_client.get(https=False, region="广东")
        assert result is not None
        assert json.loads(result)["region"] == "广东省深圳市"

    def test_get_by_region_no_match(self, ssdb_client):
        ssdb_client.put(self._proxy("1.2.3.4:8080", region="美国"))
        assert ssdb_client.get(https=False, region="广东") is None

    def test_get_by_anonymous(self, ssdb_client):
        ssdb_client.put(self._proxy("1.2.3.4:8080", anonymous=0))
        ssdb_client.put(self._proxy("5.6.7.8:8080", anonymous=2))

        result = ssdb_client.get(https=False, anonymous=2)
        assert result is not None
        assert json.loads(result)["anonymous"] == 2

    def test_get_combined_filters(self, ssdb_client):
        ssdb_client.put(self._proxy("1.2.3.4:8080", region="广东省深圳市", anonymous=2))
        ssdb_client.put(self._proxy("5.6.7.8:8080", region="广东省深圳市", anonymous=0))

        result = ssdb_client.get(https=False, region="广东", anonymous=2)
        assert result is not None
        assert json.loads(result)["anonymous"] == 2

    def test_get_filter_combined_with_https(self, ssdb_client):
        ssdb_client.put(self._proxy("1.2.3.4:8080", region="广东", https=False))
        ssdb_client.put(self._proxy("5.6.7.8:443", region="广东", https=True))

        result = ssdb_client.get(https=True, region="广东")
        assert result is not None
        data = json.loads(result)
        assert data["https"] is True
        assert data["proxy"] == "5.6.7.8:443"


class TestSsdbExists:

    def test_exists_true(self, ssdb_client):
        proxy = _make_proxy("1.2.3.4:8080")
        ssdb_client.put(proxy)
        assert ssdb_client.exists("1.2.3.4:8080") is True

    def test_exists_false(self, ssdb_client):
        assert ssdb_client.exists("9.9.9.9:9999") is False


class TestSsdbDelete:

    def test_delete(self, ssdb_client):
        proxy = _make_proxy("1.2.3.4:8080")
        ssdb_client.put(proxy)
        ssdb_client.delete("1.2.3.4:8080")
        assert ssdb_client.exists("1.2.3.4:8080") is False


class TestSsdbPop:

    def test_pop_removes_proxy(self, ssdb_client):
        proxy = _make_proxy("1.2.3.4:8080")
        ssdb_client.put(proxy)
        popped = ssdb_client.pop(https=False)
        assert popped is not None
        assert ssdb_client.exists("1.2.3.4:8080") is False

    def test_pop_empty_returns_none(self, ssdb_client):
        result = ssdb_client.pop(https=False)
        assert result is None


class TestSsdbGetAll:

    def test_get_all(self, ssdb_client):
        ssdb_client.put(_make_proxy("1.2.3.4:8080"))
        ssdb_client.put(_make_proxy("5.6.7.8:443", https=True))
        all_proxies = list(ssdb_client.getAll(https=False))
        assert len(all_proxies) == 2

    def test_get_all_https_filter(self, ssdb_client):
        ssdb_client.put(_make_proxy("1.2.3.4:8080", https=False))
        ssdb_client.put(_make_proxy("5.6.7.8:443", https=True))
        https_proxies = list(ssdb_client.getAll(https=True))
        assert len(https_proxies) == 1


class TestSsdbGetCount:

    def test_get_count(self, ssdb_client):
        ssdb_client.put(_make_proxy("1.2.3.4:8080", https=False))
        ssdb_client.put(_make_proxy("5.6.7.8:443", https=True))
        count = ssdb_client.getCount()
        assert count["total"] == 2
        assert count["https"] == 1

    def test_get_count_empty(self, ssdb_client):
        count = ssdb_client.getCount()
        assert count["total"] == 0
        assert count["https"] == 0


class TestSsdbClear:

    def test_clear(self, ssdb_client):
        ssdb_client.put(_make_proxy("1.2.3.4:8080"))
        ssdb_client.put(_make_proxy("5.6.7.8:443"))
        ssdb_client.clear()
        count = ssdb_client.getCount()
        assert count["total"] == 0


class TestSsdbChangeTable:

    def test_change_table_isolation(self, ssdb_client):
        ssdb_client.put(_make_proxy("1.2.3.4:8080"))
        ssdb_client.changeTable("other_table")
        assert ssdb_client.getCount()["total"] == 0
        ssdb_client.changeTable("test_proxy")
        assert ssdb_client.getCount()["total"] == 1