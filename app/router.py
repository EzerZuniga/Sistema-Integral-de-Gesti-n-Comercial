from typing import Dict, Optional, Type, Any
import tkinter as tk
from core.logger import logger
from core.auth import AuthService
from app.app_context import app_context

class Router:
    """Router para manejar navegación entre vistas"""
    
    def __init__(self):
        self.routes: Dict[str, Any] = {}
        self.current_route: Optional[str] = None
        self.route_params: Dict[str, Any] = {}
    
    def register_route(self, name: str, view_class: Type, controller_class: Type = None):
        """Registrar una ruta"""
        self.routes[name] = {
            'view_class': view_class,
            'controller_class': controller_class
        }
        logger.debug(f"Ruta registrada: {name}")
    
    def navigate_to(self, route_name: str, **kwargs):
        """Navegar a una ruta específica"""
        try:
            if route_name not in self.routes:
                logger.error(f"Ruta no encontrada: {route_name}")
                return
            
            # Verificar autenticación para rutas protegidas
            if route_name != 'login' and not AuthService.is_authenticated():
                logger.warning("Intento de acceso a ruta protegida sin autenticación")
                self.navigate_to('login')
                return
            
            # Ocultar vista actual
            current_view = app_context.get_current_view()
            if current_view:
                if hasattr(current_view, 'on_hide'):
                    current_view.on_hide()
                current_view.grid_forget()
            
            # Guardar parámetros de la ruta
            self.route_params = kwargs
            self.current_route = route_name
            
            # Crear nueva vista
            route_info = self.routes[route_name]
            view_class = route_info['view_class']
            controller_class = route_info.get('controller_class')
            
            main_window = app_context.get_main_window()
            
            # Crear controlador si existe
            controller = None
            if controller_class:
                controller = controller_class()
                controller.initialize()
            
            # Crear/ocultar menú según ruta
            try:
                # Si no es la pantalla de login, asegurarnos de mostrar la barra de menú
                if route_name != 'login':
                    try:
                        if not hasattr(main_window, '_menu_bar') or not getattr(main_window, '_menu_bar'):
                            from ui.components.menu_bar import MenuBar
                            main_window._menu_bar = MenuBar(main_window)
                            try:
                                main_window._menu_bar.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
                            except Exception:
                                main_window._menu_bar.pack(side='left', fill='y')
                    except Exception:
                        pass
                else:
                    # Si navegamos al login, remover la barra de menú si existe y restaurar tamaño compact
                    try:
                        mb = getattr(main_window, '_menu_bar', None)
                        if mb:
                            mb.destroy()
                            main_window._menu_bar = None
                    except Exception:
                        pass
            except Exception:
                pass

            # Crear vista
            view = view_class(main_window, controller)
            
            if controller:
                controller.set_view(view)
            
            # Configurar vista en la ventana principal.
            # Por defecto colocamos la vista en la columna 1 (columna 0 reserva para menú)
            # Si navegamos al dashboard, queremos que ocupe toda la ventana y se muestre a pantalla completa.
            try:
                if route_name == 'dashboard':
                    # Intentar maximizar la ventana en Windows
                    try:
                        main_window.state('zoomed')
                    except Exception:
                        try:
                            main_window.attributes('-zoomed', True)
                        except Exception:
                            pass
                    # Asegurar que ambas columnas crezcan para que el grid pueda ocupar toda la anchura
                    try:
                        main_window.grid_columnconfigure(0, weight=1)
                        main_window.grid_columnconfigure(1, weight=1)
                    except Exception:
                        pass
                    # Mostrar la vista ocupando ambas columnas
                    view.grid(row=0, column=0, columnspan=2, sticky="nsew")
                else:
                    view.grid(row=0, column=1, sticky="nsew")
            except Exception:
                # Fallback a colocación estándar
                view.grid(row=0, column=1, sticky="nsew")
            app_context.set_current_view(view)

            # Resaltar la ruta en la barra de menú si existe
            try:
                mb = getattr(main_window, '_menu_bar', None)
                if mb and hasattr(mb, 'highlight_current_route'):
                    mb.highlight_current_route(route_name)
            except Exception:
                pass
            
            # Llamar método on_show si existe
            if hasattr(view, 'on_show'):
                view.on_show()
            
            # Actualizar título de ventana
            self._update_window_title(route_name)
            
            logger.info(f"Navegación a: {route_name}")
            
        except Exception as e:
            logger.error(f"Error en navegación a {route_name}: {e}")
            self.show_error("Error de Navegación", f"No se pudo cargar la vista: {route_name}")
    
    def _update_window_title(self, route_name: str):
        """Actualizar título de la ventana según la ruta"""
        main_window = app_context.get_main_window()
        if not main_window:
            return
        
        titles = {
            'login': 'Iniciar Sesión',
            'dashboard': 'Dashboard Principal',
            'empresa': 'Información de la Empresa',
            'trabajadores': 'Gestión de Trabajadores',
            'proveedores': 'Gestión de Proveedores',
            'ventas': 'Registro de Ventas',
            'compras': 'Registro de Compras',
            'inventario': 'Gestión de Inventario',
            'stock': 'Control de Stock'
        }
        
        base_title = "Doña Rosa - Sistema de Gestión"
        route_title = titles.get(route_name, 'Sistema de Gestión')
        
        main_window.title(f"{base_title} | {route_title}")
    
    def show_error(self, title: str, message: str):
        """Mostrar mensaje de error"""
        from core.utils import utils
        main_window = app_context.get_main_window()
        utils.show_message(main_window, title, message, "error")
    
    def show_message(self, title: str, message: str, type: str = "info"):
        """Mostrar un mensaje genérico (info, warning, error, question).

        Retorna True/False solo para tipo 'question', o None en otros casos.
        """
        from core.utils import utils
        main_window = app_context.get_main_window()
        return utils.show_message(main_window, title, message, type)
    def get_current_route(self) -> Optional[str]:
        """Obtener ruta actual"""
        return self.current_route
    
    def get_route_param(self, key: str, default: Any = None) -> Any:
        """Obtener parámetro de ruta"""
        return self.route_params.get(key, default)

# Instancia global del router
router = Router()