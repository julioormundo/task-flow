from tkinter import filedialog
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
        
        title = ctk.CTkLabel(self, text="📢 Blog de Atualizações", font=("Segoe UI", 20, "bold"), text_color=COLORS["text"])
        title.pack(anchor="w", padx=20, pady=(20, 10))
        
        card = RoundedFrame(self, fg_color=COLORS["panel"])
        card.pack(fill="x", padx=20, pady=10)
        
        notice_badge = ctk.CTkLabel(
            card, 
            text="⚠️ TOME NOTA", 
            font=("Segoe UI", 11, "bold"), 
            text_color="#f59e0b"
        )
        notice_badge.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.post = ctk.CTkLabel(
            card, 
            text="Este programa foi desenvolvido por Julio Ormundo utilizando um modelo gerado por Inteligência Artificial. Ele é um protótipo educacional e pode conter limitações ou bugs. Use com cautela e mantenha backup dos seus dados.",
            font=("Segoe UI", 13),
            text_color=COLORS["muted"],
            justify="left",
            anchor="w"
        )
        self.post.pack(fill="x", padx=20, pady=(0, 15))
        
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        largura_disponivel = event.width - 80
        if largura_disponivel > 100:
            self.post.configure(wraplength=largura_disponivel)


class SettingsView(ctk.CTkFrame):
    """Tela de Configurações com opções de Exportação de Dados."""
    def __init__(self, master, task_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.task_manager = task_manager

        title = ctk.CTkLabel(self, text="⚙️ Configurações", font=("Segoe UI", 20, "bold"), text_color=COLORS["text"])
        title.pack(anchor="w", padx=20, pady=(20, 10))

        # Card de Exportação de Dados
        card = RoundedFrame(self, fg_color=COLORS["panel"])
        card.pack(fill="x", padx=20, pady=10)

        card_title = ctk.CTkLabel(card, text="📁 Exportação de Dados", font=("Segoe UI", 16, "bold"), text_color=COLORS["text"])
        card_title.pack(anchor="w", padx=20, pady=(15, 5))

        card_desc = ctk.CTkLabel(
            card, 
            text="Exporte suas tarefas salvas no SQLite para formatos externos como backup ou análise em planilhas.",
            font=("Segoe UI", 13),
            text_color=COLORS["muted"]
        )
        card_desc.pack(anchor="w", padx=20, pady=(0, 15))

        # Container de Botões
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(anchor="w", padx=20, pady=(0, 15))

        btn_json = ctk.CTkButton(
            btn_frame,
            text="📄 Exportar em JSON",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.export_json
        )
        btn_json.pack(side="left", padx=(0, 10))

        btn_csv = ctk.CTkButton(
            btn_frame,
            text="📊 Exportar em CSV (Excel)",
            fg_color=COLORS["surface"],
            hover_color=COLORS["primary"],
            command=self.export_csv
        )
        btn_csv.pack(side="left")

        # Label de Status/Mensagem
        self.status_label = ctk.CTkLabel(card, text="", font=("Segoe UI", 12), text_color=COLORS["success"])
        self.status_label.pack(anchor="w", padx=20, pady=(0, 15))

    def export_json(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Arquivo JSON", "*.json"), ("Todos os arquivos", "*.*")],
            title="Salvar exportação JSON"
        )
        if filepath:
            try:
                self.task_manager.export_to_json(filepath)
                self.status_label.configure(text=f"✓ Exportado com sucesso em: {filepath}", text_color=COLORS["success"])
            except Exception as e:
                self.status_label.configure(text=f"❌ Erro ao exportar: {str(e)}", text_color="#ef4444")

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv"), ("Todos os arquivos", "*.*")],
            title="Salvar exportação CSV"
        )
        if filepath:
            try:
                self.task_manager.export_to_csv(filepath)
                self.status_label.configure(text=f"✓ Exportado com sucesso em: {filepath}", text_color=COLORS["success"])
            except Exception as e:
                self.status_label.configure(text=f"❌ Erro ao exportar: {str(e)}", text_color="#ef4444")


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
            "settings": SettingsView(self.main_container, self.task_manager),
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

        btn_tasks = ctk.CTkButton(
            sidebar, 
            text="📋 Minhas Tarefas", 
            fg_color="transparent", 
            hover_color=COLORS["surface"],
            anchor="w",
            command=lambda: self.show_view("tasks")
        )
        btn_tasks.pack(fill="x", padx=10, pady=5)

        btn_blog = ctk.CTkButton(
            sidebar, 
            text="📢 Blog", 
            fg_color="transparent", 
            hover_color=COLORS["surface"],
            anchor="w",
            command=lambda: self.show_view("blog")
        )
        btn_blog.pack(fill="x", padx=10, pady=5)

        btn_settings = ctk.CTkButton(
            sidebar, 
            text="⚙️ Configurações", 
            fg_color="transparent", 
            hover_color=COLORS["surface"],
            anchor="w",
            command=lambda: self.show_view("settings")
        )
        btn_settings.pack(fill="x", padx=10, pady=5)

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
        for view in self.views.values():
            view.pack_forget()

        if view_name in self.views:
            self.views[view_name].pack(fill="both", expand=True)


def run():
    app = TaskFlowApp()
    app.mainloop()