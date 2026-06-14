import json
import os
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
    if ROOT.name == "dist" and ROOT.parent.name == "artifacts":
        ROOT = ROOT.parent.parent
else:
    ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "todo-data"
STORE_PATH = DATA_DIR / "store.json"
NOTIFIED_PATH = DATA_DIR / "notified.json"
HOST = "127.0.0.1"
PORT = 8765
REMINDER_CATCH_UP_MINUTES = 12 * 60
STARTUP_REMINDER_DELAY_SECONDS = 30
LOCK_PORT = 18765
APP_ID = "TodoDaily.Background"
APP_NAME = "Daily Todo"
APP_SHORTCUT_NAME = "Daily Todo.lnk"
PROGRAMS_DIR = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
SHORTCUT_SCRIPT_PATH = ROOT / "register-toast-shortcut.ps1"
TOAST_SCRIPT_PATH = ROOT / "send-toast.ps1"
TRAY_SCRIPT_PATH = ROOT / "tray-icon.ps1"
NOTIFICATION_DURATION_MS = 45000
NOTIFICATION_KEEPALIVE_SECONDS = 50
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

_notification_registration_ready = False


def empty_store():
    return {"days": {}, "recurring": []}


def read_json(path, fallback):
    try:
      with path.open("r", encoding="utf-8-sig") as file:
          data = json.load(file)
      return data
    except Exception:
      return fallback


def write_json(path, data):
    DATA_DIR.mkdir(exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temp_path.replace(path)


def normalize_store(data):
    if isinstance(data, dict) and isinstance(data.get("days"), dict) and isinstance(data.get("recurring"), list):
        return data
    if isinstance(data, dict):
        return {"days": data, "recurring": []}
    return empty_store()


def date_key(value):
    return value.strftime("%Y-%m-%d")


def day_todos(store, target_date):
    target_key = date_key(target_date)
    todos = []

    for todo in store.get("days", {}).get(target_key, []):
        item = dict(todo)
        item["source"] = "single"
        item["instanceDate"] = target_key
        todos.append(item)

    for todo in store.get("recurring", []):
        if todo.get("startDate", "") > target_key:
            continue
        if todo.get("endDate") and target_key >= todo.get("endDate"):
            continue
        if target_key in todo.get("deletedDates", []):
            continue
        item = dict(todo)
        item.update(todo.get("dayState", {}).get(target_key, {}))
        item["source"] = "recurring"
        item["instanceDate"] = target_key
        todos.append(item)

    return todos


def notification_launcher_path():
    start_script = ROOT / "start.bat"
    if start_script.exists():
        return start_script

    packaged_exe = ROOT / "TodoDailyServer.exe"
    if packaged_exe.exists():
        return packaged_exe

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return Path(__file__).resolve()


def notification_icon_path():
    packaged_exe = ROOT / "TodoDailyServer.exe"
    if packaged_exe.exists():
        return packaged_exe
    return Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "shell32.dll"


def notification_shortcut_path():
    return PROGRAMS_DIR / APP_SHORTCUT_NAME


def run_powershell(args, timeout):
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", *args],
        check=False,
        creationflags=CREATE_NO_WINDOW,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def ensure_notification_registration():
    global _notification_registration_ready
    if _notification_registration_ready:
        return True

    launcher = notification_launcher_path()
    if not launcher.exists() or not SHORTCUT_SCRIPT_PATH.exists():
        return False

    try:
        result = run_powershell(
            [
                "-File",
                str(SHORTCUT_SCRIPT_PATH),
                "-ShortcutPath",
                str(notification_shortcut_path()),
                "-TargetPath",
                str(launcher),
                "-AppId",
                APP_ID,
                "-Description",
                APP_NAME,
                "-WorkingDirectory",
                str(ROOT),
                "-IconPath",
                str(notification_icon_path()),
            ],
            timeout=20,
        )
        if result.returncode != 0:
            print(f"Notification registration failed: {result.stderr or result.stdout}")
            return False
        _notification_registration_ready = True
        return True
    except Exception as error:
        print(f"Notification registration failed: {error}")
        return False


def show_windows_toast(title, body):
    if not ensure_notification_registration() or not TOAST_SCRIPT_PATH.exists():
        return False

    try:
        result = run_powershell(
            [
                "-STA",
                "-File",
                str(TOAST_SCRIPT_PATH),
                "-AppId",
                APP_ID,
                "-Title",
                str(title),
                "-Body",
                str(body),
            ],
            timeout=15,
        )
        if result.returncode != 0:
            print(f"Toast failed: {result.stderr or result.stdout}")
            return False
        return True
    except Exception as error:
        print(f"Toast failed: {error}")
        return False


def show_balloon_notification(title, body):
    title = escape_powershell(title)
    body = escape_powershell(body)
    script = f"""
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$notify = New-Object System.Windows.Forms.NotifyIcon
$shown = $false
$closed = $false
try {{
  $notify.Icon = [System.Drawing.SystemIcons]::Information
  $notify.Text = "Daily Todo"
  $notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
  $notify.BalloonTipTitle = '{title}'
  $notify.BalloonTipText = '{body}'
  $notify.add_BalloonTipShown({{ $script:shown = $true }})
  $notify.add_BalloonTipClosed({{ $script:closed = $true }})
  $notify.add_BalloonTipClicked({{ $script:closed = $true }})
  $notify.Visible = $true
  $notify.ShowBalloonTip({NOTIFICATION_DURATION_MS})
  $deadline = [DateTime]::Now.AddSeconds({NOTIFICATION_KEEPALIVE_SECONDS})
  while ([DateTime]::Now -lt $deadline -and -not $closed) {{
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 200
  }}
  if (-not $shown) {{
    exit 2
  }}
}} finally {{
  $notify.Visible = $false
  $notify.Dispose()
}}
"""
    try:
        result = run_powershell(
            ["-STA", "-Command", script],
            timeout=NOTIFICATION_KEEPALIVE_SECONDS + 10,
        )
        if result.returncode != 0:
            print(f"Balloon notification failed: {result.stderr or result.stdout}")
            return False
        return True
    except Exception as error:
        print(f"Balloon notification failed: {error}")
        return False


def toast(title, body):
    if show_windows_toast(title, body):
        return True
    return show_balloon_notification(title, body)


def escape_powershell(value):
    return str(value).replace("'", "''").replace("\r", " ").replace("\n", " ")


def start_tray_icon():
    if not TRAY_SCRIPT_PATH.exists():
        return

    launcher = notification_launcher_path()
    if not launcher.exists():
        return

    try:
        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-STA",
                "-WindowStyle",
                "Hidden",
                "-File",
                str(TRAY_SCRIPT_PATH),
                "-ParentPid",
                str(os.getpid()),
                "-LauncherPath",
                str(launcher),
                "-WorkingDirectory",
                str(ROOT),
            ],
            creationflags=CREATE_NO_WINDOW,
        )
    except Exception as error:
        print(f"Tray icon failed: {error}")


def reminder_loop():
    time.sleep(STARTUP_REMINDER_DELAY_SECONDS)
    while True:
        try:
            check_due_reminders()
        except Exception as error:
            print(f"Reminder check failed: {error}")
        time.sleep(20)


def notification_keys_before(notified, today_key):
    return [key for key in notified if not key.startswith(today_key)]


def todo_time_minutes(todo):
    try:
        hours, minutes = [int(part) for part in todo["time"].split(":")[:2]]
    except Exception:
        return None
    return hours * 60 + minutes


def is_reminder_due(todo_minutes, current_minutes):
    return todo_minutes <= current_minutes <= todo_minutes + REMINDER_CATCH_UP_MINUTES


def reminder_key(todo, today_key):
    return f"{today_key}-{todo.get('id')}-{todo.get('time')}"


def check_due_reminders():
    store = normalize_store(read_json(STORE_PATH, empty_store()))
    notified = read_json(NOTIFIED_PATH, {})
    now = datetime.now()
    today_key = date_key(now)
    current_minutes = now.hour * 60 + now.minute
    changed = False

    for key in notification_keys_before(notified, today_key):
        del notified[key]
        changed = True

    for todo in day_todos(store, now):
        if not todo.get("time") or not todo.get("remind") or todo.get("done"):
            continue
        todo_minutes = todo_time_minutes(todo)
        if todo_minutes is None:
            continue
        key = reminder_key(todo, today_key)
        if is_reminder_due(todo_minutes, current_minutes) and key not in notified:
            if toast("待办提醒", f"{todo.get('time')} {todo.get('title', '')}"):
                notified[key] = now.isoformat(timespec="seconds")
                changed = True

    if changed:
        write_json(NOTIFIED_PATH, notified)


class TodoHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/store":
            self.send_json(normalize_store(read_json(STORE_PATH, empty_store())))
            return
        if parsed.path == "/api/status":
            self.send_json({"ok": True, "backgroundReminders": True})
            return
        if parsed.path == "/api/test-notification":
            toast("每日待办后台测试", "如果你看到这条，关闭网页后也能收到提醒。")
            self.send_json({"ok": True})
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/store":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        try:
            body = self.rfile.read(length).decode("utf-8")
            store = normalize_store(json.loads(body))
            current_store = normalize_store(read_json(STORE_PATH, empty_store()))
            if has_todos(current_store) and not has_todos(store):
                self.send_json({"ok": False, "error": "Refusing to replace non-empty store with an empty store"}, status=409)
                return
            write_json(STORE_PATH, store)
            self.send_json({"ok": True})
        except Exception as error:
            self.send_json({"ok": False, "error": str(error)}, status=400)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def has_todos(store):
    return any(isinstance(todos, list) and todos for todos in store.get("days", {}).values()) or bool(store.get("recurring"))


def main():
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock_socket.bind((HOST, LOCK_PORT))
        lock_socket.listen(1)
    except OSError:
        print("每日待办后台已经在运行。")
        return

    DATA_DIR.mkdir(exist_ok=True)
    if not STORE_PATH.exists():
        write_json(STORE_PATH, empty_store())
    ensure_notification_registration()
    start_tray_icon()
    threading.Thread(target=reminder_loop, daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), TodoHandler)
    print(f"每日待办后台已启动: http://{HOST}:{PORT}/index.html")
    print("关闭网页后提醒仍会运行；关闭此窗口后后台提醒会停止。")
    server.serve_forever()


if __name__ == "__main__":
    main()
