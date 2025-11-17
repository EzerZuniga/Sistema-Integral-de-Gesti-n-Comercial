import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
from core.logger import logger
from core.utils import utils
from app.app_context import app_context

class BaseView(ttk.Frame):
    """Vista base para todas las pantallas de la aplicación"""
    
    def __init__(self, parent: tk.Widget, controller: Optional['BaseController'] = None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.widgets: Dict[str, tk.Widget] = {}
        
        # Configuración base
        self.configure(style="Main.TFrame")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_style()
        self._setup_view()
    
    def _create_style(self):
        """Crear estilos para la vista"""
        style = ttk.Style()
        
        # Estilo principal
        style.configure("Main.TFrame", background="#f5f5f5")
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), background="#f5f5f5")
        style.configure("Subtitle.TLabel", font=("Arial", 12, "bold"), background="#f5f5f5")
        style.configure("Normal.TLabel", font=("Arial", 10), background="#f5f5f5")
        
        # Botones
        style.configure("Primary.TButton", font=("Arial", 10, "bold"))
        style.configure("Success.TButton", font=("Arial", 10, "bold"))
        style.configure("Danger.TButton", font=("Arial", 10, "bold"))
        style.configure("Secondary.TButton", font=("Arial", 10))
        
        # Entradas
        style.configure("Input.TEntry", font=("Arial", 10))
        
        # Combobox
        style.configure("Custom.TCombobox", font=("Arial", 10))
    
    def _setup_view(self):
        """Configuración inicial de la vista (debe ser implementado por subclases)"""
        pass
    
    def create_title(self, text: str, row: int, column: int = 0, **kwargs) -> ttk.Label:
        """Crear título de vista"""
        # Extraer opciones de grid que podrían haberse pasado por error
        grid_opts = {}
        for opt in ("columnspan", "sticky", "pady", "padx"):
            if opt in kwargs:
                grid_opts[opt] = kwargs.pop(opt)

        label = ttk.Label(self, text=text, style="Title.TLabel", **kwargs)
        # Valores por defecto para grid si no se especifica
        label.grid(row=row, column=column, sticky=grid_opts.get("sticky", "w"),
                   pady=grid_opts.get("pady", (10, 20)), padx=grid_opts.get("padx", 10),
                   columnspan=grid_opts.get("columnspan", 1))
        return label
    
    def create_subtitle(self, text: str, row: int, column: int = 0, **kwargs) -> ttk.Label:
        """Crear subtítulo"""
        grid_opts = {}
        for opt in ("columnspan", "sticky", "pady", "padx"):
            if opt in kwargs:
                grid_opts[opt] = kwargs.pop(opt)

        label = ttk.Label(self, text=text, style="Subtitle.TLabel", **kwargs)
        label.grid(row=row, column=column, sticky=grid_opts.get("sticky", "w"),
                   pady=grid_opts.get("pady", (5, 10)), padx=grid_opts.get("padx", 10),
                   columnspan=grid_opts.get("columnspan", 1))
        return label
    
    def create_label(self, text: str, row: int, column: int = 0, **kwargs) -> ttk.Label:
        """Crear etiqueta normal"""
        grid_opts = {}
        for opt in ("columnspan", "sticky", "pady", "padx"):
            if opt in kwargs:
                grid_opts[opt] = kwargs.pop(opt)

        label = ttk.Label(self, text=text, style="Normal.TLabel", **kwargs)
        label.grid(row=row, column=column, sticky=grid_opts.get("sticky", "w"),
                   pady=grid_opts.get("pady", 2), padx=grid_opts.get("padx", 10),
                   columnspan=grid_opts.get("columnspan", 1))
        return label
    
    def create_entry(self, row: int, column: int = 0, width: int = 30, **kwargs) -> ttk.Entry:
        """Crear campo de entrada"""
        grid_opts = {}
        for opt in ("columnspan", "sticky", "pady", "padx"):
            if opt in kwargs:
                grid_opts[opt] = kwargs.pop(opt)

        entry = ttk.Entry(self, width=width, style="Input.TEntry", **kwargs)
        entry.grid(row=row, column=column, sticky=grid_opts.get("sticky", "w"),
                   pady=grid_opts.get("pady", 2), padx=grid_opts.get("padx", 10),
                   columnspan=grid_opts.get("columnspan", 1))
        return entry
    
    def create_combobox(self, values: list, row: int, column: int = 0, width: int = 30, **kwargs) -> ttk.Combobox:
        """Crear combobox"""
        grid_opts = {}
        for opt in ("columnspan", "sticky", "pady", "padx"):
            if opt in kwargs:
                grid_opts[opt] = kwargs.pop(opt)

        combobox = ttk.Combobox(self, values=values, width=width, style="Custom.TCombobox", state="readonly", **kwargs)
        combobox.grid(row=row, column=column, sticky=grid_opts.get("sticky", "w"),
                      pady=grid_opts.get("pady", 2), padx=grid_opts.get("padx", 10),
                      columnspan=grid_opts.get("columnspan", 1))
        return combobox
    
    def create_button(self, text: str, row: int, column: int = 0, command=None, style: str = "Primary.TButton", **kwargs) -> ttk.Button:
        """Crear botón"""
        grid_opts = {}
        for opt in ("columnspan", "sticky", "pady", "padx"):
            if opt in kwargs:
                grid_opts[opt] = kwargs.pop(opt)

        button = ttk.Button(self, text=text, command=command, style=style, **kwargs)
        button.grid(row=row, column=column, sticky=grid_opts.get("sticky", "w"),
                    pady=grid_opts.get("pady", 5), padx=grid_opts.get("padx", 10),
                    columnspan=grid_opts.get("columnspan", 1))
        return button
    
    def create_table(self, columns: list, row: int, column: int = 0, height: int = 15, **kwargs) -> ttk.Treeview:
        """Crear tabla/treeview"""
        # Frame para la tabla con scrollbar
        grid_opts = {}
        for opt in ("columnspan", "sticky", "pady", "padx"):
            if opt in kwargs:
                grid_opts[opt] = kwargs.pop(opt)

        table_frame = ttk.Frame(self)
        table_frame.grid(row=row, column=column, sticky=grid_opts.get("sticky", "nsew"),
                         pady=grid_opts.get("pady", 5), padx=grid_opts.get("padx", 10),
                         columnspan=grid_opts.get("columnspan", 1))
        
        # Scrollbar vertical
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        v_scrollbar.pack(side="right", fill="y")
        
        # Scrollbar horizontal
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview (tabla)
        table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=height,
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            **kwargs
        )
        table.pack(side="left", fill="both", expand=True)
        
        # Configurar scrollbars
        v_scrollbar.config(command=table.yview)
        h_scrollbar.config(command=table.xview)
        
        # Configurar columnas
        for col in columns:
            table.heading(col, text=col.title())
            table.column(col, width=100, minwidth=50)
        
        return table
    
    def show_message(self, title: str, message: str, type: str = "info"):
        """Mostrar mensaje al usuario"""
        parent = app_context.get_main_window()
        return utils.show_message(parent, title, message, type)
    
    def clear_form(self):
        """Limpiar todos los campos del formulario"""
        for widget_name, widget in self.widgets.items():
            if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Text):
                widget.delete(1.0, tk.END)
    
    def validate_required_fields(self, fields: Dict[str, str]) -> bool:
        """Validar campos requeridos"""
        for field_name, field_value in fields.items():
            if not field_value or not field_value.strip():
                self.show_message("Error de Validación", f"El campo {field_name} es requerido", "error")
                return False
        return True
    
    def on_show(self):
        """Método llamado cuando la vista se muestra"""
        logger.debug(f"Vista {self.__class__.__name__} mostrada")
    
    def on_hide(self):
        """Método llamado cuando la vista se oculta"""
        logger.debug(f"Vista {self.__class__.__name__} ocultada")