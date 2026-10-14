# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
                   2026/10/14: 采集/检查间隔改为配置项, 采集间隔默认由5分钟延长至30分钟
                   2026/10/14: 采集/复检加互斥保护, 上一轮未跑完时跳过本次触发, 避免任务堆积
-------------------------------------------------
"""
__author__ = 'JHao'

import threading

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

scheduler_log = LogHandler("scheduler")

# 采集/复检互斥锁: 保证同一时刻只有一轮任务在跑。
# 免费源单轮采集+校验耗时可能接近甚至超过采集间隔, 上一轮未跑完时本轮直接跳过,
# 否则多轮会并发堆叠, 对同一批源重复抓取、重复校验。
_fetch_lock = threading.Lock()
_check_lock = threading.Lock()


def __runProxyFetch():
    if not _fetch_lock.acquire(blocking=False):
        scheduler_log.warning("ProxyFetch : 上一轮采集校验尚未完成, 跳过本次采集")
        return
    try:
        proxy_queue = Queue()
        proxy_fetcher = Fetcher()

        for proxy in proxy_fetcher.run():
            proxy_queue.put(proxy)

        Checker("raw", proxy_queue)
    finally:
        _fetch_lock.release()


def __runProxyCheck():
    if not _check_lock.acquire(blocking=False):
        scheduler_log.warning("ProxyCheck : 上一轮复检尚未完成, 跳过本次复检")
        return
    try:
        proxy_handler = ProxyHandler()
        proxy_queue = Queue()
        if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
            # 采集侧有自己的锁, 若上一轮采集未完成会自动跳过
            __runProxyFetch()
        for proxy in proxy_handler.getAll():
            proxy_queue.put(proxy)
        Checker("use", proxy_queue)
    finally:
        _check_lock.release()


def runScheduler():
    __runProxyFetch()

    conf = ConfigHandler()
    timezone = conf.timezone
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    fetch_interval = conf.fetchIntervalMinutes
    check_interval = conf.checkIntervalMinutes
    scheduler_log.info("Scheduler : fetch every %s min, check every %s min" % (
        fetch_interval, check_interval))

    scheduler.add_job(__runProxyFetch, 'interval', minutes=fetch_interval,
                      id="proxy_fetch", name="proxy采集")
    scheduler.add_job(__runProxyCheck, 'interval', minutes=check_interval,
                      id="proxy_check", name="proxy检查")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    # max_instances=1: 同一任务不并发, 上一轮未跑完则跳过本次触发
    # coalesce=True : 错过多次触发时合并为一次, 不补跑
    job_defaults = {
        'coalesce': True,
        'max_instances': 1
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
