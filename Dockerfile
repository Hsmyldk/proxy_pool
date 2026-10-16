FROM python:3.12-slim

LABEL maintainer="jhao104 <j_hao104@163.com>"

# 运行期环境:
#   PYTHONUNBUFFERED - 关闭 stdout 缓冲, docker logs 实时可见
#   TZ               - 与 setting.py 的 TIMEZONE 保持一致, glibc 直接按该时区输出时间
#   LANG             - 校验时写入的中文地区名(region)需要 UTF-8 环境
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai \
    LANG=C.UTF-8

WORKDIR /app

COPY ./requirements.txt .

# 基础镜像是 debian, 包管理必须用 apt-get(alpine 的 apk 在这里不存在):
#   tzdata          - 提供 /usr/share/zoneinfo 时区数据
#   tini            - 作为 PID 1 回收僵尸进程并转发信号, ENTRYPOINT 使用
#   bash            - proxy_pool.sh 是 bash 脚本(用到 [[ ]] 等语法), 缺少时容器会
#                     以 "tini: exec bash failed: No such file or directory" 启动失败
#   ca-certificates - requests 访问 https 代理源需要根证书
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        tzdata \
        tini \
        bash \
        ca-certificates && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo "$TZ" > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# runtime environment
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Windows 检出时 proxy_pool.sh 可能带 CRLF 行尾, 会让 bash 报 "$'\r': command not found"
RUN sed -i 's/\r$//' proxy_pool.sh && \
    chmod +x proxy_pool.sh

EXPOSE 5010

ENTRYPOINT ["tini", "--", "bash", "proxy_pool.sh", "start", "--fg"]
