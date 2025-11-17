import tkinter as tk
from tkinter import ttk
from app.base_view import BaseView
from services.producto_service import ProductoService
from services.inventario_service import InventarioService
from core.logger import logger
from core.utils import utils
from ui.components.table import CustomTable

class AlertaStockView(BaseView):
    """Vista de alertas de stock"""
    
    def _setup_view(self):
        """Configurar vista de alertas"""
        # Título
        self.create_title("⚠️ Alertas de Stock", 0, 0, columnspan=2)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # KPIs de alertas
        self._create_alert_kpis(main_frame)
        
        # Tabla de productos con alertas
        self._create_alertas_table(main_frame)
        
        # Cargar datos
        self._load_alertas()
    
    def _create_alert_kpis(self, parent):
        """Crear KPIs de alertas"""
        kpi_frame = ttk.Frame(parent)
        kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        for i in range(3):
            kpi_frame.columnconfigure(i, weight=1)
        
        # KPI Stock Bajo
        bajo_kpi = ttk.LabelFrame(kpi_frame, text="Stock Bajo", padding=10)
        bajo_kpi.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.bajo_count_label = ttk.Label(bajo_kpi, text="0", style="Title.TLabel", foreground="#e74c3c")
        self.bajo_count_label.pack()
        
        ttk.Label(bajo_kpi, text="Productos bajo stock mínimo", style="Normal.TLabel").pack()
        
        # KPI Sin Stock
        sin_kpi = ttk.LabelFrame(kpi_frame, text="Sin Stock", padding=10)
        sin_kpi.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.sin_count_label = ttk.Label(sin_kpi, text="0", style="Title.TLabel", foreground="#c0392b")
        self.sin_count_label.pack()
        
        ttk.Label(sin_kpi, text="Productos sin stock", style="Normal.TLabel").pack()
        
        # KPI Stock Excesivo
        exceso_kpi = ttk.LabelFrame(kpi_frame, text="Stock Excesivo", padding=10)
        exceso_kpi.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self.exceso_count_label = ttk.Label(exceso_kpi, text="0", style="Title.TLabel", foreground="#f39c12")
        self.exceso_count_label.pack()
        
        ttk.Label(exceso_kpi, text="Productos sobre stock máximo", style="Normal.TLabel").pack()
    
    def _create_alertas_table(self, parent):
        """Crear tabla de alertas"""
        columns = [
            {'id': 'codigo', 'text': 'Código', 'width': 120},
            {'id': 'nombre', 'text': 'Nombre', 'width': 200},
            {'id': 'categoria', 'text': 'Categoría', 'width': 120},
            {'id': 'stock_actual', 'text': 'Stock Actual', 'width': 100},
            {'id': 'stock_minimo', 'text': 'Stock Mínimo', 'width': 100},
            {'id': 'stock_maximo', 'text': 'Stock Máximo', 'width': 100},
            {'id': 'diferencia', 'text': 'Diferencia', 'width': 100},
            {'id': 'tipo_alerta', 'text': 'Tipo Alerta', 'width': 120},
            {'id': 'prioridad', 'text': 'Prioridad', 'width': 100}
        ]
        
        self.table = CustomTable(
            parent,
            columns=columns,
            height=20,
            show_toolbar=True
        )
        self.table.grid(row=1, column=0, sticky="nsew")
        
        # Configurar menú contextual
        menu_items = [
            {'label': 'Ver Detalles', 'command': self._ver_detalles},
            {'label': 'Ajustar Stock', 'command': self._ajustar_stock},
            {'label': 'Ver Movimientos', 'command': self._ver_movimientos}
        ]
        self.table.add_context_menu(menu_items)
    
    def _load_alertas(self):
        """Cargar alertas de stock"""
        try:
            # Obtener todos los productos activos
            productos = ProductoService.obtener_todos(activos_only=True)
            
            # Filtrar productos con alertas
            productos_con_alerta = []
            
            for producto in productos:
                alerta = self._evaluar_alerta(producto)
                if alerta:
                    productos_con_alerta.append((producto, alerta))
            
            # Actualizar KPIs
            self._actualizar_kpis(productos_con_alerta)
            
            # Actualizar tabla
            self._actualizar_tabla_alertas(productos_con_alerta)
            
        except Exception as e:
            logger.error(f"Error cargando alertas: {e}")
            self.show_message("Error", "No se pudieron cargar las alertas de stock", "error")
    
    def _evaluar_alerta(self, producto):
        """Evaluar si un producto tiene alerta y de qué tipo"""
        if producto.stock_actual == 0:
            return {
                'tipo': 'SIN_STOCK',
                'prioridad': 'ALTA',
                'diferencia': 0,
                'mensaje': 'Producto sin stock'
            }
        elif producto.stock_actual <= producto.stock_minimo:
            diferencia = producto.stock_minimo - producto.stock_actual
            return {
                'tipo': 'STOCK_BAJO',
                'prioridad': 'MEDIA' if diferencia <= 5 else 'ALTA',
                'diferencia': diferencia,
                'mensaje': f'Stock {diferencia} unidades bajo el mínimo'
            }
        elif producto.stock_actual > producto.stock_maximo:
            diferencia = producto.stock_actual - producto.stock_maximo
            return {
                'tipo': 'STOCK_EXCESIVO',
                'prioridad': 'BAJA',
                'diferencia': diferencia,
                'mensaje': f'Stock {diferencia} unidades sobre el máximo'
            }
        
        return None
    
    def _actualizar_kpis(self, productos_con_alerta):
        """Actualizar KPIs de alertas"""
        bajo_count = sum(1 for _, alerta in productos_con_alerta if alerta['tipo'] == 'STOCK_BAJO')
        sin_count = sum(1 for _, alerta in productos_con_alerta if alerta['tipo'] == 'SIN_STOCK')
        exceso_count = sum(1 for _, alerta in productos_con_alerta if alerta['tipo'] == 'STOCK_EXCESIVO')
        
        self.bajo_count_label.config(text=str(bajo_count))
        self.sin_count_label.config(text=str(sin_count))
        self.exceso_count_label.config(text=str(exceso_count))
    
    def _actualizar_tabla_alertas(self, productos_con_alerta):
        """Actualizar tabla de alertas"""
        table_data = []
        
        for producto, alerta in productos_con_alerta:
            # Determinar color según prioridad
            tags = ""
            if alerta['prioridad'] == 'ALTA':
                tags = 'danger'
            elif alerta['prioridad'] == 'MEDIA':
                tags = 'warning'
            else:
                tags = 'info'
            
            table_data.append({
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'categoria': producto.categoria,
                'stock_actual': producto.stock_actual,
                'stock_minimo': producto.stock_minimo,
                'stock_maximo': producto.stock_maximo,
                'diferencia': alerta['diferencia'],
                'tipo_alerta': self._get_tipo_alerta_text(alerta['tipo']),
                'prioridad': alerta['prioridad'],
                '_tags': tags,
                '_producto': producto,
                '_alerta': alerta
            })
        
        # Ordenar por prioridad (ALTA primero)
        table_data.sort(key=lambda x: {'ALTA': 0, 'MEDIA': 1, 'BAJA': 2}[x['prioridad']])
        
        self.table.load_data(table_data)
    
    def _get_tipo_alerta_text(self, tipo):
        """Obtener texto descriptivo del tipo de alerta"""
        tipos = {
            'SIN_STOCK': '❌ Sin Stock',
            'STOCK_BAJO': '⚠️ Stock Bajo',
            'STOCK_EXCESIVO': '📈 Stock Excesivo'
        }
        return tipos.get(tipo, tipo)
    
    def _ver_detalles(self):
        """Ver detalles del producto con alerta"""
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione una alerta para ver detalles", "warning")
            return
        
        producto = selected.get('_producto')
        alerta = selected.get('_alerta')
        
        if not producto or not alerta:
            self.show_message("Error", "No se pudo obtener la información de la alerta", "error")
            return
        
        detalles = f"""
        📋 Detalles de Alerta
        
        🆔 Código: {producto.codigo}
        📦 Producto: {producto.nombre}
        🗂️ Categoría: {producto.categoria}
        📊 Stock Actual: {producto.stock_actual}
        📉 Stock Mínimo: {producto.stock_minimo}
        📈 Stock Máximo: {producto.stock_maximo}
        ⚠️ Tipo Alerta: {self._get_tipo_alerta_text(alerta['tipo'])}
        🚨 Prioridad: {alerta['prioridad']}
        📝 Mensaje: {alerta['mensaje']}
        
        💡 Recomendación: {self._get_recomendacion(alerta['tipo'])}
        """
        
        self.show_message(f"Alerta: {producto.nombre}", detalles.strip(), "warning")
    
    def _get_recomendacion(self, tipo_alerta):
        """Obtener recomendación según el tipo de alerta"""
        recomendaciones = {
            'SIN_STOCK': 'URGENTE: Realizar compra inmediata para reponer stock.',
            'STOCK_BAJO': 'Realizar compra para reponer stock pronto.',
            'STOCK_EXCESIVO': 'Considerar promociones para reducir inventario.'
        }
        return recomendaciones.get(tipo_alerta, 'Revisar situación del producto.')
    
    def _ajustar_stock(self):
        """Ajustar stock del producto con alerta"""
        from modules.inventario.stock_view import StockView
        
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione una alerta para ajustar stock", "warning")
            return
        
        producto = selected.get('_producto')
        if not producto:
            self.show_message("Error", "No se pudo obtener la información del producto", "error")
            return
        
        # Usar la funcionalidad de ajuste de stock de StockView
        stock_view = StockView(self)
        stock_view._ajustar_stock_directo(producto)
    
    def _ver_movimientos(self):
        """Ver movimientos del producto con alerta"""
        from modules.inventario.stock_view import StockView
        
        selected = self.table.get_selected_item()
        if not selected:
            self.show_message("Advertencia", "Seleccione una alerta para ver movimientos", "warning")
            return
        
        producto = selected.get('_producto')
        if not producto:
            self.show_message("Error", "No se pudo obtener la información del producto", "error")
            return
        
        # Usar la funcionalidad de movimientos de StockView
        stock_view = StockView(self)
        stock_view._ver_movimientos_directo(producto)
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        self._load_alertas()