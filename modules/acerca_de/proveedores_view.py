import tkinter as tk
from tkinter import ttk
from app.base_view import BaseView
from services.proveedor_service import ProveedorService
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from core.utils import utils
from ui.components.table import CustomTable
from ui.components.modal import InputModal

class ProveedoresView(BaseView):
    """Vista de gestión de proveedores"""
    
    def _setup_view(self):
        """Configurar vista de proveedores"""
        # Título
        self.create_title("🚚 Gestión de Proveedores", 0, 0, columnspan=2)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Toolbar
        self._create_toolbar(main_frame)
        
        # Tabla de proveedores
        self._create_proveedores_table(main_frame)
        
        # Cargar datos
        self._load_proveedores()
    
    def _create_toolbar(self, parent):
        """Crear barra de herramientas"""
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Botones principales
        ttk.Button(
            toolbar,
            text="➕ Nuevo Proveedor",
            command=self._nuevo_proveedor,
            style="Primary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="✏️ Editar",
            command=self._editar_proveedor,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="👁️ Ver Detalles",
            command=self._ver_detalles,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="🗑️ Desactivar",
            command=self._desactivar_proveedor,
            style="Danger.TButton"
        ).pack(side="left", padx=2)
        
        # Búsqueda
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side="right", padx=2)
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=2)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=20
        )
        search_entry.pack(side="left", padx=2)
        search_entry.bind("<KeyRelease>", self._buscar_proveedores)
        
        ttk.Button(
            search_frame,
            text="❌",
            command=self._limpiar_busqueda,
            width=3
        ).pack(side="left", padx=2)
    
    def _create_proveedores_table(self, parent):
        """Crear tabla de proveedores"""
        columns = [
            {'id': 'id', 'text': 'ID', 'width': 60},
            {'id': 'rut', 'text': 'RUT', 'width': 120},
            {'id': 'nombre', 'text': 'Nombre', 'width': 200},
            {'id': 'telefono', 'text': 'Teléfono', 'width': 120},
            {'id': 'email', 'text': 'Email', 'width': 200},
            {'id': 'producto_principal', 'text': 'Producto Principal', 'width': 150},
            {'id': 'activo', 'text': 'Estado', 'width': 80}
        ]
        
        self.table = CustomTable(
            parent,
            columns=columns,
            height=20,
            show_toolbar=False
        )
        self.table.grid(row=1, column=0, sticky="nsew")
        
        # Configurar menú contextual
        menu_items = [
            {'label': 'Ver Detalles', 'command': self._ver_detalles},
            {'label': 'Editar', 'command': self._editar_proveedor},
            {'separator': True},
            {'label': 'Desactivar', 'command': self._desactivar_proveedor}
        ]
        self.table.add_context_menu(menu_items)
    
    def _load_proveedores(self):
        """Cargar proveedores en la tabla"""
        try:
            self.proveedores = ProveedorService.obtener_todos(activos_only=False)
            
            # Preparar datos para la tabla
            table_data = []
            for proveedor in self.proveedores:
                table_data.append({
                    'id': proveedor.id,
                    'rut': utils.format_rut(proveedor.rut),
                    'nombre': proveedor.nombre,
                    'telefono': proveedor.telefono,
                    'email': proveedor.email,
                    'producto_principal': proveedor.producto_principal,
                    'activo': 'Activo' if proveedor.activo else 'Inactivo',
                    '_tags': 'success' if proveedor.activo else 'danger'
                })
            
            self.table.load_data(table_data)
            
        except Exception as e:
            logger.error(f"Error cargando proveedores: {e}")
            self.show_message("Error", "No se pudieron cargar los proveedores", "error")
    
    def _nuevo_proveedor(self):
        """Abrir modal para nuevo proveedor"""
        fields = [
            {
                'name': 'nombre',
                'label': 'Nombre *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'rut',
                'label': 'RUT *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'direccion',
                'label': 'Dirección',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'telefono',
                'label': 'Teléfono',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'email',
                'label': 'Email',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'producto_principal',
                'label': 'Producto Principal',
                'type': 'entry',
                'required': False
            }
        ]
        
        modal = InputModal(self, "Nuevo Proveedor", fields)
        result = modal.show()
        
        if result:
            self._guardar_nuevo_proveedor(result)
    
    def _guardar_nuevo_proveedor(self, datos):
        """Guardar nuevo proveedor"""
        try:
            from models.proveedor import Proveedor
            
            # Crear objeto proveedor
            proveedor = Proveedor(
                nombre=datos['nombre'],
                rut=datos['rut'],
                direccion=datos.get('direccion', ''),
                telefono=datos.get('telefono', ''),
                email=datos.get('email', ''),
                producto_principal=datos.get('producto_principal', ''),
                activo=True
            )
            
            # Guardar en base de datos
            ProveedorService.crear_proveedor(proveedor)
            
            self.show_message("Éxito", "Proveedor creado correctamente", "info")
            self._load_proveedores()
            
        except ValidationError as e:
            self.show_message("Error de Validación", str(e), "error")
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            self.show_message("Error", "No se pudo crear el proveedor", "error")
    
    def _editar_proveedor(self):
        """Editar proveedor seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un proveedor para editar", "warning")
            return
        
        # Buscar proveedor completo
        proveedor_id = selected['id']
        proveedor = next((p for p in self.proveedores if p.id == proveedor_id), None)
        
        if not proveedor:
            self.show_message("Error", "Proveedor no encontrado", "error")
            return
        
        fields = [
            {
                'name': 'nombre',
                'label': 'Nombre *',
                'type': 'entry',
                'required': True,
                'value': proveedor.nombre
            },
            {
                'name': 'rut',
                'label': 'RUT *',
                'type': 'entry',
                'required': True,
                'value': proveedor.rut
            },
            {
                'name': 'direccion',
                'label': 'Dirección',
                'type': 'entry',
                'required': False,
                'value': proveedor.direccion
            },
            {
                'name': 'telefono',
                'label': 'Teléfono',
                'type': 'entry',
                'required': False,
                'value': proveedor.telefono
            },
            {
                'name': 'email',
                'label': 'Email',
                'type': 'entry',
                'required': False,
                'value': proveedor.email
            },
            {
                'name': 'producto_principal',
                'label': 'Producto Principal',
                'type': 'entry',
                'required': False,
                'value': proveedor.producto_principal
            }
        ]
        
        modal = InputModal(self, f"Editar Proveedor: {proveedor.nombre}", fields)
        result = modal.show()
        
        if result:
            self._actualizar_proveedor(proveedor_id, result)
    
    def _actualizar_proveedor(self, proveedor_id, datos):
        """Actualizar proveedor"""
        try:
            # Actualizar en base de datos
            ProveedorService.actualizar_proveedor(proveedor_id, **datos)
            
            self.show_message("Éxito", "Proveedor actualizado correctamente", "info")
            self._load_proveedores()
            
        except Exception as e:
            logger.error(f"Error actualizando proveedor: {e}")
            self.show_message("Error", "No se pudo actualizar el proveedor", "error")
    
    def _ver_detalles(self):
        """Ver detalles del proveedor seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un proveedor para ver detalles", "warning")
            return
        
        # Buscar proveedor completo
        proveedor_id = selected['id']
        proveedor = next((p for p in self.proveedores if p.id == proveedor_id), None)
        
        if not proveedor:
            self.show_message("Error", "Proveedor no encontrado", "error")
            return
        
        # Mostrar detalles en un mensaje
        detalles = f"""
        📋 Detalles del Proveedor
        
        🆔 ID: {proveedor.id}
        🏷️ RUT: {utils.format_rut(proveedor.rut)}
        🏢 Nombre: {proveedor.nombre}
        📍 Dirección: {proveedor.direccion or 'No especificada'}
        📞 Teléfono: {proveedor.telefono or 'No especificado'}
        📧 Email: {proveedor.email or 'No especificado'}
        📦 Producto Principal: {proveedor.producto_principal or 'No especificado'}
        🟢 Estado: {'Activo' if proveedor.activo else 'Inactivo'}
        """
        
        self.show_message(f"Detalles: {proveedor.nombre}", detalles.strip(), "info")
    
    def _desactivar_proveedor(self):
        """Desactivar proveedor seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un proveedor para desactivar", "warning")
            return
        
        proveedor_id = selected['id']
        nombre = selected['nombre']
        
        if not self.show_message(
            "Confirmar Desactivación",
            f"¿Está seguro que desea desactivar al proveedor {nombre}?",
            "question"
        ):
            return
        
        try:
            ProveedorService.desactivar_proveedor(proveedor_id)
            self.show_message("Éxito", "Proveedor desactivado correctamente", "info")
            self._load_proveedores()
            
        except Exception as e:
            logger.error(f"Error desactivando proveedor: {e}")
            self.show_message("Error", "No se pudo desactivar el proveedor", "error")
    
    def _buscar_proveedores(self, event=None):
        """Buscar proveedores por nombre"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            self._load_proveedores()
            return
        
        try:
            resultados = ProveedorService.buscar_por_nombre(search_term)
            
            # Preparar datos para la tabla
            table_data = []
            for proveedor in resultados:
                table_data.append({
                    'id': proveedor.id,
                    'rut': utils.format_rut(proveedor.rut),
                    'nombre': proveedor.nombre,
                    'telefono': proveedor.telefono,
                    'email': proveedor.email,
                    'producto_principal': proveedor.producto_principal,
                    'activo': 'Activo' if proveedor.activo else 'Inactivo',
                    '_tags': 'success' if proveedor.activo else 'danger'
                })
            
            self.table.load_data(table_data)
            
        except Exception as e:
            logger.error(f"Error buscando proveedores: {e}")
    
    def _limpiar_busqueda(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self._load_proveedores()
    
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