import sqlite3
import os
from typing import List
from models.task import Task

class SQLiteDatabase:
    """Gerencia a persistência de dados em um banco SQLite."""

    def __init__(self, db_path: str = "data/tasks.db"):
        self.db_path = db_path
        self._ensure_file_exists()
        self._init_db()

    def _ensure_file_exists(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'Média',
                    completed INTEGER NOT NULL DEFAULT 0,
                    is_favorite INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT
                )
            """)
            # Migração automática de colunas caso a tabela antiga já exista
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            if "priority" not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Média'")
            if "is_favorite" not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN is_favorite INTEGER DEFAULT 0")
            conn.commit()

    def load_tasks(self) -> List[Task]:
        tasks = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, priority, completed, is_favorite, created_at FROM tasks")
            rows = cursor.fetchall()
            for row in rows:
                tasks.append(
                    Task(
                        id=row[0],
                        title=row[1],
                        description=row[2] or "",
                        priority=row[3] or "Média",
                        completed=bool(row[4]),
                        is_favorite=bool(row[5]),
                        created_at=row[6]
                    )
                )
        return tasks

    def save_tasks(self, tasks: List[Task]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks")
            for task in tasks:
                cursor.execute(
                    """INSERT INTO tasks (id, title, description, priority, completed, is_favorite, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (task.id, task.title, task.description, task.priority, 1 if task.completed else 0, 1 if task.is_favorite else 0, task.created_at)
                )
            conn.commit()