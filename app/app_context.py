import tkinter as tk
from typing import Any, Dict, Optional
from core.auth import AuthService
from core.logger import logger

class AppContext:
    """Contexto global de la aplicación para compartir estado entre componentes"""
    
    def __init__(self):
        self._data = {}
        self._main_window: Optional[tk.Tk] = None
        self._current_view: Optional[tk.Frame] = None
    
    def set_main_window(self, window: tk.Tk):
        """Establecer ventana principal"""
        self._main_window = window
    
    def get_main_window(self) -> Optional[tk.Tk]:
        """Obtener ventana principal"""
        return self._main_window
    
    def set_current_view(self, view: tk.Frame):
        """Establecer vista actual"""
        self._current_view = view
    
    def get_current_view(self) -> Optional[tk.Frame]:
        """Obtener vista actual"""
        return self._current_view
    
    def set_data(self, key: str, value: Any):
        """Almacenar dato en contexto"""
        self._data[key] = value
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Obtener dato del contexto"""
        return self._data.get(key, default)
    
    def remove_data(self, key: str):
        """Remover dato del contexto"""
        if key in self._data:
            del self._data[key]
    
    def clear_context(self):
        """Limpiar contexto (útil para logout)"""
        self._data.clear()
        self._current_view = None
        logger.info("Contexto de aplicación limpiado")
    
    def get_user_session(self):
        """Obtener información de sesión del usuario"""
        return {
            'usuario': AuthService.get_current_user(),
            'authenticated': AuthService.is_authenticated(),
            'is_admin': AuthService.get_current_user() and AuthService.get_current_user().rol == 'admin'
        }

# Instancia global del contexto
app_context = AppContext()