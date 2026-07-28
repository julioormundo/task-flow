import customtkinter as ctk


class RoundedFrame(ctk.CTkFrame):
    """Um frame com aparência mais limpa e organizada.

    Reutilizar este componente ajuda a manter a interface consistente sem
    repetir muitos blocos de configuração.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=16, **kwargs)


class SectionTitle(ctk.CTkLabel):
    """Label reutilizável para títulos de seção."""

    def __init__(self, master, text: str, **kwargs):
        super().__init__(master, text=text, font=("Segoe UI", 16, "bold"), **kwargs)
