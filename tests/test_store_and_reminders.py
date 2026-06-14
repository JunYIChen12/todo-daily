from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime as RealDateTime
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import todo_server  # noqa: E402


class StoreAndReminderTests(unittest.TestCase):
    def test_normalize_store_keeps_current_shape_and_migrates_legacy_days(self) -> None:
        current = {"days": {"2026-06-14": []}, "recurring": []}
        legacy = {"2026-06-14": [{"id": "one"}]}

        self.assertIs(todo_server.normalize_store(current), current)
        self.assertEqual(todo_server.normalize_store(legacy), {"days": legacy, "recurring": []})
        self.assertEqual(todo_server.normalize_store(None), todo_server.empty_store())

    def test_day_todos_combines_single_and_active_recurring_instances(self) -> None:
        store = {
            "days": {
                "2026-06-14": [
                    {"id": "single", "title": "Single", "done": False},
                ]
            },
            "recurring": [
                {
                    "id": "active",
                    "title": "Recurring",
                    "startDate": "2026-06-01",
                    "dayState": {"2026-06-14": {"done": True, "note": "today only"}},
                },
                {"id": "future", "startDate": "2026-06-15"},
                {"id": "ended", "startDate": "2026-06-01", "endDate": "2026-06-14"},
                {"id": "deleted", "startDate": "2026-06-01", "deletedDates": ["2026-06-14"]},
            ],
        }

        todos = todo_server.day_todos(store, RealDateTime(2026, 6, 14, 9, 0))

        self.assertEqual([todo["id"] for todo in todos], ["single", "active"])
        self.assertEqual(todos[0]["source"], "single")
        self.assertEqual(todos[0]["instanceDate"], "2026-06-14")
        self.assertEqual(todos[1]["source"], "recurring")
        self.assertTrue(todos[1]["done"])
        self.assertEqual(todos[1]["note"], "today only")

    def test_check_due_reminders_notifies_due_todos_once_and_prunes_old_keys(self) -> None:
        class FixedDateTime(RealDateTime):
            @classmethod
            def now(cls) -> "FixedDateTime":
                return cls(2026, 6, 14, 10, 5, 30)

        store = {
            "days": {
                "2026-06-14": [
                    {"id": "due", "title": "Due task", "time": "10:00", "remind": True, "done": False},
                    {"id": "done", "title": "Done task", "time": "09:55", "remind": True, "done": True},
                    {"id": "bad-time", "title": "Bad time", "time": "oops", "remind": True, "done": False},
                ]
            },
            "recurring": [
                {
                    "id": "repeat",
                    "title": "Repeat task",
                    "time": "09:00",
                    "remind": True,
                    "done": False,
                    "startDate": "2026-06-01",
                    "dayState": {},
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "todo-data"
            store_path = data_dir / "store.json"
            notified_path = data_dir / "notified.json"
            data_dir.mkdir()
            todo_server.write_json(store_path, store)
            todo_server.write_json(
                notified_path,
                {
                    "2026-06-13-old-09:00": "2026-06-13T09:00:00",
                    "2026-06-14-already-09:00": "2026-06-14T09:00:00",
                },
            )

            with (
                mock.patch.object(todo_server, "DATA_DIR", data_dir),
                mock.patch.object(todo_server, "STORE_PATH", store_path),
                mock.patch.object(todo_server, "NOTIFIED_PATH", notified_path),
                mock.patch.object(todo_server, "datetime", FixedDateTime),
                mock.patch.object(todo_server, "toast", return_value=True) as toast,
            ):
                todo_server.check_due_reminders()

            notified = todo_server.read_json(notified_path, {})

        self.assertEqual(
            toast.call_args_list,
            [
                mock.call("待办提醒", "10:00 Due task"),
                mock.call("待办提醒", "09:00 Repeat task"),
            ],
        )
        self.assertNotIn("2026-06-13-old-09:00", notified)
        self.assertIn("2026-06-14-already-09:00", notified)
        self.assertIn("2026-06-14-due-10:00", notified)
        self.assertIn("2026-06-14-repeat-09:00", notified)


if __name__ == "__main__":
    unittest.main()
