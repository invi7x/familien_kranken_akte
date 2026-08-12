from __future__ import annotations

import base64
import csv
import io
import json
import os
from html import escape
import sqlite3
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from typing import Any

from flask import Flask, Response, abort, flash, redirect, render_template, request, send_file, url_for
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "stinkis.db"
APP_VERSION = "0.8.1"
SCHEMA_VERSION = 8
MAX_PROFILE_IMAGE_BYTES = 2 * 1024 * 1024

BACKUP_DEFAULTS = {
    "backup_enabled": "0",
    "backup_day": "1",
    "backup_dir": "/backups",
    "backup_keep": "10",
    "backup_last_run": "",
}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-portainer")
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024


def get_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in db.execute(f"PRAGMA table_info({table})").fetchall()}


def _add_column(db: sqlite3.Connection, table: str, definition: str) -> None:
    name = definition.split()[0]
    if name not in _columns(db, table):
        db.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")


def init_db() -> None:
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                birth_date TEXT,
                notes TEXT DEFAULT '',
                gender TEXT DEFAULT '',
                profile_image TEXT DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS treatment_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                notes TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                notes TEXT DEFAULT '',
                document_url TEXT DEFAULT '',
                is_important INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS allergies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                reaction TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                start_date TEXT,
                end_date TEXT,
                resolved_note TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                dosage TEXT DEFAULT '',
                reason TEXT DEFAULT '',
                start_date TEXT,
                end_date TEXT,
                intolerance INTEGER NOT NULL DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
            );
            """
        )
        _add_column(db, "people", "gender TEXT DEFAULT ''")
        _add_column(db, "people", "profile_image TEXT DEFAULT ''")
        _add_column(db, "people", "sort_order INTEGER NOT NULL DEFAULT 0")
        people_for_order = db.execute("SELECT id, sort_order FROM people ORDER BY sort_order, name, id").fetchall()
        if people_for_order and all(int(row["sort_order"] or 0) == 0 for row in people_for_order):
            for position, row in enumerate(people_for_order, start=1):
                db.execute("UPDATE people SET sort_order=? WHERE id=?", (position * 10, row["id"]))
        _add_column(db, "events", "is_important INTEGER NOT NULL DEFAULT 0")
        _add_column(db, "events", "medication_dosage TEXT DEFAULT ''")
        _add_column(db, "events", "medication_reason TEXT DEFAULT ''")
        _add_column(db, "events", "medication_intolerance INTEGER NOT NULL DEFAULT 0")
        _add_column(db, "events", "legacy_medication_id INTEGER")
        _add_column(db, "events", "is_sick_note INTEGER NOT NULL DEFAULT 0")
        _add_column(db, "events", "sick_from TEXT")
        _add_column(db, "events", "sick_to TEXT")
        _add_column(db, "events", "has_attest INTEGER NOT NULL DEFAULT 0")
        _add_column(db, "events", "attest_type TEXT DEFAULT ''")
        _add_column(db, "events", "case_id INTEGER")
        _add_column(db, "treatment_cases", "status TEXT NOT NULL DEFAULT 'active'")
        _add_column(db, "treatment_cases", "updated_at TEXT")
        _add_column(db, "allergies", "start_date TEXT")
        _add_column(db, "allergies", "end_date TEXT")
        _add_column(db, "allergies", "resolved_note TEXT DEFAULT ''")

        for key, value in BACKUP_DEFAULTS.items():
            db.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)", (key, value))

        # v0.3 vereinheitlicht Medikamente: Die Timeline ist die einzige Datenquelle.
        # Bereits vorhandene Datensätze aus der alten separaten Medikamenten-Tabelle
        # werden einmalig in Timeline-Einträge überführt.
        legacy_meds = db.execute("SELECT * FROM medications ORDER BY id").fetchall()
        for med in legacy_meds:
            already_migrated = db.execute(
                "SELECT id FROM events WHERE legacy_medication_id = ?", (med["id"],)
            ).fetchone()
            if already_migrated:
                continue
            start_date = med["start_date"] or (med["created_at"] or "")[:10] or date.today().isoformat()
            existing = db.execute(
                """
                SELECT id FROM events
                WHERE person_id=? AND category='Medikament' AND title=?
                  AND start_date=? AND COALESCE(end_date,'')=COALESCE(?,'')
                ORDER BY id LIMIT 1
                """,
                (med["person_id"], med["name"], start_date, med["end_date"]),
            ).fetchone()
            if existing:
                db.execute(
                    """UPDATE events SET medication_dosage=?, medication_reason=?,
                       medication_intolerance=?, legacy_medication_id=? WHERE id=?""",
                    (med["dosage"], med["reason"], med["intolerance"], med["id"], existing["id"]),
                )
            else:
                db.execute(
                    """
                    INSERT INTO events (
                        person_id, category, title, start_date, end_date, notes,
                        document_url, is_important, medication_dosage, medication_reason,
                        medication_intolerance, legacy_medication_id
                    ) VALUES (?, 'Medikament', ?, ?, ?, ?, '', 0, ?, ?, ?, ?)
                    """,
                    (med["person_id"], med["name"], start_date, med["end_date"], med["notes"],
                     med["dosage"], med["reason"], med["intolerance"], med["id"]),
                )
        if legacy_meds:
            db.execute("DELETE FROM medications")


def _load_backup_settings(db: sqlite3.Connection | None = None) -> dict[str, Any]:
    owns_connection = db is None
    db = db or get_db()
    try:
        rows = db.execute("SELECT key, value FROM app_settings").fetchall()
        values = {row["key"]: row["value"] for row in rows}
        for key, default in BACKUP_DEFAULTS.items():
            values.setdefault(key, default)
        return {
            "enabled": values["backup_enabled"] == "1",
            "day": int(values["backup_day"] or 1),
            "directory": values["backup_dir"] or "/backups",
            "keep": min(10, max(1, int(values["backup_keep"] or 10))),
            "last_run": values["backup_last_run"] or "",
        }
    finally:
        if owns_connection:
            db.close()


def _set_app_setting(db: sqlite3.Connection, key: str, value: str) -> None:
    db.execute(
        "INSERT INTO app_settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


def _build_export_payload(db: sqlite3.Connection) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "appVersion": APP_VERSION,
        "exportedAt": datetime.now().isoformat(timespec="seconds"),
        "people": [dict(row) for row in db.execute("SELECT * FROM people").fetchall()],
        "treatmentCases": [dict(row) for row in db.execute("SELECT * FROM treatment_cases").fetchall()],
        "events": [dict(row) for row in db.execute("SELECT * FROM events").fetchall()],
        "allergies": [dict(row) for row in db.execute("SELECT * FROM allergies").fetchall()],
        "medications": [
            {
                "person_id": row["person_id"], "name": row["title"],
                "dosage": row["medication_dosage"], "reason": row["medication_reason"],
                "start_date": row["start_date"], "end_date": row["end_date"],
                "intolerance": row["medication_intolerance"], "notes": row["notes"],
                "created_at": row["created_at"],
            }
            for row in db.execute("SELECT * FROM events WHERE category='Medikament'").fetchall()
        ],
    }


def _backup_due(settings: dict[str, Any], today_value: date | None = None) -> bool:
    if not settings.get("enabled"):
        return False
    today_value = today_value or date.today()
    if today_value.day < int(settings.get("day") or 1):
        return False
    last_run = str(settings.get("last_run") or "")[:10]
    if not last_run:
        return True
    try:
        previous = date.fromisoformat(last_run)
    except ValueError:
        return True
    return (previous.year, previous.month) != (today_value.year, today_value.month)


def _known_backup_files(backup_dir: Path) -> list[Path]:
    files: dict[str, Path] = {}
    for pattern in ("familienakte-backup-*.json", "stinkis-backup-*.json"):
        for item in backup_dir.glob(pattern):
            if item.is_file():
                files[str(item.resolve())] = item
    return sorted(files.values(), key=lambda item: item.stat().st_mtime, reverse=True)


def _prune_server_backups(backup_dir: Path, keep: int) -> None:
    keep = max(1, min(10, int(keep)))
    for old_file in _known_backup_files(backup_dir)[keep:]:
        old_file.unlink(missing_ok=True)


def _list_server_backups(settings: dict[str, Any]) -> list[dict[str, Any]]:
    backup_dir = Path(settings.get("directory") or "/backups")
    if not backup_dir.is_absolute() or not backup_dir.exists():
        return []
    result = []
    for item in _known_backup_files(backup_dir):
        stat = item.stat()
        size = stat.st_size
        if size < 1024:
            size_label = f"{size} B"
        elif size < 1024 * 1024:
            size_label = f"{size / 1024:.1f} KB"
        else:
            size_label = f"{size / (1024 * 1024):.1f} MB"
        result.append({
            "name": item.name,
            "size": size_label,
            "created": datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M"),
        })
    return result


def _write_server_backup() -> Path:
    with get_db() as db:
        settings = _load_backup_settings(db)
        backup_dir = Path(settings["directory"])
        if not backup_dir.is_absolute():
            raise ValueError("Der Backup-Pfad muss ein absoluter Pfad im Container sein.")
        backup_dir.mkdir(parents=True, exist_ok=True)
        payload = _build_export_payload(db)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        target = backup_dir / f"familienakte-backup-{timestamp}.json"
        temp_target = target.with_suffix(".json.tmp")
        temp_target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_target.replace(target)
        _prune_server_backups(backup_dir, settings.get("keep") or 10)
        _set_app_setting(db, "backup_last_run", datetime.now().isoformat(timespec="seconds"))
        return target


@app.context_processor
def inject_globals() -> dict[str, Any]:
    return {
        "categories": [
            "Krankheit",
            "Arztbesuch",
            "Medikament",
            "Labor",
            "Impfung",
            "OP",
            "Notiz",
        ],
        "category_icons": {
            "Krankheit": "🤒",
            "Arztbesuch": "🩺",
            "Medikament": "💊",
            "Labor": "🧪",
            "Impfung": "💉",
            "OP": "🏥",
            "Notiz": "📝",
        },
        "today": date.today().isoformat(),
        "app_version": APP_VERSION,
    }


def _group_by_person(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    groups: dict[int, dict[str, Any]] = {}
    for row in rows:
        person_id = int(row["person_id"])
        if person_id not in groups:
            groups[person_id] = {
                "person_id": person_id,
                "person_name": row["person_name"],
                "profile_image": row["profile_image"] if "profile_image" in row.keys() else "",
                "gender": row["gender"] if "gender" in row.keys() else "",
                "sort_order": row["sort_order"] if "sort_order" in row.keys() else 0,
                "items": [],
            }
        groups[person_id]["items"].append(row)
    return sorted(groups.values(), key=lambda group: (int(group.get("sort_order") or 0), group["person_name"].lower()))



def _age_from_birth_date(value: str | None, today_value: date | None = None) -> int | None:
    if not value:
        return None
    try:
        born = date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    today_value = today_value or date.today()
    return today_value.year - born.year - ((today_value.month, today_value.day) < (born.month, born.day))


def _age_phrase_for_event(birth_date_value: str | None, event_date_value: str | None) -> str:
    if not birth_date_value or not event_date_value:
        return ""
    try:
        event_day = date.fromisoformat(event_date_value)
    except (TypeError, ValueError):
        return ""
    age = _age_from_birth_date(birth_date_value, event_day)
    if age is None:
        return ""
    return f"im Alter von {age} {'Jahr' if age == 1 else 'Jahren'}"


GERMAN_MONTHS = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni",
    7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
}

def _group_events_by_month(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current_key = None
    for row in rows:
        try:
            year, month, _ = map(int, row["start_date"].split("-"))
            key = f"{year:04d}-{month:02d}"
            label = f"{GERMAN_MONTHS.get(month, month)} {year}"
        except (ValueError, AttributeError):
            key = "unknown"
            label = "Ohne Monatsangabe"
        if key != current_key:
            groups.append({"key": key, "label": label, "items": []})
            current_key = key
        groups[-1]["items"].append(row)
    return groups

@app.get("/")
def index():
    q = request.args.get("q", "").strip()
    person_id = request.args.get("person_id", "").strip()
    category = request.args.get("category", "").strip()
    important_only = request.args.get("important") == "1"
    status_filter = request.args.get("status", "").strip()
    if status_filter not in {"", "planned", "running", "completed"}:
        status_filter = ""
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    followup_case_id = request.args.get("followup_case_id", "").strip()

    try:
        per_page = int(request.args.get("per_page", "20"))
    except ValueError:
        per_page = 20
    if per_page not in {20, 50, 100}:
        per_page = 20

    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1

    today_iso = date.today().isoformat()
    base_where = ["1 = 1"]
    params: list[Any] = []
    if person_id:
        base_where.append("e.person_id = ?")
        params.append(person_id)
    if category:
        base_where.append("e.category = ?")
        params.append(category)
    if important_only:
        base_where.append("e.is_important = 1")
    if date_from:
        base_where.append("COALESCE(e.end_date, e.start_date) >= ?")
        params.append(date_from)
    if date_to:
        base_where.append("e.start_date <= ?")
        params.append(date_to)
    if q:
        like = f"%{q}%"
        base_where.append(
            """(
                e.title LIKE ? OR e.notes LIKE ? OR e.category LIKE ? OR p.name LIKE ?
                OR e.medication_dosage LIKE ? OR e.medication_reason LIKE ?
                OR EXISTS (
                    SELECT 1 FROM allergies a
                    WHERE a.person_id = e.person_id
                      AND (a.name LIKE ? OR a.reaction LIKE ? OR a.notes LIKE ?)
                )
                OR EXISTS (
                    SELECT 1 FROM treatment_cases tc
                    WHERE tc.id = e.case_id AND tc.title LIKE ?
                )
            )"""
        )
        params.extend([like] * 10)

    # Dieselbe Statuslogik wie die Tags der Timeline.
    if status_filter == "planned":
        base_where.append("e.start_date > ?")
        params.append(today_iso)
    elif status_filter == "running":
        # Ohne Enddatum gilt ein bereits begonnener Eintrag als laufend.
        # Abgeschlossen ist ein Eintrag nur mit explizitem Enddatum in der Vergangenheit.
        base_where.append(
            """e.start_date <= ? AND (
                e.end_date IS NULL OR e.end_date >= ?
            )"""
        )
        params.extend([today_iso, today_iso])
    elif status_filter == "completed":
        base_where.append(
            """e.start_date <= ? AND e.end_date IS NOT NULL AND e.end_date < ?"""
        )
        params.extend([today_iso, today_iso])

    base_where_sql = " AND ".join(base_where)
    history_where_sql = f"{base_where_sql} AND e.start_date <= ?"
    future_where_sql = f"{base_where_sql} AND e.start_date > ?"

    with get_db() as db:
        total_events = int(db.execute(
            f"""SELECT COUNT(*) AS total FROM events e JOIN people p ON p.id=e.person_id
                WHERE {history_where_sql}""", [*params, today_iso]
        ).fetchone()["total"])
        total_future_events = int(db.execute(
            f"""SELECT COUNT(*) AS total FROM events e JOIN people p ON p.id=e.person_id
                WHERE {future_where_sql}""", [*params, today_iso]
        ).fetchone()["total"])
        total_matches = total_events + total_future_events

        # Bei reinem Zukunftsfilter wird die Zukunft wie die Historie 20/50/100 paginiert.
        planned_only = status_filter == "planned"
        pagination_total = total_future_events if planned_only else total_events
        total_pages = max(1, (pagination_total + per_page - 1) // per_page)
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page

        if planned_only:
            events = []
            future_events = db.execute(
                f"""SELECT e.*, p.name AS person_name, p.profile_image AS person_profile_image, p.birth_date AS person_birth_date,
                           c.title AS case_title
                    FROM events e JOIN people p ON p.id=e.person_id
                    LEFT JOIN treatment_cases c ON c.id=e.case_id
                    WHERE {future_where_sql}
                    ORDER BY e.start_date DESC, e.id DESC LIMIT ? OFFSET ?""",
                [*params, today_iso, per_page, offset],
            ).fetchall()
        else:
            events = db.execute(
                f"""SELECT e.*, p.name AS person_name, p.profile_image AS person_profile_image, p.birth_date AS person_birth_date,
                           c.title AS case_title
                    FROM events e JOIN people p ON p.id=e.person_id
                    LEFT JOIN treatment_cases c ON c.id=e.case_id
                    WHERE {history_where_sql}
                    ORDER BY e.start_date DESC, e.id DESC LIMIT ? OFFSET ?""",
                [*params, today_iso, per_page, offset],
            ).fetchall()
            # Im Mischbetrieb gehört die Zukunftsvorschau nur auf Seite 1.
            # Dadurch startet Seite 2+ direkt mit dem paginierten bisherigen Verlauf.
            if page == 1:
                future_events = db.execute(
                    f"""SELECT e.*, p.name AS person_name, p.profile_image AS person_profile_image, p.birth_date AS person_birth_date,
                               c.title AS case_title
                        FROM events e JOIN people p ON p.id=e.person_id
                        LEFT JOIN treatment_cases c ON c.id=e.case_id
                        WHERE {future_where_sql}
                        ORDER BY e.start_date DESC, e.id DESC""",
                    [*params, today_iso],
                ).fetchall()
            else:
                future_events = []

        events = [dict(row) for row in events]
        future_events = [dict(row) for row in future_events]
        for item in [*events, *future_events]:
            item["event_age_phrase"] = _age_phrase_for_event(item.get("person_birth_date"), item.get("start_date"))

        people_rows = db.execute("SELECT * FROM people ORDER BY sort_order, name, id").fetchall()
        people = []
        for row in people_rows:
            person = dict(row)
            person["age"] = _age_from_birth_date(person.get("birth_date"), date.fromisoformat(today_iso))
            people.append(person)

        side_params: list[Any] = []
        side_where = ""
        if person_id:
            side_where = " WHERE a.person_id = ?"
            side_params.append(person_id)
        allergies = db.execute(
            f"""SELECT a.*, p.name AS person_name, p.profile_image, p.gender, p.sort_order
                FROM allergies a JOIN people p ON p.id=a.person_id {side_where}
                ORDER BY p.sort_order, p.name, a.name""", side_params
        ).fetchall()

        med_params: list[Any] = []
        med_person_where = ""
        if person_id:
            med_person_where = " AND e.person_id = ?"
            med_params.append(person_id)
        medications = db.execute(
            f"""SELECT e.id, e.person_id, e.case_id, e.title AS name, e.medication_dosage AS dosage,
                       e.medication_reason AS reason, e.start_date, e.end_date,
                       e.medication_intolerance AS intolerance, e.notes, e.document_url,
                       e.is_important, p.name AS person_name, p.profile_image, p.gender, p.sort_order
                FROM events e JOIN people p ON p.id=e.person_id
                WHERE e.category='Medikament' {med_person_where}
                ORDER BY p.sort_order, p.name, e.start_date DESC, e.title""", med_params
        ).fetchall()

        case_rows = [dict(row) for row in db.execute(
            """SELECT c.*, p.name AS person_name, p.sort_order,
                      (SELECT COUNT(*) FROM events e WHERE e.case_id=c.id) AS event_count
               FROM treatment_cases c JOIN people p ON p.id=c.person_id
               ORDER BY p.sort_order, p.name, CASE c.status WHEN 'active' THEN 0 WHEN 'completed' THEN 1 ELSE 2 END, COALESCE(c.updated_at,c.created_at) DESC, c.id DESC"""
        ).fetchall()]
        active_case_rows = [row for row in case_rows if (row.get("status") or "active") == "active"]
        case_event_rows = [dict(row) for row in db.execute(
            """SELECT e.id, e.case_id, e.person_id, e.category, e.title, e.start_date, e.end_date,
                      e.medication_dosage, e.medication_reason
               FROM events e WHERE e.case_id IS NOT NULL
               ORDER BY e.case_id, e.start_date, e.id"""
        ).fetchall()]
        events_by_case: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for case_event in case_event_rows:
            events_by_case[int(case_event["case_id"])].append(case_event)
        for case_row in case_rows:
            case_row["items"] = events_by_case.get(int(case_row["id"]), [])
        followup_case = None
        if followup_case_id:
            try:
                wanted_case_id = int(followup_case_id)
                followup_case = next((item for item in case_rows if int(item["id"]) == wanted_case_id), None)
            except ValueError:
                followup_case = None
        backup_settings = _load_backup_settings(db)
        backup_files = _list_server_backups(backup_settings)

    active_allergies = [a for a in allergies if not a["end_date"] or a["end_date"] > today_iso]
    ended_allergies = [a for a in allergies if a["end_date"] and a["end_date"] <= today_iso]
    active_medications = [m for m in medications if m["start_date"] <= today_iso and (not m["end_date"] or m["end_date"] >= today_iso)]
    ended_medications = [m for m in medications if m["end_date"] and m["end_date"] < today_iso]

    page_start = offset + 1 if pagination_total else 0
    shown_count = len(future_events) if planned_only else len(events)
    page_end = min(offset + shown_count, pagination_total)

    return render_template(
        "index.html",
        people=people,
        events=events,
        history_month_groups=_group_events_by_month(events),
        future_events=future_events,
        allergy_groups=_group_by_person(active_allergies),
        allergy_history_groups=_group_by_person(ended_allergies),
        medication_groups=_group_by_person(active_medications),
        medication_history_groups=_group_by_person(ended_medications),
        treatment_cases=case_rows,
        active_treatment_cases=active_case_rows,
        followup_case=followup_case,
        backup_settings=backup_settings,
        backup_files=backup_files,
        q=q,
        selected_person_id=person_id,
        selected_category=category,
        important_only=important_only,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page,
        total_events=total_events,
        total_future_events=total_future_events,
        total_matches=total_matches,
        planned_only=planned_only,
        total_pages=total_pages,
        page_start=page_start,
        page_end=page_end,
    )


def _profile_image_from_upload() -> str | None:
    upload = request.files.get("profile_image")
    if not upload or not upload.filename:
        return None
    raw = upload.read(MAX_PROFILE_IMAGE_BYTES + 1)
    if len(raw) > MAX_PROFILE_IMAGE_BYTES:
        raise ValueError("Das Profilbild darf höchstens 2 MB groß sein.")
    mime = (upload.mimetype or "").lower()
    if mime not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise ValueError("Erlaubt sind JPG, PNG, WEBP oder GIF.")
    return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"


@app.post("/people")
def create_person():
    name = request.form.get("name", "").strip()
    try:
        birth_date = _validated_date(request.form.get("birth_date"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    notes = request.form.get("notes", "").strip()
    gender = request.form.get("gender", "").strip()
    if gender not in {"", "male", "female"}:
        gender = ""
    if not name:
        flash("Bitte einen Namen eingeben.", "error")
        return redirect(url_for("index"))
    try:
        profile_image = _profile_image_from_upload() or ""
        with get_db() as db:
            next_sort = int(db.execute("SELECT COALESCE(MAX(sort_order), 0) + 10 AS value FROM people").fetchone()["value"])
            db.execute(
                "INSERT INTO people (name, birth_date, notes, gender, profile_image, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
                (name, birth_date, notes, gender, profile_image, next_sort),
            )
    except ValueError as exc:
        flash(str(exc), "error")
    except sqlite3.IntegrityError:
        flash("Diese Person ist bereits vorhanden.", "error")
    else:
        flash("Person wurde angelegt.", "success")
    return redirect(url_for("index"))


@app.post("/people/reorder")
def reorder_people():
    payload = request.get_json(silent=True) or {}
    ordered_ids = payload.get("people", [])
    if not isinstance(ordered_ids, list):
        return {"ok": False, "error": "Ungültige Reihenfolge."}, 400
    try:
        ordered_ids = [int(person_id) for person_id in ordered_ids]
    except (TypeError, ValueError):
        return {"ok": False, "error": "Ungültige Personen-ID."}, 400
    with get_db() as db:
        existing = {int(row["id"]) for row in db.execute("SELECT id FROM people").fetchall()}
        if set(ordered_ids) != existing or len(ordered_ids) != len(existing):
            return {"ok": False, "error": "Die Reihenfolge ist unvollständig."}, 400
        for position, person_id in enumerate(ordered_ids, start=1):
            db.execute("UPDATE people SET sort_order=? WHERE id=?", (position * 10, person_id))
    return {"ok": True}


@app.post("/people/<int:person_id>/edit")
def edit_person(person_id: int):
    try:
        birth_date = _validated_date(request.form.get("birth_date"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    notes = request.form.get("notes", "").strip()
    gender = request.form.get("gender", "").strip()
    if gender not in {"", "male", "female"}:
        gender = ""
    try:
        image = _profile_image_from_upload()
        remove_image = request.form.get("remove_profile_image") == "on"
        with get_db() as db:
            if image is not None:
                db.execute(
                    "UPDATE people SET birth_date=?, notes=?, gender=?, profile_image=? WHERE id=?",
                    (birth_date, notes, gender, image, person_id),
                )
            elif remove_image:
                db.execute(
                    "UPDATE people SET birth_date=?, notes=?, gender=?, profile_image='' WHERE id=?",
                    (birth_date, notes, gender, person_id),
                )
            else:
                db.execute(
                    "UPDATE people SET birth_date=?, notes=?, gender=? WHERE id=?",
                    (birth_date, notes, gender, person_id),
                )
    except ValueError as exc:
        flash(str(exc), "error")
    else:
        flash("Person wurde aktualisiert.", "success")
    return redirect(url_for("index"))


@app.post("/people/<int:person_id>/delete")
def delete_person(person_id: int):
    with get_db() as db:
        db.execute("DELETE FROM people WHERE id = ?", (person_id,))
    return _post_action_response("Person und zugehörige Daten wurden gelöscht.")



def _post_action_response(message: str):
    """Keep the current filter context on normal POSTs and support modal AJAX actions."""
    if request.headers.get("X-Requested-With") == "fetch":
        return ("", 204)
    flash(message, "success")
    referrer = request.referrer or url_for("index")
    return redirect(referrer)


def _valid_date_range(start_date: str, end_date: str | None) -> bool:
    return not end_date or end_date >= start_date


def _validated_date(raw: str | None, *, required: bool = False) -> str | None:
    value = (raw or "").strip()
    if not value:
        if required:
            raise ValueError("Bitte ein vollständiges Datum eingeben.")
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Bitte ein gültiges Datum eingeben.") from exc
    return parsed.isoformat()


def _resolve_case_id(db: sqlite3.Connection, person_id: int, raw_case_id: str | None, new_case_title: str | None) -> int | None:
    new_title = (new_case_title or "").strip()
    if new_title:
        cursor = db.execute(
            "INSERT INTO treatment_cases (person_id, title) VALUES (?, ?)",
            (person_id, new_title),
        )
        return int(cursor.lastrowid)
    raw = (raw_case_id or "").strip()
    if not raw or raw == "__new__":
        return None
    try:
        case_id = int(raw)
    except ValueError:
        return None
    row = db.execute(
        "SELECT id FROM treatment_cases WHERE id=? AND person_id=?",
        (case_id, person_id),
    ).fetchone()
    return int(row["id"]) if row else None


def _redirect_with_query(**updates):
    target = request.referrer or url_for("index")
    parts = urlsplit(target)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    for key, value in updates.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = str(value)
    return redirect(urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)))


@app.post("/cases/<int:case_id>/edit")
def edit_treatment_case(case_id: int):
    title = request.form.get("title", "").strip()
    if not title:
        return {"ok": False, "error": "Bitte eine Bezeichnung eingeben."}, 400
    with get_db() as db:
        db.execute("UPDATE treatment_cases SET title=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (title, case_id))
    return {"ok": True, "title": title}


@app.post("/cases/<int:case_id>/status")
def set_treatment_case_status(case_id: int):
    status = request.form.get("status", "active").strip()
    if status not in {"active", "completed", "archived"}:
        return {"ok": False, "error": "Ungültiger Status."}, 400
    with get_db() as db:
        db.execute("UPDATE treatment_cases SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, case_id))
    return {"ok": True, "status": status}


@app.post("/cases/<int:case_id>/delete")
def delete_treatment_case(case_id: int):
    with get_db() as db:
        count = int(db.execute("SELECT COUNT(*) AS n FROM events WHERE case_id=?", (case_id,)).fetchone()["n"])
        db.execute("UPDATE events SET case_id=NULL, updated_at=CURRENT_TIMESTAMP WHERE case_id=?", (case_id,))
        db.execute("DELETE FROM treatment_cases WHERE id=?", (case_id,))
    return {"ok": True, "unlinked": count}


@app.post("/events")
def create_event():
    form = request.form
    required = ["person_id", "category", "title", "start_date"]
    if any(not form.get(key, "").strip() for key in required):
        flash("Person, Kategorie, Titel und Beginn sind Pflichtfelder.", "error")
        return redirect(url_for("index"))
    try:
        start_date = _validated_date(form.get("start_date"), required=True)
        end_date = _validated_date(form.get("end_date"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    if not _valid_date_range(start_date, end_date):
        flash("Das Enddatum darf nicht vor dem Beginn liegen.", "error")
        return redirect(url_for("index"))
    try:
        sick_from = _validated_date(form.get("sick_from")) or ""
        sick_to = _validated_date(form.get("sick_to")) or ""
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    if form.get("category", "").strip() == "Krankheit" and sick_from and sick_to and sick_to < sick_from:
        flash("Das Ende der Krankschreibung darf nicht vor ihrem Beginn liegen.", "error")
        return redirect(url_for("index"))
    with get_db() as db:
        person_id = int(form["person_id"])
        case_id = _resolve_case_id(db, person_id, form.get("case_id"), form.get("new_case_title"))
        db.execute(
            """
            INSERT INTO events (
                person_id, category, title, start_date, end_date, notes,
                document_url, is_important, medication_dosage, medication_reason,
                medication_intolerance, is_sick_note, sick_from, sick_to, has_attest, attest_type, case_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                person_id, form["category"].strip(), form["title"].strip(),
                start_date, end_date,
                form.get("notes", "").strip(), form.get("document_url", "").strip(),
                1 if form.get("is_important") == "on" else 0,
                form.get("medication_dosage", "").strip() if form["category"].strip() == "Medikament" else "",
                form.get("medication_reason", "").strip() if form["category"].strip() == "Medikament" else "",
                1 if form["category"].strip() == "Medikament" and form.get("medication_intolerance") == "on" else 0,
                1 if form["category"].strip() == "Krankheit" and form.get("is_sick_note") == "on" else 0,
                sick_from or None if form["category"].strip() == "Krankheit" else None,
                sick_to or None if form["category"].strip() == "Krankheit" else None,
                1 if form["category"].strip() == "Krankheit" and form.get("has_attest") == "on" else 0,
                form.get("attest_type", "").strip() if form["category"].strip() == "Krankheit" else "",
                case_id,
            ),
        )
    if case_id:
        flash("Eintrag wurde gespeichert und dem Vorgang zugeordnet.", "success")
        return _redirect_with_query(followup_case_id=case_id)
    return _post_action_response("Eintrag wurde gespeichert.")


@app.post("/events/<int:event_id>/edit")
def edit_event(event_id: int):
    form = request.form
    try:
        start_date = _validated_date(form.get("start_date"), required=True)
        end_date = _validated_date(form.get("end_date"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    if not start_date or not _valid_date_range(start_date, end_date):
        flash("Bitte einen gültigen Zeitraum eingeben; das Ende darf nicht vor dem Beginn liegen.", "error")
        return redirect(url_for("index"))
    try:
        sick_from = _validated_date(form.get("sick_from")) or ""
        sick_to = _validated_date(form.get("sick_to")) or ""
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    if form.get("category", "").strip() == "Krankheit" and sick_from and sick_to and sick_to < sick_from:
        flash("Das Ende der Krankschreibung darf nicht vor ihrem Beginn liegen.", "error")
        return redirect(url_for("index"))
    with get_db() as db:
        person_id = int(form["person_id"])
        case_id = _resolve_case_id(db, person_id, form.get("case_id"), form.get("new_case_title"))
        db.execute(
            """
            UPDATE events
            SET person_id=?, category=?, title=?, start_date=?, end_date=?, notes=?,
                document_url=?, is_important=?, medication_dosage=?, medication_reason=?,
                medication_intolerance=?, is_sick_note=?, sick_from=?, sick_to=?,
                has_attest=?, attest_type=?, case_id=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                person_id, form["category"].strip(), form["title"].strip(),
                start_date, end_date,
                form.get("notes", "").strip(), form.get("document_url", "").strip(),
                1 if form.get("is_important") == "on" else 0,
                form.get("medication_dosage", "").strip() if form["category"].strip() == "Medikament" else "",
                form.get("medication_reason", "").strip() if form["category"].strip() == "Medikament" else "",
                1 if form["category"].strip() == "Medikament" and form.get("medication_intolerance") == "on" else 0,
                1 if form["category"].strip() == "Krankheit" and form.get("is_sick_note") == "on" else 0,
                sick_from or None if form["category"].strip() == "Krankheit" else None,
                sick_to or None if form["category"].strip() == "Krankheit" else None,
                1 if form["category"].strip() == "Krankheit" and form.get("has_attest") == "on" else 0,
                form.get("attest_type", "").strip() if form["category"].strip() == "Krankheit" else "",
                case_id,
                event_id,
            ),
        )
    return _post_action_response("Eintrag wurde aktualisiert.")


@app.post("/events/<int:event_id>/delete")
def delete_event(event_id: int):
    with get_db() as db:
        db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    return _post_action_response("Eintrag wurde gelöscht.")


@app.post("/allergies")
def create_allergy():
    form = request.form
    if not form.get("person_id") or not form.get("name", "").strip():
        flash("Person und Allergie/Unverträglichkeit sind Pflichtfelder.", "error")
        return redirect(url_for("index"))
    try:
        allergy_start_date = _validated_date(form.get("start_date"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    with get_db() as db:
        db.execute(
            "INSERT INTO allergies (person_id, name, reaction, notes, start_date) VALUES (?, ?, ?, ?, ?)",
            (form["person_id"], form["name"].strip(), form.get("reaction", "").strip(),
             form.get("notes", "").strip(), allergy_start_date),
        )
    return _post_action_response("Allergie oder Unverträglichkeit wurde gespeichert.")


@app.post("/allergies/<int:allergy_id>/edit")
def edit_allergy(allergy_id: int):
    form = request.form
    if not form.get("person_id") or not form.get("name", "").strip():
        flash("Person und Allergie/Unverträglichkeit sind Pflichtfelder.", "error")
        return redirect(url_for("index"))
    resolved = form.get("resolved") == "on"
    try:
        start_date = _validated_date(form.get("start_date"))
        end_date = _validated_date(form.get("end_date"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    if resolved and not end_date:
        end_date = date.today().isoformat()
    if not resolved:
        end_date = None
    if start_date and end_date and end_date < start_date:
        flash("Das Enddatum darf nicht vor dem Beginn liegen.", "error")
        return redirect(url_for("index"))
    with get_db() as db:
        db.execute(
            """UPDATE allergies SET person_id=?, name=?, reaction=?, notes=?,
               start_date=?, end_date=?, resolved_note=? WHERE id=?""",
            (form["person_id"], form["name"].strip(), form.get("reaction", "").strip(),
             form.get("notes", "").strip(), start_date, end_date,
             form.get("resolved_note", "").strip() if resolved else "", allergy_id),
        )
    return _post_action_response("Allergie oder Unverträglichkeit wurde aktualisiert.")


@app.post("/allergies/<int:allergy_id>/delete")
def delete_allergy(allergy_id: int):
    with get_db() as db:
        db.execute("DELETE FROM allergies WHERE id = ?", (allergy_id,))
    return _post_action_response("Allergie oder Unverträglichkeit wurde gelöscht.")


@app.get("/export")
def export_data():
    with get_db() as db:
        payload = _build_export_payload(db)
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    return Response(body, mimetype="application/json", headers={"Content-Disposition": "attachment; filename=familienakte-export.json"})


@app.post("/settings/backups")
def update_backup_settings():
    enabled = request.form.get("backup_enabled") == "on"
    directory = request.form.get("backup_dir", "/backups").strip() or "/backups"
    try:
        day = int(request.form.get("backup_day", "1"))
        keep = int(request.form.get("backup_keep", "10"))
    except ValueError:
        flash("Backup-Tag und Anzahl der Sicherungen müssen Zahlen sein.", "error")
        return redirect(url_for("index"))
    if not 1 <= day <= 28:
        flash("Der Backup-Tag muss zwischen 1 und 28 liegen.", "error")
        return redirect(url_for("index"))
    if not 1 <= keep <= 10:
        flash("Es können zwischen 1 und 10 Sicherungen aufbewahrt werden.", "error")
        return redirect(url_for("index"))
    if not Path(directory).is_absolute():
        flash("Der Backup-Pfad muss ein absoluter Pfad im Container sein.", "error")
        return redirect(url_for("index"))
    with get_db() as db:
        _set_app_setting(db, "backup_enabled", "1" if enabled else "0")
        _set_app_setting(db, "backup_day", str(day))
        _set_app_setting(db, "backup_dir", directory)
        _set_app_setting(db, "backup_keep", str(keep))
    try:
        backup_dir = Path(directory)
        if backup_dir.exists():
            _prune_server_backups(backup_dir, keep)
    except OSError:
        pass
    flash("Backup-Einstellungen wurden gespeichert.", "success")
    return redirect(url_for("index", open_modal="backup-modal"))


@app.post("/settings/backups/run")
def run_backup_now():
    try:
        target = _write_server_backup()
    except (OSError, ValueError) as exc:
        flash(f"Server-Backup fehlgeschlagen: {exc}", "error")
    else:
        flash("Server-Backup wurde gespeichert.", "success")
    return redirect(url_for("index", open_modal="backup-modal"))


@app.get("/backups/<path:filename>/download")
def download_server_backup(filename: str):
    if Path(filename).name != filename or not filename.endswith(".json"):
        abort(404)
    if not (filename.startswith("familienakte-backup-") or filename.startswith("stinkis-backup-")):
        abort(404)
    settings = _load_backup_settings()
    backup_dir = Path(settings["directory"])
    target = (backup_dir / filename).resolve()
    try:
        target.relative_to(backup_dir.resolve())
    except ValueError:
        abort(404)
    if not target.is_file():
        abort(404)
    return send_file(target, as_attachment=True, download_name=target.name, mimetype="application/json")


def _clean_record(record: dict[str, Any], allowed: list[str]) -> dict[str, Any]:
    return {key: record.get(key) for key in allowed if key in record}


@app.post("/import")
def import_data():
    upload = request.files.get("backup_file")
    if not upload or not upload.filename:
        flash("Bitte eine JSON-Sicherungsdatei auswählen.", "error")
        return redirect(url_for("index"))
    try:
        payload = json.load(upload.stream)
        if not isinstance(payload, dict):
            raise ValueError("Ungültiges Sicherungsformat.")
        # Exporte aus v0.1 besitzen noch keine schemaVersion und gelten als Version 1.
        schema_version = int(payload.get("schemaVersion", 1))
        if schema_version > SCHEMA_VERSION:
            raise ValueError("Diese Sicherung stammt aus einer neueren App-Version.")
        people = payload.get("people", [])
        treatment_cases = payload.get("treatmentCases", [])
        events = payload.get("events", [])
        allergies = payload.get("allergies", [])
        medications = payload.get("medications", [])
        if not all(isinstance(items, list) for items in (people, treatment_cases, events, allergies, medications)):
            raise ValueError("Die Sicherung enthält ungültige Datenlisten.")

        with get_db() as db:
            db.execute("DELETE FROM medications")
            db.execute("DELETE FROM allergies")
            db.execute("DELETE FROM events")
            db.execute("DELETE FROM treatment_cases")
            db.execute("DELETE FROM people")

            for row in people:
                item = _clean_record(row, ["id", "name", "birth_date", "notes", "gender", "profile_image", "sort_order", "created_at"])
                item.setdefault("gender", "")
                item.setdefault("profile_image", "")
                item.setdefault("sort_order", 0)
                cols = list(item)
                db.execute(f"INSERT INTO people ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [item[c] for c in cols])
            imported_people = db.execute("SELECT id, sort_order FROM people ORDER BY sort_order, name, id").fetchall()
            if imported_people and all(int(row["sort_order"] or 0) == 0 for row in imported_people):
                for position, row in enumerate(imported_people, start=1):
                    db.execute("UPDATE people SET sort_order=? WHERE id=?", (position * 10, row["id"]))
            for row in treatment_cases:
                item = _clean_record(row, ["id", "person_id", "title", "notes", "status", "created_at", "updated_at"])
                if not item.get("person_id") or not item.get("title"):
                    continue
                item.setdefault("status", "active")
                cols = list(item)
                db.execute(f"INSERT INTO treatment_cases ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [item[c] for c in cols])
            for row in events:
                item = _clean_record(row, ["id", "person_id", "category", "title", "start_date", "end_date", "notes", "document_url", "is_important", "medication_dosage", "medication_reason", "medication_intolerance", "legacy_medication_id", "is_sick_note", "sick_from", "sick_to", "has_attest", "attest_type", "case_id", "created_at", "updated_at"])
                item.setdefault("is_important", 0)
                cols = list(item)
                db.execute(f"INSERT INTO events ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [item[c] for c in cols])
            for row in allergies:
                item = _clean_record(row, ["id", "person_id", "name", "reaction", "notes", "start_date", "end_date", "resolved_note", "created_at"])
                cols = list(item)
                db.execute(f"INSERT INTO allergies ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [item[c] for c in cols])

            # Bis Schema 2 lagen Medikamente separat. Beim Import werden sie
            # direkt in das neue Timeline-Modell übernommen. Schema 3 enthält
            # sie bereits vollständig in 'events'.
            if schema_version < 3:
                for row in medications:
                    item = _clean_record(row, ["id", "person_id", "name", "dosage", "reason", "start_date", "end_date", "intolerance", "notes", "created_at"])
                    start_date = item.get("start_date") or str(item.get("created_at") or "")[:10] or date.today().isoformat()
                    existing = db.execute(
                        """SELECT id FROM events WHERE person_id=? AND category='Medikament' AND title=?
                           AND start_date=? AND COALESCE(end_date,'')=COALESCE(?,'')
                           ORDER BY id LIMIT 1""",
                        (item.get("person_id"), item.get("name") or "Medikament", start_date, item.get("end_date")),
                    ).fetchone()
                    if existing:
                        db.execute(
                            """UPDATE events SET medication_dosage=?, medication_reason=?,
                               medication_intolerance=?, legacy_medication_id=? WHERE id=?""",
                            (item.get("dosage") or "", item.get("reason") or "", item.get("intolerance") or 0,
                             item.get("id"), existing["id"]),
                        )
                    else:
                        db.execute(
                            """
                            INSERT INTO events (person_id, category, title, start_date, end_date, notes,
                                                document_url, is_important, medication_dosage,
                                                medication_reason, medication_intolerance, legacy_medication_id)
                            VALUES (?, 'Medikament', ?, ?, ?, ?, '', 0, ?, ?, ?, ?)
                            """,
                            (item.get("person_id"), item.get("name") or "Medikament", start_date,
                             item.get("end_date"), item.get("notes") or "", item.get("dosage") or "",
                             item.get("reason") or "", item.get("intolerance") or 0, item.get("id")),
                        )
        flash(f"Sicherung (Schema {schema_version}) wurde erfolgreich importiert.", "success")
    except (ValueError, TypeError, json.JSONDecodeError, sqlite3.Error) as exc:
        flash(f"Import fehlgeschlagen: {exc}", "error")
    return redirect(url_for("index"))


def _report_data():
    person_id = request.args.get("person_id", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    category = request.args.get("category", "").strip()
    important_only = request.args.get("important") == "1"
    if not person_id:
        return None
    where = ["e.person_id = ?"]
    params: list[Any] = [person_id]
    if category:
        where.append("e.category = ?")
        params.append(category)
    if important_only:
        where.append("e.is_important = 1")
    if date_from:
        where.append("COALESCE(e.end_date, e.start_date) >= ?")
        params.append(date_from)
    if date_to:
        where.append("e.start_date <= ?")
        params.append(date_to)
    with get_db() as db:
        person = db.execute("SELECT * FROM people WHERE id=?", (person_id,)).fetchone()
        if not person:
            return None
        events = db.execute(
            f"""SELECT e.*, c.title AS case_title FROM events e
                LEFT JOIN treatment_cases c ON c.id=e.case_id
                WHERE {' AND '.join(where)} ORDER BY e.start_date ASC, e.id ASC""", params
        ).fetchall()
        allergy_where = ["person_id = ?"]
        allergy_params: list[Any] = [person_id]
        if date_from:
            allergy_where.append("COALESCE(end_date, ?) >= ?")
            allergy_params.extend([date.today().isoformat(), date_from])
        if date_to:
            allergy_where.append("COALESCE(start_date, created_at) <= ?")
            allergy_params.append(date_to)
        allergies = db.execute(
            f"SELECT * FROM allergies WHERE {' AND '.join(allergy_where)} ORDER BY COALESCE(start_date, created_at), id",
            allergy_params,
        ).fetchall()
    return person, events, allergies, date_from, date_to, category, important_only


@app.get("/reports/csv")
def report_csv():
    data = _report_data()
    if not data:
        flash("Für einen Bericht bitte eine gültige Person auswählen.", "error")
        return redirect(url_for("index"))
    person, events, allergies, date_from, date_to, category, important_only = data

    stream = io.StringIO()
    writer = csv.writer(stream, delimiter=';')
    writer.writerow(["Datentyp", "Person", "Kategorie", "Titel", "Vorgang", "Beginn", "Ende",
                     "Details", "Notizen", "Wichtig", "Externe URL / Link"])
    for event in events:
        details = []
        if event["category"] == "Medikament":
            if event["medication_dosage"]:
                details.append(f"Dosierung: {event['medication_dosage']}")
            if event["medication_reason"]:
                details.append(f"Grund: {event['medication_reason']}")
            if event["medication_intolerance"]:
                details.append("Unverträglichkeit")
        if event["category"] == "Krankheit":
            if event["is_sick_note"]:
                details.append(f"Krankgeschrieben: {event['sick_from'] or event['start_date']} bis {event['sick_to'] or event['end_date'] or event['start_date']}")
            if event["has_attest"]:
                details.append("Attest: " + (event["attest_type"] or "vorhanden"))
        writer.writerow(["Timeline", person["name"], event["category"], event["title"], event["case_title"] or "",
                         event["start_date"], event["end_date"] or "", " | ".join(details),
                         event["notes"] or "", "ja" if event["is_important"] else "nein",
                         event["document_url"] or ""])
    for allergy in allergies:
        details = allergy["reaction"] or ""
        if allergy["resolved_note"]:
            details = (details + " | " if details else "") + "Abschluss: " + allergy["resolved_note"]
        writer.writerow(["Allergie", person["name"], "Allergie/Unverträglichkeit", allergy["name"], "",
                         allergy["start_date"] or "", allergy["end_date"] or "", details,
                         allergy["notes"] or "", "", ""])

    filename = f"krankenakte-{person['name'].lower().replace(' ', '-')}.csv"
    body = '\ufeff' + stream.getvalue()
    return Response(body, mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.get("/reports/pdf")
def report_pdf():
    data = _report_data()
    if not data:
        flash("Für einen Bericht bitte eine gültige Person auswählen.", "error")
        return redirect(url_for("index"))
    person, events, allergies, date_from, date_to, category, important_only = data
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Meta", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.HexColor("#475569")))
    styles.add(ParagraphStyle(name="EventTitle", parent=styles["Heading3"], fontSize=11, leading=14, spaceAfter=3))
    story = [Paragraph("Gesundheitsakte", styles["Title"]), Paragraph(escape(person["name"]), styles["Heading2"])]
    meta = []
    if person["birth_date"]:
        age = _age_from_birth_date(person["birth_date"])
        age_text = f" · {age} {'Jahr' if age == 1 else 'Jahre'}" if age is not None else ""
        meta.append(f"Geboren: {person['birth_date']}{age_text}")
    if date_from or date_to: meta.append(f"Zeitraum: {date_from or 'offen'} bis {date_to or 'offen'}")
    if category: meta.append(f"Kategorie: {category}")
    if important_only: meta.append("Nur wichtige Einträge")
    if meta: story.append(Paragraph(escape(" | ".join(meta)), styles["Meta"]))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("Allergien & Unverträglichkeiten", styles["Heading2"]))
    if allergies:
        table_data = [["Bezeichnung", "Reaktion", "Von", "Bis", "Notiz"]]
        for a in allergies:
            note = a["notes"] or ""
            if a["resolved_note"]: note = (note + " / " if note else "") + "Abschluss: " + a["resolved_note"]
            table_data.append([a["name"], a["reaction"] or "", a["start_date"] or "", a["end_date"] or "", note])
        table = Table(table_data, colWidths=[38*mm, 34*mm, 23*mm, 23*mm, 50*mm], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e2e8f0")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#cbd5e1")),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]))
        story.append(table)
    else:
        story.append(Paragraph("Keine passenden Allergieeinträge.", styles["Meta"]))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("Timeline", styles["Heading2"]))
    if not events:
        story.append(Paragraph("Keine passenden Timeline-Einträge.", styles["Meta"]))
    for e in events:
        period = e["start_date"] + ((" bis " + e["end_date"]) if e["end_date"] else "")
        marker = "! " if e["is_important"] else ""
        story.append(Paragraph(escape(f"{marker}{e['title']}"), styles["EventTitle"]))
        story.append(Paragraph(escape(f"{period} | {e['category']}"), styles["Meta"]))
        extras = []
        if e["category"] == "Medikament":
            if e["medication_dosage"]: extras.append("Dosierung: " + e["medication_dosage"])
            if e["medication_reason"]: extras.append("Grund: " + e["medication_reason"])
        if e["category"] == "Krankheit":
            if e["is_sick_note"]: extras.append(f"Krankgeschrieben: {e['sick_from'] or e['start_date']} bis {e['sick_to'] or e['end_date'] or e['start_date']}")
            if e["has_attest"]: extras.append("Attest: " + (e["attest_type"] or "vorhanden"))
        if extras: story.append(Paragraph(escape(" | ".join(extras)), styles["Meta"]))
        if e["notes"]: story.append(Paragraph(escape(e["notes"]).replace("\n", "<br/>"), styles["BodyText"]))
        if e["document_url"]: story.append(Paragraph("Externe URL / Link: " + escape(e["document_url"]), styles["Meta"]))
        story.append(Spacer(1, 3*mm))
    doc.build(story)
    body = buffer.getvalue()
    filename = f"krankenakte-{person['name'].lower().replace(' ', '-')}.pdf"
    return Response(body, mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})


@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8484, debug=False)
