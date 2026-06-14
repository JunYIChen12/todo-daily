import json,os,socket,subprocess,sys,threading,time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
F=getattr(sys,'frozen',False);ROOT=Path(sys.executable if F else __file__).resolve().parent
if F and ROOT.name=='dist' and ROOT.parent.name=='artifacts':ROOT=ROOT.parent.parent
DATA_DIR=ROOT/'todo-data';STORE_PATH=DATA_DIR/'store.json';NOTIFIED_PATH=DATA_DIR/'notified.json';HOST='127.0.0.1';PORT=8765;LOCK_PORT=18765;REMINDER_CATCH_UP_MINUTES=720;STARTUP_REMINDER_DELAY_SECONDS=30;APP_ID='TodoDaily.Background';APP_NAME='Daily Todo';APP_SHORTCUT_NAME='Daily Todo.lnk';PROGRAMS_DIR=Path(os.environ.get('APPDATA',''))/'Microsoft'/'Windows'/'Start Menu'/'Programs';SHORTCUT_SCRIPT_PATH=ROOT/'register-toast-shortcut.ps1';TOAST_SCRIPT_PATH=ROOT/'send-toast.ps1';TRAY_SCRIPT_PATH=ROOT/'tray-icon.ps1';NOTIFICATION_DURATION_MS=45000;NOTIFICATION_KEEPALIVE_SECONDS=50;CREATE_NO_WINDOW=getattr(subprocess,'CREATE_NO_WINDOW',0);_notification_registration_ready=False
def empty_store():return {'days':{},'recurring':[]}
def read_json(path,fallback):
    try:
        with path.open('r',encoding='utf-8-sig')as f:return json.load(f)
    except Exception:return fallback
def write_json(path,data):
    DATA_DIR.mkdir(exist_ok=True);t=path.with_suffix('.tmp')
    with t.open('w',encoding='utf-8')as f:json.dump(data,f,ensure_ascii=False,indent=2)
    t.replace(path)
def normalize_store(data):return data if isinstance(data,dict)and isinstance(data.get('days'),dict)and isinstance(data.get('recurring'),list)else({'days':data,'recurring':[]}if isinstance(data,dict)else empty_store())
def date_key(value):return value.strftime('%Y-%m-%d')
def day_todos(store,target_date):
    k=date_key(target_date);out=[]
    for t in store.get('days',{}).get(k,[]):i=dict(t);i.update(source='single',instanceDate=k);out.append(i)
    for t in store.get('recurring',[]):
        if t.get('startDate','')>k or t.get('endDate')and k>=t.get('endDate')or k in t.get('deletedDates',[]):continue
        i=dict(t);i.update(t.get('dayState',{}).get(k,{}));i.update(source='recurring',instanceDate=k);out.append(i)
    return out
def notification_launcher_path():
    for p in (ROOT/'start.bat',ROOT/'TodoDailyServer.exe'):
        if p.exists():return p
    return Path(sys.executable).resolve()if F else Path(__file__).resolve()
def notification_icon_path():
    p=ROOT/'TodoDailyServer.exe';return p if p.exists()else Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32'/'shell32.dll'
def notification_shortcut_path():return PROGRAMS_DIR/APP_SHORTCUT_NAME
def run_powershell(args,timeout):return subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass',*args],check=False,creationflags=CREATE_NO_WINDOW,capture_output=True,text=True,timeout=timeout)
def ensure_notification_registration():
    global _notification_registration_ready
    if _notification_registration_ready:return True
    l=notification_launcher_path()
    if not l.exists()or not SHORTCUT_SCRIPT_PATH.exists():return False
    try:
        r=run_powershell(['-File',str(SHORTCUT_SCRIPT_PATH),'-ShortcutPath',str(notification_shortcut_path()),'-TargetPath',str(l),'-AppId',APP_ID,'-Description',APP_NAME,'-WorkingDirectory',str(ROOT),'-IconPath',str(notification_icon_path())],20)
        if r.returncode:print(f'Notification registration failed: {r.stderr or r.stdout}');return False
        _notification_registration_ready=True;return True
    except Exception as e:print(f'Notification registration failed: {e}');return False
def show_windows_toast(title,body):
    if not ensure_notification_registration()or not TOAST_SCRIPT_PATH.exists():return False
    try:
        r=run_powershell(['-STA','-File',str(TOAST_SCRIPT_PATH),'-AppId',APP_ID,'-Title',str(title),'-Body',str(body)],timeout=15)
        if r.returncode:print(f'Toast failed: {r.stderr or r.stdout}');return False
        return True
    except Exception as e:print(f'Toast failed: {e}');return False
def escape_powershell(value):return str(value).replace("'","''").replace('\r',' ').replace('\n',' ')
def show_balloon_notification(title,body):
    title=escape_powershell(title);body=escape_powershell(body);script=f"""$ErrorActionPreference='Stop';Add-Type -AssemblyName System.Windows.Forms;Add-Type -AssemblyName System.Drawing;$n=New-Object System.Windows.Forms.NotifyIcon;$shown=$false;$closed=$false;try{{$n.Icon=[System.Drawing.SystemIcons]::Information;$n.Text='Daily Todo';$n.BalloonTipIcon=[System.Windows.Forms.ToolTipIcon]::Info;$n.BalloonTipTitle='{title}';$n.BalloonTipText='{body}';$n.add_BalloonTipShown({{$script:shown=$true}});$n.add_BalloonTipClosed({{$script:closed=$true}});$n.add_BalloonTipClicked({{$script:closed=$true}});$n.Visible=$true;$n.ShowBalloonTip({NOTIFICATION_DURATION_MS});$d=[DateTime]::Now.AddSeconds({NOTIFICATION_KEEPALIVE_SECONDS});while([DateTime]::Now -lt $d -and -not $closed){{[System.Windows.Forms.Application]::DoEvents();Start-Sleep -Milliseconds 200}};if(-not $shown){{exit 2}}}}finally{{$n.Visible=$false;$n.Dispose()}}"""
    try:
        r=run_powershell(['-STA','-Command',script],NOTIFICATION_KEEPALIVE_SECONDS+10)
        if r.returncode:print(f'Balloon notification failed: {r.stderr or r.stdout}');return False
        return True
    except Exception as e:print(f'Balloon notification failed: {e}');return False
def toast(title,body):return True if show_windows_toast(title,body)else show_balloon_notification(title,body)
def start_tray_icon():
    l=notification_launcher_path()
    if not TRAY_SCRIPT_PATH.exists()or not l.exists():return
    try:subprocess.Popen(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-STA','-WindowStyle','Hidden','-File',str(TRAY_SCRIPT_PATH),'-ParentPid',str(os.getpid()),'-LauncherPath',str(l),'-WorkingDirectory',str(ROOT)],creationflags=CREATE_NO_WINDOW)
    except Exception as e:print(f'Tray icon failed: {e}')
def reminder_loop():
    time.sleep(STARTUP_REMINDER_DELAY_SECONDS)
    while True:
        try:check_due_reminders()
        except Exception as e:print(f'Reminder check failed: {e}')
        time.sleep(20)
def notification_keys_before(notified,today_key):return[k for k in notified if not k.startswith(today_key)]
def todo_time_minutes(todo):
    try:h,m=[int(x)for x in todo['time'].split(':')[:2]];return h*60+m
    except Exception:return None
def is_reminder_due(todo_minutes,current_minutes):return todo_minutes<=current_minutes<=todo_minutes+REMINDER_CATCH_UP_MINUTES
def reminder_key(todo,today_key):return f"{today_key}-{todo.get('id')}-{todo.get('time')}"
def check_due_reminders():
    store=normalize_store(read_json(STORE_PATH,empty_store()));notified=read_json(NOTIFIED_PATH,{});now=datetime.now();k=date_key(now);cm=now.hour*60+now.minute;changed=False
    for old in notification_keys_before(notified,k):del notified[old];changed=True
    for t in day_todos(store,now):
        if not t.get('time')or not t.get('remind')or t.get('done'):continue
        tm=todo_time_minutes(t)
        if tm is None:continue
        rk=reminder_key(t,k)
        if is_reminder_due(tm,cm)and rk not in notified and toast('\u5f85\u529e\u63d0\u9192',f"{t.get('time')} {t.get('title','')}"):
            notified[rk]=now.isoformat(timespec='seconds');changed=True
    if changed:write_json(NOTIFIED_PATH,notified)
class TodoHandler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,format,*args):return
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/api/store':return self.send_json(normalize_store(read_json(STORE_PATH,empty_store())))
        if p=='/api/status':return self.send_json({'ok':True,'backgroundReminders':True})
        if p=='/api/test-notification':toast('Daily Todo test','Background reminders work.');return self.send_json({'ok':True})
        super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path!='/api/store':return self.send_error(404)
        try:
            store=normalize_store(json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))).decode('utf-8')));cur=normalize_store(read_json(STORE_PATH,empty_store()))
            if has_todos(cur)and not has_todos(store):return self.send_json({'ok':False,'error':'Refusing to replace non-empty store with an empty store'},409)
            write_json(STORE_PATH,store);self.send_json({'ok':True})
        except Exception as e:self.send_json({'ok':False,'error':str(e)},400)
    def send_json(self,data,status=200):
        b=json.dumps(data,ensure_ascii=False).encode('utf-8');self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
def has_todos(store):return any(isinstance(x,list)and x for x in store.get('days',{}).values())or bool(store.get('recurring'))
def main():
    lock_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:lock_socket.bind((HOST,LOCK_PORT));lock_socket.listen(1)
    except OSError:print('Daily Todo already running.');return
    DATA_DIR.mkdir(exist_ok=True)
    if not STORE_PATH.exists():write_json(STORE_PATH,empty_store())
    ensure_notification_registration();start_tray_icon();threading.Thread(target=reminder_loop,daemon=True).start();server=ThreadingHTTPServer((HOST,PORT),TodoHandler);print(f'Daily Todo: http://{HOST}:{PORT}/index.html');print('Close this window to stop background reminders.');server.serve_forever()
if __name__=='__main__':main()
