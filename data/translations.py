TRANSLATIONS = {
    "pt": {
        # Sidebar
        "my_tasks": " Minhas Tarefas",
        "blog": " Blog",
        "settings": " Configurações",
        "talk": " Fale Conosco",
        "logout": " Sair da Conta",
        
        # Dashboard
        "new_task": "+ Nova Tarefa",
        "search_placeholder": " Buscar por título ou descrição...",
        "stat_total": "Total",
        "stat_pending": "Pendentes",
        "stat_completed": "Concluídas",
        "stat_progress": "Progresso",
        
        # Configurações
        "theme_title": " Aparência e Tema",
        "lang_title": " Idioma / Language",
        "export_title": " Backup e Exportação",
        "dark": "Escuro",
        "light": "Claro",
        "system": "Sistema",
    },
    "en": {
        # Sidebar
        "my_tasks": " My Tasks",
        "blog": " Blog",
        "settings": " Settings",
        "talk": " Contact Us",
        "logout": " Log Out",
        
        # Dashboard
        "new_task": "+ New Task",
        "search_placeholder": " Search by title or description...",
        "stat_total": "Total",
        "stat_pending": "Pending",
        "stat_completed": "Completed",
        "stat_progress": "Progress",
        
        # Configurações
        "theme_title": " Appearance & Theme",
        "lang_title": " Language / Idioma",
        "export_title": " Backup & Export",
        "dark": "Dark",
        "light": "Light",
        "system": "System",
    }
}

# Idioma padrão
CURRENT_LANG = "pt"

def set_language(lang_code: str):
    global CURRENT_LANG
    if lang_code in TRANSLATIONS:
        CURRENT_LANG = lang_code

def t(key: str) -> str:
    """Retorna a tradução da chave no idioma atual."""
    return TRANSLATIONS.get(CURRENT_LANG, {}).get(key, key)