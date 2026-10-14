# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_scheduler.py
   Description :   helper/scheduler.py 单元测试
   Author :        JHao
   date：          2026/6/15
-------------------------------------------------
     Change Activity:
                     2026/06/15:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
import pytest
from unittest.mock import patch, MagicMock


# apscheduler 依赖 pkg_resources，在 tox/uv 环境中可能缺失
# 在 import 前 mock 掉，避免 collection 阶段报错
_apscheduler_mock = MagicMock()
sys.modules.setdefault("apscheduler", _apscheduler_mock)
sys.modules.setdefault("apscheduler.schedulers", _apscheduler_mock.schedulers)
sys.modules.setdefault("apscheduler.schedulers.blocking", _apscheduler_mock.schedulers.blocking)
sys.modules.setdefault("apscheduler.executors", _apscheduler_mock.executors)
sys.modules.setdefault("apscheduler.executors.pool", _apscheduler_mock.executors.pool)

import helper.scheduler as scheduler_mod


def _get_attr(name):
    """获取模块中双下划线开头的属性（绕过类内 name mangling）"""
    return getattr(scheduler_mod, name)


class TestRunProxyFetch:

    @patch("helper.scheduler.Checker")
    @patch("helper.scheduler.Fetcher")
    def test_fetcher_yields_go_to_queue(self, mock_fetcher_cls, mock_checker):
        """Fetcher yield 的代理放入 queue，传给 Checker"""
        mock_proxy = MagicMock()
        mock_fetcher = MagicMock()
        mock_fetcher.run.return_value = iter([mock_proxy])
        mock_fetcher_cls.return_value = mock_fetcher

        _get_attr("__runProxyFetch")()

        mock_fetcher_cls.assert_called_once()
        mock_checker.assert_called_once()
        call_args = mock_checker.call_args
        assert call_args[0][0] == "raw"


class TestConcurrencyGuard:
    """上一轮未跑完时跳过本次触发（防任务堆积）"""

    @patch("helper.scheduler.Fetcher")
    def test_fetch_skipped_when_previous_round_running(self, mock_fetcher_cls):
        """采集锁被占用 -> 直接跳过, 不创建 Fetcher"""
        assert scheduler_mod._fetch_lock.acquire(blocking=False)
        try:
            _get_attr("__runProxyFetch")()
            mock_fetcher_cls.assert_not_called()
        finally:
            scheduler_mod._fetch_lock.release()

    @patch("helper.scheduler.ProxyHandler")
    def test_check_skipped_when_previous_round_running(self, mock_ph_cls):
        """复检锁被占用 -> 直接跳过, 不读代理池"""
        assert scheduler_mod._check_lock.acquire(blocking=False)
        try:
            _get_attr("__runProxyCheck")()
            mock_ph_cls.assert_not_called()
        finally:
            scheduler_mod._check_lock.release()

    @patch("helper.scheduler.Checker")
    @patch("helper.scheduler.Fetcher")
    def test_fetch_lock_released_after_success(self, mock_fetcher_cls, mock_checker):
        """正常跑完后必须释放锁, 否则后续轮次会被永久跳过"""
        mock_fetcher = MagicMock()
        mock_fetcher.run.return_value = iter([])
        mock_fetcher_cls.return_value = mock_fetcher

        _get_attr("__runProxyFetch")()

        assert scheduler_mod._fetch_lock.acquire(blocking=False) is True
        scheduler_mod._fetch_lock.release()

    @patch("helper.scheduler.Fetcher")
    def test_fetch_lock_released_on_exception(self, mock_fetcher_cls):
        """采集过程抛异常也要释放锁"""
        mock_fetcher_cls.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError):
            _get_attr("__runProxyFetch")()

        assert scheduler_mod._fetch_lock.acquire(blocking=False) is True
        scheduler_mod._fetch_lock.release()


class TestRunProxyCheck:

    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.Checker")
    @patch("helper.scheduler.ProxyHandler")
    def test_triggers_fetch_when_pool_low(self, mock_ph_cls, mock_checker, mock_fetch):
        """count < poolSizeMin -> 触发 __runProxyFetch"""
        mock_ph = MagicMock()
        mock_ph.db.getCount.return_value = {"total": 5}
        mock_ph.conf.poolSizeMin = 20
        mock_ph.getAll.return_value = []
        mock_ph_cls.return_value = mock_ph

        _get_attr("__runProxyCheck")()

        mock_fetch.assert_called_once()

    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.Checker")
    @patch("helper.scheduler.ProxyHandler")
    def test_skips_fetch_when_pool_sufficient(self, mock_ph_cls, mock_checker, mock_fetch):
        """count >= poolSizeMin -> 不触发 __runProxyFetch"""
        mock_ph = MagicMock()
        mock_ph.db.getCount.return_value = {"total": 50}
        mock_ph.conf.poolSizeMin = 20
        mock_ph.getAll.return_value = []
        mock_ph_cls.return_value = mock_ph

        _get_attr("__runProxyCheck")()

        mock_fetch.assert_not_called()


class TestRunScheduler:

    @patch("helper.scheduler.BlockingScheduler")
    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.ConfigHandler")
    @patch("helper.scheduler.LogHandler")
    def test_adds_two_jobs(self, mock_log, mock_conf_cls, mock_fetch, mock_sched_cls):
        """runScheduler 添加两个定时任务"""
        mock_conf = MagicMock()
        mock_conf.timezone = "Asia/Shanghai"
        mock_conf_cls.return_value = mock_conf
        mock_sched = MagicMock()
        mock_sched_cls.return_value = mock_sched

        scheduler_mod.runScheduler()

        assert mock_sched.add_job.call_count == 2

    @patch("helper.scheduler.BlockingScheduler")
    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.ConfigHandler")
    @patch("helper.scheduler.LogHandler")
    def test_fetch_job_interval_from_config(self, mock_log, mock_conf_cls, mock_fetch, mock_sched_cls):
        """采集任务间隔取自配置(默认30分钟)"""
        mock_conf = MagicMock()
        mock_conf.timezone = "Asia/Shanghai"
        mock_conf.fetchIntervalMinutes = 30
        mock_conf.checkIntervalMinutes = 2
        mock_conf_cls.return_value = mock_conf
        mock_sched = MagicMock()
        mock_sched_cls.return_value = mock_sched

        scheduler_mod.runScheduler()

        calls = mock_sched.add_job.call_args_list
        first_call = calls[0]
        assert first_call[0][1] == "interval"
        assert first_call[1]["minutes"] == 30
        assert first_call[1]["id"] == "proxy_fetch"

    @patch("helper.scheduler.BlockingScheduler")
    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.ConfigHandler")
    @patch("helper.scheduler.LogHandler")
    def test_check_job_interval_from_config(self, mock_log, mock_conf_cls, mock_fetch, mock_sched_cls):
        """检查任务间隔取自配置(默认2分钟)"""
        mock_conf = MagicMock()
        mock_conf.timezone = "Asia/Shanghai"
        mock_conf.fetchIntervalMinutes = 30
        mock_conf.checkIntervalMinutes = 2
        mock_conf_cls.return_value = mock_conf
        mock_sched = MagicMock()
        mock_sched_cls.return_value = mock_sched

        scheduler_mod.runScheduler()

        calls = mock_sched.add_job.call_args_list
        second_call = calls[1]
        assert second_call[0][1] == "interval"
        assert second_call[1]["minutes"] == 2
        assert second_call[1]["id"] == "proxy_check"

    @patch("helper.scheduler.BlockingScheduler")
    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.ConfigHandler")
    @patch("helper.scheduler.LogHandler")
    def test_intervals_follow_custom_config(self, mock_log, mock_conf_cls, mock_fetch, mock_sched_cls):
        """自定义间隔生效"""
        mock_conf = MagicMock()
        mock_conf.timezone = "Asia/Shanghai"
        mock_conf.fetchIntervalMinutes = 45
        mock_conf.checkIntervalMinutes = 7
        mock_conf_cls.return_value = mock_conf
        mock_sched = MagicMock()
        mock_sched_cls.return_value = mock_sched

        scheduler_mod.runScheduler()

        calls = mock_sched.add_job.call_args_list
        assert calls[0][1]["minutes"] == 45
        assert calls[1][1]["minutes"] == 7

    @patch("helper.scheduler.BlockingScheduler")
    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.ConfigHandler")
    @patch("helper.scheduler.LogHandler")
    def test_job_defaults_prevent_overlap(self, mock_log, mock_conf_cls, mock_fetch, mock_sched_cls):
        """job_defaults 必须禁止同一任务并发, 并合并错过的触发"""
        mock_conf = MagicMock()
        mock_conf.timezone = "Asia/Shanghai"
        mock_conf.fetchIntervalMinutes = 30
        mock_conf.checkIntervalMinutes = 2
        mock_conf_cls.return_value = mock_conf
        mock_sched = MagicMock()
        mock_sched_cls.return_value = mock_sched

        scheduler_mod.runScheduler()

        _, kwargs = mock_sched.configure.call_args
        assert kwargs["job_defaults"]["max_instances"] == 1
        assert kwargs["job_defaults"]["coalesce"] is True