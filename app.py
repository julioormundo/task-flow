import customtkinter as ctk
from config import COLORS, WINDOW_SIZE, WINDOW_TITLE
from data.database import SQLiteDatabase
from logic.task_manager import TaskManager
from ui.components import RoundedFrame
from ui.dashboard import DashboardView

class BlogView(ctk.CTkFrame):
    """Tela do Blog/Novidades do App com texto responsivo."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Título da tela
        title = ctk.CTkLabel(self, text="📢 Blog de Atualizações", font=("Segoe UI", 20, "bold"), text_color=COLORS["text"])
        title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Card para envolver a mensagem
        card = RoundedFrame(self, fg_color=COLORS["panel"])
        card.pack(fill="x", padx=20, pady=10)
        
        # Rótulo de aviso destacado
        notice_badge = ctk.CTkLabel(
            card, 
            text="⚠️ TOME NOTA", 
            font=("Segoe UI", 11, "bold"), 
            text_color="#f59e0b"
        )
        notice_badge.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Texto principal que ajustará a quebra de linha dinamicamente
        self.post = ctk.CTkLabel(
            card, 
            text="Este programa foi desenvolvido por Julio Ormundo utilizando um modelo gerado por Inteligência Artificial. Ele é um protótipo educacional e pode conter limitações ou bugs. Use com cautela e mantenha backup dos seus dados.",
            font=("Segoe UI", 13),
            text_color=COLORS["muted"],
            justify="left",
            anchor="w"
        )
        self.post.pack(fill="x", padx=20, pady=(0, 15))
        
        # Detecta o redimensionamento do frame para recalcular a quebra de linha
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        """Ajusta a largura de quebra do texto de acordo com o tamanho da janela."""
        largura_disponivel = event.width - 80
        if largura_disponivel > 100:
            self.post.configure(wraplength=largura_disponivel)


class SettingsView(ctk.CTkFrame):
    """Tela de Configurações do App."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        title = ctk.CTkLabel(self, text="⚙️ Configurações", font=("Segoe UI", 20, "bold"), text_color=COLORS["text"])
        title.pack(anchor="w", padx=20, pady=20)
        
        label = ctk.CTkLabel(self, text="Preferências e opções do aplicativo.", font=("Segoe UI", 13), text_color=COLORS["muted"])
        label.pack(anchor="w", padx=20)


class TalkDevsView(ctk.CTkFrame):
    """Tela Fale Conosco."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        title = ctk.CTkLabel(self, text="💬 Fale Conosco", font=("Segoe UI", 20, "bold"), text_color=COLORS["text"])
        title.pack(anchor="w", padx=20, pady=20)
        
        label = ctk.CTkLabel(self, text="Fale com os desenvolvedores.", font=("Segoe UI", 13), text_color=COLORS["muted"])
        label.pack(anchor="w", padx=20)


class TaskFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(900, 600)
        self.configure(fg_color=COLORS["background"])

        # Inicialização com SQLite
        storage = SQLiteDatabase("data/tasks.db")
        self.task_manager = TaskManager(storage)

        # Configuração do Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Menu Lateral (Sidebar)
        self.setup_sidebar()

        # 2. Container Principal
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # 3. Mapeamento de Telas (Views)
        self.views = {
            "tasks": DashboardView(self.main_container, self.task_manager),
            "blog": BlogView(self.main_container),
            "settings": SettingsView(self.main_container),
            "talk": TalkDevsView(self.main_container),
        }

        # Exibir a tela padrão
        self.show_view("tasks")

    def setup_sidebar(self):
        """Cria a barra lateral de navegação."""
        sidebar = ctk.CTkFrame(self, fg_color=COLORS["panel"], width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")

        title = ctk.CTkLabel(sidebar, text="TaskFlow", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"])
        title.pack(pady=(20, 30), padx=20)

        # Item 1: Minhas Tarefas
        btn_tasks = ctk.CTkButton(
            sidebar, 
            text="📋 Minhas Tarefas", 
            fg_color="transparent", 
            hover_color=COLORS["surface"],
            anchor="w",
            command=lambda: self.show_view("tasks")
        )
        btn_tasks.pack(fill="x", padx=10, pady=5)

        # Item 2: Blog
        btn_blog = ctk.CTkButton(
            sidebar, 
            text="📢 Blog", 
            fg_color="transparent", 
            hover_color=COLORS["surface"],
            anchor="w",
            command=lambda: self.show_view("blog")
        )
        btn_blog.pack(fill="x", padx=10, pady=5)

        # Item 3: Configurações
        btn_settings = ctk.CTkButton(
            sidebar, 
            text="⚙️ Configurações", 
            fg_color="transparent", 
            hover_color=COLORS["surface"],
            anchor="w",
            command=lambda: self.show_view("settings")
        )
        btn_settings.pack(fill="x", padx=10, pady=5)

        # Item 4: Fale Conosco
        btn_talk = ctk.CTkButton(
            sidebar, 
            text="💬 Fale Conosco", 
            fg_color="transparent", 
            hover_color=COLORS["surface"],
            anchor="w",
            command=lambda: self.show_view("talk")
        )
        btn_talk.pack(fill="x", padx=10, pady=5)

    def show_view(self, view_name: str):
        """Oculta todas as telas e exibe apenas a escolhida."""
        for view in self.views.values():
            view.pack_forget()

        if view_name in self.views:
            self.views[view_name].pack(fill="both", expand=True)


def run():
    app = TaskFlowApp()
    app.mainloop()