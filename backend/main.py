import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import uvicorn


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
PID_FILE = LOG_DIR / "server.pid"
SERVER_LOG_FILE = LOG_DIR / "server.log"
HOST = "0.0.0.0"
PORT = 6567


def is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def read_pid() -> int | None:
    if not PID_FILE.exists():
        return None

    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except ValueError:
        PID_FILE.unlink(missing_ok=True)
        return None


def start_server() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    pid = read_pid()
    if pid and is_process_running(pid):
        print(f"后端服务已运行，PID: {pid}")
        return

    PID_FILE.unlink(missing_ok=True)

    log_file = SERVER_LOG_FILE.open("a", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ],
        cwd=BASE_DIR,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    PID_FILE.write_text(str(process.pid), encoding="utf-8")
    print(f"后端服务已后台启动，PID: {process.pid}，日志: {SERVER_LOG_FILE}")


def stop_server() -> None:
    pid = read_pid()
    if not pid:
        print("后端服务未运行")
        return

    if not is_process_running(pid):
        PID_FILE.unlink(missing_ok=True)
        print("后端服务未运行，已清理过期 PID")
        return

    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not is_process_running(pid):
            PID_FILE.unlink(missing_ok=True)
            print(f"后端服务已停止，PID: {pid}")
            return
        time.sleep(0.2)

    os.kill(pid, signal.SIGKILL)
    PID_FILE.unlink(missing_ok=True)
    print(f"后端服务已强制停止，PID: {pid}")


def show_status() -> None:
    pid = read_pid()
    if pid and is_process_running(pid):
        print(f"后端服务运行中，PID: {pid}")
        return

    PID_FILE.unlink(missing_ok=True)
    print("后端服务未运行")


def restart_server() -> None:
    stop_server()
    start_server()


def run_foreground() -> None:
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="出彩中原后端服务管理")
    parser.add_argument("--start", action="store_true", help="后台持久化启动服务")
    parser.add_argument("--stop", action="store_true", help="停止后台服务")
    parser.add_argument("--status", action="store_true", help="查看后台服务状态")
    parser.add_argument("--restart", action="store_true", help="重启后台服务")
    parser.add_argument("--resatrt", action="store_true", help="重启后台服务（兼容错误拼写）")
    args = parser.parse_args()

    actions = [args.start, args.stop, args.status, args.restart, args.resatrt]
    if sum(bool(action) for action in actions) > 1:
        parser.error("--start、--stop、--status、--restart、--resatrt 只能同时使用一个")

    if args.start:
        start_server()
    elif args.stop:
        stop_server()
    elif args.status:
        show_status()
    elif args.restart or args.resatrt:
        restart_server()
    else:
        run_foreground()


if __name__ == "__main__":
    main()
