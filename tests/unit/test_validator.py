# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testValidator.py
   Description :   formatValidator正则测试
   Author :        JHao
   date：          2026/5/28
-------------------------------------------------
   Change Activity:
                   2026/05/28:
                   2026/10/12: 同步随机二选一可用性校验
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import pytest
from unittest.mock import patch, MagicMock

# 直接导入校验函数，不导入整个 validator 模块（避免模块级副作用）
from helper.validator import (IP_REGEX, formatValidator, verifyByHttpbinUuid,
                              verifyByBrightDataText, randomHttpValidator,
                              httpsTimeOutValidator, customValidatorExample)


class TestIPRegex:

    @pytest.mark.parametrize("proxy", [
        "1.2.3.4:8080",
        "192.168.1.1:3128",
        "10.0.0.1:80",
        "255.255.255.255:65535",
        "0.0.0.0:1",
        "1.2.3.4:99999",   # regex 不校验端口范围
        "999.1.1.1:80",    # regex 不校验 IP 范围
        "user:pass@1.2.3.4:8080",
        "admin:secret@192.168.1.1:443",
    ])
    def test_valid_proxy_format(self, proxy):
        assert IP_REGEX.fullmatch(proxy) is not None, f"应匹配: {proxy}"

    @pytest.mark.parametrize("proxy", [
        "",
        "abc",
        "1.2.3.4",
        "1.2.3.4:",
        ":8080",
        "1.2.3.4:abc",
        "1.2.3.4:8080:extra",
        "host:8080",
    ])
    def test_invalid_proxy_format(self, proxy):
        assert IP_REGEX.fullmatch(proxy) is None, f"不应匹配: {proxy}"


class TestFormatValidator:

    @pytest.mark.parametrize("proxy", [
        "1.2.3.4:8080",
        "192.168.1.1:3128",
        "user:pass@10.0.0.1:80",
    ])
    def test_valid_returns_true(self, proxy):
        assert formatValidator(proxy) is True

    @pytest.mark.parametrize("proxy", [
        "",
        "abc",
        "1.2.3.4",
    ])
    def test_invalid_returns_false(self, proxy):
        assert formatValidator(proxy) is False


class TestVerifyByHttpbinUuid:
    """verifyByHttpbinUuid 测试（方式1）"""

    @patch("helper.validator.get")
    def test_returns_true_when_uuid_present(self, mock_get):
        """status_code=200 且 JSON 含 uuid -> True"""
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"uuid": "6f1a0b7c-6f5e-4a2b-9c3d-1e2f3a4b5c6d"}
        mock_get.return_value = resp
        assert verifyByHttpbinUuid("1.2.3.4:8080") is True

    @patch("helper.validator.get")
    def test_returns_false_when_uuid_missing(self, mock_get):
        """status_code=200 但 JSON 无 uuid -> False"""
        resp = MagicMock(status_code=200)
        resp.json.return_value = {}
        mock_get.return_value = resp
        assert verifyByHttpbinUuid("1.2.3.4:8080") is False

    @patch("helper.validator.get")
    def test_returns_false_when_json_invalid(self, mock_get):
        """status_code=200 但响应非 JSON -> False"""
        resp = MagicMock(status_code=200)
        resp.json.side_effect = ValueError("No JSON object could be decoded")
        mock_get.return_value = resp
        assert verifyByHttpbinUuid("1.2.3.4:8080") is False

    @patch("helper.validator.get")
    def test_returns_false_on_non_200(self, mock_get):
        """status_code=502 -> False"""
        mock_get.return_value = MagicMock(status_code=502)
        assert verifyByHttpbinUuid("1.2.3.4:8080") is False

    @patch("helper.validator.get")
    def test_returns_false_on_exception(self, mock_get):
        """get() raise Timeout -> False"""
        mock_get.side_effect = TimeoutError("connection timed out")
        assert verifyByHttpbinUuid("1.2.3.4:8080") is False


class TestVerifyByBrightDataText:
    """verifyByBrightDataText 测试（方式2）"""

    @patch("helper.validator.get")
    def test_returns_true_when_keyword_present(self, mock_get):
        """status_code=200 且文本含关键字 -> True"""
        mock_get.return_value = MagicMock(status_code=200, text="Welcome to Bright Data!\n")
        assert verifyByBrightDataText("1.2.3.4:8080") is True

    @patch("helper.validator.get")
    def test_returns_false_when_keyword_missing(self, mock_get):
        """status_code=200 但文本不含关键字 -> False"""
        mock_get.return_value = MagicMock(status_code=200, text="Access denied")
        assert verifyByBrightDataText("1.2.3.4:8080") is False

    @patch("helper.validator.get")
    def test_returns_false_on_non_200(self, mock_get):
        """status_code=403 -> False"""
        mock_get.return_value = MagicMock(status_code=403, text="Welcome to Bright Data")
        assert verifyByBrightDataText("1.2.3.4:8080") is False

    @patch("helper.validator.get")
    def test_returns_false_on_exception(self, mock_get):
        """get() raise Timeout -> False"""
        mock_get.side_effect = TimeoutError("connection timed out")
        assert verifyByBrightDataText("1.2.3.4:8080") is False


class TestRandomHttpValidator:
    """randomHttpValidator 随机分派测试"""

    @patch("helper.validator.random.choice")
    def test_dispatches_to_picked_validator(self, mock_choice):
        """随机选中的校验函数被调用一次"""
        picked = MagicMock(return_value=True)
        mock_choice.return_value = picked

        assert randomHttpValidator("1.2.3.4:8080") is True
        picked.assert_called_once_with("1.2.3.4:8080")

    @patch("helper.validator.random.choice")
    def test_candidates_are_two_validators(self, mock_choice):
        """候选为两种校验方式，任一种返回 False 即 False"""
        mock_choice.return_value = MagicMock(return_value=False)

        assert randomHttpValidator("1.2.3.4:8080") is False
        candidates = mock_choice.call_args[0][0]
        assert len(candidates) == 2
        assert candidates[0] is verifyByHttpbinUuid
        assert candidates[1] is verifyByBrightDataText


class TestHttpsTimeOutValidator:
    """httpsTimeOutValidator 测试"""

    @patch("helper.validator.head")
    def test_returns_true_on_200(self, mock_head):
        """status_code=200 -> True"""
        mock_head.return_value = MagicMock(status_code=200)
        assert httpsTimeOutValidator("1.2.3.4:8080") is True
        # 验证 verify=False 被传递
        call_kwargs = mock_head.call_args
        assert call_kwargs[1]["verify"] is False

    @patch("helper.validator.head")
    def test_returns_false_on_non_200(self, mock_head):
        """status_code=502 -> False"""
        mock_head.return_value = MagicMock(status_code=502)
        assert httpsTimeOutValidator("1.2.3.4:8080") is False

    @patch("helper.validator.head")
    def test_returns_false_on_exception(self, mock_head):
        """head() raise Timeout -> False"""
        mock_head.side_effect = TimeoutError("connection timed out")
        assert httpsTimeOutValidator("1.2.3.4:8080") is False


class TestCustomValidatorExample:
    """customValidatorExample 测试"""

    def test_always_returns_true(self):
        """customValidatorExample 始终返回 True"""
        assert customValidatorExample("1.2.3.4:8080") is True
