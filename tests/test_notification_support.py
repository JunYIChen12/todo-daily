from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import todo_server  # noqa: E402


class NotificationSupportTests(unittest.TestCase):
    def test_notification_launcher_prefers_start_script(self) -> None:
        launcher = todo_server.notification_launcher_path()

        self.assertEqual(launcher, PROJECT_ROOT / "start.bat")
        self.assertTrue(launcher.exists())

    def test_notification_shortcut_targets_start_menu_programs(self) -> None:
        shortcut = todo_server.notification_shortcut_path()

        self.assertEqual(shortcut.name, todo_server.APP_SHORTCUT_NAME)
        self.assertIn("Start Menu", str(shortcut))
        self.assertIn("Programs", str(shortcut))

    def test_toast_falls_back_to_balloon_notification(self) -> None:
        with (
            mock.patch.object(todo_server, "show_windows_toast", return_value=False),
            mock.patch.object(todo_server, "show_balloon_notification", return_value=True) as fallback,
        ):
            ok = todo_server.toast("title", "body")

        self.assertTrue(ok)
        fallback.assert_called_once_with("title", "body")

    def test_successful_toast_skips_balloon_fallback(self) -> None:
        with (
            mock.patch.object(todo_server, "show_windows_toast", return_value=True),
            mock.patch.object(todo_server, "show_balloon_notification", return_value=True) as fallback,
        ):
            ok = todo_server.toast("title", "body")

        self.assertTrue(ok)
        fallback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
