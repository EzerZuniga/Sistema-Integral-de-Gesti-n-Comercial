import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from app.base_view import BaseView
from services.venta_service import VentaService
from services.inventario_service import InventarioService
from services.producto_service import ProductoService
from core.utils import utils
from core.logger import logger

class DashboardView(BaseView):
    """Vista del Dashboard Principal"""
    
    def _setup_view(self):
        """Configurar el dashboard"""
        # Título
        self.create_title("📊 Dashboard Principal", 0, 0, columnspan=3)
        
        # Frame para KPIs
        kpi_frame = ttk.Frame(self)
        kpi_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        # Configurar grid para KPIs
        for i in range(4):
            kpi_frame.columnconfigure(i, weight=1)
        
        # KPIs principales
        self._create_kpi_cards(kpi_frame)
        
        # Frame para gráficos y tablas
        content_frame = ttk.Frame(self)
        content_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid del contenido
        self.grid_rowconfigure(2, weight=1)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Ventas recientes
        self._create_recent_sales(content_frame)
        
        # Productos bajos en stock
        self._create_low_stock_products(content_frame)
        
        # Cargar datos
        self._load_dashboard_data()
    
    def _create_kpi_cards(self, parent):
        """Crear tarjetas de KPIs"""
        # KPI 1: Ventas del día
        self.kpi_sales_frame = ttk.LabelFrame(parent, text="Ventas Hoy", padding=10)
        self.kpi_sales_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.sales_amount = ttk.Label(
            self.kpi_sales_frame, 
            text="$0", 
            style="Title.TLabel",
            foreground="#27ae60"
        )
        self.sales_amount.pack()
        
        ttk.Label(
            self.kpi_sales_frame,
            text="Total en ventas",
            style="Normal.TLabel"
        ).pack()
        
        # KPI 2: Productos bajos stock
        self.kpi_stock_frame = ttk.LabelFrame(parent, text="Stock Bajo", padding=10)
        self.kpi_stock_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.low_stock_count = ttk.Label(
            self.kpi_stock_frame,
            text="0",
            style="Title.TLabel",
            foreground="#e74c3c"
        )
        self.low_stock_count.pack()
        
        ttk.Label(
            self.kpi_stock_frame,
            text="Productos por reponer",
            style="Normal.TLabel"
        ).pack()
        
        # KPI 3: Valor inventario
        self.kpi_inventory_frame = ttk.LabelFrame(parent, text="Valor Inventario", padding=10)
        self.kpi_inventory_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self.inventory_value = ttk.Label(
            self.kpi_inventory_frame,
            text="$0",
            style="Title.TLabel",
            foreground="#3498db"
        )
        self.inventory_value.pack()
        
        ttk.Label(
            self.kpi_inventory_frame,
            text="Valor total en stock",
            style="Normal.TLabel"
        ).pack()
        
        # KPI 4: Ventas del mes
        self.kpi_monthly_frame = ttk.LabelFrame(parent, text="Ventas Mes", padding=10)
        self.kpi_monthly_frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
        
        self.monthly_sales = ttk.Label(
            self.kpi_monthly_frame,
            text="$0",
            style="Title.TLabel",
            foreground="#9b59b6"
        )
        self.monthly_sales.pack()
        
        ttk.Label(
            self.kpi_monthly_frame,
            text="Total mensual",
            style="Normal.TLabel"
        ).pack()
    
    def _create_recent_sales(self, parent):
        """Crear sección de ventas recientes"""
        sales_frame = ttk.LabelFrame(parent, text="🛒 Ventas Recientes", padding=10)
        sales_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        sales_frame.columnconfigure(0, weight=1)
        sales_frame.rowconfigure(1, weight=1)
        
        # Toolbar
        toolbar = ttk.Frame(sales_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="Nueva Venta",
            command=self._navigate_to_ventas,
            style="Primary.TButton"
        ).pack(side="left")
        
        ttk.Button(
            toolbar,
            text="Ver Todas",
            command=self._view_all_sales,
            style="Secondary.TButton"
        ).pack(side="right")
        
        # Tabla de ventas
        columns = [
            {'id': 'fecha', 'text': 'Fecha', 'width': 100},
            {'id': 'boleta', 'text': 'Boleta', 'width': 120},
            {'id': 'cliente', 'text': 'Cliente', 'width': 150},
            {'id': 'total', 'text': 'Total', 'width': 100}
        ]
        
        self.sales_table = ttk.Treeview(
            sales_frame,
            columns=[col['id'] for col in columns],
            show='headings',
            height=8
        )
        
        for col in columns:
            self.sales_table.heading(col['id'], text=col['text'])
            self.sales_table.column(col['id'], width=col['width'])
        
        self.sales_table.grid(row=1, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(sales_frame, orient="vertical", command=self.sales_table.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.sales_table.configure(yscrollcommand=scrollbar.set)
    
    def _create_low_stock_products(self, parent):
        """Crear sección de productos bajos en stock"""
        stock_frame = ttk.LabelFrame(parent, text="⚠️ Productos por Reponer", padding=10)
        stock_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        stock_frame.columnconfigure(0, weight=1)
        stock_frame.rowconfigure(1, weight=1)
        
        # Toolbar
        toolbar = ttk.Frame(stock_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="Ver Inventario",
            command=self._navigate_to_inventario,
            style="Primary.TButton"
        ).pack(side="left")
        
        # Tabla de productos bajos en stock
        columns = [
            {'id': 'producto', 'text': 'Producto', 'width': 150},
            {'id': 'stock', 'text': 'Stock Actual', 'width': 100},
            {'id': 'minimo', 'text': 'Mínimo', 'width': 80},
            {'id': 'estado', 'text': 'Estado', 'width': 100}
        ]
        
        self.stock_table = ttk.Treeview(
            stock_frame,
            columns=[col['id'] for col in columns],
            show='headings',
            height=8
        )
        
        for col in columns:
            self.stock_table.heading(col['id'], text=col['text'])
            self.stock_table.column(col['id'], width=col['width'])
        
        self.stock_table.grid(row=1, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(stock_frame, orient="vertical", command=self.stock_table.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.stock_table.configure(yscrollcommand=scrollbar.set)
    
    def _load_dashboard_data(self):
        """Cargar datos del dashboard"""
        try:
            # KPIs principales
            self._load_kpi_data()
            
            # Ventas recientes
            self._load_recent_sales()
            
            # Productos bajos en stock
            self._load_low_stock_products()
            
        except Exception as e:
            logger.error(f"Error cargando datos del dashboard: {e}")
            self.show_message("Error", "No se pudieron cargar los datos del dashboard", "error")
    
    def _load_kpi_data(self):
        """Cargar datos de KPIs"""
        try:
            # Ventas de hoy
            hoy = datetime.now().date()
            ventas_hoy = VentaService.obtener_ventas_por_fecha(
                datetime(hoy.year, hoy.month, hoy.day),
                datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)
            )
            total_hoy = sum(venta.total for venta in ventas_hoy)
            self.sales_amount.config(text=utils.format_currency(total_hoy))
            
            # Productos bajos en stock
            productos_bajos = ProductoService.obtener_productos_bajo_stock()
            self.low_stock_count.config(text=str(len(productos_bajos)))
            
            # Valor del inventario
            kpi_inventario = InventarioService.obtener_kpi_inventario()
            self.inventory_value.config(text=utils.format_currency(kpi_inventario['valor_total']))
            
            # Ventas del mes
            inicio_mes = datetime(hoy.year, hoy.month, 1)
            fin_mes = datetime(hoy.year, hoy.month, hoy.day, 23, 59, 59)
            ventas_mes = VentaService.obtener_ventas_por_fecha(inicio_mes, fin_mes)
            total_mes = sum(venta.total for venta in ventas_mes)
            self.monthly_sales.config(text=utils.format_currency(total_mes))
            
        except Exception as e:
            logger.error(f"Error cargando KPIs: {e}")
    
    def _load_recent_sales(self):
        """Cargar ventas recientes"""
        try:
            # Limpiar tabla
            for item in self.sales_table.get_children():
                self.sales_table.delete(item)
            
            # Obtener ventas de los últimos 7 días
            fecha_inicio = datetime.now() - timedelta(days=7)
            ventas = VentaService.obtener_ventas_por_fecha(fecha_inicio, datetime.now())
            
            # Mostrar las 10 más recientes
            for venta in ventas[:10]:
                fecha_str = venta.fecha.strftime("%d/%m %H:%M") if venta.fecha else ""
                cliente = venta.cliente_nombre or "Consumidor Final"
                
                self.sales_table.insert("", "end", values=(
                    fecha_str,
                    venta.numero_boleta,
                    cliente,
                    utils.format_currency(venta.total)
                ))
                
        except Exception as e:
            logger.error(f"Error cargando ventas recientes: {e}")
    
    def _load_low_stock_products(self):
        """Cargar productos bajos en stock"""
        try:
            # Limpiar tabla
            for item in self.stock_table.get_children():
                self.stock_table.delete(item)
            
            productos = ProductoService.obtener_productos_bajo_stock()
            
            for producto in productos[:10]:  # Mostrar máximo 10
                estado = "CRÍTICO" if producto.stock_actual == 0 else "BAJO"
                
                self.stock_table.insert("", "end", values=(
                    producto.nombre,
                    producto.stock_actual,
                    producto.stock_minimo,
                    estado
                ))
                
        except Exception as e:
            logger.error(f"Error cargando productos bajos en stock: {e}")
    
    def _navigate_to_ventas(self):
        """Navegar a módulo de ventas"""
        from app.router import router
        router.navigate_to('ventas')
    
    def _navigate_to_inventario(self):
        """Navegar a módulo de inventario"""
        from app.router import router
        router.navigate_to('stock')
    
    def _view_all_sales(self):
        """Ver todas las ventas"""
        from app.router import router
        router.navigate_to('resumen')
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        self._load_dashboard_data()