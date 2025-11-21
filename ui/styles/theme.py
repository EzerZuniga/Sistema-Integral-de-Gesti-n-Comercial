import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

# Tema central para la aplicación
# Define colores, estilos y una función para aplicar responsividad básica

PALETTE = {
    'bg': '#f5f7f9',
    'panel': '#ffffff',
    'muted': '#9aa3ab',
    'primary': '#2C73D2',
    'accent': '#27ae60',
    'danger': '#e74c3c',
    'border': '#d0d6db',
}


class Theme:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style()
        self.base_font = tkfont.nametofont('TkDefaultFont')
        self._init_fonts()
        self._configure_styles()
        # Ajusta automáticamente al redimensionar
        self.root.bind('<Configure>', self._on_resize)

    def _init_fonts(self):
        # Establece fuentes base (usar Segoe UI si está disponible en Windows)
        try:
            self.title_font = tkfont.Font(family='Segoe UI', size=14, weight='bold')
            self.subtitle_font = tkfont.Font(family='Segoe UI', size=10)
            self.form_font = tkfont.Font(family='Segoe UI', size=10)
            self.button_font = tkfont.Font(family='Segoe UI', size=10, weight='bold')
        except Exception:
            self.title_font = tkfont.Font(size=14, weight='bold')
            self.subtitle_font = tkfont.Font(size=10)
            self.form_font = tkfont.Font(size=10)
            self.button_font = tkfont.Font(size=10, weight='bold')

    def _configure_styles(self):
        s = self.style
        # General
        s.configure('.', background=PALETTE['bg'], foreground='#222222')
        s.configure('TFrame', background=PALETTE['bg'])
        # LabelFrame (cards) estilo
        s.configure('TLabelframe', background=PALETTE['panel'], bordercolor=PALETTE['border'], relief='flat')
        s.configure('TLabelframe.Label', background=PALETTE['panel'], font=self.form_font, foreground='#222222')
        s.configure('Normal.TLabel', background=PALETTE['panel'], font=self.form_font, foreground='#222222')
        s.configure('Card.TFrame', background=PALETTE['panel'], relief='flat', borderwidth=1)
        s.configure('TLabel', background=PALETTE['bg'], font=self.form_font)

        # Titles
        s.configure('Title.TLabel', background=PALETTE['bg'], font=self.title_font, foreground=PALETTE['primary'])
        s.configure('Subtitle.TLabel', background=PALETTE['bg'], font=self.subtitle_font, foreground=PALETTE['muted'])
        s.configure('Muted.TLabel', background=PALETTE['bg'], font=self.form_font, foreground=PALETTE['muted'])
        s.configure('BannerTitle.TLabel', background=PALETTE['bg'], font=tkfont.Font(size=20, weight='bold'))
        s.configure('BannerSubtitle.TLabel', background=PALETTE['bg'], font=tkfont.Font(size=10), foreground=PALETTE['muted'])

        # Forms
        s.configure('Form.TLabel', background=PALETTE['panel'], font=self.form_font, foreground='#2E2E2E')
        # Entradas: padding y foco visible
        s.configure('TEntry', padding=6, relief='flat', borderwidth=0)
        s.configure('TEntry.Entry', fieldbackground=PALETTE['panel'], background=PALETTE['panel'])
        s.map('TEntry', focuscolor=[('focus', PALETTE['primary'])])

        # Buttons
        s.configure('Primary.TButton', background=PALETTE['primary'], foreground='white', font=self.button_font, padding=8, relief='flat')
        s.map('Primary.TButton', background=[('active', '#2566b8'), ('disabled', PALETTE['border'])])
        s.configure('Secondary.TButton', background=PALETTE['accent'], foreground='white', font=self.button_font, padding=6)
        s.map('Secondary.TButton', background=[('active', '#1e8449'), ('disabled', PALETTE['border'])])
        # Link style: apariencia limpia (no subrayado por defecto)
        s.configure('Link.TButton', background=PALETTE['bg'], foreground=PALETTE['primary'], font=self.form_font, relief='flat')

        # Menu / Sidebar
        s.configure('Menu.TFrame', background='#2f4050')
        s.configure('Menu.TButton', background='#324a5b', foreground='white', font=self.form_font)
        s.configure('MenuTitle.TLabel', background='#2f4050', foreground='white', font=self.form_font)

        # Treeview / tables
        s.configure('Treeview', background='white', fieldbackground='white', foreground='#222222')
        s.configure('Treeview.Heading', font=self.form_font, relief='flat')

        # Card / panel style
        try:
            s.configure('Card.TFrame', background=PALETTE['panel'], borderwidth=1, relief='flat')
        except Exception:
            pass
    def _on_resize(self, event):
        # Scaling simple: ajustar tamaños de fuente en función del ancho de la ventana
        try:
            w = max(420, self.root.winfo_width())
            scale = max(0.8, min(1.3, w / 800))

            # Aplica escala a fuentes
            self.title_font.configure(size=int(14 * scale))
            self.subtitle_font.configure(size=int(10 * scale))
            self.form_font.configure(size=int(10 * scale))
            self.button_font.configure(size=max(9, int(10 * scale)))
        except Exception:
            pass


def apply_theme(root: tk.Tk):
    """Función conveniente para aplicar el tema a la ventana principal."""
    Theme(root)
