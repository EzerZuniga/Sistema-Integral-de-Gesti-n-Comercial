import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from app.base_view import BaseView
from services.venta_service import VentaService
from services.compra_service import CompraService
from core.logger import logger
from core.utils import utils
from ui.components.table import CustomTable

class ResumenView(BaseView):
    """Vista de resumen de ventas y compras"""
    
    def _setup_view(self):
        """Configurar vista de resumen"""
        # Título
        self.create_title("📈 Resumen de Ventas y Compras", 0, 0, columnspan=2)
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Configurar grid principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Filtros
        self._create_filters(main_frame)
        
        # Pestañas
        self._create_tabs(main_frame)
        
        # Cargar datos iniciales
        self._cargar_resumen()
    
    def _create_filters(self, parent):
        """Crear sección de filtros"""
        filter_frame = ttk.LabelFrame(parent, text="Filtros", padding=10)
        filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Período
        ttk.Label(filter_frame, text="Período:", style="Normal.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )
        
        self.periodo_var = tk.StringVar(value="7d")
        periodos = [
            ("Hoy", "1d"),
            ("Últimos 7 días", "7d"),
            ("Últimos 30 días", "30d"),
            ("Este mes", "month"),
            ("Mes anterior", "last_month"),
            ("Personalizado", "custom")
        ]
        
        for i, (text, value) in enumerate(periodos):
            ttk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.periodo_var,
                value=value,
                command=self._aplicar_filtros
            ).grid(row=0, column=i+1, sticky="w", padx=5)
        
        # Fechas personalizadas
        custom_frame = ttk.Frame(filter_frame)
        custom_frame.grid(row=1, column=0, columnspan=7, sticky="ew", pady=(5, 0))
        
        ttk.Label(custom_frame, text="Desde:", style="Normal.TLabel").pack(side="left", padx=(0, 5))
        self.fecha_desde_var = tk.StringVar()
        self.fecha_desde_entry = ttk.Entry(custom_frame, textvariable=self.fecha_desde_var, width=12)
        self.fecha_desde_entry.pack(side="left", padx=5)
        
        ttk.Label(custom_frame, text="Hasta:", style="Normal.TLabel").pack(side="left", padx=(10, 5))
        self.fecha_hasta_var = tk.StringVar()
        self.fecha_hasta_entry = ttk.Entry(custom_frame, textvariable=self.fecha_hasta_var, width=12)
        self.fecha_hasta_entry.pack(side="left", padx=5)
        
        ttk.Button(
            custom_frame,
            text="Aplicar",
            command=self._aplicar_filtros_personalizados,
            style="Secondary.TButton"
        ).pack(side="left", padx=10)
    
    def _create_tabs(self, parent):
        """Crear pestañas de contenido"""
        notebook = ttk.Notebook(parent)
        notebook.grid(row=1, column=0, sticky="nsew")
        
        # Pestaña de resumen
        resumen_frame = ttk.Frame(notebook, padding=10)
        notebook.add(resumen_frame, text="📊 Resumen General")
        
        # Pestaña de ventas
        ventas_frame = ttk.Frame(notebook, padding=10)
        notebook.add(ventas_frame, text="💰 Ventas")
        
        # Pestaña de compras
        compras_frame = ttk.Frame(notebook, padding=10)
        notebook.add(compras_frame, text="🛒 Compras")
        
        # Configurar pestañas
        self._setup_resumen_tab(resumen_frame)
        self._setup_ventas_tab(ventas_frame)
        self._setup_compras_tab(compras_frame)
    
    def _setup_resumen_tab(self, parent):
        """Configurar pestaña de resumen"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # KPIs
        kpi_frame = ttk.Frame(parent)
        kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        for i in range(4):
            kpi_frame.columnconfigure(i, weight=1)
        
        # KPI Ventas
        ventas_kpi = ttk.LabelFrame(kpi_frame, text="Total Ventas", padding=10)
        ventas_kpi.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.ventas_total_label = ttk.Label(ventas_kpi, text="$0", style="Title.TLabel", foreground="#27ae60")
        self.ventas_total_label.pack()
        
        ttk.Label(ventas_kpi, text="Ingresos totales", style="Normal.TLabel").pack()
        
        # KPI Compras
        compras_kpi = ttk.LabelFrame(kpi_frame, text="Total Compras", padding=10)
        compras_kpi.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.compras_total_label = ttk.Label(compras_kpi, text="$0", style="Title.TLabel", foreground="#e74c3c")
        self.compras_total_label.pack()
        
        ttk.Label(compras_kpi, text="Egresos totales", style="Normal.TLabel").pack()
        
        # KPI Utilidad
        utilidad_kpi = ttk.LabelFrame(kpi_frame, text="Utilidad Bruta", padding=10)
        utilidad_kpi.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self.utilidad_label = ttk.Label(utilidad_kpi, text="$0", style="Title.TLabel", foreground="#3498db")
        self.utilidad_label.pack()
        
        ttk.Label(utilidad_kpi, text="Ventas - Compras", style="Normal.TLabel").pack()
        
        # KPI Cantidad
        cantidad_kpi = ttk.LabelFrame(kpi_frame, text="Total Transacciones", padding=10)
        cantidad_kpi.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
        
        self.transacciones_label = ttk.Label(cantidad_kpi, text="0", style="Title.TLabel", foreground="#9b59b6")
        self.transacciones_label.pack()
        
        ttk.Label(cantidad_kpi, text="Ventas + Compras", style="Normal.TLabel").pack()
        
        # Gráfico de tendencia (simulado)
        trend_frame = ttk.LabelFrame(parent, text="Tendencia de Ventas", padding=10)
        trend_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        trend_frame.rowconfigure(0, weight=1)
        trend_frame.columnconfigure(0, weight=1)
        
        # Simular gráfico con texto
        self.trend_text = tk.Text(trend_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.trend_text.grid(row=0, column=0, sticky="nsew")
        
        # Últimas transacciones
        transacciones_frame = ttk.LabelFrame(parent, text="Últimas Transacciones", padding=10)
        transacciones_frame.grid(row=2, column=0, sticky="nsew")
        transacciones_frame.columnconfigure(0, weight=1)
        transacciones_frame.rowconfigure(0, weight=1)
        
        columns = [
            {'id': 'fecha', 'text': 'Fecha', 'width': 120},
            {'id': 'tipo', 'text': 'Tipo', 'width': 80},
            {'id': 'numero', 'text': 'Número', 'width': 120},
            {'id': 'total', 'text': 'Total', 'width': 100, 'formatter': utils.format_currency}
        ]
        
        self.transacciones_table = CustomTable(
            transacciones_frame,
            columns=columns,
            height=6,
            show_toolbar=False
        )
        self.transacciones_table.grid(row=0, column=0, sticky="nsew")
    
    def _setup_ventas_tab(self, parent):
        """Configurar pestaña de ventas"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        columns = [
            {'id': 'fecha', 'text': 'Fecha', 'width': 120},
            {'id': 'numero_boleta', 'text': 'N° Boleta', 'width': 120},
            {'id': 'cliente', 'text': 'Cliente', 'width': 150},
            {'id': 'subtotal', 'text': 'Subtotal', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'iva', 'text': 'IVA', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'total', 'text': 'Total', 'width': 100, 'formatter': utils.format_currency}
        ]
        
        self.ventas_table = CustomTable(
            parent,
            columns=columns,
            height=20,
            show_toolbar=True
        )
        self.ventas_table.grid(row=0, column=0, sticky="nsew")
    
    def _setup_compras_tab(self, parent):
        """Configurar pestaña de compras"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        columns = [
            {'id': 'fecha', 'text': 'Fecha', 'width': 120},
            {'id': 'numero_factura', 'text': 'N° Factura', 'width': 120},
            {'id': 'proveedor', 'text': 'Proveedor', 'width': 150},
            {'id': 'subtotal', 'text': 'Subtotal', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'iva', 'text': 'IVA', 'width': 100, 'formatter': utils.format_currency},
            {'id': 'total', 'text': 'Total', 'width': 100, 'formatter': utils.format_currency}
        ]
        
        self.compras_table = CustomTable(
            parent,
            columns=columns,
            height=20,
            show_toolbar=True
        )
        self.compras_table.grid(row=0, column=0, sticky="nsew")
    
    def _cargar_resumen(self):
        """Cargar datos del resumen"""
        try:
            # Obtener fechas según el período seleccionado
            fecha_inicio, fecha_fin = self._obtener_rango_fechas()
            
            # Cargar ventas y compras
            self.ventas = VentaService.obtener_ventas_por_fecha(fecha_inicio, fecha_fin)
            self.compras = CompraService.obtener_compras_por_fecha(fecha_inicio, fecha_fin)
            
            # Actualizar KPIs
            self._actualizar_kpis()
            
            # Actualizar tablas
            self._actualizar_tabla_ventas()
            self._actualizar_tabla_compras()
            self._actualizar_transacciones_recientes()
            self._actualizar_tendencia()
            
        except Exception as e:
            logger.error(f"Error cargando resumen: {e}")
            self.show_message("Error", "No se pudieron cargar los datos del resumen", "error")
    
    def _obtener_rango_fechas(self):
        """Obtener rango de fechas según el período seleccionado"""
        hoy = datetime.now()
        periodo = self.periodo_var.get()
        
        if periodo == "1d":
            return datetime(hoy.year, hoy.month, hoy.day), hoy
        elif periodo == "7d":
            return hoy - timedelta(days=7), hoy
        elif periodo == "30d":
            return hoy - timedelta(days=30), hoy
        elif periodo == "month":
            return datetime(hoy.year, hoy.month, 1), hoy
        elif periodo == "last_month":
            if hoy.month == 1:
                return datetime(hoy.year-1, 12, 1), datetime(hoy.year, 1, 1) - timedelta(seconds=1)
            else:
                return datetime(hoy.year, hoy.month-1, 1), datetime(hoy.year, hoy.month, 1) - timedelta(seconds=1)
        else:  # custom
            try:
                fecha_desde = utils.parse_date(self.fecha_desde_var.get())
                fecha_hasta = utils.parse_date(self.fecha_hasta_var.get())
                return fecha_desde, fecha_hasta
            except:
                # Si hay error en fechas personalizadas, usar último mes
                return hoy - timedelta(days=30), hoy
    
    def _actualizar_kpis(self):
        """Actualizar KPIs del resumen"""
        total_ventas = sum(venta.total for venta in self.ventas)
        total_compras = sum(compra.total for compra in self.compras)
        utilidad = total_ventas - total_compras
        total_transacciones = len(self.ventas) + len(self.compras)
        
        self.ventas_total_label.config(text=utils.format_currency(total_ventas))
        self.compras_total_label.config(text=utils.format_currency(total_compras))
        self.utilidad_label.config(text=utils.format_currency(utilidad))
        self.transacciones_label.config(text=str(total_transacciones))
    
    def _actualizar_tabla_ventas(self):
        """Actualizar tabla de ventas"""
        table_data = []
        for venta in self.ventas:
            table_data.append({
                'fecha': venta.fecha.strftime("%d/%m/%Y %H:%M") if venta.fecha else "",
                'numero_boleta': venta.numero_boleta,
                'cliente': venta.cliente_nombre or "Consumidor Final",
                'subtotal': venta.subtotal,
                'iva': venta.iva,
                'total': venta.total
            })
        
        self.ventas_table.load_data(table_data)
    
    def _actualizar_tabla_compras(self):
        """Actualizar tabla de compras"""
        table_data = []
        for compra in self.compras:
            # Obtener nombre del proveedor
            proveedor_nombre = "Proveedor"
            try:
                from services.proveedor_service import ProveedorService
                proveedor = ProveedorService.obtener_por_id(compra.proveedor_id)
                if proveedor:
                    proveedor_nombre = proveedor.nombre
            except:
                pass
            
            table_data.append({
                'fecha': compra.fecha.strftime("%d/%m/%Y %H:%M") if compra.fecha else "",
                'numero_factura': compra.numero_factura,
                'proveedor': proveedor_nombre,
                'subtotal': compra.subtotal,
                'iva': compra.iva,
                'total': compra.total
            })
        
        self.compras_table.load_data(table_data)
    
    def _actualizar_transacciones_recientes(self):
        """Actualizar transacciones recientes"""
        # Combinar ventas y compras
        transacciones = []
        
        for venta in self.ventas[-10:]:  # Últimas 10 ventas
            transacciones.append({
                'fecha': venta.fecha,
                'tipo': 'VENTA',
                'numero': venta.numero_boleta,
                'total': venta.total,
                'obj': venta
            })
        
        for compra in self.compras[-10:]:  # Últimas 10 compras
            transacciones.append({
                'fecha': compra.fecha,
                'tipo': 'COMPRA',
                'numero': compra.numero_factura,
                'total': compra.total,
                'obj': compra
            })
        
        # Ordenar por fecha (más recientes primero)
        transacciones.sort(key=lambda x: x['fecha'] if x['fecha'] else datetime.min, reverse=True)
        
        # Preparar datos para tabla
        table_data = []
        for trans in transacciones[:10]:  # Mostrar solo 10 más recientes
            table_data.append({
                'fecha': trans['fecha'].strftime("%d/%m %H:%M") if trans['fecha'] else "",
                'tipo': trans['tipo'],
                'numero': trans['numero'],
                'total': trans['total']
            })
        
        self.transacciones_table.load_data(table_data)
    
    def _actualizar_tendencia(self):
        """Actualizar tendencia de ventas"""
        try:
            # Agrupar ventas por día
            ventas_por_dia = {}
            for venta in self.ventas:
                if venta.fecha:
                    fecha_str = venta.fecha.strftime("%d/%m")
                    if fecha_str not in ventas_por_dia:
                        ventas_por_dia[fecha_str] = 0
                    ventas_por_dia[fecha_str] += venta.total
            
            # Crear texto de tendencia
            trend_text = "Tendencia de ventas por día:\n\n"
            for fecha, total in list(ventas_por_dia.items())[-7:]:  # Últimos 7 días
                bar = "█" * int(total / 1000)  # Un carácter por cada $1000
                trend_text += f"{fecha}: {utils.format_currency(total)} {bar}\n"
            
            # Actualizar widget de texto
            self.trend_text.config(state=tk.NORMAL)
            self.trend_text.delete(1.0, tk.END)
            self.trend_text.insert(1.0, trend_text)
            self.trend_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error actualizando tendencia: {e}")
    
    def _aplicar_filtros(self):
        """Aplicar filtros automáticos"""
        if self.periodo_var.get() != "custom":
            self._cargar_resumen()
    
    def _aplicar_filtros_personalizados(self):
        """Aplicar filtros personalizados"""
        self.periodo_var.set("custom")
        self._cargar_resumen()
    
    def on_show(self):
        """Cuando se muestra la vista"""
        super().on_show()
        self._cargar_resumen()