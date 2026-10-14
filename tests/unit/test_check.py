# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_check.py
   Description :   helper/check.py 单元测试
   Author :        JHao
   date：          2026/6/15
-------------------------------------------------
     Change Activity:
                     2026/06/15:
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime

from helper.proxy import Proxy
from helper.check import DoValidator, _ThreadChecker


class TestDoValidator:
    """DoValidator.validator 测试"""

    @patch("helper.check.DoValidator.anonymousValidator", return_value=2)
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_http_pass_https_pass(self, mock_pv_cls, mock_conf_cls, mock_anon):
        """HTTP 通过 + HTTPS 通过 -> https=True, fail_count 不变"""
        mock_pv = MagicMock()
        mock_pv.http_validator = [MagicMock(return_value=True)]
        mock_pv.https_validator = [MagicMock(return_value=True)]
        mock_pv_cls.http_validator = mock_pv.http_validator
        mock_pv_cls.https_validator = mock_pv.https_validator

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False
        mock_conf_cls.return_value = mock_conf

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.fail_count = 0

        # Patch DoValidator.conf at class level
        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.https is True
        assert result.last_status is True
        assert result.check_count == 1
        assert result.fail_count == 0
        assert result.anonymous == 2
        mock_anon.assert_called_once_with("1.2.3.4:8080", True)

    @patch("helper.check.DoValidator.anonymousValidator", return_value=1)
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_http_pass_https_fail(self, mock_pv_cls, mock_conf_cls, mock_anon):
        """HTTP 通过 + HTTPS 失败 -> https=False"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=False)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.https is False
        assert result.last_status is True
        # 匿名度检测使用刚判定的 https 值
        mock_anon.assert_called_once_with("1.2.3.4:8080", False)

    @patch("helper.check.DoValidator.anonymousValidator")
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_http_fail(self, mock_pv_cls, mock_conf_cls, mock_anon):
        """HTTP 失败 -> fail_count += 1, last_status=False, 不检测匿名度"""
        mock_pv_cls.http_validator = [MagicMock(return_value=False)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.fail_count = 0

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.last_status is False
        assert result.fail_count == 1
        mock_anon.assert_not_called()

    @patch("helper.check.DoValidator.anonymousValidator", return_value=2)
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_fail_count_decrement(self, mock_pv_cls, mock_conf_cls, mock_anon):
        """HTTP 通过 + fail_count > 0 -> fail_count -= 1"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.fail_count = 3

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.fail_count == 2

    @patch("helper.check.DoValidator.anonymousValidator", return_value=2)
    @patch("helper.check.DoValidator.region_get", return_value="广东省深圳市")
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_sets_region(self, mock_pv_cls, mock_conf_cls, mock_region, mock_anon):
        """proxyRegion=True -> region_get 被调用并写入 region"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = True

        proxy = Proxy("1.2.3.4:8080", source="test")

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.region == "广东省深圳市"
        mock_region.assert_called_once_with("1.2.3.4:8080")

    @patch("helper.check.DoValidator.anonymousValidator", return_value=2)
    @patch("helper.check.DoValidator.region_get")
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_skips_region_when_disabled(self, mock_pv_cls, mock_conf_cls,
                                                  mock_region, mock_anon):
        """proxyRegion=False -> 不调用 region_get"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")

        with patch.object(DoValidator, "conf", mock_conf):
            DoValidator.validator(proxy, "use")

        mock_region.assert_not_called()

    @patch("helper.check.DoValidator.anonymousValidator", return_value=2)
    @patch("helper.check.DoValidator.region_get")
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_keeps_existing_region(self, mock_pv_cls, mock_conf_cls,
                                             mock_region, mock_anon):
        """region 已有有效值 -> 不重复查询"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = True

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.region = "广东省深圳市"

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.region == "广东省深圳市"
        mock_region.assert_not_called()

    @patch("helper.check.DoValidator.anonymousValidator", return_value=2)
    @patch("helper.check.DoValidator.region_get", return_value="广东省深圳市")
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_refreshes_failed_region(self, mock_pv_cls, mock_conf_cls,
                                               mock_region, mock_anon):
        """region 为失败值 -> 重新查询"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = True

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.region = "未知或请求失败"

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.region == "广东省深圳市"
        mock_region.assert_called_once_with("1.2.3.4:8080")


class TestRegionGet:
    """DoValidator.region_get 测试"""

    @patch("helper.check.requests.get")
    def test_success_returns_address(self, mock_get):
        """CSDN 正常返回 -> 中文地址, 不再回退"""
        resp = MagicMock()
        resp.text = '{"data": {"address": "广东省深圳市"}}'
        mock_get.return_value = resp

        result = DoValidator.region_get("1.2.3.4:8080")
        assert result == "广东省深圳市"
        assert mock_get.call_count == 1

    @patch("helper.check.requests.get")
    def test_fallback_to_ipapi_when_csdn_forbidden(self, mock_get):
        """CSDN 403(非JSON) -> 回退 ip-api 并返回中文地区"""
        csdn = MagicMock(text='<html>403 Forbidden</html>')
        ipapi = MagicMock(
            text='{"status": "success", "country": "美国", "regionName": "弗吉尼亚州"}')
        mock_get.side_effect = [csdn, ipapi]

        result = DoValidator.region_get("8.8.8.8:8080")
        assert result == "美国弗吉尼亚州"
        assert mock_get.call_count == 2

    @patch("helper.check.requests.get")
    def test_ipapi_quota_exceeded_returns_unknown(self, mock_get):
        """ip-api 返回 status=fail(限流等) -> '未知或请求失败'"""
        csdn = MagicMock(text='<html>403</html>')
        ipapi = MagicMock(text='{"status": "fail", "message": "quota exceeded"}')
        mock_get.side_effect = [csdn, ipapi]

        result = DoValidator.region_get("1.2.3.4:8080")
        assert result == "未知或请求失败"

    @patch("helper.check.requests.get")
    def test_all_sources_failed_returns_unknown(self, mock_get):
        """所有数据源异常 -> '未知或请求失败'"""
        mock_get.side_effect = Exception("timeout")

        result = DoValidator.region_get("1.2.3.4:8080")
        assert result == "未知或请求失败"

    @patch("helper.check.requests.get")
    def test_auth_proxy_queries_ip_only(self, mock_get):
        """user:pass@ip:port -> 只查询IP部分"""
        resp = MagicMock()
        resp.text = '{"data": {"address": "美国"}}'
        mock_get.return_value = resp

        DoValidator.region_get("user:pass@1.2.3.4:8080")
        assert mock_get.call_args[1]["params"] == {"ip": "1.2.3.4"}


class TestAnonymousValidator:
    """DoValidator.anonymousValidator 测试"""

    @patch("helper.check.requests.get")
    def test_transparent_when_origin_has_comma(self, mock_get):
        """origin 含逗号(暴露真实IP链) -> 0"""
        resp = MagicMock()
        resp.text = '{"origin": "1.1.1.1, 2.2.2.2", "headers": {}}'
        mock_get.return_value = resp

        assert DoValidator.anonymousValidator("1.2.3.4:8080", False) == 0

    @patch("helper.check.requests.get")
    def test_anonymous_when_proxy_connection_header(self, mock_get):
        """带 Proxy-Connection 头(暴露代理身份) -> 1"""
        resp = MagicMock()
        resp.text = '{"origin": "1.1.1.1", "headers": {"Proxy-Connection": "keep-alive"}}'
        mock_get.return_value = resp

        assert DoValidator.anonymousValidator("1.2.3.4:8080", False) == 1

    @patch("helper.check.requests.get")
    def test_elite_when_clean(self, mock_get):
        """既无多IP也无代理头 -> 2"""
        resp = MagicMock()
        resp.text = '{"origin": "1.1.1.1", "headers": {"Host": "httpbin.org"}}'
        mock_get.return_value = resp

        assert DoValidator.anonymousValidator("1.2.3.4:8080", False) == 2

    @patch("helper.check.requests.get")
    def test_https_uses_https_target(self, mock_get):
        """https=True -> 请求 https 目标并使用 https 代理"""
        resp = MagicMock()
        resp.text = '{"origin": "1.1.1.1", "headers": {}}'
        mock_get.return_value = resp

        DoValidator.anonymousValidator("1.2.3.4:8080", True)

        args, kwargs = mock_get.call_args
        assert args[0] == 'https://httpbin.org/get'
        assert kwargs["proxies"] == {'https': 'https://1.2.3.4:8080'}

    @patch("helper.check.requests.get")
    def test_exception_returns_minus_one(self, mock_get):
        """请求异常 -> -1"""
        mock_get.side_effect = Exception("timeout")

        assert DoValidator.anonymousValidator("1.2.3.4:8080", False) == -1

    @patch("helper.check.requests.get")
    def test_invalid_json_returns_minus_one(self, mock_get):
        """响应非JSON -> -1"""
        resp = MagicMock()
        resp.text = 'not a json'
        mock_get.return_value = resp

        assert DoValidator.anonymousValidator("1.2.3.4:8080", False) == -1


def _make_checker(work_type, proxy_handler, conf=None):
    """构造手动注入依赖的 _ThreadChecker（绕过 Thread.__init__）"""
    checker = _ThreadChecker.__new__(_ThreadChecker)
    # 手动初始化 Thread 所需的状态
    checker._initialized = True
    checker._name = "test_thread"
    checker._target = None
    checker._args = ()
    checker._kwargs = {}
    checker._daemonic = False
    checker._ident = None
    checker._tstate_lock = None
    checker._started = MagicMock()
    checker._is_stopped = False
    checker._block = MagicMock()
    checker._waiters = []
    checker._stderr = None
    # 注入依赖
    checker.proxy_handler = proxy_handler
    checker.log = MagicMock()
    checker.work_type = work_type
    checker.conf = conf or MagicMock()
    return checker


class TestThreadCheckerIfRaw:
    """_ThreadChecker.__ifRaw 测试"""

    def test_ifraw_new_proxy_gets_put(self):
        """last_status=True, exists=False -> put"""
        mock_ph = MagicMock()
        mock_ph.exists.return_value = False

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = True

        checker = _make_checker("raw", mock_ph)
        checker._ThreadChecker__ifRaw(proxy)
        mock_ph.put.assert_called_once_with(proxy)

    def test_ifraw_existing_proxy_skipped(self):
        """last_status=True, exists=True -> 不 put"""
        mock_ph = MagicMock()
        mock_ph.exists.return_value = True

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = True

        checker = _make_checker("raw", mock_ph)
        checker._ThreadChecker__ifRaw(proxy)
        mock_ph.put.assert_not_called()

    def test_ifraw_failed_proxy_not_put(self):
        """last_status=False -> 不 put"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False

        checker = _make_checker("raw", mock_ph)
        checker._ThreadChecker__ifRaw(proxy)
        mock_ph.put.assert_not_called()


class TestThreadCheckerIfUse:
    """_ThreadChecker.__ifUse 测试"""

    def test_ifuse_pass_gets_put(self):
        """last_status=True -> put"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = True

        checker = _make_checker("use", mock_ph)
        checker._ThreadChecker__ifUse(proxy)
        mock_ph.put.assert_called_once_with(proxy)

    def test_ifuse_fail_exceeds_max_deleted(self):
        """fail_count > maxFailCount -> delete"""
        mock_ph = MagicMock()
        mock_conf = MagicMock()
        mock_conf.maxFailCount = 3

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False
        proxy.fail_count = 5

        checker = _make_checker("use", mock_ph, mock_conf)
        checker._ThreadChecker__ifUse(proxy)
        mock_ph.delete.assert_called_once_with(proxy)
        mock_ph.put.assert_not_called()

    def test_ifuse_fail_below_max_kept(self):
        """fail_count <= maxFailCount -> put"""
        mock_ph = MagicMock()
        mock_conf = MagicMock()
        mock_conf.maxFailCount = 3

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False
        proxy.fail_count = 2

        checker = _make_checker("use", mock_ph, mock_conf)
        checker._ThreadChecker__ifUse(proxy)
        mock_ph.put.assert_called_once_with(proxy)
        mock_ph.delete.assert_not_called()
