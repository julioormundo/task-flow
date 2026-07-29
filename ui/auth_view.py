import customtkinter as ctk
from config import COLORS, FONTS
from ui.components import RoundedFrame

class WelcomeBackView(ctk.CTkFrame):
    """Tela exibida quando o aplicativo reconhece o usuário da última sessão."""

    def __init__(self, master, username: str, on_enter_callback, on_switch_account_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_enter_callback = on_enter_callback
        self.on_switch_account_callback = on_switch_account_callback

        card = RoundedFrame(self, fg_color=COLORS["panel"], width=420, height=320)
        card.pack_propagate(False)
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(
            card,
            text=f"👋 Olá, {username}!",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text"]
        )
        title.pack(pady=(40, 5))

        subtitle = ctk.CTkLabel(
            card,
            text="Bem-vindo de volta ao TaskFlow",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"]
        )
        subtitle.pack(pady=(0, 30))

        enter_btn = ctk.CTkButton(
            card,
            text="🚀 Entrar no TaskFlow",
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=42,
            width=280,
            command=self.on_enter_callback
        )
        enter_btn.pack(pady=10)

        switch_btn = ctk.CTkButton(
            card,
            text="Entrar com outra conta",
            font=FONTS["body"],
            fg_color="transparent",
            hover_color=COLORS["surface"],
            text_color=COLORS["muted"],
            command=self.on_switch_account_callback
        )
        switch_btn.pack(pady=5)


class LoginRegisterView(ctk.CTkFrame):
    """Tela de Formulário para realizar Login ou Cadastrar uma nova conta."""

    def __init__(self, master, auth_manager, on_success_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.auth_manager = auth_manager
        self.on_success_callback = on_success_callback
        self.mode = "login"

        card = RoundedFrame(self, fg_color=COLORS["panel"], width=380, height=440)
        card.pack_propagate(False)
        card.place(relx=0.5, rely=0.5, anchor="center")

        self.title_lbl = ctk.CTkLabel(card, text="TaskFlow", font=("Segoe UI", 26, "bold"), text_color=COLORS["primary"])
        self.title_lbl.pack(pady=(25, 5))

        self.sub_lbl = ctk.CTkLabel(card, text="Acesse ou crie sua conta para continuar", font=FONTS["small"], text_color=COLORS["muted"])
        self.sub_lbl.pack(pady=(0, 15))

        self.mode_segmented = ctk.CTkSegmentedButton(
            card,
            values=["Login", "Cadastrar"],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            command=self.on_mode_change
        )
        self.mode_segmented.set("Login")
        self.mode_segmented.pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(card, placeholder_text="Nome de usuário", width=300, height=38)
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(card, placeholder_text="Senha", show="•", width=300, height=38)
        self.password_entry.pack(pady=8)

        self.error_label = ctk.CTkLabel(card, text="", font=FONTS["small"], text_color="#ef4444")
        self.error_label.pack(pady=5)

        self.submit_btn = ctk.CTkButton(
            card,
            text="Entrar",
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            width=300,
            height=40,
            command=self.submit
        )
        self.submit_btn.pack(pady=10)

    def on_mode_change(self, value):
        self.mode = "login" if value == "Login" else "register"
        self.submit_btn.configure(text="Entrar" if self.mode == "login" else "Criar Conta")
        self.error_label.configure(text="")

    def submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = None
        try:
            if self.mode == "login":
                user = self.auth_manager.login(username, password)
            else:
                user = self.auth_manager.register(username, password)
        except Exception as e:
            self.error_label.configure(text=str(e))
            return

        if user:
            self.on_success_callback(user)