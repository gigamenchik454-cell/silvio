"""Диалоги входа и вступительного экрана."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.constants import INTRO_PROFILES
from app.storage import ASSETS_DIR, Storage
from app.widgets import hint_label, primary_button


class AuthDialog(QDialog):
    """Экран входа (тренер / ученик)."""

    def __init__(self, storage: Storage, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.storage = storage
        self.user: dict | None = None
        self.setWindowTitle("Вход в Студию")
        self.setFixedSize(400, 420)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("Вход в Студию")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        tabs = QHBoxLayout()
        self.btn_trainer = QPushButton("Тренер")
        self.btn_student = QPushButton("Ученик")
        for btn in (self.btn_trainer, self.btn_student):
            btn.setCheckable(True)
            btn.setStyleSheet(
                "QPushButton { padding: 10px; border-radius: 8px; border: 1px solid #333; }"
                "QPushButton:checked { background: #e24a4a; color: white; border-color: #e24a4a; }"
            )
            tabs.addWidget(btn)
        self.btn_trainer.setChecked(True)
        self.role_group = QButtonGroup(self)
        self.role_group.addButton(self.btn_trainer)
        self.role_group.addButton(self.btn_student)
        layout.addLayout(tabs)

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин")
        layout.addWidget(QLabel("Логин"))
        layout.addWidget(self.login_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Пароль")
        layout.addWidget(QLabel("Пароль"))
        layout.addWidget(self.password_edit)

        self.name_label = QLabel("Имя")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Как к вам обращаться")
        self.name_hint = hint_label("Ваше имя для отображения в личном кабинете")
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.name_hint)
        self.name_label.hide()
        self.name_edit.hide()
        self.name_hint.hide()

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c;")
        layout.addWidget(self.error_label)

        submit = primary_button("Войти")
        submit.clicked.connect(self._submit)
        layout.addWidget(submit)

        self.btn_trainer.clicked.connect(self._on_role)
        self.btn_student.clicked.connect(self._on_role)
        self.password_edit.returnPressed.connect(self._submit)
        self.login_edit.returnPressed.connect(self._submit)

    def _on_role(self) -> None:
        student = self.btn_student.isChecked()
        self.name_label.setVisible(student)
        self.name_edit.setVisible(student)
        self.name_hint.setVisible(student)
        self.error_label.clear()

    def _submit(self) -> None:
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        self.error_label.clear()

        if self.btn_trainer.isChecked():
            trainer = next(
                (t for t in self.storage.trainers if t["login"] == login and t["password"] == password),
                None,
            )
            if not trainer:
                self.error_label.setText("Неверный логин или пароль")
                return
            self.user = {"role": "trainer", "login": login}
        else:
            student = next(
                (s for s in self.storage.students if s["login"] == login and s["password"] == password),
                None,
            )
            if not student:
                self.error_label.setText("Неверный логин или пароль")
                return
            client = next((c for c in self.storage.clients if c["id"] == student["clientId"]), None)
            name = self.name_edit.text().strip() or (client["name"] if client else login)
            self.user = {
                "role": "student",
                "clientId": student["clientId"],
                "name": name,
            }
        self.accept()


class IntroDialog(QDialog):
    """Вступительный экран после входа."""

    def __init__(self, user: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Добро пожаловать")
        self.setMinimumSize(800, 450)
        self._build()

    def _profile_key(self) -> str:
        if self.user.get("role") == "student":
            return "student"
        if self.user.get("role") == "trainer" and self.user.get("login") == "admin":
            return "trainer_admin"
        return "trainer"

    def _build(self) -> None:
        profile = INTRO_PROFILES[self._profile_key()]
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(40, 40, 40, 40)

        title = QLabel(profile["title"])
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        title.setWordWrap(True)
        text_col.addWidget(title)

        for key in ("text1", "text2"):
            p = QLabel(profile[key])
            p.setWordWrap(True)
            text_col.addWidget(p)

        text_col.addStretch()
        hint = QLabel(profile["hint"])
        hint.setStyleSheet("color: #e24a4a; font-size: 9pt;")
        text_col.addWidget(hint)

        btn = primary_button("Продолжить")
        btn.clicked.connect(self.accept)
        text_col.addWidget(btn)
        layout.addLayout(text_col, 1)

        img_path = ASSETS_DIR / profile["image"]
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_label.setMinimumWidth(320)
        if img_path.exists():
            pix = QPixmap(str(img_path))
            if profile.get("logo"):
                img_label.setStyleSheet("background: #000;")
                scaled = pix.scaled(280, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            else:
                scaled = pix.scaled(360, 400, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            img_label.setPixmap(scaled)
        else:
            img_label.setText(f"Положите {profile['image']} в папку assets")
            img_label.setStyleSheet("color: #8a8a8a; padding: 20px;")
        layout.addWidget(img_label, 1)
