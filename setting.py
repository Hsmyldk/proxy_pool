# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
                    2026/10/12: 代理可用性校验配置改为随机二选一
                    2026/10/12: 校验目标改为http, 兼容仅支持HTTP转发的代理
                    2026/10/14: 采集/检查间隔可配置, 采集间隔延长至30分钟
                    2026/10/14: 新增https兜底校验开关, 失效源加入黑名单
                    2026/10/15: 新增HProxy非透明HTTP/HTTPS代理源
                    2026/10/15: 新增HProxy非透明HTTP/HTTPS代理源
-------------------------------------------------
"""

BANNER = r"""
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

VERSION = "2.4.3"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5010

# ############### database config ###################
# db connection uri
# 真实连接串请通过环境变量 DB_CONN 注入(configHandler 会优先读取该变量), 不要提交到版本库
# example:
#      Redis: redis://:password@ip:port/db
#      Ssdb:  ssdb://:password@ip:port
DB_CONN = 'redis://:password@127.0.0.1:6379/0'

# proxy table name
TABLE_NAME = 'use_proxy'

# ###### config the proxy fetch function ######
# 自动扫描 fetcher/sources/ 目录，加载所有 enabled=True 的 fetcher
# 如需临时禁用某个 fetcher，在下方黑名单中添加类名（不改源文件）
# 以下源在 2026/10/14 实测为零产出或异常(详见 docs/proxy-sources-survey.md):
#   DaiLi66Fetcher     - api.66daili.com 返回 502
#   FreeVPNNodeFetcher - cn.freevpnnode.com 返回 526
#   KxdailiFetcher     - 页面改版, 无明文 IP
#   DocipFetcher       - /data/free.json 连接被重置
#   ZdayeFetcher       - 页面结构变化, fetch 抛 IndexError
# 某个源恢复后, 从列表移除对应类名即可重新启用
PROXY_FETCHER_EXCLUDE = [
    "DaiLi66Fetcher",
    "FreeVPNNodeFetcher",
    "KxdailiFetcher",
    "DocipFetcher",
    "ZdayeFetcher",
]

# ############# proxy validator #################
# 代理可用性校验: 以下两种方式每次校验随机选一种执行
# 两个目标都用http, 以免要求代理必须支持HTTPS CONNECT(多数免费代理仅支持HTTP转发)
# 方式1: 通过代理访问该地址, 响应JSON中需含uuid字段
VERIFY_UUID_URL = "http://httpbin.org/uuid"

# 方式2: 通过代理访问该地址, 响应文本中需含VERIFY_TEXT_KEYWORD
VERIFY_TEXT_URL = "http://geo.brdtest.com/welcome.txt?product=dc&method=native"
VERIFY_TEXT_KEYWORD = "Welcome to Bright Data"

# 代理https支持检测目标网站
HTTPS_URL = "https://www.qq.com"

# http转发校验失败时, 是否再用https探测一次
# 部分免费代理仅支持https转发, 开启后这类代理也可入池(校验只用http或https任一通过即可)
# 代价: http不通的代理都会多探一次, 单轮校验耗时增加, 可通过调小VERIFY_TIMEOUT缓解
VERIFY_HTTPS_FALLBACK = True

# 代理验证时超时时间
VERIFY_TIMEOUT = 10

# 近PROXY_CHECK_COUNT次校验中允许的最大失败次数,超过则剔除代理
MAX_FAIL_COUNT = 0

# 近PROXY_CHECK_COUNT次校验中允许的最大失败率,超过则剔除代理
# MAX_FAIL_RATE = 0.1

# proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
POOL_SIZE_MIN = 20

# ############# proxy attributes #################
# 是否启用代理地域属性
PROXY_REGION = True

# ############# scheduler config #################

# 代理采集间隔(分钟)
# 免费源更新较慢, 间隔过短多数轮次抓不到新代理, 只是白白消耗请求
FETCH_INTERVAL_MINUTES = 30

# 代理可用性复检间隔(分钟)
CHECK_INTERVAL_MINUTES = 2

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"
