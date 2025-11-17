import tkinter as tk
from tkinter import ttk
from datetime import datetime
from app.base_view import BaseView
from services.venta_service import VentaService
from services.producto_service import ProductoService
from core.auth import AuthService
from core.exceptions import DatabaseError, ValidationError, InsufficientStockError
from core.logger import logger
from core.utils import utils
from models.venta import Venta, DetalleVenta
from ui.components.table import CustomTable
from ui.components.modal import InputModal

class VentaView(BaseView):
    """Vista de registro de ventas"""
    
    def _setup_view(self):
        """Configurar vista de ventas"""
        # Título
        self.create_title("💰 Registro de Ventas", 0, 0, columnspan=2)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Crear paneles
        self._create_form_panel(main_frame)
        self._create_details_panel(main_frame)
        
        # Inicializar venta
        self.venta_actual = Venta()
        self.venta_actual.usuario_id = AuthService.get_current_user().id if AuthService.get_current_user() else 1
        
        # Cargar productos
        self._load_productos()
    
    def _create_form_panel(self, parent):
        """Crear panel de formulario"""
        form_frame = ttk.LabelFrame(parent, text="Datos de la Venta", padding=10)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        form_frame.columnconfigure(1, weight=1)
        
        # Información del cliente
        ttk.Label(form_frame, text="Cliente:", style="Normal.TLabel").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.cliente_entry = ttk.Entry(form_frame, width=30)
        self.cliente_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(5, 0))
        self.cliente_entry.insert(0, "Consumidor Final")
        
        ttk.Label(form_frame, text="RUT Cliente:", style="Normal.TLabel").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.rut_entry = ttk.Entry(form_frame, width=30)
        self.rut_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(5, 0))
        
        # Separador
        separator = ttk.Separator(form_frame, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Búsqueda de productos
        ttk.Label(form_frame, text="Buscar Producto:", style="Normal.TLabel").grid(
            row=3, column=0, sticky="w", pady=5
        )
        
        search_frame = ttk.Frame(form_frame)
        search_frame.grid(row=3, column=1, sticky="ew", pady=5, padx=(5, 0))
        search_frame.columnconfigure(0, weight=1)
        
        self.producto_search_var = tk.StringVar()
        self.producto_search = ttk.Entry(
            search_frame,
            textvariable=self.producto_search_var
        )
        self.producto_search.grid(row=0, column=0, sticky="ew")
        self.producto_search.bind("<KeyRelease>", self._buscar_productos)
        
        # Lista de productos
        ttk.Label(form_frame, text="Productos:", style="Normal.TLabel").grid(
            row=4, column=0, sticky="w", pady=5
        )
        
        self.productos_listbox = tk.Listbox(form_frame, height=8)
        self.productos_listbox.grid(row=4, column=1, sticky="nsew", pady=5, padx=(5, 0))
        self.productos_listbox.bind("<<ListboxSelect>>", self._seleccionar_producto)
        
        # Scrollbar para lista de productos
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=self.productos_listbox.yview)
        scrollbar.grid(row=4, column=2, sticky="ns", pady=5)
        self.productos_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Información del producto seleccionado
        info_frame = ttk.Frame(form_frame)
        info_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=5)
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Producto:", style="Normal.TLabel").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.producto_info = ttk.Label(info_frame, text="Seleccione un producto", style="Normal.TLabel")
        self.producto_info.grid(row=0, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text="Precio:", style="Normal.TLabel").grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.precio_info = ttk.Label(info_frame, text="$0", style="Normal.TLabel")
        self.precio_info.grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(info_frame, text="Stock:", style="Normal.TLabel").grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.stock_info = ttk.Label(info_frame, text="0", style="Normal.TLabel")
        self.stock_info.grid(row=2, column=1, sticky="w", pady=2)
        
        # Cantidad
        ttk.Label(info_frame, text="Cantidad:", style="Normal.TLabel").grid(
            row=3, column=0, sticky="w", pady=2
        )
        self.cantidad_var = tk.StringVar(value="1")
        self.cantidad_entry = ttk.Entry(
            info_frame,
            textvariable=self.cantidad_var,
            width=10
        )
        self.cantidad_entry.grid(row=3, column=1, sticky="w", pady=2)
        
        # Botones de producto
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Button(
            button_frame,
            text="➕ Agregar Producto",
            command=self._agregar_producto,
            style="Success.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame,
            text="🔄 Limpiar",
            command=self._limpiar_seleccion,
            style="Secondary.TButton"
        ).pack(side="left", padx=2)
        
        # Configurar pesos
        form_frame.rowconfigure(4, weight=1)
    
    def _create_details_panel(self, parent):
        """Crear panel de detalles de venta"""
        details_frame = ttk.LabelFrame(parent, text="Detalles de la Venta", padding=10)
        details_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        
        # Tabla de detalles
        columns = [
            {'id': 'producto', 'text': 'Producto', 'width': 200},
            {'id': 'cantidad', 'text': 'Cantidad', 'width': 80},
            {'id': 'precio', 'text': 'Precio Unit.', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'total', 'text': 'Total', 'width': 100, 'formatter': utils.format_currency}
        ]
        
        self.detalles_table = CustomTable(
            details_frame,
            columns=columns,
            height=12,
            show_toolbar=False
        )
        self.detalles_table.grid(row=1, column=0, sticky="nsew")
        
        # Totales
        totals_frame = ttk.Frame(details_frame)
        totals_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Label(totals_frame, text="Subtotal:", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.subtotal_label = ttk.Label(totals_frame, text="$0", style="Subtitle.TLabel")
        self.subtotal_label.grid(row=0, column=1, sticky="e")
        
        ttk.Label(totals_frame, text="IVA (19%):", style="Normal.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        self.iva_label = ttk.Label(totals_frame, text="$0", style="Normal.TLabel")
        self.iva_label.grid(row=1, column=1, sticky="e")
        
        ttk.Label(totals_frame, text="TOTAL:", style="Title.TLabel").grid(
            row=2, column=0, sticky="w"
        )
        self.total_label = ttk.Label(totals_frame, text="$0", style="Title.TLabel")
        self.total_label.grid(row=2, column=1, sticky="e")
        
        totals_frame.columnconfigure(1, weight=1)
        
        # Botones de acción
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            action_frame,
            text="🗑️ Eliminar Producto",
            command=self._eliminar_producto,
            style="Danger.TButton"
        ).pack(side="left", padx=2)
        
        ttk.Button(
            action_frame,
            text="💾 Guardar Venta",
            command=self._guardar_venta,
            style="Primary.TButton"
        ).pack(side="right", padx=2)
        
        ttk.Button(
            action_frame,
            text="🔄 Nueva Venta",
            command=self._nueva_venta,
            style="Secondary.TButton"
        ).pack(side="right", padx=2)
    
    def _load_productos(self):
        """Cargar lista de productos"""
        try:
            self.productos = ProductoService.obtener_todos()
            self.productos_filtrados = self.productos.copy()
            self._actualizar_lista_productos()
        except Exception as e:
            logger.error(f"Error cargando productos: {e}")
            self.show_message("Error", "No se pudieron cargar los productos", "error")
    
    def _actualizar_lista_productos(self):
        """Actualizar lista de productos"""
        self.productos_listbox.delete(0, tk.END)
        for producto in self.productos_filtrados:
            self.productos_listbox.insert(tk.END, f"{producto.codigo} - {producto.nombre}")
    
    def _buscar_productos(self, event=None):
        """Buscar productos por nombre o código"""
        search_term = self.producto_search_var.get().lower().strip()
        
        if not search_term:
            self.productos_filtrados = self.productos.copy()
        else:
            self.productos_filtrados = [
                p for p in self.productos 
                if search_term in p.nombre.lower() or search_term in p.codigo.lower()
            ]
        
        self._actualizar_lista_productos()
        self._limpiar_seleccion()
    
    def _seleccionar_producto(self, event):
        """Seleccionar producto de la lista"""
        selection = self.productos_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.productos_filtrados):
                self.producto_seleccionado = self.productos_filtrados[index]
                self._mostrar_info_producto()
    
    def _mostrar_info_producto(self):
        """Mostrar información del producto seleccionado"""
        if self.producto_seleccionado:
            self.producto_info.config(text=self.producto_seleccionado.nombre)
            self.precio_info.config(text=utils.format_currency(self.producto_seleccionado.precio_venta))
            self.stock_info.config(text=str(self.producto_seleccionado.stock_actual))
            
            # Establecer cantidad máxima disponible
            self.cantidad_entry.config(state="normal")
        else:
            self._limpiar_seleccion()
    
    def _limpiar_seleccion(self):
        """Limpiar selección de producto"""
        self.producto_seleccionado = None
        self.producto_info.config(text="Seleccione un producto")
        self.precio_info.config(text="$0")
        self.stock_info.config(text="0")
        self.cantidad_var.set("1")
        self.cantidad_entry.config(state="normal")
    
    def _agregar_producto(self):
        """Agregar producto a la venta"""
        if not self.producto_seleccionado:
            self.show_message("Advertencia", "Seleccione un producto primero", "warning")
            return
        
        try:
            cantidad = int(self.cantidad_var.get())
            if cantidad <= 0:
                self.show_message("Error", "La cantidad debe ser mayor a 0", "error")
                return
            
            # Verificar stock
            if self.producto_seleccionado.stock_actual < cantidad:
                self.show_message(
                    "Stock Insuficiente", 
                    f"Stock disponible: {self.producto_seleccionado.stock_actual}", 
                    "error"
                )
                return
            
            # Crear detalle
            detalle = DetalleVenta(
                producto_id=self.producto_seleccionado.id,
                cantidad=cantidad,
                precio_unitario=self.producto_seleccionado.precio_venta
            )
            detalle.calcular_total()
            
            # Verificar si el producto ya está en la venta
            for det in self.venta_actual.detalles:
                if det.producto_id == self.producto_seleccionado.id:
                    # Actualizar cantidad
                    det.cantidad += cantidad
                    det.calcular_total()
                    break
            else:
                # Agregar nuevo detalle
                self.venta_actual.agregar_detalle(detalle)
            
            # Actualizar interfaz
            self._actualizar_detalles_tabla()
            self._actualizar_totales()
            self._limpiar_seleccion()
            
        except ValueError:
            self.show_message("Error", "La cantidad debe ser un número válido", "error")
        except Exception as e:
            logger.error(f"Error agregando producto: {e}")
            self.show_message("Error", "No se pudo agregar el producto", "error")
    
    def _actualizar_detalles_tabla(self):
        """Actualizar tabla de detalles"""
        # Limpiar tabla
        for item in self.detalles_table.tree.get_children():
            self.detalles_table.tree.delete(item)
        
        # Agregar detalles
        for detalle in self.venta_actual.detalles:
            producto = next((p for p in self.productos if p.id == detalle.producto_id), None)
            if producto:
                self.detalles_table.tree.insert("", "end", values=(
                    producto.nombre,
                    detalle.cantidad,
                    detalle.precio_unitario,
                    detalle.total_linea
                ))
    
    def _actualizar_totales(self):
        """Actualizar totales de la venta"""
        self.venta_actual.calcular_totales()
        
        self.subtotal_label.config(text=utils.format_currency(self.venta_actual.subtotal))
        self.iva_label.config(text=utils.format_currency(self.venta_actual.iva))
        self.total_label.config(text=utils.format_currency(self.venta_actual.total))
    
    def _eliminar_producto(self):
        """Eliminar producto seleccionado de la venta"""
        selected = self.detalles_table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione un producto para eliminar", "warning")
            return
        
        # Encontrar índice del producto
        producto_nombre = selected['producto']
        for i, detalle in enumerate(self.venta_actual.detalles):
            producto = next((p for p in self.productos if p.id == detalle.producto_id), None)
            if producto and producto.nombre == producto_nombre:
                self.venta_actual.detalles.pop(i)
                break
        
        self._actualizar_detalles_tabla()
        self._actualizar_totales()
    
    def _guardar_venta(self):
        """Guardar la venta"""
        if not self.venta_actual.detalles:
            self.show_message("Advertencia", "Agregue al menos un producto a la venta", "warning")
            return
        
        try:
            # Establecer datos del cliente
            self.venta_actual.cliente_nombre = self.cliente_entry.get().strip()
            self.venta_actual.cliente_rut = self.rut_entry.get().strip()
            self.venta_actual.fecha = datetime.now()
            
            # Guardar venta
            venta_id = VentaService.crear_venta(self.venta_actual)
            
            self.show_message(
                "Éxito", 
                f"Venta registrada correctamente\nN° Boleta: {self.venta_actual.numero_boleta}", 
                "info"
            )
            
            # Limpiar para nueva venta
            self._nueva_venta()
            
        except (ValidationError, InsufficientStockError) as e:
            self.show_message("Error de Validación", str(e), "error")
        except Exception as e:
            logger.error(f"Error guardando venta: {e}")
            self.show_message("Error", "No se pudo guardar la venta", "error")
    
    def _nueva_venta(self):
        """Iniciar nueva venta"""
        self.venta_actual = Venta()
        self.venta_actual.usuario_id = AuthService.get_current_user().id if AuthService.get_current_user() else 1
        
        self.cliente_entry.delete(0, tk.END)
        self.cliente_entry.insert(0, "Consumidor Final")
        self.rut_entry.delete(0, tk.END)
        
        self._limpiar_seleccion()
        self._actualizar_detalles_tabla()
        self._actualizar_totales()
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        self._nueva_venta()