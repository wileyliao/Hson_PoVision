import os
import signal
import psutil


def find_flask_pid_by_name(name):
    # 查找所有正在運行的進程，並根據名稱匹配 Flask 應用的 PID
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name']:
                for cmd in proc.cmdline():
                    if name in cmd:  # 匹配命令行參數中的應用名稱
                        return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


def shutdown_flask_app_by_name(name):
    pid = find_flask_pid_by_name(name)
    if pid:
        print(f"Sending SIGTERM to Flask application '{name}' (PID: {pid})")
        os.kill(pid, signal.SIGTERM)  # 發送 SIGTERM 信號

        try:
            print("Waiting for Flask application to shut down...")
            psutil.Process(pid).wait()  # 等待應用程序結束
        except psutil.NoSuchProcess:
            print(f"Process with PID {pid} no longer exists. Application has been shut down.")

        print(f"Flask application '{name}' has been shut down.")
    else:
        print(f"Flask application '{name}' is not running.")


if __name__ == "__main__":
    # 假設你在命令行中以 'po_vision_app' 作為參數啟動該應用
    shutdown_flask_app_by_name('OCR_app')
