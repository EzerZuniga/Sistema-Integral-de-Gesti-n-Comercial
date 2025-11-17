from abc import ABC, abstractmethod
from typing import Optional, Any
from core.logger import logger
from app.app_context import app_context

class BaseController(ABC):
    """Controlador base para la lógica de presentación"""
    
    def __init__(self):
        self.view = None
        self._initialized = False
    
    def initialize(self):
        """Inicializar controlador (cargar datos iniciales)"""
        if not self._initialized:
            try:
                self._load_initial_data()
                self._initialized = True
                logger.debug(f"Controlador {self.__class__.__name__} inicializado")
            except Exception as e:
                logger.error(f"Error inicializando controlador {self.__class__.__name__}: {e}")
                raise
    
    @abstractmethod
    def _load_initial_data(self):
        """Cargar datos iniciales (debe ser implementado por subclases)"""
        pass
    
    def set_view(self, view):
        """Establecer vista asociada"""
        self.view = view
    
    def handle_navigation(self, target: str, **kwargs):
        """Manejar navegación entre vistas"""
        from app.router import router
        router.navigate_to(target, **kwargs)
    
    def show_message(self, title: str, message: str, type: str = "info"):
        """Mostrar mensaje al usuario"""
        if self.view:
            return self.view.show_message(title, message, type)
        return None
    
    def validate_input(self, data: dict, required_fields: list) -> bool:
        """Validar datos de entrada"""
        for field in required_fields:
            if field not in data or not data[field]:
                self.show_message("Error de Validación", f"El campo {field} es requerido", "error")
                return False
        return True
    
    def format_currency(self, amount: float) -> str:
        """Formatear moneda"""
        from core.utils import utils
        return utils.format_currency(amount)
    
    def format_rut(self, rut: str) -> str:
        """Formatear RUT"""
        from core.utils import utils
        return utils.format_rut(rut)
    
    def get_user_session(self) -> dict:
        """Obtener información de sesión del usuario"""
        return app_context.get_user_session()