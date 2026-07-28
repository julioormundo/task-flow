from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    """Representa uma tarefa do aplicativo TaskFlow."""
    id: int
    title: str
    description: str = ""
    priority: str = "Média"      # "Baixa", "Média", "Alta"
    completed: bool = False
    is_favorite: bool = False    # Para a aba de Favoritas
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M")