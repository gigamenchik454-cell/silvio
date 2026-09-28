"""Общие виджеты и утилиты UI."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


def hint_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setProperty("class", "hint")
    lbl.setWordWrap(True)
    lbl.setStyleSheet("color: #8a8a8a; font-size: 9pt;")
    return lbl


def primary_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setProperty("class", "primary")
    btn.setStyleSheet(
        "QPushButton { background: #e24a4a; color: white; border: none; "
        "border-radius: 8px; padding: 8px 16px; font-weight: 500; }"
        "QPushButton:hover { background: #f25a5a; }"
    )
    return btn


def danger_button(text: str, small: bool = True) -> QPushButton:
    btn = QPushButton(text)
    pad = "4px 10px" if small else "8px 16px"
    fs = "8pt" if small else "10pt"
    btn.setStyleSheet(
        f"QPushButton {{ background: #e74c3c; color: white; border: none; "
        f"border-radius: 6px; padding: {pad}; font-size: {fs}; }}"
        "QPushButton:hover { background: #c0392b; }"
    )
    return btn


def setup_table(table: QTableWidget, headers: list[str]) -> None:
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)


def set_table_row(table: QTableWidget, row: int, values: list, item_id: int | None = None) -> None:
    table.insertRow(row)
    for col, val in enumerate(values):
        item = QTableWidgetItem(str(val) if val is not None else "")
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if item_id is not None and col == 0:
            item.setData(Qt.ItemDataRole.UserRole, item_id)
        table.setItem(row, col, item)


def confirm(parent: QWidget, title: str, text: str) -> bool:
    return (
        QMessageBox.question(parent, title, text, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        == QMessageBox.StandardButton.Yes
    )


def alert(parent: QWidget, title: str, text: str) -> None:
    QMessageBox.warning(parent, title, text)


class FormRow(QWidget):
    """Горизонтальный ряд полей формы."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

    def add_field(self, label: str, widget: QWidget, hint: str = "") -> None:
        col = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #8a8a8a; font-size: 9pt;")
        col.addWidget(lbl)
        col.addWidget(widget)
        if hint:
            col.addWidget(hint_label(hint))
        self.layout.addLayout(col, 1)
