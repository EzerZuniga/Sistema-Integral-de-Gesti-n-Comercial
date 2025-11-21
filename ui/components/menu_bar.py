import tkinter as tk
from tkinter import ttk
from core.auth import AuthService
from core.logger import logger
from app.app_context import app_context
from app.router import router

class MenuBar(ttk.Frame):
    """Barra de menú lateral para navegación"""
    
    def __init__(self, parent):
        super().__init__(parent, style="Menu.TFrame")
        self.parent = parent
        self.buttons = {}
        
        self._create_style()
        self._setup_menu()
    
    def _create_style(self):
        """Crear estilos para el menú"""
        style = ttk.Style()
        style.configure("Menu.TFrame", background="#2c3e50")
        style.configure("Menu.TButton", 
                       background="#34495e", 
                       foreground="#ecf0f1",
                       borderwidth=0,
                       focuscolor="none",
                       font=("Arial", 10))
        
        style.map("Menu.TButton",
                 background=[('active', '#3498db'),
                           ('pressed', '#2980b9')])
        
        style.configure("MenuTitle.TLabel",
                       background="#2c3e50",
                       foreground="#ecf0f1",
                       font=("Arial", 12, "bold"))
        
        style.configure("UserInfo.TLabel",
                       background="#2c3e50",
                       foreground="#bdc3c7",
                       font=("Arial", 9))
        
        # Estilo para el botón activo (ruta seleccionada)
        style.configure("ActiveMenu.TButton",
                   background="#16a085",
                   foreground="#ffffff",
                   font=("Arial", 10, 'bold'))
        style.map("ActiveMenu.TButton",
              background=[('active', '#1abc9c')])
    
    def _setup_menu(self):
        """Configurar el menú lateral"""
        # Información del usuario
        user_frame = ttk.Frame(self, style="Menu.TFrame")
        user_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        user = AuthService.get_current_user()
        if user:
            ttk.Label(
                user_frame,
                text=f"👤 {user.nombre}",
                style="MenuTitle.TLabel"
            ).pack(anchor="w")
            
            ttk.Label(
                user_frame,
                text=f"Rol: {user.rol.title()}",
                style="UserInfo.TLabel"
            ).pack(anchor="w")
        
        # Separador
        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=5)
        
        # Botones de navegación
        nav_frame = ttk.Frame(self, style="Menu.TFrame")
        nav_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        menu_items = self._get_menu_items()

        for item in menu_items:
            # Solo mostrar items permitidos para el rol del usuario
            if item.get('admin_only') and not (user and user.rol == 'admin'):
                continue

            if item.get('requires_auth') and not AuthService.is_authenticated():
                continue

            if item['type'] == 'separator':
                separator = ttk.Separator(nav_frame, orient="horizontal")
                separator.pack(fill="x", pady=5)
                continue

            if item['type'] == 'section':
                # Sección: título no clicable
                lbl = ttk.Label(nav_frame, text=item.get('text', ''), style='MenuTitle.TLabel')
                lbl.pack(fill='x', pady=(8, 4), padx=6)
                continue

            if item['type'] == 'button':
                # Si el item tiene subitems ('children'), crear un frame plegable
                if item.get('children'):
                    # Botón principal que expande/colapsa
                    frame = ttk.Frame(nav_frame, style="Menu.TFrame")
                    frame.pack(fill='x', pady=2)

                    def make_toggle(children, parent_frame):
                        child_frame = ttk.Frame(parent_frame, style="Menu.TFrame")
                        child_frame.pack(fill='x', padx=(12,0))
                        # inicialmente visible = False
                        child_frame.pack_forget()

                        def toggle():
                            if child_frame.winfo_ismapped():
                                child_frame.pack_forget()
                            else:
                                child_frame.pack(fill='x', padx=(12,0))

                        return child_frame, toggle

                    # crear toggle area
                    child_frame, toggle_fn = make_toggle(item['children'], frame)

                    btn = ttk.Button(frame, text=item['text'] + ' ▾', command=toggle_fn, style="Menu.TButton", takefocus=True)
                    btn.pack(fill='x', padx=2)
                    # allow keyboard activation
                    btn.bind('<Return>', lambda e, b=btn: b.invoke())
                    if item.get('route'):
                        self.buttons[item['route']] = btn

                    # Render children
                    for child in item['children']:
                        if child.get('admin_only') and not (user and user.rol == 'admin'):
                            continue
                        if child.get('requires_auth') and not AuthService.is_authenticated():
                            continue
                        cbtn = ttk.Button(child_frame, text='  ' + child.get('text', ''), command=lambda r=child['route']: self._safe_navigate(r), style='Menu.TButton', takefocus=True)
                        cbtn.pack(fill='x', pady=1, padx=(4,0))
                        cbtn.bind('<Return>', lambda e, b=cbtn: b.invoke())
                        self.buttons[child['route']] = cbtn
                else:
                    btn = ttk.Button(
                        nav_frame,
                        text=item['text'],
                        command=lambda r=item['route']: self._safe_navigate(r),
                        style="Menu.TButton",
                        width=20
                    )
                    btn.pack(fill="x", pady=2, padx=2)
                    btn.bind('<Return>', lambda e, b=btn: b.invoke())
                    self.buttons[item['route']] = btn
        
        # Separador final
        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=5)
        
        # Botón de cerrar sesión
        if AuthService.is_authenticated():
            logout_btn = ttk.Button(
                self,
                text="🚪 Cerrar Sesión",
                command=self._logout,
                style="Menu.TButton",
                width=20
            )
            logout_btn.pack(side="bottom", fill="x", padx=5, pady=10)
            logout_btn.bind('<Return>', lambda e, b=logout_btn: b.invoke())
    
    def _get_menu_items(self):
        """Obtener items del menú según permisos"""
        user = AuthService.get_current_user()
        is_admin = user and user.rol == 'admin'
        
        items = [
            # Módulo Inicio
            {'type': 'section', 'text': 'INICIO', 'route': ''},
            {'type': 'button', 'text': '📊 Dashboard', 'route': 'dashboard', 'requires_auth': True},
            
            # Módulo Acerca De
            {'type': 'separator'},
            {'type': 'section', 'text': 'EMPRESA', 'route': ''},
            {'type': 'button', 'text': '🏢 Información', 'route': 'empresa', 'requires_auth': True, 'admin_only': True},
            {'type': 'button', 'text': '👥 Trabajadores', 'route': 'trabajadores', 'requires_auth': True, 'admin_only': True},
            {'type': 'button', 'text': '🚚 Proveedores', 'route': 'proveedores', 'requires_auth': True, 'admin_only': True},
            
            # Módulo Procesos
            {'type': 'separator'},
            {'type': 'section', 'text': 'PROCESOS', 'route': ''},
            {'type': 'button', 'text': '💰 Ventas', 'route': 'ventas', 'requires_auth': True},
            {'type': 'button', 'text': '🛒 Compras', 'route': 'compras', 'requires_auth': True, 'admin_only': True},
            {'type': 'button', 'text': '📈 Resumen', 'route': 'resumen', 'requires_auth': True},
            
            # Módulo Inventario
            {'type': 'separator'},
            {'type': 'section', 'text': 'INVENTARIO', 'route': ''},
            {'type': 'button', 'text': '📦 Stock', 'route': 'stock', 'requires_auth': True},
            {'type': 'button', 'text': '⚠️ Alertas', 'route': 'alertas', 'requires_auth': True},
        ]
        
        # Devolver todos los items (incluyendo 'section') para que
        # la interfaz pueda renderizar títulos y submenús.
        return items
    
    def _logout(self):
        """Cerrar sesión"""
        try:
            if router.show_message(
                "Cerrar Sesión", 
                "¿Está seguro que desea cerrar sesión?",
                "question"
            ):
                AuthService.logout()
                app_context.clear_context()
                router.navigate_to('login')
                logger.info("Sesión cerrada por el usuario")
        except Exception as e:
            logger.error(f"Error al cerrar sesión: {e}")

    def _safe_navigate(self, route):
        """Navegar de forma segura, atrapando excepciones del router."""
        try:
            from app.router import router as _router
            _router.navigate_to(route)
        except Exception as e:
            logger.error(f"Error navegando a {route}: {e}")
    
    def update_menu(self):
        """Actualizar el menú (útil después de cambios de permisos)"""
        for widget in self.winfo_children():
            widget.destroy()
        self._setup_menu()
    
    def highlight_current_route(self, route_name: str):
        """Resaltar la ruta actual en el menú"""
        for route, button in self.buttons.items():
            if route == route_name:
                button.configure(style="ActiveMenu.TButton")
            else:
                button.configure(style="Menu.TButton")