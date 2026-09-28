"""Темы оформления (тёмная / светлая)."""

DARK_STYLE = """
QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
    color: #ececec;
    background-color: #0a0a0a;
}
QMainWindow, QDialog {
    background-color: #0a0a0a;
}
QTabWidget::pane {
    border: 1px solid #333333;
    background: #0a0a0a;
    border-radius: 8px;
}
QTabBar::tab {
    background: #141414;
    color: #ececec;
    border: 1px solid #333333;
    padding: 8px 14px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
QTabBar::tab:selected {
    background: #e24a4a;
    color: white;
    border-color: #e24a4a;
}
QTabBar::tab:hover:!selected {
    background: #1f1f1f;
}
QGroupBox {
    background: #141414;
    border: 1px solid #333333;
    border-radius: 12px;
    margin-top: 14px;
    padding: 16px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #ececec;
}
QLabel {
    background: transparent;
    color: #ececec;
}
QLabel.hint {
    color: #8a8a8a;
    font-size: 9pt;
}
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QTextEdit {
    background: #1f1f1f;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 8px 10px;
    color: #ececec;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus, QTextEdit:focus {
    border-color: #e24a4a;
}
QPushButton {
    background: #141414;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 8px 16px;
    color: #ececec;
}
QPushButton:hover {
    background: #1f1f1f;
}
QPushButton.primary {
    background: #e24a4a;
    border-color: #e24a4a;
    color: white;
    font-weight: 500;
}
QPushButton.primary:hover {
    background: #f25a5a;
}
QPushButton.danger {
    background: #e74c3c;
    border-color: #e74c3c;
    color: white;
}
QPushButton.danger:hover {
    background: #c0392b;
}
QTableWidget {
    background: #141414;
    alternate-background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 8px;
    gridline-color: #333333;
}
QHeaderView::section {
    background: #1f1f1f;
    color: #8a8a8a;
    border: none;
    border-bottom: 1px solid #333333;
    padding: 8px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QRadioButton {
    background: transparent;
    spacing: 6px;
}
"""

LIGHT_STYLE = """
QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
    color: #1a1a1a;
    background-color: #f2f2f2;
}
QMainWindow, QDialog {
    background-color: #f2f2f2;
}
QTabWidget::pane {
    border: 1px solid #d4d4d4;
    background: #f2f2f2;
    border-radius: 8px;
}
QTabBar::tab {
    background: #ffffff;
    color: #1a1a1a;
    border: 1px solid #d4d4d4;
    padding: 8px 14px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
QTabBar::tab:selected {
    background: #dc2626;
    color: white;
    border-color: #dc2626;
}
QTabBar::tab:hover:!selected {
    background: #ebebeb;
}
QGroupBox {
    background: #ffffff;
    border: 1px solid #d4d4d4;
    border-radius: 12px;
    margin-top: 14px;
    padding: 16px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #1a1a1a;
}
QLabel {
    background: transparent;
    color: #1a1a1a;
}
QLabel.hint {
    color: #6e6e6e;
    font-size: 9pt;
}
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox, QTextEdit {
    background: #ebebeb;
    border: 1px solid #d4d4d4;
    border-radius: 8px;
    padding: 8px 10px;
    color: #1a1a1a;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus, QTextEdit:focus {
    border-color: #dc2626;
}
QPushButton {
    background: #ffffff;
    border: 1px solid #d4d4d4;
    border-radius: 8px;
    padding: 8px 16px;
    color: #1a1a1a;
}
QPushButton:hover {
    background: #ebebeb;
}
QPushButton.primary {
    background: #dc2626;
    border-color: #dc2626;
    color: white;
    font-weight: 500;
}
QPushButton.primary:hover {
    background: #b91c1c;
}
QPushButton.danger {
    background: #d32f2f;
    border-color: #d32f2f;
    color: white;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8f8f8;
    border: 1px solid #d4d4d4;
    border-radius: 8px;
    gridline-color: #d4d4d4;
}
QHeaderView::section {
    background: #ebebeb;
    color: #6e6e6e;
    border: none;
    border-bottom: 1px solid #d4d4d4;
    padding: 8px;
}
QScrollArea { border: none; background: transparent; }
QRadioButton { background: transparent; spacing: 6px; }
"""

STUDENT_EXTRA_DARK = """
QMainWindow#studentWindow {
    background-color: #0a0a0a;
}
QMainWindow#studentWindow QGroupBox {
    background: #1a0c0c;
    border-color: #5c2828;
    border-left: 4px solid #ff2d2d;
}
QMainWindow#studentWindow QLabel.title {
    color: #ff7070;
    font-size: 12pt;
    font-weight: bold;
}
"""


def get_stylesheet(theme: str, student: bool = False) -> str:
    base = LIGHT_STYLE if theme == "light" else DARK_STYLE
    if student and theme == "dark":
        base += STUDENT_EXTRA_DARK
    return base
