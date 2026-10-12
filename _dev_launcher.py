# -*- coding: utf-8 -*-
"""
DSH 沙箱兼容启动器 (server / schedule)

沙箱限制与对应绕行:
1) socket.fromfd 被拒绝(OSError 10022)
   werkzeug 的 run_simple 必然经由 prepare_socket -> make_server(fd=fd) -> fromfd,
   故把 Flask.run 替换为等价的 make_server(fd=None) 实现(直接 bind_and_activate)。
2) multiprocessing.Pipe 需要创建命名管道, 被沙箱拒绝(PermissionError WinError 5)
   scheduler 配置里的 ProcessPoolExecutor 在构造时即触发该错误,
   故替换为 apscheduler 自带的 ThreadPoolExecutor —— 该项目两个 job 都未指定 executor,
   processpool 实际未被使用, 行为等价。

普通终端(非 DSH 沙箱)下无需本文件:
    python proxyPool.py server
    python proxyPool.py schedule

用法:
    python _dev_launcher.py server
    python _dev_launcher.py schedule
"""
import sys

import flask
from werkzeug.serving import make_server


def _patchFlaskRun():
    """让 app.run() 绕开沙箱禁止的 socket.fromfd"""
    def _runByMakeServer(self, host=None, port=None, **kwargs):
        server = make_server(host or "127.0.0.1", int(port or 5000), self, threaded=True)
        try:
            server.log_startup()
        except Exception:
            pass
        server.serve_forever()

    flask.Flask.run = _runByMakeServer


def _patchProcessPool():
    """让 scheduler 的 processpool 配置改用线程池, 避开命名管道"""
    import apscheduler.executors.pool as pool
    import helper.scheduler as scheduler
    scheduler.ProcessPoolExecutor = pool.ThreadPoolExecutor


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "server"
    if mode == "server":
        _patchFlaskRun()
        from helper.launcher import startServer
        startServer()
    elif mode == "schedule":
        _patchProcessPool()
        from helper.launcher import startScheduler
        startScheduler()
    else:
        raise SystemExit("usage: _dev_launcher.py [server|schedule]")


if __name__ == '__main__':
    main()
