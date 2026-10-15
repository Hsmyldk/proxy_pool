# 免费代理源调研记录

> 最近一次全量实测： **2026-10-14**，方法为用项目自身 `WebRequest` 真实请求各源 + 用项目校验目标抽样验证可用率。

免费代理源的生命周期很短——改版、上盾、加 JS 加密、直接下线都很常见。本页记录每个源的最后实测结论，
**下次找源前先看这里，已判定失效的直接跳过，不要重复浪费时间去试**。

---

## 一、当前已接入且产出正常

实测方式：逐个调用各 fetcher 的 `fetch()` 统计产出，"单轮实测"为 2026-10-14 的真实一轮结果。 **单轮总量约 2000 条**，按 20
线程校验估算需 10–20 分钟，与 30 分钟的采集间隔相匹配。

| 源              | 类名                 | 抓取端点                                                                  | 源内条数                | `limit` | 单轮实测 | 备注                                          |
|-----------------|----------------------|---------------------------------------------------------------------------|-------------------------|---------|----------|-----------------------------------------------|
| `hproxy`        | HproxyFetcher        | `hproxy.com/api/proxy-list`                                               | 上游过滤后100           | 100     | 100      | 🆕 2026-10-15接入, 仅http/https且排除透明代理 |
| `scdntext`      | ScdnTextFetcher      | `proxy.scdn.io/text.php`                                                  | 数万                    | 300     | 300      |                                               |
| `monosans`      | MonosansFetcher      | `raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt`     | 383                     | 300     | 300      | 🆕 本次接入，质量最高                         |
| `proxyscrape`   | ProxyScrapeFetcher   | `api.proxyscrape.com/v4/free-proxy-list/get`                              | 751(http) + 1928(https) | 200     | 200      | 🆕 本次接入                                   |
| `spysme`        | SpysMeFetcher        | `spys.me/proxy.txt`                                                       | 400                     | 200     | 200      | 🆕 本次接入                                   |
| `thespeedx`     | TheSpeedXFetcher     | `raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt`          | 2793                    | 200     | 200      | 🆕 本次接入                                   |
| `freeproxylist` | FreeProxyListFetcher | `free-proxy-list.net` / `sslproxies.org`                                  | 400                     | 200     | 200      | 🆕 本次接入                                   |
| `proxifly`      | ProxiFlyFetcher      | `cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.json` | 6 万+（筛 CN 后约 150） | -       | 145      | 只筛 `country=CN` + `protocol=http`           |
| `openproxylist` | OpenProxyListFetcher | `raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS.txt`       | ~150                    | -       | 132      |                                               |
| `scdn`          | ScdnFetcher          | `proxy.scdn.io/get_proxies.php`                                           | ~100                    | -       | 100      |                                               |
| `geonode`       | GeonodeFetcher       | `proxylist.geonode.com/api/proxy-list`                                    | 3910                    | -       | 53       | 已修复，见下文                                |
| `roundproxies`  | RoundProxiesFetcher  | `roundproxies.com/api/get-free-proxies/`                                  | ~50                     | -       | 50       |                                               |
| `ip89`          | Ip89Fetcher          | `89ip.cn`                                                                 | ~40                     | -       | 40       | 国内源，仍在更新                              |
| `ip3366`        | Ip3366Fetcher        | `ip3366.net`                                                              | ~30                     | -       | 30       | 国内源，仍在更新                              |
| `kuaidaili`     | KuaidailiFetcher     | `kuaidaili.com/free/inha/{page}`                                          | ~24                     | -       | 24       | ⚠️ 免费页已改为 JS + RSA 加密，随时可能归零   |
| `ihuan`         | IhuanFetcher         | `ip.ihuan.me`                                                             | ~18                     | -       | 18       | 国内源，需先取 cookie                         |
| `goodips`       | GoodipsFetcher       | `goodips.com`                                                             | ~15                     | -       | 15       |                                               |

## 二、已接入但实测失效（已加入黑名单）

这些源在 `setting.py` 的 `PROXY_FETCHER_EXCLUDE` 中，源文件保留， **恢复后从黑名单移除类名即可重新启用**。

| 源            | 类名               | 端点                             | 实测结果 | 失效原因                                                |
|---------------|--------------------|----------------------------------|----------|---------------------------------------------------------|
| `daili66`     | DaiLi66Fetcher     | `api.66daili.com/?format=json`   | 0 条     | 接口返回 502，服务疑似下线                              |
| `freevpnnode` | FreeVPNNodeFetcher | `cn.freevpnnode.com/free-proxy/` | 0 条     | 返回 526（Cloudflare 源站证书失效）                     |
| `kxdaili`     | KxdailiFetcher     | `kxdaili.com/dailiip.html`       | 0 条     | 页面改版，HTML 中已无明文 IP                            |
| `docip`       | DocipFetcher       | `docip.net/data/free.json`       | 0 条     | 连接被对端重置（ConnectionResetError），重试 3 次均失败 |
| `zdaye`       | ZdayeFetcher       | `zdaye.com/free/`                | 抛异常   | `IndexError`，页面结构变化导致解析越界                  |

### 已修复：geonode

- **症状**：接口返回 HTTP 200，但 `data` 恒为空，产出 0 条。
- **根因**：URL 中的 `filterLastChecked=10` 参数已失效，带上它接口恒返回空集。
- **验证**：
    - `?filterLastChecked=10&page=1&limit=100...` → `total=0`
    - `?page=1&limit=100...` → `total=3910`，`data` 有数据
- **修复**：移除该参数，并按 `protocols` 字段过滤掉 socks 代理。已于 2026-10-14 修复。

## 三、已验证可用、但尚未接入的候选源

抽样可用率 = 从该源随机取 30–40 条，经代理访问目标站点（baidu / qq / httpbin）测通的比例。
**数值对目标站点和时刻都很敏感，只用于横向相对比较，不要当成固定指标**。

| 源                               | 端点                                                                                   | 实测条数 | 抽样可用率 | 建议                                    |
|----------------------------------|----------------------------------------------------------------------------------------|----------|------------|-----------------------------------------|
| proxyspace                       | `proxyspace.pro/http.txt`                                                              | 3839     | 13%–35%    | 可接入，与 proxyscrape 重叠较多         |
| jetkai/proxy-list                | `raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt` | 1801     | 2.5%       | 量大质差，建议配 `limit` 采样           |
| sunny9577/proxy-scraper          | `sunny9577.github.io/proxy-scraper/proxies.txt`                                        | 1321     | 未测       | 可试                                    |
| ALIILAPRO/Proxy                  | `raw.githubusercontent.com/ALIILAPRO/Proxy/main/http.txt`                              | 1053     | 未测       | 可试                                    |
| vakhov/fresh-proxy-list          | `raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt`                    | 524      | **0%**     | 实测全灭，不建议                        |
| mmpx12/proxy-list                | `raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt`                          | 440      | 未测       | 可试                                    |
| clarketm/proxy-list              | `raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt`              | 400      | 未测       | 可试                                    |
| Thordata/awesome-free-proxy-list | `raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/http.txt`     | 350      | 未测       | GitHub Actions 每日复检，可试           |
| themiralay/Proxy-List-World      | `raw.githubusercontent.com/themiralay/Proxy-List-World/master/data.txt`                | 341      | 未测       | 可试                                    |
| zloi-user/hideip.me              | `raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt`                          | 225      | 未测       | 行格式为 `ip:port:国家`，正则可兼容     |
| my-proxy.com                     | `www.my-proxy.com/free-proxy-list.html`                                                | 70       | 未测       | HTML 需解析                             |
| prxchk/proxy-list                | `raw.githubusercontent.com/prxchk/proxy-list/main/http.txt`                            | 58       | 未测       | 量小                                    |
| ShiftyTR/Proxy-List              | `raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt`                        | 40       | 未测       | 量小                                    |
| **MuRongPIG/Proxy-Master**       | `raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt`                       | 101619   | 2.5%       | ⚠️ 超大源，必须配 `limit` 采样          |
| **zevtyardt/proxy-list**         | `raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt`                         | 63788    | 5%         | ⚠️ 超大源，大量 3128 端口，质量差       |
| **ErcinDedeoglu/proxies**        | `raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt`                | 65034    | 未测       | ⚠️ 混入 SOCKS，项目不支持，需按协议过滤 |
| openproxylist.xyz                | `api.openproxylist.xyz/http.txt`                                                       | 6595     | **0%**     | ⚠️ 含 `0.0.0.0:80` 脏数据，不建议       |

## 四、踩坑清单：这些别再花时间

| 源                                                      | 实测结果                                        |
|---------------------------------------------------------|-------------------------------------------------|
| `proxy-list.download` API                               | 持续返回 502                                    |
| `openproxy.space`                                       | 521，全站宕机                                   |
| `proxylist.gg`                                          | TLS 连接失败                                    |
| `checked-proxy.net`                                     | TLS 连接失败                                    |
| `proxy11.com`                                           | 返回 `need to use your token key`（需付费 key） |
| `hidemy.name`                                           | Cloudflare 403 盾                               |
| `advanced.name`                                         | 列表由 JS 渲染，页面中无明文 IP                 |
| `freeproxy.world`                                       | 同上，JS 渲染                                   |
| `spys.one`                                              | 同上，且端口用 JS 编码混淆                      |
| `proxydb.net`                                           | 分页/JS 渲染，正则抓不到                        |
| `multiproxy.org`                                        | 已改版，页面无代理列表                          |
| `proxyscan.io`                                          | 请求超时                                        |
| `freeproxyupdate.com`                                   | 404                                             |
| ProxyScrape 的 GitHub 仓库 raw 路径                     | 多个路径均 404，**直接用它的 API**              |
| `mertguvencli/http-proxy-list`、`rangertaha/proxy-list` | raw 路径 404，仓库结构已变                      |

## 五、国内免费代理站现状

结论： **国内免费站已基本不可抓**，不建议再投入时间。

| 站点                                            | 实测结果                                                                         |
|-------------------------------------------------|----------------------------------------------------------------------------------|
| 快代理免费页                                    | HTTP 200 但页面无明文 IP，已内嵌 `const _rsaPublicKey = ...`，改为 JS + RSA 加密 |
| 66ip `nmtq.php` 接口                            | 404                                                                              |
| 齐云代理、data5u、superfastip、goubanjia、ip181 | 200，但静态 HTML 中无 IP（JS 异步渲染 / 空响应）                                 |
| 7yip、9qu                                       | 403 Forbidden                                                                    |
| 西拉免费代理、尼玛代理                          | 连接超时                                                                         |

## 六、复查方法

下次复查时，按下面方式重新跑一遍，并把结论更新到本页。

**1. 测项目内各源当前产出**（只读，不写库）：

```python
import threading, time
from helper.fetch import _discover_fetchers


def run(cls, box):
    try:
        box["n"] = len(list(cls().fetch()))
    except Exception as e:
        box["err"] = repr(e)


for cls in _discover_fetchers([]):
    box, t = {}, threading.Thread(target=run, args=(cls, box), daemon=True)
    t.start();
    t.join(75)
    print(cls.name, box.get("n", "TIMEOUT"), box.get("err", ""))
```

> `_discover_fetchers([])` 传空列表可绕过黑名单，一次看到全部源的真实状态。

**2. 测候选源并抽样验证可用率**：先 `requests.get(url, timeout=15, verify=False)` 取回文本，用与
`BaseFetcher.parseProxiesFromText` 相同的正则提取 `ip:port`；再对随机抽样的 30–40 条，用
`requests.get(TEST_URL, proxies={"http": "http://%s" % p, "https": "http://%s" % p}, timeout=6)`
判断是否 200。

**3. 判断源是否值得接入**：优先选「纯文本 / JSON 接口 + 上游定期复检」的源；HTML 页面优先看是否有只读文本框直接给出
`ip:port`（如 free-proxy-list.net），这类不用解析表格。

## 七、维护约定

- 新增源前先查本页， **已失效清单里的源不要重复调研**。
- 源接入后设 `limit` 采样（见[扩展代理源](extending/fetcher.md)），避免超大源拖垮单轮校验。
- 只接入 http/https 代理，项目不支持 SOCKS。
- 复查后请更新"最近一次全量实测"日期与对应结论。
