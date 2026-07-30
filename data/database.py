import sqlite3
import os
from typing import List, Optional
from models.task import Task

class SQLiteDatabase:
    """Gerencia a persistência de dados (Usuários, Sessões e Tarefas) em SQLite."""

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
            
            # 1. Tabela de Usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT
                )
            """)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='users' AND name='idx_users_username_ci'")
            has_ci_index = cursor.fetchone() is not None
            if not has_ci_index:
                self._migrate_users_table(conn)
            else:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_ci ON users (LOWER(username))")

            # 2. Tabela de Sessão Ativa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            # 3. Tabela de Tarefas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL DEFAULT 1,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'Média',
                    completed INTEGER NOT NULL DEFAULT 0,
                    is_favorite INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Migrações automáticas de colunas
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            if "user_id" not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER DEFAULT 1")
            if "priority" not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Média'")
            if "is_favorite" not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN is_favorite INTEGER DEFAULT 0")

            cursor.execute("UPDATE tasks SET priority = 'Média' WHERE priority LIKE 'M%dia'")
            conn.commit()

    def _migrate_users_table(self, conn):
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            return

        cursor.execute("ALTER TABLE users RENAME TO users_old")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT
            )
        """)
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_ci ON users (LOWER(username))")
        cursor.execute("""
            INSERT INTO users (id, username, password_hash, created_at)
            SELECT id, username, password_hash, created_at FROM users_old
        """)
        cursor.execute("DROP TABLE users_old")
        conn.commit()

    # --- USUÁRIOS E SESSÃO ---

    def create_user(self, username: str, password_hash: str, created_at: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            normalized_username = username.strip()
            cursor.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (normalized_username, password_hash, created_at)
            )
            conn.commit()
            return cursor.lastrowid

    def get_user_by_username(self, username: str) -> Optional[dict]:
        normalized_username = username.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, created_at FROM users")
            rows = cursor.fetchall()
            for row in rows:
                stored_username = (row[1] or "").strip().lower()
                if stored_username == normalized_username:
                    return {"id": row[0], "username": row[1], "password_hash": row[2], "created_at": row[3]}
        return None

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "password_hash": row[2], "created_at": row[3]}
        return None

    def set_active_session(self, user_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO session (id, user_id) VALUES (1, ?)", (user_id,))
            conn.commit()

    def get_active_session_user_id(self) -> Optional[int]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM session WHERE id = 1")
            row = cursor.fetchone()
            return row[0] if row else None

    def clear_active_session(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM session WHERE id = 1")
            conn.commit()

    def save_language_preference(self, lang_code: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO app_settings (key, value) VALUES ('language', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (lang_code,))
            conn.commit()

    def get_language_preference(self) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM app_settings WHERE key = 'language'")
            row = cursor.fetchone()
            return row[0] if row else None

    # --- TAREFAS POR USUÁRIO ---

    def load_tasks(self, user_id: int) -> List[Task]:
        tasks = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, description, priority, completed, is_favorite, created_at FROM tasks WHERE user_id = ?",
                (user_id,)
            )
            rows = cursor.fetchall()
            for row in rows:
                p_val = row[3] or "Média"
                if "M" in p_val and "dia" in p_val:
                    p_val = "Média"
                tasks.append(
                    Task(
                        id=row[0],
                        title=row[1],
                        description=row[2] or "",
                        priority=p_val,
                        completed=bool(row[4]),
                        is_favorite=bool(row[5]),
                        created_at=row[6]
                    )
                )
        return tasks

    def add_task(self, user_id: int, title: str, description: str, priority: str, is_favorite: bool, created_at: str) -> Task:
        """Adiciona a tarefa no SQLite atribuindo o ID único do banco."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO tasks (user_id, title, description, priority, completed, is_favorite, created_at)
                   VALUES (?, ?, ?, ?, 0, ?, ?)""",
                (user_id, title, description, priority, 1 if is_favorite else 0, created_at)
            )
            conn.commit()
            task_id = cursor.lastrowid
            return Task(
                id=task_id,
                title=title,
                description=description,
                priority=priority,
                completed=False,
                is_favorite=is_favorite,
                created_at=created_at
            )

    def update_task(self, task: Task, user_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE tasks SET title = ?, description = ?, priority = ?, completed = ?, is_favorite = ?
                   WHERE id = ? AND user_id = ?""",
                (task.title, task.description, task.priority, 1 if task.completed else 0, 1 if task.is_favorite else 0, task.id, user_id)
            )
            conn.commit()

    def delete_task(self, task_id: int, user_id: int) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            conn.commit()