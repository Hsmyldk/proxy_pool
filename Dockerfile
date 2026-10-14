FROM python:3.10-alpine

LABEL maintainer="jhao104 <j_hao104@163.com>"

WORKDIR /app

COPY ./requirements.txt .

# timezone, init process and bash
# alpine 基础镜像不带 bash, 而 proxy_pool.sh 是 bash 脚本(用到 [[ ]] 等语法),
# 缺少 bash 时容器会以 "tini: exec bash failed: No such file or directory" 启动失败
RUN apk add -U tzdata tini bash && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    apk del tzdata

# runtime environment
RUN apk add musl-dev gcc libxml2-dev libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

# Windows 检出时 proxy_pool.sh 可能带 CRLF 行尾, 会让 bash 报 "$'\r': command not found"
RUN sed -i 's/\r$//' proxy_pool.sh

EXPOSE 5010

ENTRYPOINT ["tini", "--", "bash", "proxy_pool.sh", "start", "--fg"]
