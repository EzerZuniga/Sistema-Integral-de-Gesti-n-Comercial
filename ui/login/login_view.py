import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from app.base_view import BaseView
from ui.components.button import CustomButton, IconButton
from ui.login.icon_assets import ensure_icons
from core.auth import AuthService
from core.logger import logger

class LoginView(BaseView):
    """Vista de inicio de sesión (limpia y refactorizada).

    El método `_setup_view` construye la UI principal. Se han extraído
    pequeñas funciones auxiliares para evitar repetición y mejorar
    legibilidad: carga de iconos y manejo de placeholders.
    """

    def _setup_view(self):
        # --- Paleta de colores y constantes ---
        self.primary = "#2C73D2"
        self.success = "#2E7D32"
        self.white = "#FFFFFF"
        self.light_gray = "#F1F1F1"
        self.text_gray = "#2E2E2E"
        self.danger = "#DC3545"
        self.placeholder_color = "#9aa0a6"
        border_color = "#d0d6db"

        # Contenedor principal
        container = tk.Frame(self, bg=self.light_gray)
        container.grid(row=0, column=0, sticky="nsew")
        try:
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
        except Exception:
            pass

        # Card central
        main_frame = ttk.Frame(container, style='Card.TFrame')
        main_frame.pack_propagate(False)
        main_frame.pack(fill='both', expand=True, padx=28, pady=28)
        main_frame.grid_columnconfigure(0, weight=0, minsize=140)
        main_frame.grid_columnconfigure(1, weight=1)

        # Banner y títulos
        banner_frame = tk.Frame(container, bg=self.light_gray)
        banner_frame.pack(side='top', fill='x', pady=(10, 8))
        banner_title = ttk.Label(banner_frame, text="BODEGA DOÑA ROSA", style='BannerTitle.TLabel')
        banner_title.pack(pady=(8, 0))
        banner_sub = ttk.Label(banner_frame, text="Sistema de Gestión", style='BannerSubtitle.TLabel')
        banner_sub.pack(pady=(2, 8))
        self._title_label = banner_title
        self._subtitle_label = banner_sub

        try:
            ttk.Style().theme_use('clam')
        except Exception:
            pass

        title_label = ttk.Label(main_frame, text="Doña Rosa", style='Title.TLabel')
        title_label.grid(row=1, column=0, columnspan=2, pady=(12, 6), padx=6, sticky='n')
        subtitle_label = ttk.Label(main_frame, text="Sistema de Gestión - Iniciar Sesión", style='Subtitle.TLabel')
        subtitle_label.grid(row=2, column=0, columnspan=2, pady=(0, 12), padx=6, sticky='n')
        self._title_label = title_label
        self._subtitle_label = subtitle_label

        # --- Helpers internos ---
        def _load_icon(name, size=20, tint=None):
            """Carga `assets/icons/{name}.png`, opcionalmente redimensiona y tiñe al color `tint`.

            Devuelve un `ImageTk.PhotoImage` o `None` en fallo.
            """
            try:
                icons_dir = ensure_icons()
                if not icons_dir:
                    return None
                path = os.path.join(icons_dir, f"{name}.png")
                if not os.path.exists(path):
                    return None

                img = Image.open(path).convert('RGBA')
                if size:
                    img = img.resize((size, size), Image.ANTIALIAS)

                if tint:
                    # aplicar tint respetando el canal alpha
                    try:
                        r, g, b = tuple(int(tint.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                        datas = img.getdata()
                        newdata = []
                        for item in datas:
                            # item -> (r,g,b,a)
                            if item[3] == 0:
                                newdata.append(item)
                            else:
                                newdata.append((r, g, b, item[3]))
                        img.putdata(newdata)
                    except Exception:
                        # si falla el tinting, seguir con la imagen original
                        pass

                return ImageTk.PhotoImage(img)
            except Exception as e:
                logger.debug(f"No se pudo cargar icono: {name} -> {e}")
            return None

        def _apply_placeholder(entry, placeholder, is_password=False, eye_btn=None):
            """Configura comportamiento de placeholder en una Entry."""
            def on_focus_in(_e=None):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=self.text_gray)
                    if is_password:
                        entry.config(show='•')
                        if eye_btn:
                            eye_btn.config(state='normal')

            def on_focus_out(_e=None):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=self.placeholder_color)
                    if is_password:
                        entry.config(show='')
                        if eye_btn:
                            eye_btn.config(state='disabled')

            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            entry.insert(0, placeholder)
            entry.config(fg=self.placeholder_color)
            if is_password and eye_btn:
                eye_btn.config(state='disabled')

        def _create_field(row, label_text, icon_name=None):
            """Crea y posiciona un label + frame + entry con icono dentro del input.

            Estructura del frame (colums): [icon][entry][acciones]
            Devuelve (label, frame, entry).
            """
            # Contenedor izquierdo: icono (fuera del input) + texto
            left_container = tk.Frame(main_frame, bg=self.light_gray)
            left_container.grid(row=row, column=0, sticky='e', pady=6, padx=(8, 6))

            icon_img = _load_icon(icon_name, size=20, tint=self.primary) if icon_name else None
            if icon_img:
                icon_out = tk.Label(left_container, image=icon_img, bg=self.light_gray)
                icon_out.image = icon_img
                icon_out.pack(side='left', padx=(0, 6))

            lbl = ttk.Label(left_container, text=label_text, style='Form.TLabel')
            lbl.pack(side='left')

            # Frame que hace de caja blanca alrededor del entry
            frame = tk.Frame(main_frame, bg=self.white, bd=0, highlightthickness=1, highlightbackground=border_color)
            frame.grid(row=row, column=1, pady=6, padx=(4, 12), sticky='ew')
            # columnas internas: 0 = icono, 1 = entry (expand), 2 = acciones (eye, etc.)
            frame.grid_columnconfigure(0, weight=0)
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(2, weight=0)

            # No colocar iconos dentro del input; se usan iconos en el lado izquierdo
            icon_lbl = None

            # Entry principal
            entry = tk.Entry(frame, font=("Segoe UI", 11), bd=0, relief='flat', insertbackground=self.text_gray, bg=self.white, fg=self.text_gray)
            entry.grid(row=0, column=1, sticky='nsew', padx=(4, 4), pady=6, ipady=6)
            try:
                entry.config(highlightthickness=0)
            except Exception:
                pass

            return lbl, frame, entry

        # --- Usuario ---
        user_lbl, user_frame, user_entry = _create_field(3, 'Usuario:', icon_name='user')
        self._user_label = user_lbl
        self._user_frame = user_frame
        self.user_entry = user_entry
        self._user_entry = user_entry
        _apply_placeholder(self.user_entry, 'usuario')
        self.user_entry.bind('<Return>', lambda e: self._login())

        # --- Contraseña (con ojo) ---
        pass_lbl, pw_frame, pass_entry = _create_field(4, 'Contraseña:', icon_name='lock')
        self._pass_label = pass_lbl
        self._pw_frame = pw_frame
        self.pass_entry = pass_entry
        self._pass_entry = pass_entry

        # Crear botón ojo
        eye_img = _load_icon('eye')

        if eye_img:
            eye_btn = IconButton(pw_frame, icon='', command=lambda: None, tooltip='Mostrar / ocultar contraseña', size=26)
            try:
                eye_btn.config(image=eye_img)
                eye_btn.image = eye_img
            except Exception:
                eye_btn.set_icon('👁')
        else:
            eye_btn = IconButton(pw_frame, icon='👁', command=lambda: None, tooltip='Mostrar / ocultar contraseña', size=26)

        # Asegurar que el botón ojo tenga apariencia plana y fondo coherente
        try:
            eye_btn.config(relief='flat', bd=0, bg=self.white, highlightthickness=0)
        except Exception:
            pass

        # Columna 2 del frame interno reservada para controles (eye, clear, etc.)
        pw_frame.grid_columnconfigure(2, weight=0)
        # Alinear el botón ojo a la derecha del input y centrar verticalmente
        eye_btn.grid(row=0, column=2, sticky='ns', padx=(6,8), pady=6)

        # Toggle para mostrar/ocultar contraseña; se expone en self
        def _toggle_password_local(_event=None):
            txt = self.pass_entry.get()
            if txt == 'contraseña' or not txt:
                return
            self._password_visible = not getattr(self, '_password_visible', False)
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

        # asignar el toggle real al botón
        try:
            eye_btn.config(command=_toggle_password_local)
        except Exception:
            pass
        self._toggle_password = _toggle_password_local

        _apply_placeholder(self.pass_entry, 'contraseña', is_password=True, eye_btn=eye_btn)
        self.pass_entry.bind('<Return>', lambda e: self._login())

        def _on_pass_key(_e=None):
            txt = self.pass_entry.get()
            if not txt or txt == 'contraseña':
                eye_btn.config(state='disabled')
                if not getattr(self, '_password_visible', False):
                    self.pass_entry.config(show='')
            else:
                eye_btn.config(state='normal')
                if not getattr(self, '_password_visible', False):
                    self.pass_entry.config(show='•')

        self.pass_entry.bind('<Key>', _on_pass_key)
        self.pass_entry.bind('<KeyRelease>', _on_pass_key)
        try:
            self.pass_entry.bind_all('<Alt-v>', lambda e: _toggle_password_local())
        except Exception:
            pass

        # --- Botones y links ---
        login_btn = CustomButton(main_frame, text="Iniciar Sesión", command=self._login, style='Primary.TButton')
        login_btn.grid(row=5, column=0, columnspan=2, pady=(18, 12), ipadx=6, ipady=8, sticky='ew')
        try:
            login_btn.config(width=30)
        except Exception:
            pass
        self._login_btn = login_btn

        help_label = ttk.Label(main_frame, text="Si no recuerda sus credenciales, contacte al administrador.", style='Muted.TLabel')
        help_label.grid(row=6, column=0, columnspan=2, pady=(4, 6))

        opts_frame = tk.Frame(main_frame, bg=self.white)
        opts_frame.grid(row=7, column=0, columnspan=2, pady=(6, 6), sticky='ew')
        opts_frame.grid_columnconfigure(0, weight=1)
        opts_frame.grid_columnconfigure(1, weight=0)

        self.remember_var = tk.BooleanVar(value=False)
        remember_chk = tk.Checkbutton(opts_frame, text="Recordarme", variable=self.remember_var, bg=self.white, font=("Segoe UI", 10))
        remember_chk.grid(row=0, column=0, sticky='w', padx=(2,0))
        self._remember_chk = remember_chk

        forgot_label = tk.Label(opts_frame, text="¿Olvidó su contraseña?", fg=self.primary, bg=self.white, cursor="hand2", font=("Segoe UI", 10))
        forgot_label.grid(row=0, column=1, sticky='e', padx=(4,8))
        forgot_label.bind('<Button-1>', lambda e: self.show_message("Info", "Contacte al administrador", "info"))
        self._forgot_btn = forgot_label

        version_label = ttk.Label(main_frame, text="v1.0.0", style='Subtitle.TLabel')
        version_label.grid(row=9, column=0, columnspan=2, pady=(14, 6))

        # mensaje inline
        self.status_label = ttk.Label(main_frame, text="", style='Form.TLabel')
        self.status_label.grid(row=8, column=0, columnspan=2, pady=(8, 0))
        try:
            self.status_label.config(foreground=self.danger)
        except Exception:
            pass

        # guardar widgets clave
        self.widgets = {
            'user_entry': self.user_entry,
            'pass_entry': self.pass_entry,
            'login_btn': login_btn,
            'forgot_btn': getattr(self, '_forgot_btn', None)
        }

        self._main_panel = main_frame

        # --- Feedback visual: shake + resaltar campo con error ---
        def _shake(widget, distance=8, times=6, delay=20):
            """Animación de sacudida que no rompe el layout.

            - Si el widget está administrado por `place`, usa place_configure.
            - Si está administrado por `pack` o `grid`, ajusta temporalmente
              el `padx` para simular la sacudida (no cambia el gestor).
            """
            try:
                manager = widget.winfo_manager()

                # Obtener un valor de padx original para poder restaurarlo
                orig_padx = None
                if manager == 'pack':
                    try:
                        info = widget.pack_info()
                        orig_padx = info.get('padx', 0)
                    except Exception:
                        orig_padx = 0
                elif manager == 'grid':
                    try:
                        info = widget.grid_info()
                        orig_padx = info.get('padx', 0)
                    except Exception:
                        orig_padx = 0

                def _do_shake(count):
                    if count <= 0:
                        # restaurar estado original
                        try:
                            if manager == 'place':
                                widget.place_configure(x=0)
                            elif manager == 'pack':
                                widget.pack_configure(padx=orig_padx)
                            elif manager == 'grid':
                                widget.grid_configure(padx=orig_padx)
                        except Exception:
                            pass
                        return

                    offset = distance if count % 2 == 0 else -distance
                    try:
                        if manager == 'place':
                            widget.place_configure(x=offset)
                        elif manager == 'pack':
                            # ajustar padding horizontal temporalmente
                            try:
                                newpad = (orig_padx + abs(offset)) if isinstance(orig_padx, int) else orig_padx
                                widget.pack_configure(padx=newpad)
                            except Exception:
                                pass
                        elif manager == 'grid':
                            try:
                                newpad = (orig_padx + abs(offset)) if isinstance(orig_padx, int) else orig_padx
                                widget.grid_configure(padx=newpad)
                            except Exception:
                                pass
                    except Exception:
                        pass

                    widget.after(delay, _do_shake, count-1)

                _do_shake(times)
            except Exception:
                pass

        def _mark_field_error(widget, duration=1400):
            try:
                widget.config(highlightthickness=2, highlightbackground=self.danger)
            except Exception:
                try:
                    widget.config(bg=self.danger)
                except Exception:
                    pass

            def _clear():
                try:
                    widget.config(highlightthickness=0, highlightbackground='')
                except Exception:
                    try:
                        widget.config(bg=self.white)
                    except Exception:
                        pass

            try:
                widget.after(duration, _clear)
            except Exception:
                pass

        self._shake = _shake
        self._mark_field_error = _mark_field_error

        # --- Ajuste responsivo ---
        def _resize_panel(event=None):
            try:
                w = container.winfo_width() or self.winfo_width() or 800
                h = container.winfo_height() or self.winfo_height() or 600
                margin = 28
                max_card_width = 720
                available_w = max(360, int(w) - (margin * 2))
                panel_w = min(available_w, max_card_width)
                ideal_h = int(panel_w * 0.62) + 160
                panel_h = max(360, min(int(h * 0.85), ideal_h))
                if panel_w + (margin * 2) > w:
                    panel_w = max(360, w - (margin * 2))
                try:
                    self._main_panel.config(width=panel_w, height=panel_h, padx=16, pady=14)
                except Exception:
                    self._main_panel.config(width=panel_w, height=panel_h)
                try:
                    pad_x = margin
                    self._main_panel.pack_configure(padx=pad_x, pady=max(20, int((h - panel_h) / 4)))
                except Exception:
                    pass

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

        container.bind('<Configure>', _resize_panel)
        try:
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

        # Tratar placeholders como valores vacíos
        if username == 'usuario':
            username = ''
        if password == 'contraseña':
            password = ''

        if not username or not password:
            # Mostrar mensaje inline y resaltar campos necesarios
            try:
                self.status_label.config(text="Usuario y contraseña son requeridos", foreground=self.danger)
            except Exception:
                self.show_message("Error", "Usuario y contraseña son requeridos", "error")

            # resaltar campos vacíos
            try:
                if not username:
                    getattr(self, '_mark_field_error', lambda w: None)(getattr(self, '_user_frame', self.user_entry))
                if not password:
                    getattr(self, '_mark_field_error', lambda w: None)(getattr(self, '_pw_frame', self.pass_entry))
                # dar foco al primer campo vacío
                if not username:
                    self.user_entry.focus()
                else:
                    self.pass_entry.focus()
                # efecto shake
                try:
                    getattr(self, '_shake', lambda *a, **k: None)(self._main_panel)
                except Exception:
                    pass
            except Exception:
                pass

            return
        
        try:
            # Deshabilitar botón durante el login
            # indicar inicio y bloquear UI mínima
            try:
                self.widgets['login_btn'].set_text("Iniciando...")
            except Exception:
                pass
            self.widgets['login_btn'].config(state="disabled")
            
            # Intentar login
            try:
                user = AuthService.login(username, password)
            except Exception as e:
                user = None
                logger.error(f"Error llamando a AuthService.login: {e}")
            
            if user:
                logger.info(f"Login exitoso para usuario: {username}")
                # Mensaje de bienvenida y navegación al dashboard
                try:
                    # mostrar mensaje inline primero
                    try:
                        self.status_label.config(text=f"Bienvenido {user.nombre}", foreground=self.success)
                    except Exception:
                        pass
                    self.show_message("Bienvenido", f"Bienvenido {user.nombre}", "info")
                except Exception:
                    pass
                from app.router import router
                router.navigate_to('dashboard')
            else:
                try:
                    self.status_label.config(text="Credenciales inválidas", foreground=self.danger)
                except Exception:
                    self.show_message("Error", "Credenciales inválidas", "error")
                self.pass_entry.delete(0, tk.END)
                self.pass_entry.focus()
                # feedback visual de error
                try:
                    # usar el método expuesto en _setup_view
                    getattr(self, '_shake', lambda *a, **k: None)(self._main_panel)
                    # resaltar contraseña como origen probable
                    try:
                        getattr(self, '_mark_field_error', lambda w: None)(getattr(self, '_pw_frame', self.pass_entry))
                    except Exception:
                        pass
                except Exception:
                    pass
                
        except Exception as e:
            self.show_message("Error", f"Error al iniciar sesión: {str(e)}", "error")
            logger.error(f"Error en login: {e}")
        
        finally:
            # Rehabilitar botón
            try:
                self.widgets['login_btn'].set_text("Iniciar Sesión")
            except Exception:
                pass
            self.widgets['login_btn'].config(state="normal")
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        # Limpiar campos y enfocar en usuario
        try:
            self.user_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
            # Reinsertar placeholders para consistencia visual
            self.user_entry.insert(0, 'usuario')
            self.user_entry.config(fg=self.placeholder_color)
            self.pass_entry.insert(0, 'contraseña')
            self.pass_entry.config(fg=self.placeholder_color, show='')
            self.user_entry.focus()
        except Exception:
            try:
                self.user_entry.focus()
            except Exception:
                pass 