import sys,unittest
from pathlib import Path
from unittest import mock
PROJECT_ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJECT_ROOT));import todo_server
class NotificationSupportTests(unittest.TestCase):
 def test_notification_launcher_prefers_start_script(self):
  x=todo_server.notification_launcher_path();self.assertEqual(x,PROJECT_ROOT/'start.bat');self.assertTrue(x.exists())
 def test_notification_shortcut_targets_start_menu_programs(self):
  x=todo_server.notification_shortcut_path();self.assertEqual(x.name,todo_server.APP_SHORTCUT_NAME);self.assertIn('Start Menu',str(x));self.assertIn('Programs',str(x))
 def test_toast_falls_back_to_balloon_notification(self):
  with mock.patch.object(todo_server,'show_windows_toast',return_value=False),mock.patch.object(todo_server,'show_balloon_notification',return_value=True)as f:self.assertTrue(todo_server.toast('title','body'));f.assert_called_once_with('title','body')
 def test_successful_toast_skips_balloon_fallback(self):
  with mock.patch.object(todo_server,'show_windows_toast',return_value=True),mock.patch.object(todo_server,'show_balloon_notification',return_value=True)as f:self.assertTrue(todo_server.toast('title','body'));f.assert_not_called()
 def test_windows_toast_uses_expected_powershell_command(self):
  c=mock.Mock(returncode=0);ts=PROJECT_ROOT/'send-toast.ps1'
  with mock.patch.object(todo_server,'ensure_notification_registration',return_value=True),mock.patch.object(todo_server,'TOAST_SCRIPT_PATH',ts),mock.patch.object(todo_server,'run_powershell',return_value=c)as r:self.assertTrue(todo_server.show_windows_toast('Title','Body'))
  r.assert_called_once_with(['-STA','-File',str(ts),'-AppId',todo_server.APP_ID,'-Title','Title','-Body','Body'],timeout=15)
if __name__=='__main__':unittest.main()
