"""Личный кабинет ученика."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from app.constants import DAYS, PAYMENT_METHODS
from app.storage import Storage
from app.theme import get_stylesheet
from app.widgets import setup_table, set_table_row


class StudentWindow(QMainWindow):
    def __init__(self, storage: Storage, user: dict, on_logout, on_theme_toggle, parent=None) -> None:
        super().__init__(parent)
        self.storage = storage
        self.user = user
        self.on_logout = on_logout
        self.on_theme_toggle = on_theme_toggle
        self.setObjectName("studentWindow")
        self.setWindowTitle("Личный кабинет")
        self.resize(800, 600)
        self._build()

    def _build(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QHBoxLayout()
        title = QLabel("Личный кабинет")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #ff2d2d;")
        header.addWidget(title)
        header.addStretch()
        self.theme_btn = QPushButton("Тёмная тема" if self.storage.theme == "dark" else "Светлая тема")
        self.theme_btn.clicked.connect(self._toggle_theme)
        header.addWidget(self.theme_btn)
        logout = QPushButton("Выйти")
        logout.clicked.connect(self.on_logout)
        header.addWidget(logout)
        layout.addLayout(header)

        client = next((c for c in self.storage.clients if c["id"] == self.user.get("clientId")), None)
        name = self.user.get("name") or (client["name"] if client else "—")
        welcome = QGroupBox(f"Добро пожаловать, {name}")
        layout.addWidget(welcome)

        sched_box = QGroupBox("Моё расписание")
        sl = QVBoxLayout(sched_box)
        self.sched_table = QTableWidget()
        setup_table(self.sched_table, ["День", "Группа", "Время"])
        sl.addWidget(self.sched_table)
        layout.addWidget(sched_box)

        subs_box = QGroupBox("Мой абонемент")
        subl = QVBoxLayout(subs_box)
        self.subs_table = QTableWidget()
        setup_table(self.subs_table, ["Абонемент", "Занятий осталось", "Дата покупки"])
        subl.addWidget(self.subs_table)
        layout.addWidget(subs_box)

        pay_box = QGroupBox("Мои оплаты")
        pl = QVBoxLayout(pay_box)
        self.pay_table = QTableWidget()
        setup_table(self.pay_table, ["Дата", "Сумма", "Способ", "Комментарий"])
        pl.addWidget(self.pay_table)
        layout.addWidget(pay_box)

        self.refresh()

    def _toggle_theme(self) -> None:
        self.storage.theme = "light" if self.storage.theme == "dark" else "dark"
        self.storage.save_theme()
        self.on_theme_toggle(self.storage.theme)
        self.theme_btn.setText("Тёмная тема" if self.storage.theme == "dark" else "Светлая тема")

    def refresh(self) -> None:
        client = next((c for c in self.storage.clients if c["id"] == self.user.get("clientId")), None)
        group = client.get("group", "") if client else ""
        sched = [s for s in self.storage.schedule if s.get("group") == group]
        self.sched_table.setRowCount(0)
        for s in sched:
            row = self.sched_table.rowCount()
            set_table_row(self.sched_table, row, [DAYS.get(s["day"], s["day"]), s["group"], s["time"]])

        subs = [cs for cs in self.storage.client_subs if cs["clientId"] == self.user.get("clientId")]
        self.subs_table.setRowCount(0)
        for cs in subs:
            row = self.subs_table.rowCount()
            set_table_row(
                self.subs_table, row,
                [self.storage.sub_type_name(cs["subTypeId"]), cs.get("sessionsLeft", ""), cs.get("boughtAt", "")],
            )

        pays = [p for p in reversed(self.storage.payments) if p["clientId"] == self.user.get("clientId")]
        self.pay_table.setRowCount(0)
        for p in pays:
            row = self.pay_table.rowCount()
            method = PAYMENT_METHODS.get(p.get("method"), p.get("method"))
            set_table_row(self.pay_table, row, [p["date"], f"{p['amount']} ₽", method, p.get("comment", "")])

    def apply_theme(self, theme: str) -> None:
        self.setStyleSheet(get_stylesheet(theme, student=True))
