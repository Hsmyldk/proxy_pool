# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :   执行代理校验
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 执行代理校验
                   2021/05/25: 分别校验http和https
                   2022/08/16: 获取代理Region信息
                   2026/10/12: 合并PR#694 region/anonymous筛选
-------------------------------------------------
"""
__author__ = 'JHao'

import json
import requests

from util.six import Empty
from threading import Thread
from datetime import datetime
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


class DoValidator(object):
    """ 执行校验 """

    conf = ConfigHandler()

    @classmethod
    def validator(cls, proxy, work_type):
        """
        校验入口
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        http_r = cls.httpValidator(proxy)
        https_r = False if not http_r else cls.httpsValidator(proxy)

        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = True if http_r else False
        if http_r:
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            proxy.https = True if https_r else False
            # region是IP的固有属性, 已有有效值时不再重复查询(避免地区接口限流)
            if cls.conf.proxyRegion and (not proxy.region or proxy.region == '未知或请求失败'):
                proxy.region = cls.region_get(proxy.proxy)
            proxy.anonymous = cls.anonymousValidator(proxy.proxy, proxy.https)
        else:
            proxy.fail_count += 1
        return proxy

    @classmethod
    def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    def region_get(cls, proxy):
        """ 获取代理地区(中文地址): 依次尝试多个数据源 """
        ip = proxy.split('@')[-1].split(':')[0]

        # 1. PR#694 使用的CSDN接口(部分网络下返回403, 故需要回退)
        try:
            r = requests.get(url='https://searchplugin.csdn.net/api/v1/ip/get',
                             params={'ip': ip}, timeout=2)
            return json.loads(r.text)['data']['address']
        except:
            pass

        # 2. 回退: ip-api.com 免费接口, lang=zh-CN 返回中文地区
        try:
            r = requests.get(url='http://ip-api.com/json/%s' % ip,
                             params={'lang': 'zh-CN'}, timeout=3)
            data = json.loads(r.text)
            if data.get('status') == 'success':
                return '%s%s' % (data.get('country') or '', data.get('regionName') or '')
        except:
            pass

        return '未知或请求失败'

    @classmethod
    def anonymousValidator(cls, proxy, https):
        """
        判断代理匿名度
        Returns:
            0-透明(暴露真实IP) / 1-匿名(暴露代理身份) / 2-高匿 / -1-检测失败
        """
        if https:
            url = 'https://httpbin.org/get'
            proxies = {'https': 'https://%s' % proxy}
        else:
            url = 'http://httpbin.org/get'
            proxies = {'http': 'http://%s' % proxy}

        try:
            r = requests.get(url, proxies=proxies, timeout=cls.conf.verifyTimeout, verify=False)
            data = json.loads(r.text)
            if ',' in (data.get('origin') or ''):
                return 0
            elif data.get('headers', {}).get('Proxy-Connection', False):
                return 1
            else:
                return 2
        except:
            return -1


class _ThreadChecker(Thread):
    """ 多线程检测 """

    def __init__(self, work_type, target_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.work_type = work_type
        self.log = LogHandler("checker")
        self.proxy_handler = ProxyHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info("{}ProxyCheck - {}: start".format(self.work_type.title(), self.name))
        while True:
            try:
                proxy = self.target_queue.get(block=False)
            except Empty:
                self.log.info("{}ProxyCheck - {}: complete".format(self.work_type.title(), self.name))
                break
            proxy = DoValidator.validator(proxy, self.work_type)
            if self.work_type == "raw":
                self.__ifRaw(proxy)
            else:
                self.__ifUse(proxy)
            self.target_queue.task_done()

    def __ifRaw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck - {}: {} exist'.format(self.name, proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
        else:
            self.log.info('RawProxyCheck - {}: {} fail'.format(self.name, proxy.proxy.ljust(23)))

    def __ifUse(self, proxy):
        if proxy.last_status:
            self.log.info('UseProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
            self.proxy_handler.put(proxy)
        else:
            if proxy.fail_count > self.conf.maxFailCount:
                self.log.info('UseProxyCheck - {}: {} fail, count {} delete'.format(self.name,
                                                                                    proxy.proxy.ljust(23),
                                                                                    proxy.fail_count))
                self.proxy_handler.delete(proxy)
            else:
                self.log.info('UseProxyCheck - {}: {} fail, count {} keep'.format(self.name,
                                                                                  proxy.proxy.ljust(23),
                                                                                  proxy.fail_count))
                self.proxy_handler.put(proxy)


def Checker(tp, queue):
    """
    run Proxy ThreadChecker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    for index in range(20):
        thread_list.append(_ThreadChecker(tp, queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()

    for thread in thread_list:
        thread.join()
