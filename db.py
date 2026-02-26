from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

DB_PATH = Path("reset.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS checks (
                day TEXT NOT NULL,
                section TEXT NOT NULL,
                item TEXT NOT NULL,
                checked INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (day, section, item)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_metrics (
                day TEXT PRIMARY KEY,
                sleep_hours REAL,
                energy INTEGER,
                time_available INTEGER,
                notes TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        conn.commit()


def get_checks_for_day(day: str) -> dict[tuple[str, str], bool]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT section, item, checked FROM checks WHERE day = ?", (day,)
        ).fetchall()
    return {(r["section"], r["item"]): bool(r["checked"]) for r in rows}


def upsert_check(day: str, section: str, item: str, checked: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO checks (day, section, item, checked)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(day, section, item)
            DO UPDATE SET checked = excluded.checked
            """,
            (day, section, item, int(checked)),
        )
        conn.commit()


def get_metrics_for_day(day: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT sleep_hours, energy, time_available, notes
            FROM daily_metrics
            WHERE day = ?
            """,
            (day,),
        ).fetchone()
    if not row:
        return None
    return {
        "sleep_hours": row["sleep_hours"],
        "energy": row["energy"],
        "time_available": row["time_available"],
        "notes": row["notes"] or "",
    }


def upsert_metrics(
    day: str,
    sleep_hours: float,
    energy: int,
    time_available: int,
    notes: str,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO daily_metrics (day, sleep_hours, energy, time_available, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(day)
            DO UPDATE SET
                sleep_hours = excluded.sleep_hours,
                energy = excluded.energy,
                time_available = excluded.time_available,
                notes = excluded.notes
            """,
            (day, sleep_hours, energy, time_available, notes.strip()),
        )
        conn.commit()


def reset_day(day: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM checks WHERE day = ?", (day,))
        conn.execute("DELETE FROM daily_metrics WHERE day = ?", (day,))
        conn.commit()


def completion_for_day(day: str, protocol: dict[str, list[str]]) -> dict[str, float | int | str]:
    checks = get_checks_for_day(day)
    total = 0
    done = 0
    for section, items in protocol.items():
        for item in items:
            total += 1
            if checks.get((section, item), False):
                done += 1
    pct = (done / total * 100.0) if total else 0.0
    return {"day": day, "done": done, "total": total, "pct": round(pct, 1)}


def completion_history(protocol: dict[str, list[str]], days: int = 60) -> pd.DataFrame:
    end = date.today()
    start = end - timedelta(days=days - 1)
    records = []
    cursor = start
    while cursor <= end:
        records.append(completion_for_day(cursor.isoformat(), protocol))
        cursor += timedelta(days=1)
    return pd.DataFrame(records)


def current_streak(protocol: dict[str, list[str]], threshold_pct: float = 70.0) -> int:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT MIN(day) AS first_day
            FROM (
                SELECT day FROM checks
                UNION ALL
                SELECT day FROM daily_metrics
            )
            """
        ).fetchone()
    first_day = row["first_day"] if row else None
    if not first_day:
        return 0

    today = date.today()
    cursor = today
    floor = date.fromisoformat(first_day)
    streak = 0
    while cursor >= floor:
        pct = float(completion_for_day(cursor.isoformat(), protocol)["pct"])
        if pct >= threshold_pct:
            streak += 1
        else:
            break
        cursor -= timedelta(days=1)
    return streak


def get_setting(key: str, default: str = "") -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
    if not row or row["value"] is None:
        return default
    return str(row["value"])


def set_setting(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO app_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        conn.commit()
