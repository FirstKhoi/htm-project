"""Database manager — SQLite connection, initialization, and query helpers."""
import os
import sqlite3


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
        return conn

    def init_db(self):
        """Initialize the database with schema.sql."""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        conn = self.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single query and return the cursor."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def fetch_one(self, query: str, params: tuple = ()) -> dict | None:
        """Fetch a single row as a dictionary."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        """Fetch all rows as a list of dictionaries."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT and return the last inserted row ID."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def execute_many(self, query: str, params_list: list[tuple]):
        """Execute a query with multiple parameter sets."""
        conn = self.get_connection()
        try:
            conn.executemany(query, params_list)
            conn.commit()
        finally:
            conn.close()

    def count(self, query: str, params: tuple = ()) -> int:
        """Execute a COUNT query and return the integer result."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            conn.close()


# Singleton instance — initialized in app.py
db: DatabaseManager | None = None


def get_db() -> DatabaseManager:
    """Get the global database manager instance."""
    if db is None:
        raise RuntimeError("Database not initialized. Call init_app() first.")
    return db


def init_app(db_path: str) -> DatabaseManager:
    """Initialize the global database manager."""
    global db
    db = DatabaseManager(db_path)
    db.init_db()
    return db
