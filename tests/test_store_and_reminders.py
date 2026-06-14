import sys,tempfile,unittest
from datetime import datetime as RealDateTime
from pathlib import Path
from unittest import mock
PROJECT_ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJECT_ROOT));import todo_server
class StoreAndReminderTests(unittest.TestCase):
 def test_normalize_store_keeps_current_shape_and_migrates_legacy_days(self):
  cur={'days':{'2026-06-14':[]},'recurring':[]};old={'2026-06-14':[{'id':'one'}]};self.assertIs(todo_server.normalize_store(cur),cur);self.assertEqual(todo_server.normalize_store(old),{'days':old,'recurring':[]});self.assertEqual(todo_server.normalize_store(None),todo_server.empty_store())
 def test_day_todos_combines_single_and_active_recurring_instances(self):
  s={'days':{'2026-06-14':[{'id':'single','title':'Single','done':False}]},'recurring':[{'id':'active','title':'Recurring','startDate':'2026-06-01','dayState':{'2026-06-14':{'done':True,'note':'today only'}}},{'id':'future','startDate':'2026-06-15'},{'id':'ended','startDate':'2026-06-01','endDate':'2026-06-14'},{'id':'deleted','startDate':'2026-06-01','deletedDates':['2026-06-14']}]} ;ts=todo_server.day_todos(s,RealDateTime(2026,6,14,9,0));self.assertEqual([t['id']for t in ts],['single','active']);self.assertEqual(ts[0]['source'],'single');self.assertEqual(ts[0]['instanceDate'],'2026-06-14');self.assertEqual(ts[1]['source'],'recurring');self.assertTrue(ts[1]['done']);self.assertEqual(ts[1]['note'],'today only')
 def test_check_due_reminders_notifies_due_todos_once_and_prunes_old_keys(self):
  class FixedDateTime(RealDateTime):
   @classmethod
   def now(cls):return cls(2026,6,14,10,5,30)
  s={'days':{'2026-06-14':[{'id':'due','title':'Due task','time':'10:00','remind':True,'done':False},{'id':'done','title':'Done task','time':'09:55','remind':True,'done':True},{'id':'bad-time','title':'Bad time','time':'oops','remind':True,'done':False}]},'recurring':[{'id':'repeat','title':'Repeat task','time':'09:00','remind':True,'done':False,'startDate':'2026-06-01','dayState':{}}]}
  with tempfile.TemporaryDirectory()as td:
   dd=Path(td)/'todo-data';sp=dd/'store.json';np=dd/'notified.json';dd.mkdir();todo_server.write_json(sp,s);todo_server.write_json(np,{'2026-06-13-old-09:00':'2026-06-13T09:00:00','2026-06-14-already-09:00':'2026-06-14T09:00:00'})
   with mock.patch.object(todo_server,'DATA_DIR',dd),mock.patch.object(todo_server,'STORE_PATH',sp),mock.patch.object(todo_server,'NOTIFIED_PATH',np),mock.patch.object(todo_server,'datetime',FixedDateTime),mock.patch.object(todo_server,'toast',return_value=True)as toast:todo_server.check_due_reminders()
   n=todo_server.read_json(np,{})
  self.assertEqual(toast.call_args_list,[mock.call('\u5f85\u529e\u63d0\u9192','10:00 Due task'),mock.call('\u5f85\u529e\u63d0\u9192','09:00 Repeat task')]);self.assertNotIn('2026-06-13-old-09:00',n);self.assertIn('2026-06-14-already-09:00',n);self.assertIn('2026-06-14-due-10:00',n);self.assertIn('2026-06-14-repeat-09:00',n)
if __name__=='__main__':unittest.main()
