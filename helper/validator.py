# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     _validators
   Description :   定义proxy验证方法
   Author :        JHao
   date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2023/03/10: 支持带用户认证的代理格式 username:password@ip:port
                   2026/10/12: 可用性校验改为随机二选一(httpbin uuid / brdtest 关键字)
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import random
from requests import get, head
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler

conf = ConfigHandler()

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


def verifyByHttpbinUuid(proxy):
    """ 方式1: 通过代理访问httpbin uuid接口, 响应JSON含uuid字段则可用 """

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}

    try:
        r = get(conf.verifyUuidUrl, headers=HEADER, proxies=proxies,
                timeout=conf.verifyTimeout, verify=False)
        return True if r.status_code == 200 and r.json().get("uuid") else False
    except Exception as e:
        return False


def verifyByBrightDataText(proxy):
    """ 方式2: 通过代理访问brdtest welcome.txt, 响应文本含关键字则可用 """

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}

    try:
        r = get(conf.verifyTextUrl, headers=HEADER, proxies=proxies,
                timeout=conf.verifyTimeout, verify=False)
        return True if r.status_code == 200 and conf.verifyTextKeyword in r.text else False
    except Exception as e:
        return False


@ProxyValidator.addHttpValidator
def randomHttpValidator(proxy):
    """ 可用性校验: 两种方式每次校验随机选一种执行 """

    return random.choice((verifyByHttpbinUuid, verifyByBrightDataText))(proxy)


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy):
    """https检测超时"""

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    try:
        r = head(conf.httpsUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False


@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """自定义validator函数，校验代理是否可用, 返回True/False"""
    return True
