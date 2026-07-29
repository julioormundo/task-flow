import customtkinter as ctk
from config import COLORS, FONTS
from data.translations import t

class TaskDialog(ctk.CTkToplevel):
    """Janela Modal Pop-up para Criar e Editar Tarefas."""

    def __init__(self, master, task_manager, task=None, on_save_callback=None):
        super().__init__(master)
        self.task_manager = task_manager
        self.task = task
        self.on_save_callback = on_save_callback

        is_edit = task is not None
        self.title(t("task_dialog_title_edit") if is_edit else t("task_dialog_title_new"))
        self.geometry("450x420")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["background"])

        # Foco exclusivo na Modal
        self.transient(master)
        self.grab_set()

        # Título da modal
        dialog_title = t("task_dialog_title_edit") if is_edit else t("task_dialog_subtitle_new")
        ctk.CTkLabel(self, text=dialog_title, font=FONTS["title"], text_color=COLORS["text"]).pack(pady=(20, 10))

        # Título da Tarefa
        ctk.CTkLabel(self, text=t("task_dialog_title_label"), font=FONTS["body"], text_color=COLORS["text"]).pack(anchor="w", padx=30, pady=(10, 2))
        self.title_entry = ctk.CTkEntry(self, placeholder_text=t("task_dialog_placeholder_title"), width=390)
        self.title_entry.pack(padx=30, pady=(0, 10))
        if is_edit:
            self.title_entry.insert(0, task.title)

        # Descrição da Tarefa
        ctk.CTkLabel(self, text=t("task_dialog_description_label"), font=FONTS["body"], text_color=COLORS["text"]).pack(anchor="w", padx=30, pady=(5, 2))
        self.description_entry = ctk.CTkEntry(self, placeholder_text=t("task_dialog_placeholder_description"), width=390)
        self.description_entry.pack(padx=30, pady=(0, 10))
        if is_edit:
            self.description_entry.insert(0, task.description)

        # Prioridade
        ctk.CTkLabel(self, text=t("task_dialog_priority_label"), font=FONTS["body"], text_color=COLORS["text"]).pack(anchor="w", padx=30, pady=(5, 2))
        self.priority_option = ctk.CTkOptionMenu(
            self,
            values=["Baixa", "Média", "Alta"],
            width=390,
            fg_color=COLORS["surface"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"]
        )
        self.priority_option.pack(padx=30, pady=(0, 15))
        if is_edit:
            self.priority_option.set(task.priority)
        else:
            self.priority_option.set("Média")

        # Mensagem de erro
        self.error_label = ctk.CTkLabel(self, text="", text_color="#ef4444", font=FONTS["small"])
        self.error_label.pack(pady=(0, 5))

        # Botão Salvar
        btn_text = t("task_dialog_save_edit") if is_edit else t("task_dialog_save_new")
        save_btn = ctk.CTkButton(
            self,
            text=btn_text,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            width=390,
            height=38,
            command=self.save
        )
        save_btn.pack(padx=30, pady=10)

    def save(self):
        title = self.title_entry.get().strip()
        description = self.description_entry.get().strip()
        priority = self.priority_option.get()

        if not title:
            self.error_label.configure(text=t("task_dialog_error_title"))
            return

        try:
            if self.task:
                self.task_manager.update_task(self.task.id, title, description, priority)
            else:
                self.task_manager.add_task(title, description, priority)

            if self.on_save_callback:
                self.on_save_callback()

            self.destroy()
        except Exception as e:
            self.error_label.configure(text=t("task_dialog_error_generic"))