from typing import List, Optional
from models.task import Task

class TaskManager:
    """Controla as operações de tarefas (CRUD + Filtros + Estatísticas)."""

    def __init__(self, storage):
        self.storage = storage
        self._tasks: List[Task] = self.storage.load_tasks()

    def add_task(self, title: str, description: str = "", priority: str = "Média", is_favorite: bool = False) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("O título não pode ficar vazio.")

        task = Task(
            id=self._next_id(),
            title=title,
            description=description.strip(),
            priority=priority,
            is_favorite=is_favorite
        )
        self._tasks.append(task)
        self.storage.save_tasks(self._tasks)
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
                self.storage.save_tasks(self._tasks)
                return task
        return None

    def list_tasks(self, filter_by: str = "Todas", search_query: str = "") -> List[Task]:
        """Retorna as tarefas filtradas por aba e por termo de pesquisa."""
        tasks = self._tasks

        # 1. Filtro por Categoria / Aba
        if filter_by == "Pendentes":
            tasks = [t for t in tasks if not t.completed]
        elif filter_by == "Concluídas":
            tasks = [t for t in tasks if t.completed]
        elif filter_by == "Favoritas":
            tasks = [t for t in tasks if t.is_favorite]

        # 2. Filtro por Busca (Título ou Descrição)
        query = search_query.strip().lower()
        if query:
            tasks = [
                t for t in tasks
                if query in t.title.lower() or query in t.description.lower()
            ]

        return tasks

    def get_stats(self) -> dict:
        """Calcula as estatísticas gerais do aplicativo."""
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
                self.storage.save_tasks(self._tasks)
                return task
        return None

    def toggle_favorite(self, task_id: int) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                task.is_favorite = not task.is_favorite
                self.storage.save_tasks(self._tasks)
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        initial_count = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        if len(self._tasks) < initial_count:
            self.storage.save_tasks(self._tasks)
            return True
        return False

    def _next_id(self) -> int:
        if not self._tasks:
            return 1
        return max(task.id for task in self._tasks) + 1