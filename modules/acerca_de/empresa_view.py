import tkinter as tk
from tkinter import ttk
from app.base_view import BaseView
from services.empresa_service import EmpresaService
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger

class EmpresaView(BaseView):
    """Vista de información de la empresa"""
    
    def _setup_view(self):
        """Configurar vista de empresa"""
        # Título
        self.create_title("🏢 Información de la Empresa", 0, 0, columnspan=2)
        
        # Frame principal
        form_frame = ttk.Frame(self)
        form_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid del formulario
        for i in range(2):
            form_frame.columnconfigure(i, weight=1)
        
        # Campos del formulario
        self._create_form_fields(form_frame)
        
        # Botones
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="e", padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Guardar Cambios",
            command=self._guardar_empresa,
            style="Primary.TButton"
        ).pack(side="right", padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self._cancelar,
            style="Secondary.TButton"
        ).pack(side="right", padx=5)
        
        # Cargar datos
        self._load_empresa_data()
    
    def _create_form_fields(self, parent):
        """Crear campos del formulario"""
        row = 0
        
        # Nombre de la empresa
        ttk.Label(parent, text="Nombre de la Empresa *:", style="Normal.TLabel").grid(
            row=row, column=0, sticky="w", pady=5, padx=5
        )
        self.nombre_entry = ttk.Entry(parent, width=40, font=("Arial", 10))
        self.nombre_entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # RUT
        ttk.Label(parent, text="RUT *:", style="Normal.TLabel").grid(
            row=row, column=0, sticky="w", pady=5, padx=5
        )
        self.rut_entry = ttk.Entry(parent, width=40, font=("Arial", 10))
        self.rut_entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Dirección
        ttk.Label(parent, text="Dirección:", style="Normal.TLabel").grid(
            row=row, column=0, sticky="w", pady=5, padx=5
        )
        self.direccion_entry = ttk.Entry(parent, width=40, font=("Arial", 10))
        self.direccion_entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Teléfono
        ttk.Label(parent, text="Teléfono:", style="Normal.TLabel").grid(
            row=row, column=0, sticky="w", pady=5, padx=5
        )
        self.telefono_entry = ttk.Entry(parent, width=40, font=("Arial", 10))
        self.telefono_entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Email
        ttk.Label(parent, text="Email:", style="Normal.TLabel").grid(
            row=row, column=0, sticky="w", pady=5, padx=5
        )
        self.email_entry = ttk.Entry(parent, width=40, font=("Arial", 10))
        self.email_entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Configurar peso de columnas
        parent.columnconfigure(1, weight=1)
    
    def _load_empresa_data(self):
        """Cargar datos de la empresa"""
        try:
            empresa = EmpresaService.obtener_empresa()
            
            if empresa:
                self.nombre_entry.insert(0, empresa.get('nombre', ''))
                self.rut_entry.insert(0, empresa.get('rut', ''))
                self.direccion_entry.insert(0, empresa.get('direccion', ''))
                self.telefono_entry.insert(0, empresa.get('telefono', ''))
                self.email_entry.insert(0, empresa.get('email', ''))
            else:
                # Si no existe empresa, permitir creación
                self.show_message(
                    "Información", 
                    "No se encontró información de la empresa. Complete los datos para crear el registro.",
                    "info"
                )
                
        except Exception as e:
            logger.error(f"Error cargando datos de empresa: {e}")
            self.show_message("Error", "No se pudieron cargar los datos de la empresa", "error")
    
    def _guardar_empresa(self):
        """Guardar información de la empresa"""
        try:
            # Obtener datos del formulario
            datos = {
                'nombre': self.nombre_entry.get().strip(),
                'rut': self.rut_entry.get().strip(),
                'direccion': self.direccion_entry.get().strip(),
                'telefono': self.telefono_entry.get().strip(),
                'email': self.email_entry.get().strip()
            }
            
            # Validar campos requeridos
            if not datos['nombre'] or not datos['rut']:
                self.show_message("Error", "Nombre y RUT son campos obligatorios", "error")
                return
            
            # Obtener empresa existente
            empresa_existente = EmpresaService.obtener_empresa()
            
            if empresa_existente:
                # Actualizar empresa existente
                EmpresaService.actualizar_empresa(empresa_existente['id'], **datos)
                self.show_message("Éxito", "Información de la empresa actualizada correctamente", "info")
            else:
                # Crear nueva empresa
                EmpresaService.crear_empresa(**datos)
                self.show_message("Éxito", "Información de la empresa creada correctamente", "info")
                
        except ValidationError as e:
            self.show_message("Error de Validación", str(e), "error")
        except DatabaseError as e:
            logger.error(f"Error guardando empresa: {e}")
            self.show_message("Error", "No se pudo guardar la información de la empresa", "error")
        except Exception as e:
            logger.error(f"Error inesperado guardando empresa: {e}")
            self.show_message("Error", "Ocurrió un error inesperado", "error")
    
    def _cancelar(self):
        """Cancelar y recargar datos originales"""
        # Limpiar formulario
        for entry in [self.nombre_entry, self.rut_entry, self.direccion_entry, 
                     self.telefono_entry, self.email_entry]:
            entry.delete(0, tk.END)
        
        # Recargar datos
        self._load_empresa_data()
        self.show_message("Información", "Cambios cancelados", "info")
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        # Verificar permisos de administrador (usar AuthService cuando no hay controller)
        from core.auth import AuthService
        user = AuthService.get_current_user()
        if not user or user.rol != 'admin':
            self.show_message("Acceso Denegado", "Se requieren permisos de administrador", "error")
            from app.router import router
            router.navigate_to('dashboard')