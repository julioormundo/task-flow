import csv
import json
from datetime import datetime
from typing import List, Optional
from models.task import Task

class TaskManager:
    """Controla as operações de tarefas do usuário logado."""

    def __init__(self, storage, user_id: int):
        self.storage = storage
        self.user_id = user_id
        self._tasks: List[Task] = self.storage.load_tasks(self.user_id)

    def add_task(self, title: str, description: str = "", priority: str = "Média", is_favorite: bool = False) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("O título não pode ficar vazio.")

        created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        task = self.storage.add_task(self.user_id, title, description.strip(), priority, is_favorite, created_at)
        self._tasks.append(task)
        return task

    def update_task(self, task_id: int, title: str, description: str, priority: str) -> Optional[Task]:
        title = title.strip()
        if not title:
            raise ValueError("O título não pode ficar vazio.")

        for task in self._tasks:
            if task.id == task_id:
                task.title = title
                task.description = description.strip()
                task.priority = priority
                self.storage.update_task(task, self.user_id)
                return task
        return None

    def list_tasks(self, filter_by: str = "Todas", search_query: str = "") -> List[Task]:
        tasks = list(self._tasks)

        normalized_filter = (filter_by or "Todas").strip().lower()
        if normalized_filter in {"pendentes", "pending"}:
            tasks = [t for t in tasks if not t.completed]
        elif normalized_filter in {"concluídas", "completed"}:
            tasks = [t for t in tasks if t.completed]
        elif normalized_filter in {"favoritas", "favorites"}:
            tasks = [t for t in tasks if t.is_favorite]

        query = search_query.strip().lower()
        if query:
            tasks = [
                t for t in tasks
                if query in t.title.lower() or query in t.description.lower()
            ]

        return tasks

    def get_stats(self) -> dict:
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks if t.completed)
        pending = total - completed
        favorites = sum(1 for t in self._tasks if t.is_favorite)
        percentage = round((completed / total) * 100) if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "favorites": favorites,
            "percentage": percentage
        }

    def toggle_task_completion(self, task_id: int) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                task.completed = not task.completed
                self.storage.update_task(task, self.user_id)
                return task
        return None

    def toggle_favorite(self, task_id: int) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                task.is_favorite = not task.is_favorite
                self.storage.update_task(task, self.user_id)
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        task_to_remove = None
        for task in self._tasks:
            if task.id == task_id:
                task_to_remove = task
                break

        if task_to_remove:
            self._tasks.remove(task_to_remove)
            self.storage.delete_task(task_id, self.user_id)
            return True
        return False

    def export_to_json(self, filepath: str) -> None:
        data = [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "completed": t.completed,
                "is_favorite": t.is_favorite,
                "created_at": t.created_at
            }
            for t in self._tasks
        ]
        with open(filepath, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def export_to_csv(self, filepath: str) -> None:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(["ID", "Título", "Descrição", "Prioridade", "Concluída", "Favorita", "Data de Criação"])
            for t in self._tasks:
                writer.writerow([
                    t.id, t.title, t.description, t.priority,
                    "Sim" if t.completed else "Não",
                    "Sim" if t.is_favorite else "Não",
                    t.created_at
                ])