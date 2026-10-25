import os
import sqlite3
from datetime import date


class Database:
    def __init__(self, path: str):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT,
                lat REAL,
                lon REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lang TEXT,
                question TEXT,
                answer TEXT,
                rating INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS usage (
                day TEXT,
                user_id INTEGER,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (day, user_id)
            );
            """
        )
        self.conn.commit()

    def get_lang(self, user_id: int) -> str | None:
        row = self.conn.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row[0] if row else None

    def set_lang(self, user_id: int, lang: str) -> None:
        self.conn.execute(
            "INSERT INTO users (user_id, lang) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang",
            (user_id, lang),
        )
        self.conn.commit()

    def set_location(self, user_id: int, lat: float, lon: float) -> None:
        self.conn.execute(
            "INSERT INTO users (user_id, lat, lon) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET lat = excluded.lat, lon = excluded.lon",
            (user_id, lat, lon),
        )
        self.conn.commit()

    def get_location(self, user_id: int) -> tuple[float, float] | None:
        row = self.conn.execute("SELECT lat, lon FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not row or row[0] is None:
            return None
        return row[0], row[1]

    def usage_today(self, user_id: int) -> tuple[int, int]:
        """Return (this user's requests today, all requests today)."""
        day = date.today().isoformat()
        mine = self.conn.execute(
            "SELECT count FROM usage WHERE day = ? AND user_id = ?", (day, user_id)
        ).fetchone()
        total = self.conn.execute("SELECT COALESCE(SUM(count), 0) FROM usage WHERE day = ?", (day,)).fetchone()
        return (mine[0] if mine else 0), total[0]

    def add_usage(self, user_id: int) -> None:
        day = date.today().isoformat()
        self.conn.execute(
            "INSERT INTO usage (day, user_id, count) VALUES (?, ?, 1) "
            "ON CONFLICT(day, user_id) DO UPDATE SET count = count + 1",
            (day, user_id),
        )
        self.conn.commit()

    def log_answer(self, user_id: int, lang: str, question: str, answer: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO answers (user_id, lang, question, answer) VALUES (?, ?, ?, ?)",
            (user_id, lang, question, answer),
        )
        self.conn.commit()
        return cur.lastrowid

    def rate(self, answer_id: int, user_id: int, rating: int) -> None:
        self.conn.execute(
            "UPDATE answers SET rating = ? WHERE id = ? AND user_id = ?", (rating, answer_id, user_id)
        )
        self.conn.commit()

    def stats(self) -> dict:
        one = lambda sql, *a: self.conn.execute(sql, a).fetchone()[0]
        today = date.today().isoformat()
        return {
            "users": one("SELECT COUNT(*) FROM users"),
            "users_today": one("SELECT COUNT(*) FROM users WHERE date(created_at) = ?", today),
            "questions": one("SELECT COUNT(*) FROM answers"),
            "questions_today": one("SELECT COUNT(*) FROM answers WHERE date(created_at) = ?", today),
            "likes": one("SELECT COUNT(*) FROM answers WHERE rating = 1"),
            "dislikes": one("SELECT COUNT(*) FROM answers WHERE rating = -1"),
            "languages": self.conn.execute(
                "SELECT COALESCE(lang, '?'), COUNT(*) FROM users GROUP BY lang ORDER BY 2 DESC"
            ).fetchall(),
            "bad": self.conn.execute(
                "SELECT question FROM answers WHERE rating = -1 ORDER BY id DESC LIMIT 5"
            ).fetchall(),
        }
