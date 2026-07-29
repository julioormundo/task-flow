import customtkinter as ctk
from config import COLORS, FONTS, SPACING
from data.translations import t
from ui.components import RoundedFrame
from ui.task_dialog import TaskDialog

PRIORITY_COLORS = {
    "Alta": "#ef4444",   # Vermelho
    "Média": "#f59e0b",  # Laranja
    "Baixa": "#3b82f6"   # Azul
}

class DashboardView(ctk.CTkFrame):
    """Tela principal do TaskFlow com estatísticas e busca em tempo real."""

    def __init__(self, master, task_manager, **kwargs):
        super().__init__(master, corner_radius=18, fg_color=COLORS["background"], **kwargs)
        self.task_manager = task_manager
        self.current_filter = "Todas"
        self.build_ui()

    def build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 1. Cabeçalho
        header = RoundedFrame(self, fg_color=COLORS["panel"])
        header.grid(row=0, column=0, sticky="ew", padx=SPACING["large"], pady=(SPACING["large"], SPACING["small"]))
        header.grid_columnconfigure(0, weight=1)

        text_container = ctk.CTkFrame(header, fg_color="transparent")
        text_container.grid(row=0, column=0, sticky="w", padx=SPACING["large"], pady=SPACING["medium"])

        title = ctk.CTkLabel(text_container, text=t("dashboard_title"), font=FONTS["title"], text_color=COLORS["text"])
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_container,
            text=t("dashboard_subtitle"),
            font=FONTS["body"],
            text_color=COLORS["muted"]
        )
        subtitle.pack(anchor="w")

        add_btn = ctk.CTkButton(
            header,
            text=t("dashboard_add_task"),
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=38,
            command=self.open_add_dialog
        )
        add_btn.grid(row=0, column=1, sticky="e", padx=SPACING["large"], pady=SPACING["medium"])

        # 2. Estatísticas
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=SPACING["large"], pady=(0, SPACING["small"]))
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_stat_total = self._create_stat_card(self.stats_frame, t("stat_total"), "0", 0)
        self.lbl_stat_pending = self._create_stat_card(self.stats_frame, t("stat_pending"), "0", 1)
        self.lbl_stat_completed = self._create_stat_card(self.stats_frame, t("stat_completed"), "0", 2)
        self.lbl_stat_progress = self._create_stat_card(self.stats_frame, t("stat_progress"), "0%", 3)

        # 3. Busca e Filtros
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=SPACING["large"], pady=(0, SPACING["small"]))
        controls_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text=t("dashboard_search_placeholder"),
            height=34,
            fg_color=COLORS["panel"],
            border_color=COLORS["border"]
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, SPACING["medium"]))
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_tasks())

        self.filter_segmented = ctk.CTkSegmentedButton(
            controls_frame,
            values=[t("dashboard_filter_all"), t("dashboard_filter_pending"), t("dashboard_filter_completed"), t("dashboard_filter_favorites")],
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            unselected_color=COLORS["panel"],
            unselected_hover_color=COLORS["surface"],
            text_color=COLORS["text"],
            command=self.on_filter_changed
        )
        self.filter_segmented.set(t("dashboard_filter_all"))
        self.filter_segmented.grid(row=0, column=1, sticky="e")

        # 4. Lista de Tarefas
        self.task_list = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.task_list.grid(row=3, column=0, sticky="nsew", padx=SPACING["large"], pady=(0, SPACING["large"]))
        self.task_list.grid_columnconfigure(0, weight=1)

        self.refresh_tasks()

    def _create_stat_card(self, parent, title: str, initial_val: str, col: int) -> ctk.CTkLabel:
        card = RoundedFrame(parent, fg_color=COLORS["panel"])
        card.grid(row=0, column=col, sticky="ew", padx=4, pady=2)

        lbl_title = ctk.CTkLabel(card, text=title, font=FONTS["small"], text_color=COLORS["muted"])
        lbl_title.pack(anchor="w", padx=12, pady=(8, 0))

        lbl_value = ctk.CTkLabel(card, text=initial_val, font=("Segoe UI", 16, "bold"), text_color=COLORS["text"])
        lbl_value.pack(anchor="w", padx=12, pady=(0, 8))

        return lbl_value

    def update_stats_display(self):
        stats = self.task_manager.get_stats()
        self.lbl_stat_total.configure(text=str(stats["total"]))
        self.lbl_stat_pending.configure(text=str(stats["pending"]))
        self.lbl_stat_completed.configure(text=str(stats["completed"]))
        self.lbl_stat_progress.configure(text=f"{stats['percentage']}%")

    def on_filter_changed(self, selected_filter):
        self.current_filter = selected_filter
        self.refresh_tasks()

    def open_add_dialog(self):
        TaskDialog(self, self.task_manager, on_save_callback=self.refresh_tasks)

    def open_edit_dialog(self, task):
        TaskDialog(self, self.task_manager, task=task, on_save_callback=self.refresh_tasks)

    def refresh_tasks(self):
        self.update_stats_display()

        for child in self.task_list.winfo_children():
            child.destroy()

        search_query = self.search_entry.get()
        tasks = self.task_manager.list_tasks(filter_by=self.current_filter, search_query=search_query)

        if not tasks:
            msg = t("dashboard_empty") if not search_query else t("dashboard_empty_search", query=search_query)
            empty_label = ctk.CTkLabel(
                self.task_list,
                text=msg,
                text_color=COLORS["muted"],
                font=FONTS["body"]
            )
            empty_label.pack(pady=SPACING["large"])
            return

        for task in tasks:
            card = RoundedFrame(self.task_list, fg_color=COLORS["panel"])
            card.pack(fill="x", padx=2, pady=SPACING["small"])
            card.grid_columnconfigure(1, weight=1)

            top_bar = ctk.CTkFrame(card, fg_color="transparent")
            top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=SPACING["medium"], pady=(SPACING["small"], 2))
            top_bar.grid_columnconfigure(1, weight=1)

            p_color = PRIORITY_COLORS.get(task.priority, COLORS["primary"])
            p_badge = ctk.CTkLabel(
                top_bar,
                text=f"  {task.priority}  ",
                font=FONTS["small"],
                text_color="#ffffff",
                fg_color=p_color,
                corner_radius=10
            )
            p_badge.grid(row=0, column=0, sticky="w")

            date_text = t("dashboard_created_at", date=task.created_at) if task.created_at else ""
            date_label = ctk.CTkLabel(top_bar, text=date_text, font=FONTS["small"], text_color=COLORS["muted"])
            date_label.grid(row=0, column=1, sticky="w", padx=SPACING["medium"])

            star_symbol = "★" if task.is_favorite else "☆"
            star_color = "#f59e0b" if task.is_favorite else COLORS["muted"]
            fav_btn = ctk.CTkButton(
                top_bar,
                text=star_symbol,
                width=30,
                height=24,
                fg_color="transparent",
                hover_color=COLORS["surface"],
                text_color=star_color,
                font=("Segoe UI", 16, "bold"),
                command=lambda t_id=task.id: self.toggle_favorite(t_id)
            )
            fav_btn.grid(row=0, column=2, sticky="e")

            title_text = f"✓ {task.title}" if task.completed else task.title
            text_color = COLORS["muted"] if task.completed else COLORS["text"]

            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=SPACING["medium"], pady=(2, SPACING["small"]))

            title_label = ctk.CTkLabel(content_frame, text=title_text, font=FONTS["subtitle"], text_color=text_color)
            title_label.pack(anchor="w")

            if task.description:
                desc_label = ctk.CTkLabel(content_frame, text=task.description, font=FONTS["body"], text_color=COLORS["muted"])
                desc_label.pack(anchor="w", pady=(2, 0))

            actions_frame = ctk.CTkFrame(card, fg_color="transparent")
            actions_frame.grid(row=0, column=2, rowspan=2, sticky="e", padx=SPACING["medium"])

            status_btn = ctk.CTkButton(
                actions_frame,
                text=t("dashboard_complete_alt") if task.completed else t("dashboard_complete"),
                width=75,
                height=30,
                fg_color=COLORS["surface"] if task.completed else COLORS["success"],
                hover_color="#16a34a" if not task.completed else COLORS["border"],
                command=lambda t_id=task.id: self.toggle_task(t_id)
            )
            status_btn.pack(side="left", padx=2)

            edit_btn = ctk.CTkButton(
                actions_frame,
                text=t("dashboard_edit"),
                width=35,
                height=30,
                fg_color=COLORS["surface"],
                hover_color=COLORS["primary"],
                command=lambda t=task: self.open_edit_dialog(t)
            )
            edit_btn.pack(side="left", padx=2)

            delete_btn = ctk.CTkButton(
                actions_frame,
                text=t("dashboard_delete"),
                width=35,
                height=30,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda t_id=task.id: self.delete_task(t_id)
            )
            delete_btn.pack(side="left", padx=2)

    def toggle_task(self, task_id: int):
        self.task_manager.toggle_task_completion(task_id)
        self.refresh_tasks()

    def toggle_favorite(self, task_id: int):
        self.task_manager.toggle_favorite(task_id)
        self.refresh_tasks()

    def delete_task(self, task_id: int):
        self.task_manager.delete_task(task_id)
        self.refresh_tasks()