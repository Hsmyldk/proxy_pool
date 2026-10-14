# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
                    2026/10/12: httpUrl拆分为随机二选一的校验目标配置
                    2026/10/14: 新增https兜底校验开关与采集/检查间隔配置
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import setting
from util.singleton import Singleton
from util.lazyProperty import LazyProperty
from util.six import reload_six, withMetaclass


class ConfigHandler(withMetaclass(Singleton)):

    def __init__(self):
        pass

    @LazyProperty
    def serverHost(self):
        return os.environ.get("HOST", setting.HOST)

    @LazyProperty
    def serverPort(self):
        return os.environ.get("PORT", setting.PORT)

    @LazyProperty
    def dbConn(self):
        return os.getenv("DB_CONN", setting.DB_CONN)

    @LazyProperty
    def tableName(self):
        return os.getenv("TABLE_NAME", setting.TABLE_NAME)

    @property
    def fetcherExclude(self):
        reload_six(setting)
        return getattr(setting, 'PROXY_FETCHER_EXCLUDE', [])

    @LazyProperty
    def verifyUuidUrl(self):
        return os.getenv("VERIFY_UUID_URL", setting.VERIFY_UUID_URL)

    @LazyProperty
    def verifyTextUrl(self):
        return os.getenv("VERIFY_TEXT_URL", setting.VERIFY_TEXT_URL)

    @LazyProperty
    def verifyTextKeyword(self):
        return os.getenv("VERIFY_TEXT_KEYWORD", setting.VERIFY_TEXT_KEYWORD)

    @LazyProperty
    def httpsUrl(self):
        return os.getenv("HTTPS_URL", setting.HTTPS_URL)

    @LazyProperty
    def verifyHttpsFallback(self):
        """http校验失败后是否再用https兜底探测(仅支持https转发的代理也能入池)"""
        return str(os.getenv("VERIFY_HTTPS_FALLBACK", setting.VERIFY_HTTPS_FALLBACK)
                   ).strip().lower() not in ("0", "false", "no", "off")

    @LazyProperty
    def verifyTimeout(self):
        return int(os.getenv("VERIFY_TIMEOUT", setting.VERIFY_TIMEOUT))

    # @LazyProperty
    # def proxyCheckCount(self):
    #     return int(os.getenv("PROXY_CHECK_COUNT", setting.PROXY_CHECK_COUNT))

    @LazyProperty
    def maxFailCount(self):
        return int(os.getenv("MAX_FAIL_COUNT", setting.MAX_FAIL_COUNT))

    # @LazyProperty
    # def maxFailRate(self):
    #     return int(os.getenv("MAX_FAIL_RATE", setting.MAX_FAIL_RATE))

    @LazyProperty
    def poolSizeMin(self):
        return int(os.getenv("POOL_SIZE_MIN", setting.POOL_SIZE_MIN))

    @LazyProperty
    def fetchIntervalMinutes(self):
        return int(os.getenv("FETCH_INTERVAL_MINUTES", setting.FETCH_INTERVAL_MINUTES))

    @LazyProperty
    def checkIntervalMinutes(self):
        return int(os.getenv("CHECK_INTERVAL_MINUTES", setting.CHECK_INTERVAL_MINUTES))

    @LazyProperty
    def proxyRegion(self):
        return bool(os.getenv("PROXY_REGION", setting.PROXY_REGION))

    @LazyProperty
    def timezone(self):
        return os.getenv("TIMEZONE", setting.TIMEZONE)

