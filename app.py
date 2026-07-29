from tkinter import filedialog
import customtkinter as ctk
from config import COLORS, FONTS, SPACING, WINDOW_SIZE, WINDOW_TITLE
from data.database import SQLiteDatabase
from logic.auth_manager import AuthManager
from logic.task_manager import TaskManager
from ui.auth_view import LoginRegisterView, WelcomeBackView
from ui.components import RoundedFrame
from ui.dashboard import DashboardView

class BlogView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        title = ctk.CTkLabel(self, text="📢 Blog de Atualizações", font=("Segoe UI", 20, "bold"), text_color=COLORS["text"])
        title.pack(anchor="w", padx=20, pady=(20, 10))
        
        card = RoundedFrame(self, fg_color=COLORS["panel"])
        card.pack(fill="x", padx=20, pady=10)
        
        notice_badge = ctk.CTkLabel(card, text="⚠️ TOME NOTA", font=("Segoe UI", 11, "bold"), text_color="#f59e0b")
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
    def __init__(self, master, task_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.task_manager = task_manager

        title = ctk.CTkLabel(self, text="⚙️ Configurações", font=("Segoe UI", 20, "bold"), text_color=COLORS["text"])
        title.pack(anchor="w", padx=20, pady=(20, 10))

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

        self.storage = SQLiteDatabase("data/tasks.db")
        self.auth_manager = AuthManager(self.storage)

        self.current_user = None
        self.task_manager = None
        self.current_container = None

        self.check_initial_auth()

    def create_root_container(self):
        if self.current_container:
            self.current_container.destroy()
        self.current_container = ctk.CTkFrame(self, fg_color="transparent")
        self.current_container.pack(fill="both", expand=True)

    def check_initial_auth(self):
        remembered_user = self.auth_manager.get_current_user()
        if remembered_user:
            self.current_user = remembered_user
            self.show_welcome_back_screen()
        else:
            self.show_login_screen()

    def show_login_screen(self):
        self.create_root_container()
        login_view = LoginRegisterView(self.current_container, self.auth_manager, on_success_callback=self.on_login_success)
        login_view.pack(fill="both", expand=True)

    def show_welcome_back_screen(self):
        self.create_root_container()
        welcome_view = WelcomeBackView(
            self.current_container,
            username=self.current_user["username"],
            on_enter_callback=self.enter_app,
            on_switch_account_callback=self.logout
        )
        welcome_view.pack(fill="both", expand=True)

    def on_login_success(self, user: dict):
        self.current_user = user
        self.enter_app()

    def enter_app(self):
        self.create_root_container()

        self.task_manager = TaskManager(self.storage, user_id=self.current_user["id"])

        self.current_container.grid_columnconfigure(0, weight=0)
        self.current_container.grid_columnconfigure(1, weight=1)
        self.current_container.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()

        self.main_container = ctk.CTkFrame(self.current_container, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.views = {
            "tasks": DashboardView(self.main_container, self.task_manager),
            "blog": BlogView(self.main_container),
            "settings": SettingsView(self.main_container, self.task_manager),
            "talk": TalkDevsView(self.main_container),
        }

        self.show_view("tasks")

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.current_container, fg_color=COLORS["panel"], width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        title = ctk.CTkLabel(self.sidebar, text="TaskFlow", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"])
        title.pack(pady=(20, 10), padx=20)

        user_badge = ctk.CTkLabel(
            self.sidebar,
            text=f"👤 {self.current_user['username']}",
            font=FONTS["small"],
            text_color=COLORS["muted"]
        )
        user_badge.pack(pady=(0, 20), padx=20)

        btn_tasks = ctk.CTkButton(
            self.sidebar, text="📋 Minhas Tarefas", fg_color="transparent", hover_color=COLORS["surface"],
            anchor="w", command=lambda: self.show_view("tasks")
        )
        btn_tasks.pack(fill="x", padx=10, pady=5)

        btn_blog = ctk.CTkButton(
            self.sidebar, text="📢 Blog", fg_color="transparent", hover_color=COLORS["surface"],
            anchor="w", command=lambda: self.show_view("blog")
        )
        btn_blog.pack(fill="x", padx=10, pady=5)

        btn_settings = ctk.CTkButton(
            self.sidebar, text="⚙️ Configurações", fg_color="transparent", hover_color=COLORS["surface"],
            anchor="w", command=lambda: self.show_view("settings")
        )
        btn_settings.pack(fill="x", padx=10, pady=5)

        btn_talk = ctk.CTkButton(
            self.sidebar, text="💬 Fale Conosco", fg_color="transparent", hover_color=COLORS["surface"],
            anchor="w", command=lambda: self.show_view("talk")
        )
        btn_talk.pack(fill="x", padx=10, pady=5)

        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Sair da Conta",
            fg_color="transparent",
            hover_color="#ef4444",
            text_color="#ef4444",
            anchor="w",
            command=self.logout
        )
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=20)

    def show_view(self, view_name: str):
        for view in self.views.values():
            view.pack_forget()

        if view_name in self.views:
            self.views[view_name].pack(fill="both", expand=True)

    def logout(self):
        self.auth_manager.logout()
        self.current_user = None
        self.show_login_screen()


def run():
    app = TaskFlowApp()
    app.mainloop()