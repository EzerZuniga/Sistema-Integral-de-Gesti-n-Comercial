import tkinter as tk
from tkinter import ttk
from app.base_view import BaseView
from ui.components.button import CustomButton, IconButton
from core.auth import AuthService
from core.logger import logger

class LoginView(BaseView):
    """Vista de inicio de sesión"""
    
    def _setup_view(self):
        """Configurar la vista de login"""
        # Paleta de colores (según Pañeta Final Recomendada)
        primary = "#2C73D2"  # Azul profesional
        success = "#2E7D32"  # Verde comercio
        white = "#FFFFFF"
        light_gray = "#F1F1F1"
        text_gray = "#2E2E2E"
        danger = "#DC3545"
        accent_yellow = "#F9C846"
        placeholder_color = "#9aa0a6"
        # Guardar colores en la instancia para usarlos en otros métodos
        self.primary = primary
        self.success = success
        self.white = white
        self.light_gray = light_gray
        self.text_gray = text_gray
        self.danger = danger
        self.accent_yellow = accent_yellow
        self.placeholder_color = placeholder_color
        # Frame principal centrado (usar tk.Frame para control visual directo)
        # Contenedor que ocupa todo el espacio de la vista
        container = tk.Frame(self, bg=light_gray)
        container.grid(row=0, column=0, sticky="nsew")

        # Asegurar que la vista use todo el espacio y centre el panel
        try:
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

        # Panel central (no propagará tamaño de los widgets)
        # Borde más fino y apariencia más compacta
        # Remover borde para evitar líneas visibles en los bordes cuando se estira
        main_frame = tk.Frame(container, bg=white, bd=0, relief="flat")
        main_frame.pack_propagate(False)
        # Empaquetar el card centrado; usaremos padding horizontal que actualizaremos en resize
        main_frame.pack(anchor='center', pady=20)
        try:
            # columnas: etiqueta fija, campo expandible
            main_frame.grid_columnconfigure(0, weight=0, minsize=140)
            main_frame.grid_columnconfigure(1, weight=1)
        except Exception:
            pass

        # Banner superior (diseño similar a la referencia)
        banner_frame = tk.Frame(container, bg=light_gray)
        banner_frame.pack(side='top', fill='x', pady=(10, 8))
        banner_frame.grid_columnconfigure(0, weight=1)

        # Estilos de banner
        style = ttk.Style()
        style.configure('BannerTitle.TLabel', font=("Segoe UI", 16, "bold"), foreground=text_gray, background=light_gray)
        style.configure('BannerSubtitle.TLabel', font=("Segoe UI", 10), foreground="#67707a", background=light_gray)

        banner_title = ttk.Label(banner_frame, text="BODEGA DOÑA ROSA", style='BannerTitle.TLabel', anchor='center')
        banner_title.pack(pady=(8, 0))
        banner_sub = ttk.Label(banner_frame, text="Sistema de Gestión", style='BannerSubtitle.TLabel', anchor='center')
        banner_sub.pack(pady=(2, 8))

        # Guardar referencias para ajuste responsivo (se usan más abajo)
        self._title_label = banner_title
        self._subtitle_label = banner_sub

        # Estilos básicos usando ttk.Style para consistencia (ya creado arriba)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Title.TLabel', font=("Segoe UI", 20, "bold"), foreground=text_gray, background=white)
        style.configure('Subtitle.TLabel', font=("Segoe UI", 12), foreground="#67707a", background=white)
        style.configure('Form.TLabel', font=("Segoe UI", 11), background=white)
        style.configure('Link.TButton', font=("Segoe UI", 10, 'underline'), foreground=primary, background=white)
        style.configure('TEntry', padding=6)
        style.configure('Primary.TButton', font=("Segoe UI", 11, "bold"), foreground=white, background=primary)

        # Título en su propia fila para evitar solapamiento con el logo
        title_label = ttk.Label(main_frame, text="Doña Rosa", style='Title.TLabel', anchor='center')
        title_label.grid(row=1, column=0, columnspan=2, pady=(6, 6), padx=6, sticky='n')
        self._title_label = title_label

        subtitle_label = ttk.Label(main_frame, text="Sistema de Gestión - Iniciar Sesión", style='Subtitle.TLabel', anchor='center')
        subtitle_label.grid(row=2, column=0, columnspan=2, pady=(0, 12), padx=6, sticky='n')
        self._subtitle_label = subtitle_label

        # Campo usuario con placeholder
        user_label = ttk.Label(main_frame, text="Usuario:", style='Form.TLabel')
        user_label.grid(row=3, column=0, sticky="e", pady=6, padx=(8, 6))
        self._user_label = user_label

        # Usamos tk.Entry para soporte sencillo de placeholder visual
        self.user_entry = tk.Entry(main_frame, font=("Segoe UI", 11), bd=1, relief='solid')
        self.user_entry.grid(row=3, column=1, pady=6, padx=(4, 12), sticky="ew")
        self._user_entry = self.user_entry
        # Focus visual y accesibilidad
        try:
            self.user_entry.config(highlightthickness=1, highlightbackground='#d1d5d9', highlightcolor=primary)
        except Exception:
            pass
        # placeholder
        def _ph_on_focus_in(e):
            if self.user_entry.get() == 'usuario':
                self.user_entry.delete(0, tk.END)
                self.user_entry.config(fg=text_gray)
        def _ph_on_focus_out(e):
            if not self.user_entry.get():
                self.user_entry.insert(0, 'usuario')
                self.user_entry.config(fg=placeholder_color)
        self.user_entry.bind('<FocusIn>', _ph_on_focus_in)
        self.user_entry.bind('<FocusOut>', _ph_on_focus_out)
        self.user_entry.insert(0, 'usuario')
        self.user_entry.config(fg=placeholder_color)
        self.user_entry.focus()

        # Campo contraseña con placeholder
        pass_label = ttk.Label(main_frame, text="Contraseña:", style='Form.TLabel')
        pass_label.grid(row=4, column=0, sticky="e", pady=6, padx=(8, 6))
        self._pass_label = pass_label

        # Contenedor para el campo de contraseña + botón mostrar/ocultar
        pw_frame = tk.Frame(main_frame, bg=white)
        pw_frame.grid(row=4, column=1, pady=6, padx=(4, 12), sticky="ew")
        pw_frame.grid_columnconfigure(0, weight=1)

        self.pass_entry = tk.Entry(pw_frame, show='', font=("Segoe UI", 11), bd=1, relief='solid')
        self.pass_entry.grid(row=0, column=0, sticky='ew')
        self._pass_entry = self.pass_entry

        # Estado para visibilidad de contraseña
        self._password_visible = False

        # Botón 'ojito' para mostrar/ocultar contraseña (usar IconButton para apariencia consistente)
        def _toggle_password(event=None):
            # Sólo alternar si no está el placeholder
            txt = self.pass_entry.get()
            if txt == 'contraseña' or not txt:
                return
            self._password_visible = not self._password_visible
            if self._password_visible:
                self.pass_entry.config(show='')
                try:
                    eye_btn.set_icon('🙈')
                except Exception:
                    try:
                        eye_btn.config(text='🙈')
                    except Exception:
                        pass
            else:
                self.pass_entry.config(show='•')
                try:
                    eye_btn.set_icon('👁')
                except Exception:
                    try:
                        eye_btn.config(text='👁')
                    except Exception:
                        pass

        eye_btn = IconButton(pw_frame, icon='👁', command=_toggle_password, tooltip='Mostrar / ocultar contraseña', size=26)
        try:
            eye_btn.grid(row=0, column=1, padx=(6,0))
        except Exception:
            eye_btn.pack(side='right', padx=(6,0))

        # placeholder handling para contraseña
        def _ph_pass_focus_in(e):
            if self.pass_entry.get() == 'contraseña':
                self.pass_entry.delete(0, tk.END)
                self.pass_entry.config(show='•', fg=text_gray)
                # habilitar ojo
                eye_btn.config(state='normal')

        def _ph_pass_focus_out(e):
            if not self.pass_entry.get():
                self.pass_entry.config(show='', fg=placeholder_color)
                self.pass_entry.insert(0, 'contraseña')
                # deshabilitar ojo cuando placeholder visible
                eye_btn.config(state='disabled')

        self.pass_entry.bind('<FocusIn>', _ph_pass_focus_in)
        self.pass_entry.bind('<FocusOut>', _ph_pass_focus_out)
        self.pass_entry.insert(0, 'contraseña')
        self.pass_entry.config(fg=placeholder_color)
        eye_btn.config(state='disabled')
        self.pass_entry.bind('<Return>', lambda e: self._login())
        # Enter también en usuario dispara login
        try:
            self.user_entry.bind('<Return>', lambda e: self._login())
        except Exception:
            pass

        # Activar/desactivar el ojo según contenido mientras se escribe
        def _on_pass_key(event=None):
            # Asegurar que por defecto los caracteres queden ocultos mientras
            # no se haya activado la visibilidad con el ojito.
            txt = self.pass_entry.get()
            if not txt or txt == 'contraseña':
                eye_btn.config(state='disabled')
                # mantenemos placeholder/oculto
                if not self._password_visible:
                    self.pass_entry.config(show='')
            else:
                eye_btn.config(state='normal')
                if not self._password_visible:
                    # Asegurar que el caracter de ocultación esté activo antes
                    # de que el siguiente carácter sea mostrado. Usar <Key>
                    # evita parpadeos visibles.
                    self.pass_entry.config(show='•')

        # Usar <Key> para aplicar el ocultamiento inmediatamente al teclear
        self.pass_entry.bind('<Key>', _on_pass_key)
        # También actualizar estado tras pegar texto u otras acciones
        self.pass_entry.bind('<KeyRelease>', _on_pass_key)
        # Acceso por teclado: Alt+V para alternar ver/ocultar contraseña
        try:
            self.pass_entry.bind_all('<Alt-v>', lambda e: _toggle_password())
        except Exception:
            pass

        # Botones
        # Botón primario destacado (usar CustomButton para mayor control)
        login_btn = CustomButton(main_frame, text="Iniciar Sesión", command=self._login, style='Primary.TButton', width=18)
        login_btn.grid(row=5, column=0, columnspan=2, pady=(14, 10), sticky='ew')
        self._login_btn = login_btn

        # Añadir pequeño helper debajo del botón para usuarios novatos
        help_label = ttk.Label(main_frame, text="Si no recuerda sus credenciales, contacte al administrador.", style='Subtitle.TLabel')
        help_label.grid(row=6, column=0, columnspan=2, pady=(4, 6))

        # Row con checkbox y "olvidó"
        opts_frame = tk.Frame(main_frame, bg=white)
        opts_frame.grid(row=7, column=0, columnspan=2, pady=(6, 6), sticky='ew')
        opts_frame.grid_columnconfigure(0, weight=1)
        opts_frame.grid_columnconfigure(1, weight=0)

        self.remember_var = tk.BooleanVar(value=False)
        # Check grande y claro
        remember_chk = tk.Checkbutton(opts_frame, text="Recordarme", variable=self.remember_var, bg=white, font=("Segoe UI", 10))
        remember_chk.grid(row=0, column=0, sticky='w', padx=(2,0))
        self._remember_chk = remember_chk

        # 'Olvidó su contraseña' como link (label clickable)
        # Botón estilo link para 'olvidó contraseña' (mejor accesibilidad)
        try:
            forgot_btn = ttk.Button(opts_frame, text="¿Olvidó su contraseña?", style='Link.TButton', command=lambda: self.show_message("Info", "Contacte al administrador", "info"))
            forgot_btn.grid(row=0, column=1, sticky='e', padx=(4,8))
            self._forgot_btn = forgot_btn
        except Exception:
            forgot_label = tk.Label(opts_frame, text="¿Olvidó su contraseña?", fg=primary, bg=white, cursor="hand2", font=("Segoe UI", 10, 'underline'))
            forgot_label.grid(row=0, column=1, sticky='e', padx=(4,8))
            forgot_label.bind('<Button-1>', lambda e: self.show_message("Info", "Contacte al administrador", "info"))
            self._forgot_btn = forgot_label

        # Botón de registrar (solo muestra información por ahora)

        # Se eliminó el botón 'Registrarse' por petición del usuario

        # Versión pequeña
        version_label = ttk.Label(main_frame, text="v1.0.0", style='Subtitle.TLabel')
        version_label.grid(row=9, column=0, columnspan=2, pady=(10, 0))

        # Label inline para mostrar errores/estado debajo del formulario
        self.status_label = ttk.Label(main_frame, text="", style='Form.TLabel')
        self.status_label.grid(row=8, column=0, columnspan=2, pady=(8, 0))
        self._status_label = self.status_label
        try:
            self.status_label.config(foreground=danger)
        except Exception:
            pass

        # Guardar widgets
        self.widgets = {
            'user_entry': self.user_entry,
            'pass_entry': self.pass_entry,
            'login_btn': login_btn,
            'forgot_btn': getattr(self, '_forgot_btn', None)
        }

        # Guardar referencia al panel central para control responsivo
        self._main_panel = main_frame

        # Función para ajustar tamaño del panel según el tamaño del contenedor
        def _resize_panel(event=None):
            try:
                w = container.winfo_width() or self.winfo_width() or 800
                h = container.winfo_height() or self.winfo_height() or 600

                # Mostrar el contenido en forma de 'card' centrada (cuadradito)
                margin = 28  # margen mínimo a cada lado
                max_card_width = 720  # ancho máximo del card para apariencia profesional

                # Calcular ancho disponible restando márgenes y evitar overflow
                available_w = max(360, int(w) - (margin * 2))
                panel_w = min(available_w, max_card_width)

                # Altura proporcional al ancho, con límites razonables
                ideal_h = int(panel_w * 0.62) + 160
                panel_h = max(360, min(int(h * 0.85), ideal_h))

                # Asegurar que el card quepa horizontalmente
                if panel_w + (margin * 2) > w:
                    panel_w = max(360, w - (margin * 2))

                try:
                    # padding interior ligero para estética
                    self._main_panel.config(width=panel_w, height=panel_h, padx=16, pady=14)
                except Exception:
                    self._main_panel.config(width=panel_w, height=panel_h)

                # Centrar el card utilizando pack y usando el margen fijo
                try:
                    pad_x = margin
                    self._main_panel.pack_configure(padx=pad_x, pady=max(20, int((h - panel_h) / 4)))
                except Exception:
                    pass

                # Ajustar tamaños de fuente para mantener apariencia como en la primera imagen
                try:
                    base = max(12, int(panel_w / 36))
                    title_size = max(18, base + 6)
                    subtitle_size = max(11, base + 1)
                    label_size = max(12, base)
                    entry_size = max(12, base)
                    btn_size = max(11, base - 1)

                    try:
                        if hasattr(self, '_title_label'):
                            self._title_label.config(font=("Segoe UI", title_size, "bold"))
                        if hasattr(self, '_subtitle_label'):
                            self._subtitle_label.config(font=("Segoe UI", subtitle_size))
                    except Exception:
                        pass

                    for wgt in [getattr(self, '_user_label', None), getattr(self, '_pass_label', None)]:
                        if wgt:
                            try:
                                wgt.config(font=("Segoe UI", label_size))
                            except Exception:
                                pass

                    for ent in [getattr(self, '_user_entry', None), getattr(self, '_pass_entry', None)]:
                        if ent:
                            try:
                                ent.config(font=("Segoe UI", entry_size))
                            except Exception:
                                pass

                    for b in [getattr(self, '_login_btn', None), getattr(self, '_forgot_btn', None), getattr(self, '_register_btn', None)]:
                        if b:
                            try:
                                b.config(font=("Segoe UI", btn_size))
                            except Exception:
                                pass

                    try:
                        if hasattr(self, '_status_label'):
                            self._status_label.config(font=("Segoe UI", max(9, label_size - 1)))
                    except Exception:
                        pass
                except Exception:
                    pass
            except Exception:
                pass

        # Vincular al cambio de tamaño del contenedor/ventana
        container.bind('<Configure>', _resize_panel)
        try:
            # Llamada inicial para ajustar tamaño al crear la vista
            self.after(10, _resize_panel)
        except Exception:
            _resize_panel()
    
    def _login(self):
        """Manejar intento de login"""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        # Limpiar estado previo
        try:
            self.status_label.config(text="")
        except Exception:
            pass

        if not username or not password:
            # Mostrar mensaje inline si está disponible
            try:
                self.status_label.config(text="Usuario y contraseña son requeridos")
            except Exception:
                self.show_message("Error", "Usuario y contraseña son requeridos", "error")
            return
        
        try:
            # Deshabilitar botón durante el login
            self.widgets['login_btn'].config(state="disabled")
            
            # Intentar login
            user = AuthService.login(username, password)
            
            if user:
                logger.info(f"Login exitoso para usuario: {username}")
                # Mensaje de bienvenida y navegación al dashboard
                try:
                    # mostrar mensaje inline primero
                    try:
                        self.status_label.config(text=f"Bienvenido {user.nombre}", fg=self.success)
                    except Exception:
                        pass
                    self.show_message("Bienvenido", f"Bienvenido {user.nombre}", "info")
                except Exception:
                    pass
                from app.router import router
                router.navigate_to('dashboard')
            else:
                try:
                    self.status_label.config(text="Credenciales inválidas", fg=self.danger)
                except Exception:
                    self.show_message("Error", "Credenciales inválidas", "error")
                self.pass_entry.delete(0, tk.END)
                self.pass_entry.focus()
                
        except Exception as e:
            self.show_message("Error", f"Error al iniciar sesión: {str(e)}", "error")
            logger.error(f"Error en login: {e}")
        
        finally:
            # Rehabilitar botón
            self.widgets['login_btn'].config(state="normal")
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        # Limpiar campos y enfocar en usuario
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.user_entry.focus()