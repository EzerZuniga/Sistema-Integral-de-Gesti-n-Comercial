import tkinter as tk
from tkinter import ttk
from app.base_view import BaseView
from services.producto_service import ProductoService
from services.inventario_service import InventarioService
from core.auth import AuthService
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from core.utils import utils
from ui.components.table import CustomTable
from ui.components.modal import InputModal

class StockView(BaseView):
    """Vista de control de stock"""
    
    def _setup_view(self):
        """Configurar vista de stock"""
        # Título
        self.create_title("📦 Control de Stock", 0, 0, columnspan=2)
        
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
        
        # Tabla de productos
        self._create_productos_table(main_frame)
        
        # Cargar datos
        self._load_productos()
    
    def _create_toolbar(self, parent):
        """Crear barra de herramientas"""
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Botones principales
        ttk.Button(
            toolbar,
            text="➕ Nuevo Producto",
            command=self._nuevo_producto,
            style="Primary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="✏️ Editar",
            command=self._editar_producto,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="📊 Ajustar Stock",
            command=self._ajustar_stock,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="📋 Movimientos",
            command=self._ver_movimientos,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            toolbar,
            text="🗑️ Desactivar",
            command=self._desactivar_producto,
            style="Danger.TButton"
        ).pack(side="left", padx=2)
        
        # Filtros
        filter_frame = ttk.Frame(toolbar)
        filter_frame.pack(side="right", padx=2)
        
        ttk.Label(filter_frame, text="Filtrar:").pack(side="left", padx=2)
        
        self.filter_var = tk.StringVar(value="todos")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["Todos", "Activos", "Inactivos", "Stock Bajo", "Sin Stock"],
            state="readonly",
            width=12
        )
        filter_combo.pack(side="left", padx=2)
        filter_combo.bind("<<ComboboxSelected>>", self._aplicar_filtro)
        
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
        search_entry.bind("<KeyRelease>", self._buscar_productos)
    
    def _create_productos_table(self, parent):
        """Crear tabla de productos"""
        columns = [
            {'id': 'id', 'text': 'ID', 'width': 60},
            {'id': 'codigo', 'text': 'Código', 'width': 120},
            {'id': 'nombre', 'text': 'Nombre', 'width': 200},
            {'id': 'categoria', 'text': 'Categoría', 'width': 120},
            {'id': 'precio_compra', 'text': 'P. Compra', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'precio_venta', 'text': 'P. Venta', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'stock_actual', 'text': 'Stock Actual', 'width': 100},
            {'id': 'stock_minimo', 'text': 'Stock Mínimo', 'width': 100},
            {'id': 'stock_maximo', 'text': 'Stock Máximo', 'width': 100},
            {'id': 'estado', 'text': 'Estado', 'width': 80}
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
            {'label': 'Editar', 'command': self._editar_producto},
            {'label': 'Ajustar Stock', 'command': self._ajustar_stock},
            {'label': 'Ver Movimientos', 'command': self._ver_movimientos},
            {'separator': True},
            {'label': 'Desactivar', 'command': self._desactivar_producto}
        ]
        self.table.add_context_menu(menu_items)
    
    def _load_productos(self):
        """Cargar productos en la tabla"""
        try:
            self.productos = ProductoService.obtener_todos(activos_only=False)
            self.productos_filtrados = self.productos.copy()
            self._actualizar_tabla()
            
        except Exception as e:
            logger.error(f"Error cargando productos: {e}")
            self.show_message("Error", "No se pudieron cargar los productos", "error")
    
    def _actualizar_tabla(self):
        """Actualizar tabla con productos filtrados"""
        table_data = []
        for producto in self.productos_filtrados:
            # Determinar estado del stock
            estado = "NORMAL"
            tags = "success"
            
            if producto.stock_actual <= 0:
                estado = "SIN STOCK"
                tags = "danger"
            elif producto.stock_actual <= producto.stock_minimo:
                estado = "BAJO"
                tags = "warning"
            elif producto.stock_actual > producto.stock_maximo:
                estado = "EXCESO"
                tags = "info"
            
            if not producto.activo:
                estado = "INACTIVO"
                tags = "danger"
            
            table_data.append({
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'categoria': producto.categoria,
                'precio_compra': producto.precio_compra,
                'precio_venta': producto.precio_venta,
                'stock_actual': producto.stock_actual,
                'stock_minimo': producto.stock_minimo,
                'stock_maximo': producto.stock_maximo,
                'estado': estado,
                '_tags': tags
            })
        
        self.table.load_data(table_data)
    
    def _nuevo_producto(self):
        """Abrir modal para nuevo producto"""
        from services.proveedor_service import ProveedorService
        
        try:
            proveedores = ProveedorService.obtener_todos()
            proveedores_values = [f"{p.nombre} ({p.id})" for p in proveedores]
        except:
            proveedores_values = []
        
        fields = [
            {
                'name': 'codigo',
                'label': 'Código *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'nombre',
                'label': 'Nombre *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'descripcion',
                'label': 'Descripción',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'categoria',
                'label': 'Categoría *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'precio_compra',
                'label': 'Precio Compra *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'precio_venta',
                'label': 'Precio Venta *',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'stock_minimo',
                'label': 'Stock Mínimo',
                'type': 'entry',
                'required': False,
                'value': '10'
            },
            {
                'name': 'stock_maximo',
                'label': 'Stock Máximo',
                'type': 'entry',
                'required': False,
                'value': '100'
            },
            {
                'name': 'proveedor',
                'label': 'Proveedor',
                'type': 'combobox',
                'values': proveedores_values,
                'required': False
            }
        ]
        
        modal = InputModal(self, "Nuevo Producto", fields)
        result = modal.show()
        
        if result:
            self._guardar_nuevo_producto(result)
    
    def _guardar_nuevo_producto(self, datos):
        """Guardar nuevo producto"""
        try:
            from models.producto import Producto
            
            # Parsear proveedor_id
            proveedor_id = None
            if datos['proveedor']:
                try:
                    # Extraer ID del proveedor del texto seleccionado
                    proveedor_id = int(datos['proveedor'].split('(')[-1].rstrip(')'))
                except:
                    pass
            
            # Crear objeto producto
            producto = Producto(
                codigo=datos['codigo'],
                nombre=datos['nombre'],
                descripcion=datos.get('descripcion', ''),
                categoria=datos['categoria'],
                precio_compra=float(datos['precio_compra']),
                precio_venta=float(datos['precio_venta']),
                stock_actual=0,
                stock_minimo=int(datos.get('stock_minimo', 10)),
                stock_maximo=int(datos.get('stock_maximo', 100)),
                proveedor_id=proveedor_id,
                activo=True
            )
            
            # Guardar en base de datos
            ProductoService.crear_producto(producto)
            
            self.show_message("Éxito", "Producto creado correctamente", "info")
            self._load_productos()
            
        except ValidationError as e:
            self.show_message("Error de Validación", str(e), "error")
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            self.show_message("Error", "No se pudo crear el producto", "error")
    
    def _editar_producto(self):
        """Editar producto seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un producto para editar", "warning")
            return
        
        # Buscar producto completo
        producto_id = selected['id']
        producto = next((p for p in self.productos if p.id == producto_id), None)
        
        if not producto:
            self.show_message("Error", "Producto no encontrado", "error")
            return
        
        from services.proveedor_service import ProveedorService
        
        try:
            proveedores = ProveedorService.obtener_todos()
            proveedores_values = [f"{p.nombre} ({p.id})" for p in proveedores]
            proveedor_actual = f"{next((p.nombre for p in proveedores if p.id == producto.proveedor_id), '')} ({producto.proveedor_id})" if producto.proveedor_id else ""
        except:
            proveedores_values = []
            proveedor_actual = ""
        
        fields = [
            {
                'name': 'codigo',
                'label': 'Código *',
                'type': 'entry',
                'required': True,
                'value': producto.codigo
            },
            {
                'name': 'nombre',
                'label': 'Nombre *',
                'type': 'entry',
                'required': True,
                'value': producto.nombre
            },
            {
                'name': 'descripcion',
                'label': 'Descripción',
                'type': 'entry',
                'required': False,
                'value': producto.descripcion or ''
            },
            {
                'name': 'categoria',
                'label': 'Categoría *',
                'type': 'entry',
                'required': True,
                'value': producto.categoria
            },
            {
                'name': 'precio_compra',
                'label': 'Precio Compra *',
                'type': 'entry',
                'required': True,
                'value': str(producto.precio_compra)
            },
            {
                'name': 'precio_venta',
                'label': 'Precio Venta *',
                'type': 'entry',
                'required': True,
                'value': str(producto.precio_venta)
            },
            {
                'name': 'stock_minimo',
                'label': 'Stock Mínimo',
                'type': 'entry',
                'required': False,
                'value': str(producto.stock_minimo)
            },
            {
                'name': 'stock_maximo',
                'label': 'Stock Máximo',
                'type': 'entry',
                'required': False,
                'value': str(producto.stock_maximo)
            },
            {
                'name': 'proveedor',
                'label': 'Proveedor',
                'type': 'combobox',
                'values': proveedores_values,
                'required': False,
                'value': proveedor_actual
            }
        ]
        
        modal = InputModal(self, f"Editar Producto: {producto.nombre}", fields)
        result = modal.show()
        
        if result:
            self._actualizar_producto(producto_id, result)
    
    def _actualizar_producto(self, producto_id, datos):
        """Actualizar producto"""
        try:
            # Parsear datos
            update_data = {}
            
            for field in ['codigo', 'nombre', 'descripcion', 'categoria']:
                if field in datos:
                    update_data[field] = datos[field]
            
            for field in ['precio_compra', 'precio_venta']:
                if field in datos and datos[field]:
                    update_data[field] = float(datos[field])
            
            for field in ['stock_minimo', 'stock_maximo']:
                if field in datos and datos[field]:
                    update_data[field] = int(datos[field])
            
            # Parsear proveedor_id
            if 'proveedor' in datos and datos['proveedor']:
                try:
                    update_data['proveedor_id'] = int(datos['proveedor'].split('(')[-1].rstrip(')'))
                except:
                    pass
            
            # Actualizar en base de datos
            ProductoService.actualizar_producto(producto_id, **update_data)
            
            self.show_message("Éxito", "Producto actualizado correctamente", "info")
            self._load_productos()
            
        except Exception as e:
            logger.error(f"Error actualizando producto: {e}")
            self.show_message("Error", "No se pudo actualizar el producto", "error")
    
    def _ajustar_stock(self):
        """Ajustar stock del producto seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un producto para ajustar stock", "warning")
            return
        
        producto_id = selected['id']
        producto = next((p for p in self.productos if p.id == producto_id), None)
        
        if not producto:
            self.show_message("Error", "Producto no encontrado", "error")
            return
        
        fields = [
            {
                'name': 'nuevo_stock',
                'label': 'Nuevo Stock *',
                'type': 'entry',
                'required': True,
                'value': str(producto.stock_actual)
            },
            {
                'name': 'motivo',
                'label': 'Motivo del Ajuste *',
                'type': 'entry',
                'required': True,
                'value': 'Ajuste manual de inventario'
            }
        ]
        
        modal = InputModal(self, f"Ajustar Stock: {producto.nombre}", fields)
        result = modal.show()
        
        if result:
            self._aplicar_ajuste_stock(producto_id, result)
    
    def _aplicar_ajuste_stock(self, producto_id, datos):
        """Aplicar ajuste de stock"""
        try:
            nuevo_stock = int(datos['nuevo_stock'])
            motivo = datos['motivo']
            
            if nuevo_stock < 0:
                self.show_message("Error", "El stock no puede ser negativo", "error")
                return
            
            # Obtener usuario actual
            usuario_id = AuthService.get_current_user().id if AuthService.get_current_user() else 1
            
            # Aplicar ajuste
            InventarioService.ajustar_stock(producto_id, nuevo_stock, motivo, usuario_id)
            
            self.show_message("Éxito", "Stock ajustado correctamente", "info")
            self._load_productos()
            
        except ValueError:
            self.show_message("Error", "El stock debe ser un número válido", "error")
        except Exception as e:
            logger.error(f"Error ajustando stock: {e}")
            self.show_message("Error", "No se pudo ajustar el stock", "error")
    
    def _ver_movimientos(self):
        """Ver movimientos del producto seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un producto para ver movimientos", "warning")
            return
        
        producto_id = selected['id']
        producto = next((p for p in self.productos if p.id == producto_id), None)
        
        if not producto:
            self.show_message("Error", "Producto no encontrado", "error")
            return
        
        try:
            movimientos = InventarioService.obtener_movimientos_por_producto(producto_id, limit=50)
            
            # Crear ventana de movimientos
            self._mostrar_movimientos(producto, movimientos)
            
        except Exception as e:
            logger.error(f"Error cargando movimientos: {e}")
            self.show_message("Error", "No se pudieron cargar los movimientos", "error")
    
    def _mostrar_movimientos(self, producto, movimientos):
        """Mostrar ventana con movimientos del producto"""
        movimientos_window = tk.Toplevel(self)
        movimientos_window.title(f"Movimientos - {producto.nombre}")
        movimientos_window.geometry("800x400")
        movimientos_window.transient(self)
        movimientos_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(movimientos_window, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Información del producto
        info_frame = ttk.LabelFrame(main_frame, text="Información del Producto", padding=5)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Producto: {producto.nombre} ({producto.codigo})", style="Normal.TLabel").pack(anchor="w")
        ttk.Label(info_frame, text=f"Stock actual: {producto.stock_actual}", style="Normal.TLabel").pack(anchor="w")
        
        # Tabla de movimientos
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        columns = [
            {'id': 'fecha', 'text': 'Fecha', 'width': 120},
            {'id': 'tipo', 'text': 'Tipo', 'width': 80},
            {'id': 'cantidad', 'text': 'Cantidad', 'width': 80},
            {'id': 'stock_anterior', 'text': 'Stock Ant.', 'width': 80},
            {'id': 'stock_nuevo', 'text': 'Stock Nuevo', 'width': 80},
            {'id': 'motivo', 'text': 'Motivo', 'width': 200},
            {'id': 'usuario', 'text': 'Usuario', 'width': 100}
        ]
        
        table = CustomTable(table_frame, columns=columns, height=15, show_toolbar=False)
        table.grid(row=0, column=0, sticky="nsew")
        
        # Cargar datos en la tabla
        table_data = []
        for mov in movimientos:
            table_data.append({
                'fecha': mov.created_at.strftime("%d/%m/%Y %H:%M") if mov.created_at else "",
                'tipo': mov.tipo.upper(),
                'cantidad': mov.cantidad,
                'stock_anterior': mov.cantidad_anterior,
                'stock_nuevo': mov.cantidad_nueva,
                'motivo': mov.motivo,
                'usuario': f"Usuario {mov.usuario_id}"
            })
        
        table.load_data(table_data)
    
    def _ver_detalles(self):
        """Ver detalles del producto seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un producto para ver detalles", "warning")
            return
        
        producto_id = selected['id']
        producto = next((p for p in self.productos if p.id == producto_id), None)
        
        if not producto:
            self.show_message("Error", "Producto no encontrado", "error")
            return
        
        # Obtener nombre del proveedor
        proveedor_nombre = "No asignado"
        if producto.proveedor_id:
            try:
                from services.proveedor_service import ProveedorService
                proveedor = ProveedorService.obtener_por_id(producto.proveedor_id)
                if proveedor:
                    proveedor_nombre = proveedor.nombre
            except:
                pass
        
        # Mostrar detalles
        detalles = f"""
        📋 Detalles del Producto
        
        🆔 ID: {producto.id}
        🏷️ Código: {producto.codigo}
        📦 Nombre: {producto.nombre}
        📝 Descripción: {producto.descripcion or 'No especificada'}
        🗂️ Categoría: {producto.categoria}
        💰 Precio Compra: {utils.format_currency(producto.precio_compra)}
        💵 Precio Venta: {utils.format_currency(producto.precio_venta)}
        📊 Stock Actual: {producto.stock_actual}
        📉 Stock Mínimo: {producto.stock_minimo}
        📈 Stock Máximo: {producto.stock_maximo}
        🚚 Proveedor: {proveedor_nombre}
        🟢 Estado: {'Activo' if producto.activo else 'Inactivo'}
        """
        
        self.show_message(f"Detalles: {producto.nombre}", detalles.strip(), "info")
    
    def _desactivar_producto(self):
        """Desactivar producto seleccionado"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un producto para desactivar", "warning")
            return
        
        producto_id = selected['id']
        nombre = selected['nombre']
        
        if not self.show_message(
            "Confirmar Desactivación",
            f"¿Está seguro que desea desactivar el producto {nombre}?",
            "question"
        ):
            return
        
        try:
            ProductoService.actualizar_producto(producto_id, activo=False)
            self.show_message("Éxito", "Producto desactivado correctamente", "info")
            self._load_productos()
            
        except Exception as e:
            logger.error(f"Error desactivando producto: {e}")
            self.show_message("Error", "No se pudo desactivar el producto", "error")
    
    def _buscar_productos(self, event=None):
        """Buscar productos por nombre o código"""
        search_term = self.search_var.get().lower().strip()
        
        if not search_term:
            self.productos_filtrados = self.productos.copy()
        else:
            self.productos_filtrados = [
                p for p in self.productos 
                if search_term in p.nombre.lower() or search_term in p.codigo.lower()
            ]
        
        self._aplicar_filtro()
    
    def _aplicar_filtro(self, event=None):
        """Aplicar filtro seleccionado"""
        filtro = self.filter_var.get()
        
        if filtro == "Todos":
            productos_filtrados = self.productos_filtrados
        elif filtro == "Activos":
            productos_filtrados = [p for p in self.productos_filtrados if p.activo]
        elif filtro == "Inactivos":
            productos_filtrados = [p for p in self.productos_filtrados if not p.activo]
        elif filtro == "Stock Bajo":
            productos_filtrados = [p for p in self.productos_filtrados if p.activo and p.stock_actual <= p.stock_minimo]
        elif filtro == "Sin Stock":
            productos_filtrados = [p for p in self.productos_filtrados if p.activo and p.stock_actual == 0]
        else:
            productos_filtrados = self.productos_filtrados
        
        self.productos_filtrados = productos_filtrados
        self._actualizar_tabla()
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        self._load_productos()