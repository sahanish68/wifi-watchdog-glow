"""Tiny SQLite layer for scan history, whitelist, and alerts."""
import os
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(os.path.expanduser("~")) / ".netsentinel" / "data.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            kind TEXT NOT NULL,
            summary TEXT NOT NULL,
            payload TEXT
        );
        CREATE TABLE IF NOT EXISTS whitelist (
            mac TEXT PRIMARY KEY,
            label TEXT,
            added INTEGER
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        );
        """)


def add_scan(kind: str, summary: str, payload: str = ""):
    with _conn() as c:
        c.execute(
            "INSERT INTO scan_history(ts, kind, summary, payload) VALUES (?,?,?,?)",
            (int(time.time()), kind, summary, payload),
        )


def list_scans(limit=200):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM scan_history ORDER BY ts DESC LIMIT ?", (limit,)
        )]


def whitelist_add(mac: str, label: str = ""):
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO whitelist(mac,label,added) VALUES (?,?,?)",
            (mac.lower(), label, int(time.time())),
        )


def whitelist_remove(mac: str):
    with _conn() as c:
        c.execute("DELETE FROM whitelist WHERE mac=?", (mac.lower(),))


def whitelist_all():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM whitelist ORDER BY label")]


def add_alert(level: str, message: str):
    with _conn() as c:
        c.execute(
            "INSERT INTO alerts(ts,level,message) VALUES (?,?,?)",
            (int(time.time()), level, message),
        )


def list_alerts(limit=100):
    with _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM alerts ORDER BY ts DESC LIMIT ?", (limit,)
        )]
