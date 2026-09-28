"""Хранилище данных (JSON-файлы вместо localStorage)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _project_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _data_dir() -> Path:
    if getattr(sys, "frozen", False):
        d = Path(sys.executable).parent / "data"
    else:
        d = _project_dir() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _assets_dir() -> Path:
    if getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / "assets"
        if bundled.exists():
            return bundled
    base = _project_dir()
    for candidate in (base / "assets", base.parent):
        if (candidate / "leadsport-logo.png").exists():
            return candidate
    assets = base / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    return assets


ASSETS_DIR = _assets_dir()


def _load_json(name: str, default: Any) -> Any:
    path = _data_dir() / name
    if not path.exists():
        return default
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(name: str, data: Any) -> None:
    path = _data_dir() / name
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class Storage:
    """Единое хранилище данных студии."""

    def __init__(self) -> None:
        self.trainers: list[dict] = _load_json(
            "trainers.json", [{"login": "admin", "password": "admin"}]
        )
        self.students: list[dict] = _load_json("students.json", [])
        self.clients: list[dict] = _load_json("clients.json", [])
        self.payments: list[dict] = _load_json("payments.json", [])
        self.visits: list[dict] = _load_json("visits.json", [])
        self.schedule: list[dict] = _load_json("schedule.json", [])
        self.sub_types: list[dict] = _load_json("sub_types.json", [])
        self.client_subs: list[dict] = _load_json("client_subs.json", [])
        self.theme: str = _load_json("theme.json", "dark")
        self._id_counter = self._calc_id_counter() + 1

    def _calc_id_counter(self) -> int:
        ids: list[int] = []
        for coll in (
            self.clients,
            self.payments,
            self.visits,
            self.schedule,
            self.sub_types,
            self.client_subs,
        ):
            ids.extend(item.get("id", 0) for item in coll)
        return max(ids) if ids else 0

    def next_id(self) -> int:
        nid = self._id_counter
        self._id_counter += 1
        return nid

    def save_auth(self) -> None:
        _save_json("trainers.json", self.trainers)
        _save_json("students.json", self.students)

    def save_data(self) -> None:
        _save_json("clients.json", self.clients)
        _save_json("payments.json", self.payments)
        _save_json("visits.json", self.visits)
        _save_json("schedule.json", self.schedule)
        _save_json("sub_types.json", self.sub_types)
        _save_json("client_subs.json", self.client_subs)

    def save_theme(self) -> None:
        _save_json("theme.json", self.theme)

    def get_groups(self) -> list[str]:
        groups: set[str] = set()
        for s in self.schedule:
            if s.get("group"):
                groups.add(s["group"])
        for c in self.clients:
            if c.get("group"):
                groups.add(c["group"])
        return sorted(groups)

    def visit_group(self, visit: dict) -> str:
        if visit.get("group"):
            return visit["group"]
        client = next((c for c in self.clients if c["id"] == visit.get("clientId")), None)
        return client.get("group", "") if client else ""

    def client_name(self, client_id: int) -> str:
        c = next((x for x in self.clients if x["id"] == client_id), None)
        return c["name"] if c else "—"

    def sub_type_name(self, sub_type_id: int) -> str:
        st = next((x for x in self.sub_types if x["id"] == sub_type_id), None)
        return st["type"] if st else "—"
