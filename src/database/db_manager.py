"""Database manager — SQLite connection and query helpers."""
import os
import sqlite3


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Run schema.sql to create tables."""
        schema = os.path.join(os.path.dirname(__file__), "schema.sql")
        conn = self.get_connection()
        try:
            conn.executescript(open(schema, encoding="utf-8").read())
            conn.commit()
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def fetch_one(self, query: str, params: tuple = ()) -> dict | None:
        conn = self.get_connection()
        try:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        conn = self.get_connection()
        try:
            return [dict(r) for r in conn.execute(query, params).fetchall()]
        finally:
            conn.close()

    def insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT, return last row ID."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def execute_many(self, query: str, params_list: list[tuple]):
        conn = self.get_connection()
        try:
            conn.executemany(query, params_list)
            conn.commit()
        finally:
            conn.close()

    def count(self, query: str, params: tuple = ()) -> int:
        conn = self.get_connection()
        try:
            result = conn.execute(query, params).fetchone()
            return result[0] if result else 0
        finally:
            conn.close()


# Module-level singleton
db: DatabaseManager | None = None


def get_db() -> DatabaseManager:
    if db is None:
        raise RuntimeError("Database not initialized. Call init_app() first.")
    return db


def init_app(db_path: str) -> DatabaseManager:
    global db
    db = DatabaseManager(db_path)
    db.init_db()
    return db
