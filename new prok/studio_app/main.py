#!/usr/bin/env python3
"""Студия — десктопное приложение управления студией (PyQt6)."""

import sys

from PyQt6.QtWidgets import QApplication, QDialog

from app.dialogs import AuthDialog, IntroDialog
from app.storage import Storage
from app.student_window import StudentWindow
from app.theme import get_stylesheet
from app.trainer_window import TrainerWindow


class StudioApp:
    def __init__(self) -> None:
        self.storage = Storage()
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Студия")
        self.main_window: TrainerWindow | StudentWindow | None = None

    def _apply_theme(self, theme: str | None = None) -> None:
        t = theme or self.storage.theme
        self.app.setStyleSheet(get_stylesheet(t))
        if self.main_window:
            self.main_window.apply_theme(t)

    def _show_auth(self) -> None:
        if self.main_window:
            self.main_window.close()
            self.main_window.deleteLater()
            self.main_window = None

        auth = AuthDialog(self.storage)
        self._apply_theme()
        if auth.exec() != QDialog.DialogCode.Accepted or not auth.user:
            self.app.quit()
            return

        intro = IntroDialog(auth.user)
        self._apply_theme()
        if intro.exec() != QDialog.DialogCode.Accepted:
            self._show_auth()
            return

        user = auth.user
        if user["role"] == "trainer":
            self.main_window = TrainerWindow(
                self.storage, user, self._show_auth, self._apply_theme
            )
        else:
            self.main_window = StudentWindow(
                self.storage, user, self._show_auth, self._apply_theme
            )
        self._apply_theme()
        self.main_window.show()

    def run(self) -> int:
        self._show_auth()
        return self.app.exec()


def main() -> int:
    return StudioApp().run()


if __name__ == "__main__":
    sys.exit(main())
