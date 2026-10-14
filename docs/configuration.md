# 配置参考

配置文件 `setting.py` 位于项目的主目录下，配置主要分为五类： **服务配置**、 **数据库配置**、 **采集配置**、 **校验配置**、
**调度配置**。

## 服务配置

### `HOST`

API 服务监听的 IP。本机访问设置为 `127.0.0.1`，开启远程访问设置为 `0.0.0.0`。

- 默认值：`"0.0.0.0"`

### `PORT`

API 服务监听的端口。

- 默认值：`5010`

## 数据库配置

### `DB_CONN`

存放代理 IP 的数据库 URI，配置格式为：

```
db_type://[[user]:[pwd]]@ip:port/[db]
```

目前支持的 `db_type`：`redis`、`ssdb`。

配置示例：

```python
# Redis
DB_CONN = 'redis://@127.0.0.1:6379'
DB_CONN = 'redis://:123456@127.0.0.1:6379'
DB_CONN = 'redis://:123456@127.0.0.1:6379/15'

# SSDB
DB_CONN = 'ssdb://@127.0.0.1:8888'
DB_CONN = 'ssdb://:123456@127.0.0.1:8888'
```

### `TABLE_NAME`

存放代理的数据载体名称。SSDB 和 Redis 的存放结构为 hash。

- 默认值：`"use_proxy"`

## 采集配置

代理采集采用插件架构，调度器自动扫描 `fetcher/sources/` 目录，加载所有 `enabled=True` 的代理源。新增代理源只需在 `sources/`
下创建文件，无需修改配置。

查看当前启用的代理源：

```bash
python proxyPool.py fetcher
```

### `PROXY_FETCHER_EXCLUDE`

代理源黑名单。列表中的类名对应的代理源不会被加载，即使 `enabled=True`。适用于临时禁用某个代理源而不修改其源文件。

```python
PROXY_FETCHER_EXCLUDE = [
    "DaiLi66Fetcher",  # api.66daili.com 返回 502
    "FreeVPNNodeFetcher",  # cn.freevpnnode.com 返回 526
    "KxdailiFetcher",  # 页面改版, 无明文 IP
    "DocipFetcher",  # /data/free.json 连接被重置
    "ZdayeFetcher",  # 页面结构变化, fetch 抛异常
]
```

默认为空列表；项目内置了若干 **实测已失效**
的源，它们的类名默认就在黑名单里。某个源恢复后，把对应类名从列表移除即可重新启用。各源的实测状态见[代理源调研记录](proxy-sources-survey.md)。

如需永久禁用，建议直接在源文件中设置 `enabled = False`。

## 校验配置

### `VERIFY_UUID_URL`

代理可用性校验方式1 的目标地址：通过代理访问该地址，响应 JSON 中需包含 `uuid` 字段。

- 默认值：`"http://httpbin.org/uuid"`

### `VERIFY_TEXT_URL`

代理可用性校验方式2 的目标地址：通过代理访问该地址，响应文本中需包含 `VERIFY_TEXT_KEYWORD`。

- 默认值：`"http://geo.brdtest.com/welcome.txt?product=dc&method=native"`

### `VERIFY_TEXT_KEYWORD`

方式2 需要匹配的响应关键字。

- 默认值：`"Welcome to Bright Data"`

以上两种方式 **每次校验随机选择一种执行**，判定结果写入代理的 `last_status` 字段。

> 两个校验目标都用 http 协议，因此只要求代理支持 HTTP 转发，不要求支持 HTTPS CONNECT。若改成 https 目标，绝大多数免费代理会因无法建立
> CONNECT 隧道而被判为不可用（实测通过率会从约 37% 降到约 3%）。

### `HTTPS_URL`

用于检验代理是否支持 HTTPS 的地址，决定代理的 `https` 属性（`/get?type=https` 依赖该属性）。

- 默认值：`"https://www.qq.com"`

### `VERIFY_HTTPS_FALLBACK`

HTTP 转发校验失败时，是否再用 `HTTPS_URL` 兜底探测一次。

代理只要求 **支持 HTTP 或 HTTPS 其中之一**：`http` 通即通过；`http` 不通时若该开关开启，会再用 HTTPS 探测一次，通过则同样视为可用（这类代理的
`https` 属性为 `True`，可用 `/get?type=https` 取到）。

- 默认值：`True`
- 代价：HTTP 不通的代理都会多做一次 HTTPS 探测，单轮校验耗时增加。若校验压力过大，可将其设为 `False`，或调小
  `VERIFY_TIMEOUT`。

### `VERIFY_TIMEOUT`

检验代理的超时时间，单位秒。使用代理访问 `VERIFY_UUID_URL` / `VERIFY_TEXT_URL` / `HTTPS_URL` 耗时超过 `VERIFY_TIMEOUT`
时，视为不可用。

- 默认值：`10`

### `MAX_FAIL_COUNT`

检验代理允许的最大失败次数。超过则剔除代理。

- 默认值：`0`（即失败一次即删除）

### `POOL_SIZE_MIN`

代理检测定时任务运行前，若代理数量小于 `POOL_SIZE_MIN`，则先运行抓取程序。

- 默认值：`20`

## 代理属性

### `PROXY_REGION`

是否启用代理地域属性。开启后会尝试解析代理 IP 的地理位置信息。

- 默认值：`True`

## 调度配置

### `FETCH_INTERVAL_MINUTES`

代理采集定时任务的执行间隔，单位分钟。

免费源更新较慢（多数为每天或每小时更新一次），间隔过短的话多数轮次抓不到新代理，只是白白消耗请求。默认已由 5 分钟延长至 30
分钟。

- 默认值：`30`

### `CHECK_INTERVAL_MINUTES`

已入池代理的可用性复检间隔，单位分钟。复检时若池内代理总数少于 `POOL_SIZE_MIN`，会先触发一次采集。

- 默认值：`2`

### `TIMEZONE`

调度器的时区设置。如果在虚拟机上运行时出现 `ValueError: Timezone offset does not match system offset` 错误，请设置该配置项。

- 默认值：`"Asia/Shanghai"`