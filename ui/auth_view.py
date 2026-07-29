import customtkinter as ctk
from config import COLORS, FONTS
from data.translations import t
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
            text=t("welcome_back_title", username=username),
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text"]
        )
        title.pack(pady=(40, 5))

        subtitle = ctk.CTkLabel(
            card,
            text=t("welcome_back_subtitle"),
            font=FONTS["subtitle"],
            text_color=COLORS["muted"]
        )
        subtitle.pack(pady=(0, 30))

        enter_btn = ctk.CTkButton(
            card,
            text=t("welcome_back_enter"),
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
            text=t("welcome_back_switch"),
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

        self.title_lbl = ctk.CTkLabel(card, text=t("login_title"), font=("Segoe UI", 26, "bold"), text_color=COLORS["primary"])
        self.title_lbl.pack(pady=(25, 5))

        self.sub_lbl = ctk.CTkLabel(card, text=t("login_subtitle"), font=FONTS["small"], text_color=COLORS["muted"])
        self.sub_lbl.pack(pady=(0, 15))

        self.mode_segmented = ctk.CTkSegmentedButton(
            card,
            values=[t("login_mode_login"), t("login_mode_register")],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            command=self.on_mode_change
        )
        self.mode_segmented.set(t("login_mode_login"))
        self.mode_segmented.pack(pady=(0, 20))

        self.username_entry = ctk.CTkEntry(card, placeholder_text=t("login_username_placeholder"), width=300, height=38)
        self.username_entry.pack(pady=8)
        self.username_entry.bind("<Return>", lambda event: self.submit())

        self.password_entry = ctk.CTkEntry(card, placeholder_text=t("login_password_placeholder"), show="•", width=300, height=38)
        self.password_entry.pack(pady=8)
        self.password_entry.bind("<Return>", lambda event: self.submit())

        self.error_label = ctk.CTkLabel(card, text="", font=FONTS["small"], text_color="#ef4444")
        self.error_label.pack(pady=5)

        self.submit_btn = ctk.CTkButton(
            card,
            text=t("login_submit_login"),
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            width=300,
            height=40,
            command=self.submit
        )
        self.submit_btn.pack(pady=10)

    def on_mode_change(self, value):
        self.mode = "login" if value == t("login_mode_login") else "register"
        self.submit_btn.configure(text=t("login_submit_login") if self.mode == "login" else t("login_submit_register"))
        self.error_label.configure(text="")

    def submit(self):
        self.error_label.configure(text="")
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