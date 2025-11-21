import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from core.utils import utils

class CustomButton(ttk.Button):
    """Botón personalizado con funcionalidades extendidas"""
    
    def __init__(self, parent, text: str = "", command: Optional[Callable] = None,
                 style: str = "Primary.TButton", icon: str = "", 
                 tooltip: str = "", width: Optional[int] = None,
                 state: str = "normal", **kwargs):
        
        self.text = text
        self.command = command
        self.icon = icon
        self.tooltip_text = tooltip
        self._state = state
        
        # Texto con icono si se especifica
        display_text = f"{icon} {text}" if icon else text
        
        # Asegurar que los estilos base existan
        self._ensure_styles()

        super().__init__(
            parent,
            text=display_text,
            command=self._wrap_command,
            style=style,
            width=width,
            state=state,
            **kwargs
        )
        
        # Configurar tooltip
        if tooltip:
            self._setup_tooltip()
        # Bind hover para cambio visual
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
            
    def _wrap_command(self):
        """Wrapper para el comando que maneja excepciones"""
        try:
            if self.command:
                self.command()
        except Exception as e:
            utils.show_message(self.winfo_toplevel(), "Error", f"Error en botón: {str(e)}", "error")
            
    def _setup_tooltip(self):
        """Configurar tooltip"""
        self.tooltip = None
        # show tooltip after short delay to avoid flicker
        self._tooltip_after_id = None
        self.bind("<Enter>", self._schedule_tooltip)
        self.bind("<Leave>", self._hide_tooltip)

    def _schedule_tooltip(self, event=None):
        if self.tooltip_text and self._state != "disabled":
            # schedule show after 250ms
            try:
                self._tooltip_after_id = self.after(250, self._show_tooltip)
            except Exception:
                # fallback immediate
                self._show_tooltip()
        
    def _show_tooltip(self, event=None):
        """Mostrar tooltip"""
        # cancel scheduled show if cancelled
        try:
            if hasattr(self, '_tooltip_after_id') and self._tooltip_after_id:
                self.after_cancel(self._tooltip_after_id)
                self._tooltip_after_id = None
        except Exception:
            pass

        if not (self.tooltip_text and self._state != "disabled"):
            return

        # position near pointer to be robust across widgets
        px = self.winfo_pointerx()
        py = self.winfo_pointery()

        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        # small offset to avoid covering the cursor
        self.tooltip.wm_geometry(f"+{px+12}+{py+20}")

        label = tk.Label(
            self.tooltip,
            text=self.tooltip_text,
            bg="#F9C846",
            fg="#2E2E2E",
            relief="solid",
            bd=1,
            padx=6,
            pady=3,
            font=("Segoe UI", 9)
        )
        label.pack()
            
    def _hide_tooltip(self, event=None):
        """Ocultar tooltip"""
        try:
            if hasattr(self, '_tooltip_after_id') and self._tooltip_after_id:
                self.after_cancel(self._tooltip_after_id)
                self._tooltip_after_id = None
        except Exception:
            pass

        if self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None
            
    def set_text(self, text: str):
        """Cambiar texto del botón"""
        self.text = text
        display_text = f"{self.icon} {text}" if self.icon else text
        self.config(text=display_text)
        
    def set_icon(self, icon: str):
        """Cambiar icono del botón"""
        self.icon = icon
        display_text = f"{icon} {self.text}" if icon else self.text
        self.config(text=display_text)
        
    def set_tooltip(self, tooltip: str):
        """Cambiar tooltip"""
        self.tooltip_text = tooltip
        
    def set_state(self, state: str):
        """Cambiar estado del botón"""
        self._state = state
        self.config(state=state)
        # actualizar estilo visual cuando está deshabilitado
        try:
            if state == "disabled":
                cur = self.cget("style")
                # si existe variante .Disabled, aplicarla
                disabled_style = f"{cur}.Disabled"
                style = ttk.Style()
                if disabled_style in style.element_names():
                    self.config(style=disabled_style)
                else:
                    # aplicar relief y opacidad visual
                    self.state = 'disabled'
            else:
                # restaurar estilo normal
                cur = self.cget("style")
                if cur.endswith('.Disabled'):
                    self.config(style=cur.replace('.Disabled', ''))
        except Exception:
            pass
        
    def enable(self):
        """Habilitar botón"""
        self.set_state("normal")
        
    def disable(self):
        """Deshabilitar botón"""
        self.set_state("disabled")
        
    def flash(self, times: int = 3, delay: int = 200):
        """Hacer parpadear el botón"""
        original_style = self.cget("style")
        flash_style = "Success.TButton"
        
        def flash(count):
            if count > 0:
                current_style = flash_style if count % 2 == 1 else original_style
                self.config(style=current_style)
                self.after(delay, flash, count - 1)
            else:
                self.config(style=original_style)
                
        flash(times * 2)

    # Hover handlers
    def _on_enter(self, event=None):
        try:
            cur = self.cget("style")
            hover = f"{cur}.Hover"
            style = ttk.Style()
            # si la variante hover fue registrada, aplicarla
            if hover in style.element_names():
                try:
                    self.config(style=hover)
                except Exception:
                    self.config(cursor="hand2")
            else:
                try:
                    self.config(cursor="hand2")
                except Exception:
                    pass
        except Exception:
            pass

    def _on_leave(self, event=None):
        try:
            cur = self.cget("style")
            if cur.endswith('.Hover'):
                self.config(style=cur.replace('.Hover', ''))
            else:
                try:
                    self.config(cursor="")
                except Exception:
                    pass
        except Exception:
            pass

    @staticmethod
    def _ensure_styles():
        """Registrar estilos base para botones usando la paleta recomendada.
        Esto crea variantes Primary/Secondary y variantes Hover/Disabled para consistencia.
        """
        s = ttk.Style()
        # Registrar estilos si no existen (no lanzar si ya están definidos)
        try:
            # Primary
            s.configure('Primary.TButton', background='#2C73D2', foreground='#FFFFFF', focusthickness=3, padding=6)
            s.map('Primary.TButton', background=[('active', '#2566b8'), ('disabled', '#9fb7e0')])
            s.configure('Primary.TButton.Hover', background='#2566b8', foreground='#FFFFFF')
            s.configure('Primary.TButton.Disabled', background='#9fb7e0', foreground='#ffffff')

            # Secondary (neutral / menu)
            s.configure('Secondary.TButton', background='#1a252f', foreground='#FFFFFF', padding=6)
            s.map('Secondary.TButton', background=[('active', '#0f1417'), ('disabled', '#5f6b73')])
            s.configure('Secondary.TButton.Hover', background='#0f1417', foreground='#FFFFFF')
            s.configure('Secondary.TButton.Disabled', background='#5f6b73', foreground='#ffffff')

            # Success / Danger
            s.configure('Success.TButton', background='#2E7D32', foreground='#FFFFFF', padding=6)
            s.map('Success.TButton', background=[('active', '#219a52'), ('disabled', '#9fb7e0')])
            s.configure('Danger.TButton', background='#DC3545', foreground='#FFFFFF', padding=6)
            s.map('Danger.TButton', background=[('active', '#c0392b'), ('disabled', '#e6a1a6')])
        except Exception:
            # algunos temas no permiten configurar ciertas propiedades; ignorar fallos
            pass

class IconButton(CustomButton):
    """Botón que solo muestra un icono"""
    
    def __init__(self, parent, icon: str, command: Optional[Callable] = None,
                 tooltip: str = "", size: int = 30, **kwargs):
        
        super().__init__(
            parent,
            text="",  # No texto, solo icono
            command=command,
            icon=icon,
            tooltip=tooltip,
            width=size // 10,  # Aproximar ancho basado en tamaño
            **kwargs
        )
        
        self.size = size
        
    def set_size(self, size: int):
        """Cambiar tamaño del botón"""
        self.size = size
        self.config(width=size // 10)

class ToggleButton(CustomButton):
    """Botón que mantiene estado toggle"""
    
    def __init__(self, parent, text: str = "", command: Optional[Callable] = None,
                 style: str = "Secondary.TButton", toggle_style: str = "Primary.TButton",
                 icon: str = "", toggle_icon: str = "", **kwargs):
        
        self.is_toggled = False
        self.toggle_style = toggle_style
        self.toggle_icon = toggle_icon
        self.normal_style = style
        self.normal_icon = icon
        self.toggle_command = command
        
        super().__init__(
            parent,
            text=text,
            command=self._toggle,
            style=style,
            icon=icon,
            **kwargs
        )
        
    def _toggle(self):
        """Alternar estado"""
        self.is_toggled = not self.is_toggled
        
        if self.is_toggled:
            self.config(style=self.toggle_style)
            if self.toggle_icon:
                self.set_icon(self.toggle_icon)
        else:
            self.config(style=self.normal_style)
            if self.normal_icon:
                self.set_icon(self.normal_icon)
                
        if self.toggle_command:
            self.toggle_command(self.is_toggled)
            
    def set_toggled(self, toggled: bool):
        """Establecer estado toggle"""
        if toggled != self.is_toggled:
            self._toggle()
            
    def get_state(self) -> bool:
        """Obtener estado toggle"""
        return self.is_toggled

class ButtonGroup(ttk.Frame):
    """Grupo de botones organizados"""
    
    def __init__(self, parent, orientation: str = "horizontal", 
                 spacing: int = 5, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.orientation = orientation
        self.spacing = spacing
        self.buttons = []
        
    def add_button(self, text: str, command: Callable, **kwargs):
        """Agregar botón al grupo"""
        button = CustomButton(self, text=text, command=command, **kwargs)
        
        if self.orientation == "horizontal":
            button.pack(side="left", padx=self.spacing)
        else:
            button.pack(side="top", pady=self.spacing)
            
        self.buttons.append(button)
        return button
        
    def add_icon_button(self, icon: str, command: Callable, **kwargs):
        """Agregar botón de icono al grupo"""
        button = IconButton(self, icon=icon, command=command, **kwargs)
        
        if self.orientation == "horizontal":
            button.pack(side="left", padx=self.spacing)
        else:
            button.pack(side="top", pady=self.spacing)
            
        self.buttons.append(button)
        return button
        
    def add_toggle_button(self, text: str, command: Callable, **kwargs):
        """Agregar botón toggle al grupo"""
        button = ToggleButton(self, text=text, command=command, **kwargs)
        
        if self.orientation == "horizontal":
            button.pack(side="left", padx=self.spacing)
        else:
            button.pack(side="top", pady=self.spacing)
            
        self.buttons.append(button)
        return button
        
    def set_enabled(self, enabled: bool):
        """Habilitar/deshabilitar todos los botones"""
        for button in self.buttons:
            if enabled:
                button.enable()
            else:
                button.disable()
                
    def clear(self):
        """Limpiar todos los botones"""
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()

class ActionButton(CustomButton):
    """Botón de acción con confirmación"""
    
    def __init__(self, parent, text: str, command: Callable,
                 confirm: bool = False, confirm_text: str = None,
                 style: str = "Danger.TButton", **kwargs):
        
        self.confirm = confirm
        self.confirm_text = confirm_text or f"¿Está seguro de {text.lower()}?"
        self.action_command = command
        
        if confirm:
            super().__init__(
                parent,
                text=text,
                command=self._confirm_action,
                style=style,
                **kwargs
            )
        else:
            super().__init__(
                parent,
                text=text,
                command=command,
                style=style,
                **kwargs
            )
            
    def _confirm_action(self):
        """Confirmar acción antes de ejecutar"""
        if utils.show_message(
            self.winfo_toplevel(),
            "Confirmar Acción",
            self.confirm_text,
            "question"
        ):
            self.action_command()

class ProgressButton(CustomButton):
    """Botón que muestra progreso"""
    
    def __init__(self, parent, text: str, command: Callable, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        
        self.progress_var = tk.DoubleVar()
        self.progress_style = ttk.Style()
        self.progress_style.configure("Progress.Horizontal.TProgressbar", 
                                    thickness=20)
        
        self.progress = ttk.Progressbar(
            self,
            variable=self.progress_var,
            style="Progress.Horizontal.TProgressbar",
            mode='determinate'
        )
        
    def show_progress(self):
        """Mostrar barra de progreso"""
        self.progress.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)
        self.config(text="")
        
    def hide_progress(self):
        """Ocultar barra de progreso"""
        self.progress.place_forget()
        
    def set_progress(self, value: float):
        """Establecer valor de progreso (0-100)"""
        self.progress_var.set(value)
        
    def start_loading(self, text: str = "Cargando..."):
        """Iniciar estado de carga"""
        self.disable()
        self.set_text(text)
        self.show_progress()
        self.set_progress(0)
        
    def stop_loading(self, original_text: str = None):
        """Detener estado de carga"""
        self.enable()
        self.hide_progress()
        if original_text:
            self.set_text(original_text)
        self.set_progress(0)