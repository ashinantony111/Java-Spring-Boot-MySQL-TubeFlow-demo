import sys
import socket
import webbrowser
import threading
import time
import uvicorn
from app import config
from app.database import db_manager

def find_available_port(default_port=8000, max_tries=10):
    for port in range(default_port, default_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return default_port

def open_browser_delayed(url, delay=1.5):
    def _open():
        time.sleep(delay)
        print(f"\n[TubeFlow] Opening browser at {url} ...")
        webbrowser.open(url)
    t = threading.Thread(target=_open, daemon=True)
    t.start()

def main():
    port = find_available_port(config.APP_PORT)
    app_url = f"http://localhost:{port}"

    print("=" * 65)
    print("           TUBEFLOW - MYSQL YOUTUBE ALTERNATIVE APP           ")
    print("=" * 65)
    print(f" Web Application URL : {app_url}")
    print(f" MySQL Admin Console : {app_url}/database")
    print(f" API Documentation   : {app_url}/docs")
    print("-" * 65)
    print(f" Active Database     : {db_manager.active_engine_type.upper()}")
    print(f" MySQL Target DB     : {config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DB}")
    if db_manager.active_engine_type == "sqlite":
        print(f" Status Notice       : MySQL is offline/unreachable on {config.MYSQL_HOST}:{config.MYSQL_PORT}.")
        print(f"                       Using SQLite fallback ({config.SQLITE_DB_PATH.name}).")
        print(f"                       You can connect MySQL anytime via {app_url}/database !")
    else:
        print(f" Status Notice       : Connected to MySQL database successfully!")
    print("=" * 65)

    # Launch default web browser
    open_browser_delayed(app_url)

    # Run Uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, log_level="info", reload=False)

if __name__ == "__main__":
    main()
