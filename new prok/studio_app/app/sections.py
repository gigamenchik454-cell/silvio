"""Разделы приложения тренера."""

from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app.constants import DAYS, DAY_ORDER, PAYMENT_METHODS, STATUS_LABELS
from app.storage import Storage
from app.widgets import (
    FormRow,
    alert,
    confirm,
    danger_button,
    hint_label,
    primary_button,
    set_table_row,
    setup_table,
)


class BaseSection(QWidget):
    def __init__(self, storage: Storage, on_change, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.storage = storage
        self.on_change = on_change


class ClientsSection(BaseSection):
    def __init__(self, storage, on_change, parent=None):
        super().__init__(storage, on_change, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(hint_label("Здесь хранятся все клиенты студии."))

        form_box = QGroupBox("Добавить клиента")
        form_layout = QVBoxLayout(form_box)
        row = FormRow()
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.group_edit = QLineEdit()
        self.status_combo = QComboBox()
        self.status_combo.addItem("Активен", "active")
        self.status_combo.addItem("Неактивен", "inactive")
        self.status_combo.addItem("Пробный", "trial")
        row.add_field("ФИО", self.name_edit, "Полное имя для отчётов")
        row.add_field("Телефон", self.phone_edit)
        row.add_field("Группа / уровень", self.group_edit, "Как в расписании")
        row.add_field("Статус", self.status_combo)
        form_layout.addWidget(row)
        add_btn = primary_button("Добавить клиента")
        add_btn.clicked.connect(self._add)
        form_layout.addWidget(add_btn)
        layout.addWidget(form_box)

        list_box = QGroupBox("Список клиентов")
        list_layout = QVBoxLayout(list_box)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по ФИО, телефону, группе...")
        self.search.textChanged.connect(self.refresh)
        list_layout.addWidget(self.search)
        self.table = QTableWidget()
        setup_table(self.table, ["ФИО", "Телефон", "Группа", "Статус", ""])
        self.table.cellClicked.connect(self._on_cell)
        list_layout.addWidget(self.table)
        layout.addWidget(list_box)

    def _add(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            return
        self.storage.clients.append({
            "id": self.storage.next_id(),
            "name": name,
            "phone": self.phone_edit.text().strip(),
            "group": self.group_edit.text().strip(),
            "status": self.status_combo.currentData(),
        })
        self.storage.save_data()
        self.name_edit.clear()
        self.phone_edit.clear()
        self.group_edit.clear()
        self.on_change()
        self.refresh()

    def _on_cell(self, row: int, col: int) -> None:
        if col != 4:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        cid = item.data(Qt.ItemDataRole.UserRole)
        client = next((c for c in self.storage.clients if c["id"] == cid), None)
        if not client:
            return
        if confirm(self, "Удаление", f'Удалить клиента "{client["name"]}" и все связанные данные?'):
            self.storage.clients = [c for c in self.storage.clients if c["id"] != cid]
            self.storage.students = [s for s in self.storage.students if s.get("clientId") != cid]
            self.storage.payments = [p for p in self.storage.payments if p.get("clientId") != cid]
            self.storage.visits = [v for v in self.storage.visits if v.get("clientId") != cid]
            self.storage.client_subs = [cs for cs in self.storage.client_subs if cs.get("clientId") != cid]
            self.storage.save_data()
            self.storage.save_auth()
            self.on_change()
            self.refresh()

    def refresh(self) -> None:
        q = self.search.text().lower()
        items = self.storage.clients
        if q:
            items = [
                c for c in items
                if q in c.get("name", "").lower()
                or q in c.get("phone", "")
                or q in (c.get("group") or "").lower()
            ]
        self.table.setRowCount(0)
        for c in items:
            row = self.table.rowCount()
            status = STATUS_LABELS.get(c.get("status"), c.get("status"))
            set_table_row(self.table, row, [c["name"], c.get("phone", ""), c.get("group", ""), status, "Удалить"], c["id"])
            btn_item = self.table.item(row, 4)
            if btn_item:
                btn_item.setForeground(Qt.GlobalColor.red)


class ScheduleSection(BaseSection):
    def __init__(self, storage, on_change, parent=None):
        super().__init__(storage, on_change, parent)
        layout = QVBoxLayout(self)
        layout.addWidget(hint_label("Расписание занятий по группам и дням."))

        form_box = QGroupBox("Добавить в расписание")
        fl = QVBoxLayout(form_box)
        row = FormRow()
        self.group_edit = QLineEdit()
        self.day_combo = QComboBox()
        for d in DAY_ORDER:
            self.day_combo.addItem(DAYS[d], d)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        row.add_field("Название группы", self.group_edit)
        row.add_field("День недели", self.day_combo)
        row.add_field("Время начала", self.time_edit)
        fl.addWidget(row)
        btn = primary_button("Добавить в расписание")
        btn.clicked.connect(self._add)
        fl.addWidget(btn)
        layout.addWidget(form_box)

        self.chips = QHBoxLayout()
        layout.addLayout(self.chips)
        self.table = QTableWidget()
        setup_table(self.table, ["День", "Группа", "Время", ""])
        self.table.cellClicked.connect(self._on_cell)
        layout.addWidget(self.table)

    def _add(self) -> None:
        group = self.group_edit.text().strip()
        if not group:
            return
        self.storage.schedule.append({
            "id": self.storage.next_id(),
            "group": group,
            "day": self.day_combo.currentData(),
            "time": self.time_edit.time().toString("HH:mm"),
        })
        self.storage.save_data()
        self.group_edit.clear()
        self.on_change()
        self.refresh()

    def _on_cell(self, row: int, col: int) -> None:
        if col != 3:
            return
        item = self.table.item(row, 0)
        sid = item.data(Qt.ItemDataRole.UserRole) if item else None
        slot = next((s for s in self.storage.schedule if s["id"] == sid), None)
        if slot and confirm(self, "Удаление", f"Удалить занятие: {slot['group']}, {DAYS[slot['day']]} {slot['time']}?"):
            self.storage.schedule = [s for s in self.storage.schedule if s["id"] != sid]
            self.storage.save_data()
            self.on_change()
            self.refresh()

    def _delete_group(self, group: str) -> None:
        count = sum(1 for s in self.storage.schedule if s["group"] == group)
        if count and confirm(self, "Удаление", f"Удалить всё расписание группы «{group}» ({count} занятий)?"):
            self.storage.schedule = [s for s in self.storage.schedule if s["group"] != group]
            self.storage.save_data()
            self.on_change()
            self.refresh()

    def refresh(self) -> None:
        while self.chips.count():
            item = self.chips.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        groups = sorted({s["group"] for s in self.storage.schedule})
        if groups:
            self.chips.addWidget(QLabel("Удалить группу:"))
            for g in groups:
                btn = danger_button(f"{g} ×")
                btn.clicked.connect(lambda checked, gn=g: self._delete_group(gn))
                self.chips.addWidget(btn)

        self.table.setRowCount(0)
        rows = []
        for d in DAY_ORDER:
            for s in sorted([x for x in self.storage.schedule if x["day"] == d], key=lambda x: x["time"]):
                rows.append((d, s))
        for d, s in rows:
            row = self.table.rowCount()
            set_table_row(self.table, row, [DAYS[d], s["group"], s["time"], "Удалить"], s["id"])


class AttendanceSection(BaseSection):
    def __init__(self, storage, on_change, parent=None):
        super().__init__(storage, on_change, parent)
        self.visit_rows: dict[int, dict] = {}
        layout = QVBoxLayout(self)

        journal = QGroupBox("Журнал посещений")
        jl = QVBoxLayout(journal)
        row = FormRow()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self._load_clients)
        row.add_field("Дата занятия", self.date_edit)
        row.add_field("Группа", self.group_combo)
        jl.addWidget(row)
        self.clients_area = QVBoxLayout()
        jl.addLayout(self.clients_area)
        save_btn = primary_button("Сохранить посещения")
        save_btn.clicked.connect(self._save)
        jl.addWidget(save_btn)
        layout.addWidget(journal)

        records = QGroupBox("Записи посещений")
        rl = QVBoxLayout(records)
        frow = FormRow()
        self.filter_group = QComboBox()
        self.filter_date = QDateEdit()
        self.filter_date.setCalendarPopup(True)
        self.filter_date.setDisplayFormat("yyyy-MM-dd")
        self.filter_date.setSpecialValueText("Все даты")
        self.filter_date.setDate(QDate(2000, 1, 1))
        frow.add_field("Группа", self.filter_group)
        frow.add_field("Дата", self.filter_date)
        rl.addWidget(frow)
        btns = QHBoxLayout()
        show_btn = primary_button("Показать")
        show_btn.clicked.connect(self.refresh_journal)
        del_grp = danger_button("Удалить группу", small=False)
        del_grp.clicked.connect(self._del_group)
        del_date = danger_button("Удалить за дату", small=False)
        del_date.clicked.connect(self._del_date)
        btns.addWidget(show_btn)
        btns.addWidget(del_grp)
        btns.addWidget(del_date)
        btns.addStretch()
        rl.addLayout(btns)
        self.journal_table = QTableWidget()
        setup_table(self.journal_table, ["Дата", "Группа", "Клиент", "Статус", "Опоздание", ""])
        self.journal_table.cellClicked.connect(self._on_journal_cell)
        rl.addWidget(self.journal_table)
        layout.addWidget(records)

    def _fill_groups(self) -> None:
        groups = self.storage.get_groups()
        for combo in (self.group_combo, self.filter_group):
            cur = combo.currentData() if combo.count() else ""
            combo.clear()
            combo.addItem("Выберите группу" if combo is self.group_combo else "Все группы", "")
            for g in groups:
                combo.addItem(g, g)
            if cur:
                idx = combo.findData(cur)
                if idx >= 0:
                    combo.setCurrentIndex(idx)

    def _load_clients(self) -> None:
        while self.clients_area.count():
            item = self.clients_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.visit_rows.clear()
        group = self.group_combo.currentData()
        if not group:
            return
        clients = [c for c in self.storage.clients if c.get("group") == group and c.get("status") != "inactive"]
        if not clients:
            self.clients_area.addWidget(QLabel("Нет клиентов в этой группе"))
            return
        for c in clients:
            w = QWidget()
            hl = QHBoxLayout(w)
            hl.addWidget(QLabel(c["name"]), 1)
            ok = QRadioButton("Пришёл")
            miss = QRadioButton("Пропуск")
            miss.setChecked(True)
            grp = QButtonGroup(w)
            grp.addButton(ok)
            grp.addButton(miss)
            late = QSpinBox()
            late.setRange(0, 999)
            late.setPrefix("Опозд: ")
            late.setSuffix(" мин")
            reason = QLineEdit()
            reason.setPlaceholderText("Причина")
            hl.addWidget(ok)
            hl.addWidget(miss)
            hl.addWidget(late)
            hl.addWidget(reason, 2)
            self.clients_area.addWidget(w)
            self.visit_rows[c["id"]] = {"ok": ok, "miss": miss, "late": late, "reason": reason}

    def _save(self) -> None:
        group = self.group_combo.currentData()
        if not group:
            alert(self, "Ошибка", "Выберите группу")
            return
        d = self.date_edit.date().toString("yyyy-MM-dd")
        clients = [c for c in self.storage.clients if c.get("group") == group]
        for c in clients:
            row = self.visit_rows.get(c["id"])
            status = "ok" if row and row["ok"].isChecked() else "miss"
            late = row["late"].value() if row else 0
            reason = row["reason"].text().strip() if row else ""
            self.storage.visits.append({
                "id": self.storage.next_id(),
                "clientId": c["id"],
                "group": group,
                "date": d,
                "status": status,
                "lateMinutes": late,
                "reason": reason,
            })
        self.storage.save_data()
        self.on_change()
        self._load_clients()
        self.refresh_journal()

    def _del_group(self) -> None:
        g = self.filter_group.currentData()
        if not g:
            alert(self, "Ошибка", "Выберите группу")
            return
        to_del = [v for v in self.storage.visits if self.storage.visit_group(v) == g]
        if not to_del:
            alert(self, "Инфо", "Нет посещений для этой группы")
            return
        if confirm(self, "Удаление", f"Удалить все посещения группы «{g}» ({len(to_del)} записей)?"):
            ids = {v["id"] for v in to_del}
            self.storage.visits = [v for v in self.storage.visits if v["id"] not in ids]
            self.storage.save_data()
            self.on_change()
            self.refresh_journal()

    def _del_date(self) -> None:
        g = self.filter_group.currentData()
        d = self.filter_date.date().toString("yyyy-MM-dd")
        if not g:
            alert(self, "Ошибка", "Выберите группу")
            return
        if self.filter_date.date().year() < 2001:
            alert(self, "Ошибка", "Выберите дату")
            return
        to_del = [v for v in self.storage.visits if self.storage.visit_group(v) == g and v["date"] == d]
        if not to_del:
            alert(self, "Инфо", "Нет посещений за эту дату и группу")
            return
        if confirm(self, "Удаление", f"Удалить посещения группы «{g}» за {d} ({len(to_del)} записей)?"):
            ids = {v["id"] for v in to_del}
            self.storage.visits = [v for v in self.storage.visits if v["id"] not in ids]
            self.storage.save_data()
            self.on_change()
            self.refresh_journal()

    def _on_journal_cell(self, row: int, col: int) -> None:
        if col != 5:
            return
        item = self.table_item_id(self.journal_table, row)
        if item and confirm(self, "Удаление", "Удалить посещение?"):
            self.storage.visits = [v for v in self.storage.visits if v["id"] != item]
            self.storage.save_data()
            self.on_change()
            self.refresh_journal()

    @staticmethod
    def table_item_id(table: QTableWidget, row: int) -> int | None:
        item = table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh_journal(self) -> None:
        self._fill_groups()
        fg = self.filter_group.currentData() or ""
        fd = ""
        if self.filter_date.date().year() > 2000:
            fd = self.filter_date.date().toString("yyyy-MM-dd")
        items = sorted(self.storage.visits, key=lambda v: (v["date"], -v["id"]), reverse=True)
        if fg:
            items = [v for v in items if self.storage.visit_group(v) == fg]
        if fd:
            items = [v for v in items if v["date"] == fd]
        self.journal_table.setRowCount(0)
        for v in items:
            row = self.journal_table.rowCount()
            status = "Пришёл" if v["status"] == "ok" else "Пропуск"
            late = f"{v.get('lateMinutes', 0)} мин" if v.get("lateMinutes") else "—"
            set_table_row(
                self.journal_table, row,
                [v["date"], self.storage.visit_group(v), self.storage.client_name(v["clientId"]), status, late, "Удалить"],
                v["id"],
            )

    def refresh(self) -> None:
        self._fill_groups()
        self._load_clients()
        self.refresh_journal()


class PaymentsSection(BaseSection):
    def __init__(self, storage, on_change, parent=None):
        super().__init__(storage, on_change, parent)
        layout = QVBoxLayout(self)
        form_box = QGroupBox("Принять оплату")
        fl = QVBoxLayout(form_box)
        row = FormRow()
        self.client_combo = QComboBox()
        self.amount_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.method_combo = QComboBox()
        for k, v in PAYMENT_METHODS.items():
            self.method_combo.addItem(v, k)
        row.add_field("Клиент", self.client_combo)
        row.add_field("Сумма (₽)", self.amount_edit)
        row.add_field("Дата оплаты", self.date_edit)
        row.add_field("Способ оплаты", self.method_combo)
        fl.addWidget(row)
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(80)
        fl.addWidget(QLabel("Комментарий"))
        fl.addWidget(self.comment_edit)
        btn = primary_button("Принять оплату")
        btn.clicked.connect(self._add)
        fl.addWidget(btn)
        layout.addWidget(form_box)

        list_box = QGroupBox("История оплат")
        ll = QVBoxLayout(list_box)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по клиенту...")
        self.search.textChanged.connect(self.refresh)
        ll.addWidget(self.search)
        self.table = QTableWidget()
        setup_table(self.table, ["Дата", "Клиент", "Сумма", "Способ", "Комментарий", ""])
        self.table.cellClicked.connect(self._on_cell)
        ll.addWidget(self.table)
        layout.addWidget(list_box)

    def _fill_clients(self) -> None:
        self.client_combo.clear()
        self.client_combo.addItem("Выберите клиента", 0)
        for c in self.storage.clients:
            self.client_combo.addItem(c["name"], c["id"])

    def _add(self) -> None:
        cid = self.client_combo.currentData()
        try:
            amount = float(self.amount_edit.text())
        except ValueError:
            return
        if not cid or amount < 1:
            return
        self.storage.payments.append({
            "id": self.storage.next_id(),
            "clientId": cid,
            "amount": amount,
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "method": self.method_combo.currentData(),
            "comment": self.comment_edit.toPlainText().strip(),
        })
        self.storage.save_data()
        self.amount_edit.clear()
        self.comment_edit.clear()
        self.on_change()
        self.refresh()

    def _on_cell(self, row: int, col: int) -> None:
        if col != 5:
            return
        item = self.table.item(row, 0)
        pid = item.data(Qt.ItemDataRole.UserRole) if item else None
        p = next((x for x in self.storage.payments if x["id"] == pid), None)
        if p and confirm(self, "Удаление", f"Удалить оплату {p['amount']} ₽?"):
            self.storage.payments = [x for x in self.storage.payments if x["id"] != pid]
            self.storage.save_data()
            self.on_change()
            self.refresh()

    def refresh(self) -> None:
        self._fill_clients()
        q = self.search.text().lower()
        items = list(reversed(self.storage.payments))
        if q:
            items = [
                p for p in items
                if q in self.storage.client_name(p["clientId"]).lower()
                or q in next((c.get("phone", "") for c in self.storage.clients if c["id"] == p["clientId"]), "")
            ]
        self.table.setRowCount(0)
        for p in items:
            row = self.table.rowCount()
            method = PAYMENT_METHODS.get(p.get("method"), p.get("method"))
            set_table_row(
                self.table, row,
                [p["date"], self.storage.client_name(p["clientId"]), f"{p['amount']} ₽", method, p.get("comment", ""), "Удалить"],
                p["id"],
            )


class SubscriptionsSection(BaseSection):
    def __init__(self, storage, on_change, parent=None):
        super().__init__(storage, on_change, parent)
        layout = QVBoxLayout(self)

        types_box = QGroupBox("Типы абонементов")
        tl = QVBoxLayout(types_box)
        row = FormRow()
        self.type_edit = QLineEdit()
        self.sessions_edit = QLineEdit()
        self.price_edit = QLineEdit()
        row.add_field("Название типа", self.type_edit)
        row.add_field("Занятий или срок (дней)", self.sessions_edit)
        row.add_field("Цена (₽)", self.price_edit)
        tl.addWidget(row)
        btn = primary_button("Добавить тип абонемента")
        btn.clicked.connect(self._add_type)
        tl.addWidget(btn)
        self.types_table = QTableWidget()
        setup_table(self.types_table, ["Тип", "Занятий/срок", "Цена", ""])
        self.types_table.cellClicked.connect(self._on_type_cell)
        tl.addWidget(self.types_table)
        layout.addWidget(types_box)

        assign_box = QGroupBox("Выдать абонемент клиенту")
        al = QVBoxLayout(assign_box)
        row2 = FormRow()
        self.assign_client = QComboBox()
        self.assign_type = QComboBox()
        row2.add_field("Клиент", self.assign_client)
        row2.add_field("Тип абонемента", self.assign_type)
        al.addWidget(row2)
        abtn = primary_button("Выдать")
        abtn.clicked.connect(self._assign)
        al.addWidget(abtn)
        self.issued_table = QTableWidget()
        setup_table(self.issued_table, ["Клиент", "Тип", "Осталось", "Дата", ""])
        self.issued_table.cellClicked.connect(self._on_issued_cell)
        al.addWidget(self.issued_table)
        layout.addWidget(assign_box)

    def _add_type(self) -> None:
        t = self.type_edit.text().strip()
        try:
            price = float(self.price_edit.text())
        except ValueError:
            return
        if not t:
            return
        self.storage.sub_types.append({
            "id": self.storage.next_id(),
            "type": t,
            "sessions": self.sessions_edit.text().strip(),
            "price": price,
        })
        self.storage.save_data()
        self.type_edit.clear()
        self.sessions_edit.clear()
        self.price_edit.clear()
        self.on_change()
        self.refresh()

    def _assign(self) -> None:
        cid = self.assign_client.currentData()
        tid = self.assign_type.currentData()
        if not cid or not tid:
            return
        st = next((s for s in self.storage.sub_types if s["id"] == tid), None)
        sessions = int(st["sessions"]) if st and str(st.get("sessions", "")).isdigit() else 0
        self.storage.client_subs.append({
            "id": self.storage.next_id(),
            "clientId": cid,
            "subTypeId": tid,
            "sessionsLeft": sessions,
            "boughtAt": date.today().isoformat(),
        })
        self.storage.save_data()
        self.on_change()
        self.refresh()

    def _on_type_cell(self, row: int, col: int) -> None:
        if col != 3:
            return
        item = self.types_table.item(row, 0)
        tid = item.data(Qt.ItemDataRole.UserRole) if item else None
        st = next((s for s in self.storage.sub_types if s["id"] == tid), None)
        if st and confirm(self, "Удаление", f"Удалить тип «{st['type']}»?"):
            self.storage.sub_types = [s for s in self.storage.sub_types if s["id"] != tid]
            self.storage.client_subs = [cs for cs in self.storage.client_subs if cs.get("subTypeId") != tid]
            self.storage.save_data()
            self.on_change()
            self.refresh()

    def _on_issued_cell(self, row: int, col: int) -> None:
        if col != 4:
            return
        item = self.issued_table.item(row, 0)
        iid = item.data(Qt.ItemDataRole.UserRole) if item else None
        if iid and confirm(self, "Удаление", "Удалить выданный абонемент?"):
            self.storage.client_subs = [cs for cs in self.storage.client_subs if cs["id"] != iid]
            self.storage.save_data()
            self.on_change()
            self.refresh()

    def refresh(self) -> None:
        self.assign_client.clear()
        self.assign_client.addItem("Выберите клиента", 0)
        for c in self.storage.clients:
            self.assign_client.addItem(c["name"], c["id"])
        self.assign_type.clear()
        self.assign_type.addItem("Выберите тип", 0)
        for s in self.storage.sub_types:
            self.assign_type.addItem(f"{s['type']} — {s['price']} ₽", s["id"])

        self.types_table.setRowCount(0)
        for s in self.storage.sub_types:
            row = self.types_table.rowCount()
            set_table_row(self.types_table, row, [s["type"], s.get("sessions", ""), f"{s['price']} ₽", "Удалить"], s["id"])

        self.issued_table.setRowCount(0)
        for cs in sorted(self.storage.client_subs, key=lambda x: x.get("boughtAt", ""), reverse=True):
            row = self.issued_table.rowCount()
            set_table_row(
                self.issued_table, row,
                [
                    self.storage.client_name(cs["clientId"]),
                    self.storage.sub_type_name(cs["subTypeId"]),
                    cs.get("sessionsLeft", ""),
                    cs.get("boughtAt", ""),
                    "Удалить",
                ],
                cs["id"],
            )


class ReportsSection(BaseSection):
    def __init__(self, storage, on_change, parent=None):
        super().__init__(storage, on_change, parent)
        layout = QVBoxLayout(self)

        debts_box = QGroupBox("Долги")
        dl = QVBoxLayout(debts_box)
        self.debts_table = QTableWidget()
        setup_table(self.debts_table, ["Клиент", "Телефон", "Долг (₽)", "Абонементы"])
        dl.addWidget(self.debts_table)
        layout.addWidget(debts_box)

        rev_box = QGroupBox("Выручка за период")
        rl = QVBoxLayout(rev_box)
        row = FormRow()
        self.rev_from = QDateEdit()
        self.rev_from.setCalendarPopup(True)
        self.rev_from.setDisplayFormat("yyyy-MM-dd")
        self.rev_from.setSpecialValueText("—")
        self.rev_from.setDate(QDate(2000, 1, 1))
        self.rev_to = QDateEdit()
        self.rev_to.setCalendarPopup(True)
        self.rev_to.setDisplayFormat("yyyy-MM-dd")
        self.rev_to.setSpecialValueText("—")
        self.rev_to.setDate(QDate(2000, 1, 1))
        row.add_field("С (дата)", self.rev_from)
        row.add_field("По (дата)", self.rev_to)
        rl.addWidget(row)
        rbtn = primary_button("Показать")
        rbtn.clicked.connect(self._revenue)
        rl.addWidget(rbtn)
        self.rev_label = QLabel("")
        self.rev_table = QTableWidget()
        setup_table(self.rev_table, ["Дата", "Клиент", "Сумма"])
        rl.addWidget(self.rev_label)
        rl.addWidget(self.rev_table)
        layout.addWidget(rev_box)

        att_box = QGroupBox("Посещаемость по клиентам")
        al = QVBoxLayout(att_box)
        row2 = FormRow()
        self.att_from = QDateEdit()
        self.att_from.setCalendarPopup(True)
        self.att_from.setDisplayFormat("yyyy-MM-dd")
        self.att_from.setDate(QDate(2000, 1, 1))
        self.att_to = QDateEdit()
        self.att_to.setCalendarPopup(True)
        self.att_to.setDisplayFormat("yyyy-MM-dd")
        self.att_to.setDate(QDate(2000, 1, 1))
        row2.add_field("Период с", self.att_from)
        row2.add_field("Период по", self.att_to)
        al.addWidget(row2)
        abtn = primary_button("Показать")
        abtn.clicked.connect(self._attendance)
        al.addWidget(abtn)
        self.att_table = QTableWidget()
        setup_table(self.att_table, ["Клиент", "Посещений", "Пропусков", "Ср. опоздание (мин)"])
        al.addWidget(self.att_table)
        layout.addWidget(att_box)

    def refresh(self) -> None:
        self._debts()

    def _debts(self) -> None:
        debt_map: dict[int, dict] = {}
        for cs in self.storage.client_subs:
            c = next((x for x in self.storage.clients if x["id"] == cs["clientId"]), None)
            if not c:
                continue
            st = next((x for x in self.storage.sub_types if x["id"] == cs["subTypeId"]), None)
            paid = sum(p["amount"] for p in self.storage.payments if p["clientId"] == c["id"])
            bought = len([x for x in self.storage.client_subs if x["clientId"] == c["id"]]) * (st["price"] if st else 0)
            diff = bought - paid
            if diff > 0:
                subs = sorted([x for x in self.storage.client_subs if x["clientId"] == c["id"]], key=lambda x: x.get("boughtAt", ""), reverse=True)
                subs_txt = ", ".join(f"{self.storage.sub_type_name(s['subTypeId'])} ({s.get('boughtAt')})" for s in subs)
                debt_map[c["id"]] = {"name": c["name"], "phone": c.get("phone", ""), "debt": diff, "subs": subs_txt}
        self.debts_table.setRowCount(0)
        for d in debt_map.values():
            row = self.debts_table.rowCount()
            set_table_row(self.debts_table, row, [d["name"], d["phone"], f"{d['debt']} ₽", d["subs"]])

    def _revenue(self) -> None:
        items = self.storage.payments
        if self.rev_from.date().year() > 2000:
            fd = self.rev_from.date().toString("yyyy-MM-dd")
            items = [p for p in items if p["date"] >= fd]
        if self.rev_to.date().year() > 2000:
            td = self.rev_to.date().toString("yyyy-MM-dd")
            items = [p for p in items if p["date"] <= td]
        total = sum(p["amount"] for p in items)
        self.rev_label.setText(f"<b>Выручка: {total} ₽</b>  |  Оплат: {len(items)}")
        self.rev_table.setRowCount(0)
        for p in reversed(items):
            row = self.rev_table.rowCount()
            set_table_row(self.rev_table, row, [p["date"], self.storage.client_name(p["clientId"]), f"{p['amount']} ₽"])

    def _attendance(self) -> None:
        visits = self.storage.visits
        if self.att_from.date().year() > 2000:
            fd = self.att_from.date().toString("yyyy-MM-dd")
            visits = [v for v in visits if v["date"] >= fd]
        if self.att_to.date().year() > 2000:
            td = self.att_to.date().toString("yyyy-MM-dd")
            visits = [v for v in visits if v["date"] <= td]
        by_client: dict[int, dict] = {}
        for v in visits:
            cid = v["clientId"]
            if cid not in by_client:
                by_client[cid] = {"ok": 0, "miss": 0, "late": []}
            if v["status"] == "ok":
                by_client[cid]["ok"] += 1
            else:
                by_client[cid]["miss"] += 1
            if v.get("lateMinutes", 0) > 0:
                by_client[cid]["late"].append(v["lateMinutes"])
        self.att_table.setRowCount(0)
        for cid, d in by_client.items():
            avg = round(sum(d["late"]) / len(d["late"])) if d["late"] else "—"
            row = self.att_table.rowCount()
            set_table_row(self.att_table, row, [self.storage.client_name(cid), d["ok"], d["miss"], avg])


class AccountsSection(BaseSection):
    def __init__(self, storage, on_change, current_user, parent=None):
        super().__init__(storage, on_change, parent)
        self.current_user = current_user
        self.show_passwords = False
        layout = QVBoxLayout(self)

        form_box = QGroupBox("Создать аккаунт ученика")
        fl = QVBoxLayout(form_box)
        row = FormRow()
        self.client_combo = QComboBox()
        self.login_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        row.add_field("Клиент", self.client_combo)
        row.add_field("Логин", self.login_edit)
        row.add_field("Пароль", self.password_edit)
        fl.addWidget(row)
        btn = primary_button("Создать аккаунт")
        btn.clicked.connect(self._create)
        fl.addWidget(btn)
        if self._is_admin():
            fl.addWidget(hint_label("Администратор (admin) может просматривать пароли учеников."))
        layout.addWidget(form_box)

        self.table = QTableWidget()
        headers = ["Клиент", "Логин"]
        if self._is_admin():
            headers.append("Пароль")
        setup_table(self.table, headers)
        layout.addWidget(self.table)

    def _is_admin(self) -> bool:
        return self.current_user.get("role") == "trainer" and self.current_user.get("login") == "admin"

    def _create(self) -> None:
        cid = self.client_combo.currentData()
        login = self.login_edit.text().strip()
        password = self.password_edit.text()
        if not cid or not login or not password:
            return
        if any(s["login"] == login for s in self.storage.students):
            alert(self, "Ошибка", "Такой логин уже занят")
            return
        if any(s["clientId"] == cid for s in self.storage.students):
            alert(self, "Ошибка", "У этого клиента уже есть аккаунт")
            return
        self.storage.students.append({"clientId": cid, "login": login, "password": password})
        self.storage.save_auth()
        self.login_edit.clear()
        self.password_edit.clear()
        self.refresh()

    def refresh(self) -> None:
        with_account = {s["clientId"] for s in self.storage.students}
        self.client_combo.clear()
        self.client_combo.addItem("Выберите клиента", 0)
        for c in self.storage.clients:
            if c["id"] not in with_account:
                self.client_combo.addItem(f"{c['name']} — {c.get('group', '—')}", c["id"])

        headers = ["Клиент", "Логин"]
        if self._is_admin():
            headers.append("Пароль")
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(0)
        for s in self.storage.students:
            row = self.table.rowCount()
            pw = s["password"] if self.show_passwords else "••••••"
            vals = [self.storage.client_name(s["clientId"]), s["login"]]
            if self._is_admin():
                vals.append(pw)
            set_table_row(self.table, row, vals)
