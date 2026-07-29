"""Configurações centrais do projeto.

Alteração de aparência, textos e valores em um só lugar.
"""

import customtkinter


WINDOW_SIZE = "1080x680"
WINDOW_TITLE = "TaskFlow"

# Cores principais da interface
COLORS = {
    "background": "#0f172a",
    "panel": "#111827",
    "surface": "#1f2937",
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "text": "#f8fafc",
    "muted": "#94a3b8",
    "border": "#334155",
    "success": "#22c55e",
}

# Fontes simples e legíveis
FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 13),
    "small": ("Segoe UI", 11),
}

# Espaçamentos e tamanhos reutilizáveis
SPACING = {
    "small": 8,
    "medium": 12,
    "large": 20,
}

# Configuração global do CustomTkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
