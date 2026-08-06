from __future__ import annotations

import base64
import json
import os
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from flask import Flask, Response, flash, redirect, render_template, request, url_for

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "stinkis.db"
APP_VERSION = "0.2.1"
SCHEMA_VERSION = 2
MAX_PROFILE_IMAGE_BYTES = 2 * 1024 * 1024

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
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
        _add_column(db, "events", "is_important INTEGER NOT NULL DEFAULT 0")


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
                "items": [],
            }
        groups[person_id]["items"].append(row)
    return list(groups.values())


@app.get("/")
def index():
    q = request.args.get("q", "").strip()
    person_id = request.args.get("person_id", "").strip()
    category = request.args.get("category", "").strip()
    important_only = request.args.get("important") == "1"

    sql = """
        SELECT e.*, p.name AS person_name
        FROM events e
        JOIN people p ON p.id = e.person_id
        WHERE 1 = 1
    """
    params: list[Any] = []

    if person_id:
        sql += " AND e.person_id = ?"
        params.append(person_id)
    if category:
        sql += " AND e.category = ?"
        params.append(category)
    if important_only:
        sql += " AND e.is_important = 1"
    if q:
        like = f"%{q}%"
        sql += """
            AND (
                e.title LIKE ? OR e.notes LIKE ? OR e.category LIKE ? OR p.name LIKE ?
                OR EXISTS (
                    SELECT 1 FROM medications m
                    WHERE m.person_id = e.person_id
                      AND (m.name LIKE ? OR m.reason LIKE ? OR m.notes LIKE ?)
                )
                OR EXISTS (
                    SELECT 1 FROM allergies a
                    WHERE a.person_id = e.person_id
                      AND (a.name LIKE ? OR a.reaction LIKE ? OR a.notes LIKE ?)
                )
            )
        """
        params.extend([like] * 10)
    sql += " ORDER BY e.start_date DESC, e.id DESC"

    with get_db() as db:
        people = db.execute("SELECT * FROM people ORDER BY name").fetchall()
        events = db.execute(sql, params).fetchall()
        allergies = db.execute(
            """
            SELECT a.*, p.name AS person_name, p.profile_image, p.gender
            FROM allergies a JOIN people p ON p.id = a.person_id
            ORDER BY p.name, a.name
            """
        ).fetchall()
        medications = db.execute(
            """
            SELECT m.*, p.name AS person_name, p.profile_image, p.gender
            FROM medications m JOIN people p ON p.id = m.person_id
            ORDER BY p.name, m.name
            """
        ).fetchall()

    today_iso = date.today().isoformat()
    active_medications = [m for m in medications if not m["end_date"] or m["end_date"] >= today_iso]
    ended_medications = [m for m in medications if m["end_date"] and m["end_date"] < today_iso]

    return render_template(
        "index.html",
        people=people,
        events=events,
        allergy_groups=_group_by_person(allergies),
        medication_groups=_group_by_person(active_medications),
        medication_history_groups=_group_by_person(ended_medications),
        q=q,
        selected_person_id=person_id,
        selected_category=category,
        important_only=important_only,
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
    birth_date = request.form.get("birth_date", "").strip() or None
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
            db.execute(
                "INSERT INTO people (name, birth_date, notes, gender, profile_image) VALUES (?, ?, ?, ?, ?)",
                (name, birth_date, notes, gender, profile_image),
            )
    except ValueError as exc:
        flash(str(exc), "error")
    except sqlite3.IntegrityError:
        flash("Diese Person ist bereits vorhanden.", "error")
    else:
        flash("Person wurde angelegt.", "success")
    return redirect(url_for("index"))


@app.post("/people/<int:person_id>/edit")
def edit_person(person_id: int):
    birth_date = request.form.get("birth_date", "").strip() or None
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
    flash("Person und zugehörige Daten wurden gelöscht.", "success")
    return redirect(url_for("index"))


@app.post("/events")
def create_event():
    form = request.form
    required = ["person_id", "category", "title", "start_date"]
    if any(not form.get(key, "").strip() for key in required):
        flash("Person, Kategorie, Titel und Beginn sind Pflichtfelder.", "error")
        return redirect(url_for("index"))
    with get_db() as db:
        db.execute(
            """
            INSERT INTO events (
                person_id, category, title, start_date, end_date, notes,
                document_url, is_important
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form["person_id"], form["category"].strip(), form["title"].strip(),
                form["start_date"].strip(), form.get("end_date", "").strip() or None,
                form.get("notes", "").strip(), form.get("document_url", "").strip(),
                1 if form.get("is_important") == "on" else 0,
            ),
        )
    flash("Eintrag wurde gespeichert.", "success")
    return redirect(url_for("index"))


@app.post("/events/<int:event_id>/edit")
def edit_event(event_id: int):
    form = request.form
    with get_db() as db:
        db.execute(
            """
            UPDATE events
            SET person_id=?, category=?, title=?, start_date=?, end_date=?, notes=?,
                document_url=?, is_important=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (
                form["person_id"], form["category"].strip(), form["title"].strip(),
                form["start_date"].strip(), form.get("end_date", "").strip() or None,
                form.get("notes", "").strip(), form.get("document_url", "").strip(),
                1 if form.get("is_important") == "on" else 0, event_id,
            ),
        )
    flash("Eintrag wurde aktualisiert.", "success")
    return redirect(url_for("index"))


@app.post("/events/<int:event_id>/delete")
def delete_event(event_id: int):
    with get_db() as db:
        db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    flash("Eintrag wurde gelöscht.", "success")
    return redirect(url_for("index"))


@app.post("/allergies")
def create_allergy():
    form = request.form
    if not form.get("person_id") or not form.get("name", "").strip():
        flash("Person und Allergie/Unverträglichkeit sind Pflichtfelder.", "error")
        return redirect(url_for("index"))
    with get_db() as db:
        db.execute(
            "INSERT INTO allergies (person_id, name, reaction, notes) VALUES (?, ?, ?, ?)",
            (form["person_id"], form["name"].strip(), form.get("reaction", "").strip(), form.get("notes", "").strip()),
        )
    flash("Allergie oder Unverträglichkeit wurde gespeichert.", "success")
    return redirect(url_for("index"))


@app.post("/allergies/<int:allergy_id>/delete")
def delete_allergy(allergy_id: int):
    with get_db() as db:
        db.execute("DELETE FROM allergies WHERE id = ?", (allergy_id,))
    flash("Eintrag wurde gelöscht.", "success")
    return redirect(url_for("index"))


@app.post("/medications")
def create_medication():
    form = request.form
    if not form.get("person_id") or not form.get("name", "").strip():
        flash("Person und Medikament sind Pflichtfelder.", "error")
        return redirect(url_for("index"))
    with get_db() as db:
        db.execute(
            """
            INSERT INTO medications (person_id, name, dosage, reason, start_date, end_date, intolerance, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form["person_id"], form["name"].strip(), form.get("dosage", "").strip(),
                form.get("reason", "").strip(), form.get("start_date", "").strip() or None,
                form.get("end_date", "").strip() or None,
                1 if form.get("intolerance") == "on" else 0, form.get("notes", "").strip(),
            ),
        )
    flash("Medikament wurde gespeichert.", "success")
    return redirect(url_for("index"))


@app.post("/medications/<int:medication_id>/delete")
def delete_medication(medication_id: int):
    with get_db() as db:
        db.execute("DELETE FROM medications WHERE id = ?", (medication_id,))
    flash("Medikament wurde gelöscht.", "success")
    return redirect(url_for("index"))


@app.get("/export")
def export_data():
    with get_db() as db:
        payload = {
            "schemaVersion": SCHEMA_VERSION,
            "appVersion": APP_VERSION,
            "exportedAt": date.today().isoformat(),
            "people": [dict(row) for row in db.execute("SELECT * FROM people").fetchall()],
            "events": [dict(row) for row in db.execute("SELECT * FROM events").fetchall()],
            "allergies": [dict(row) for row in db.execute("SELECT * FROM allergies").fetchall()],
            "medications": [dict(row) for row in db.execute("SELECT * FROM medications").fetchall()],
        }
    body = json.dumps(payload, ensure_ascii=False, indent=2)
    return Response(body, mimetype="application/json", headers={"Content-Disposition": "attachment; filename=stinkis-krankenakten-export.json"})


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
        events = payload.get("events", [])
        allergies = payload.get("allergies", [])
        medications = payload.get("medications", [])
        if not all(isinstance(items, list) for items in (people, events, allergies, medications)):
            raise ValueError("Die Sicherung enthält ungültige Datenlisten.")

        with get_db() as db:
            db.execute("DELETE FROM medications")
            db.execute("DELETE FROM allergies")
            db.execute("DELETE FROM events")
            db.execute("DELETE FROM people")

            for row in people:
                item = _clean_record(row, ["id", "name", "birth_date", "notes", "gender", "profile_image", "created_at"])
                item.setdefault("gender", "")
                item.setdefault("profile_image", "")
                cols = list(item)
                db.execute(f"INSERT INTO people ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [item[c] for c in cols])
            for row in events:
                item = _clean_record(row, ["id", "person_id", "category", "title", "start_date", "end_date", "notes", "document_url", "is_important", "created_at", "updated_at"])
                item.setdefault("is_important", 0)
                cols = list(item)
                db.execute(f"INSERT INTO events ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [item[c] for c in cols])
            for table, rows, allowed in (
                ("allergies", allergies, ["id", "person_id", "name", "reaction", "notes", "created_at"]),
                ("medications", medications, ["id", "person_id", "name", "dosage", "reason", "start_date", "end_date", "intolerance", "notes", "created_at"]),
            ):
                for row in rows:
                    item = _clean_record(row, allowed)
                    cols = list(item)
                    db.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})", [item[c] for c in cols])
        flash(f"Sicherung (Schema {schema_version}) wurde erfolgreich importiert.", "success")
    except (ValueError, TypeError, json.JSONDecodeError, sqlite3.Error) as exc:
        flash(f"Import fehlgeschlagen: {exc}", "error")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8484, debug=False)
