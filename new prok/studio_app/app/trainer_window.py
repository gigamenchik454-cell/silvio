"""Главное окно тренера."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.sections import (
    AccountsSection,
    AttendanceSection,
    ClientsSection,
    PaymentsSection,
    ReportsSection,
    ScheduleSection,
    SubscriptionsSection,
)
from app.storage import Storage
from app.theme import get_stylesheet
from app.widgets import primary_button


class TrainerWindow(QMainWindow):
    def __init__(self, storage: Storage, user: dict, on_logout, on_theme_toggle, parent=None) -> None:
        super().__init__(parent)
        self.storage = storage
        self.user = user
        self.on_logout = on_logout
        self.on_theme_toggle = on_theme_toggle
        self.setWindowTitle("Студия — управление")
        self.resize(1000, 700)
        self._sections: list = []
        self._build()

    def _build(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QHBoxLayout()
        title = QLabel("Студия")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        self.theme_btn = QPushButton("Тёмная тема" if self.storage.theme == "dark" else "Светлая тема")
        self.theme_btn.clicked.connect(self._toggle_theme)
        header.addWidget(self.theme_btn)
        logout = QPushButton("Выйти")
        logout.clicked.connect(self.on_logout)
        header.addWidget(logout)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.clients_sec = ClientsSection(self.storage, self._refresh_all)
        self.schedule_sec = ScheduleSection(self.storage, self._refresh_all)
        self.attendance_sec = AttendanceSection(self.storage, self._refresh_all)
        self.payments_sec = PaymentsSection(self.storage, self._refresh_all)
        self.subs_sec = SubscriptionsSection(self.storage, self._refresh_all)
        self.reports_sec = ReportsSection(self.storage, self._refresh_all)
        self.accounts_sec = AccountsSection(self.storage, self._refresh_all, self.user)

        for name, sec in (
            ("Клиенты", self.clients_sec),
            ("Расписание", self.schedule_sec),
            ("Посещения", self.attendance_sec),
            ("Оплаты", self.payments_sec),
            ("Абонементы", self.subs_sec),
            ("Отчёты", self.reports_sec),
            ("Аккаунты", self.accounts_sec),
        ):
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(sec)
            self.tabs.addTab(scroll, name)
            self._sections.append(sec)

        self.tabs.currentChanged.connect(self._on_tab)
        layout.addWidget(self.tabs)
        self._refresh_all()

    def _toggle_theme(self) -> None:
        self.storage.theme = "light" if self.storage.theme == "dark" else "dark"
        self.storage.save_theme()
        self.on_theme_toggle(self.storage.theme)
        self.theme_btn.setText("Тёмная тема" if self.storage.theme == "dark" else "Светлая тема")

    def _on_tab(self, index: int) -> None:
        if index == 5:
            self.reports_sec.refresh()

    def _refresh_all(self) -> None:
        for sec in self._sections:
            sec.refresh()

    def apply_theme(self, theme: str) -> None:
        self.setStyleSheet(get_stylesheet(theme))
