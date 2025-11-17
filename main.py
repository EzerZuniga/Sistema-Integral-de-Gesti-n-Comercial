import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import db
from core.logger import logger
from data.seeds.seed_data import SeedData
from app.app_context import app_context
from app.router import router
from ui.login.login_view import LoginView
from ui.login.login_controller import LoginController

from modules.inicio.dashboard_view import DashboardView
from modules.acerca_de.empresa_view import EmpresaView
from modules.acerca_de.trabajadores_view import TrabajadoresView
from modules.acerca_de.proveedores_view import ProveedoresView
from modules.procesos.venta_view import VentaView
from modules.procesos.compra_view import CompraView
from modules.procesos.resumen_view import ResumenView
from modules.inventario.stock_view import StockView
from modules.inventario.alerta_stock_view import AlertaStockView

class DoñaRosaApp:
    
    def __init__(self):
        self.root = None
        self.menu_bar = None
        self._initialize_app()
    
    def _initialize_app(self):
        """Inicializar la aplicación"""
        try:
            logger.info("Iniciando aplicación Doña Rosa...")
            
            # Cargar datos iniciales
            SeedData.cargar_datos_iniciales()
            
            # Crear ventana principal
            self._create_main_window()
            
            # Configurar rutas
            self._setup_routes()
            
            # Navegar a login
            router.navigate_to('login')
            
            logger.info("Aplicación inicializada correctamente")
            
        except Exception as e:
            logger.critical(f"Error crítico al inicializar aplicación: {e}")
            self._show_critical_error(e)
    
    def _create_main_window(self):
        """Crear ventana principal"""
        self.root = tk.Tk()
        self.root.title("Doña Rosa - Sistema de Gestión")
        # Tamaño inicial compacto para que el panel central se muestre como cuadro
        # Ajustado para que al iniciar la ventana tenga el tamaño deseado (ver diseño de login)
        # Valores elegidos para que el card se muestre centrado con márgenes cómodos.
        self.root.geometry("420x460")
        self.root.minsize(420, 420)
        # Fondo de la ventana para contraste con el panel de login
        try:
            self.root.configure(bg="#e9eef2")
        except Exception:
            pass
        
        # Configurar icono (si existe)
        self._set_window_icon()
        
        # Configurar grid principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Establecer en contexto
        app_context.set_main_window(self.root)
        
        # Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Centrar ventana
        self._center_window()
    
    def _set_window_icon(self):
        """Configurar icono de la ventana"""
        try:
            # Intentar cargar icono si existe
            icon_path = "assets/icons/app_icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"No se pudo cargar el icono: {e}")
    
    def _center_window(self):
        """Centrar ventana en pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_routes(self):
        """Configurar rutas de la aplicación"""
        # Ruta de login
        router.register_route('login', LoginView, LoginController)
        
        # Rutas principales
        router.register_route('dashboard', DashboardView)
        router.register_route('empresa', EmpresaView)
        router.register_route('trabajadores', TrabajadoresView)
        router.register_route('proveedores', ProveedoresView)
        router.register_route('ventas', VentaView)
        router.register_route('compras', CompraView)
        router.register_route('resumen', ResumenView)
        router.register_route('stock', StockView)
        router.register_route('alertas', AlertaStockView)
    
    def _create_menu_bar(self):
        """Crear barra de menú lateral"""
        from ui.components.menu_bar import MenuBar
        
        if self.menu_bar:
            self.menu_bar.destroy()
        
        self.menu_bar = MenuBar(self.root)
        self.menu_bar.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
    
    def _on_close(self):
        """Manejar cierre de la aplicación"""
        try:
            if router.show_message(
                "Cerrar Aplicación",
                "¿Está seguro que desea salir del sistema?",
                "question"
            ):
                logger.info("Aplicación cerrada por el usuario")
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            logger.error(f"Error al cerrar aplicación: {e}")
            self.root.quit()
    
    def _show_critical_error(self, error):
        """Mostrar error crítico y salir"""
        error_msg = f"Error crítico: {str(error)}\n\nLa aplicación no puede continuar."
        tk.messagebox.showerror("Error Crítico", error_msg)
        sys.exit(1)
    
    def run(self):
        """Ejecutar aplicación"""
        try:
            logger.info("Ejecutando aplicación...")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Aplicación interrumpida por el usuario")
        except Exception as e:
            logger.critical(f"Error durante ejecución: {e}")
            self._show_critical_error(e)
        finally:
            logger.info("Aplicación finalizada")

if __name__ == "__main__":
    app = DoñaRosaApp()
    app.run()