import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "memory" / "history.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS posted (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                url         TEXT    UNIQUE NOT NULL,
                title       TEXT    NOT NULL,
                source      TEXT    NOT NULL,
                posted_at   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scrape_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                source      TEXT    NOT NULL,
                scraped_at  TEXT    NOT NULL,
                item_count  INTEGER NOT NULL
            );
        """)


def is_duplicate(url: str) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM posted WHERE url = ?", (url,)).fetchone()
        return row is not None


def mark_posted(url: str, title: str, source: str, posted_at: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO posted (url, title, source, posted_at) VALUES (?, ?, ?, ?)",
            (url, title, source, posted_at),
        )


def log_scrape(source: str, scraped_at: str, item_count: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO scrape_log (source, scraped_at, item_count) VALUES (?, ?, ?)",
            (source, scraped_at, item_count),
        )


def get_last_scrape(source: str) -> Optional[str]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT scraped_at FROM scrape_log WHERE source = ? ORDER BY id DESC LIMIT 1",
            (source,),
        ).fetchone()
        return row["scraped_at"] if row else None


def get_today_post_count(today: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM posted WHERE posted_at LIKE ?",
            (f"{today}%",),
        ).fetchone()
        return row["cnt"]
