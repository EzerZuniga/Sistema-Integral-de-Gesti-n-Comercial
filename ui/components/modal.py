import tkinter as tk
from tkinter import ttk
from core.utils import utils

class Modal:
    """Modal/dialogo reutilizable"""
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        self.parent = parent
        self.title = title
        self.width = width
        self.height = height
        self.result = None
        
        self._create_modal()
    
    def _create_modal(self):
        """Crear la ventana modal"""
        self.modal = tk.Toplevel(self.parent)
        self.modal.title(self.title)
        self.modal.transient(self.parent)
        self.modal.grab_set()
        self.modal.resizable(False, False)
        
        # Centrar modal
        utils.center_window(self.modal, self.width, self.height)
        
        # Frame principal
        main_frame = ttk.Frame(self.modal, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Contenido (será implementado por subclases)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill="both", expand=True, pady=10)
        
        # Botones
        self._create_buttons(main_frame)
    
    def _create_buttons(self, parent):
        """Crear botones del modal"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self._on_cancel,
            style="Secondary.TButton"
        ).pack(side="right", padx=5)
        
        ttk.Button(
            button_frame,
            text="Aceptar",
            command=self._on_accept,
            style="Primary.TButton"
        ).pack(side="right", padx=5)
    
    def _on_accept(self):
        """Manejar aceptación del modal"""
        if self.validate():
            self.result = self.get_result()
            self.modal.destroy()
    
    def _on_cancel(self):
        """Manejar cancelación del modal"""
        self.result = None
        self.modal.destroy()
    
    def validate(self) -> bool:
        """Validar datos del modal (debe ser implementado por subclases)"""
        return True
    
    def get_result(self):
        """Obtener resultado del modal (debe ser implementado por subclases)"""
        return None
    
    def show(self):
        """Mostrar modal y esperar resultado"""
        self.modal.wait_window()
        return self.result

class ConfirmModal(Modal):
    """Modal de confirmación simple"""
    
    def __init__(self, parent, title: str, message: str):
        self.message = message
        super().__init__(parent, title, 300, 150)
    
    def _create_modal(self):
        """Crear modal de confirmación"""
        super()._create_modal()
        
        # Mensaje
        ttk.Label(
            self.content_frame,
            text=self.message,
            style="Normal.TLabel",
            wraplength=280
        ).pack(expand=True, pady=20)
    
    def validate(self) -> bool:
        return True
    
    def get_result(self):
        return True

class InputModal(Modal):
    """Modal para entrada de datos"""
    
    def __init__(self, parent, title: str, fields: list):
        self.fields = fields
        self.entries = {}
        super().__init__(parent, title, 400, 200)
    
    def _create_modal(self):
        """Crear modal de entrada"""
        super()._create_modal()
        
        # Crear campos de entrada
        for i, field in enumerate(self.fields):
            ttk.Label(
                self.content_frame,
                text=field['label'],
                style="Normal.TLabel"
            ).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            if field['type'] == 'entry':
                entry = ttk.Entry(
                    self.content_frame,
                    width=30,
                    show=field.get('show')
                )
                entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
                if field.get('value'):
                    entry.insert(0, field['value'])
                self.entries[field['name']] = entry
            
            elif field['type'] == 'combobox':
                combobox = ttk.Combobox(
                    self.content_frame,
                    values=field['values'],
                    width=27,
                    state="readonly"
                )
                combobox.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
                if field.get('value'):
                    combobox.set(field['value'])
                self.entries[field['name']] = combobox
        
        self.content_frame.columnconfigure(1, weight=1)
    
    def validate(self) -> bool:
        """Validar campos requeridos"""
        for field in self.fields:
            if field.get('required'):
                value = self.entries[field['name']].get()
                if not value.strip():
                    utils.show_message(self.modal, "Error", f"El campo {field['label']} es requerido", "error")
                    return False
        return True
    
    def get_result(self) -> dict:
        """Obtener datos ingresados"""
        result = {}
        for field in self.fields:
            result[field['name']] = self.entries[field['name']].get()
        return result