from config.database import db
from models.venta import Venta, DetalleVenta
from core.exceptions import DatabaseError, ValidationError, InsufficientStockError
from core.logger import logger
from core.utils import utils
from services.inventario_service import InventarioService
from services.producto_service import ProductoService
from datetime import datetime

class VentaService:
    """Servicio para gestión de ventas"""
    
    @staticmethod
    def obtener_todas():
        """Obtener todas las ventas"""
        try:
            query = """
                SELECT v.*, u.nombre as usuario_nombre 
                FROM ventas v 
                LEFT JOIN usuarios u ON v.usuario_id = u.id 
                ORDER BY v.fecha DESC
            """
            results = db.execute_query(query)
            ventas = []
            
            for row in results:
                venta_data = dict(row)
                venta = Venta(
                    id=venta_data['id'],
                    numero_boleta=venta_data['numero_boleta'],
                    fecha=datetime.fromisoformat(venta_data['fecha']) if venta_data['fecha'] else None,
                    cliente_nombre=venta_data['cliente_nombre'],
                    cliente_rut=venta_data['cliente_rut'],
                    subtotal=venta_data['subtotal'],
                    iva=venta_data['iva'],
                    total=venta_data['total'],
                    usuario_id=venta_data['usuario_id'],
                    created_at=datetime.fromisoformat(venta_data['created_at']) if venta_data['created_at'] else None
                )
                
                # Obtener detalles
                detalles_query = """
                    SELECT dv.*, p.nombre as producto_nombre, p.codigo as producto_codigo
                    FROM detalle_ventas dv 
                    LEFT JOIN productos p ON dv.producto_id = p.id 
                    WHERE dv.venta_id = ?
                """
                detalles_results = db.execute_query(detalles_query, (venta.id,))
                
                for detalle_row in detalles_results:
                    detalle_data = dict(detalle_row)
                    detalle = DetalleVenta(
                        id=detalle_data['id'],
                        venta_id=detalle_data['venta_id'],
                        producto_id=detalle_data['producto_id'],
                        cantidad=detalle_data['cantidad'],
                        precio_unitario=detalle_data['precio_unitario'],
                        total_linea=detalle_data['total_linea']
                    )
                    venta.agregar_detalle(detalle)
                
                ventas.append(venta)
            
            return ventas
            
        except Exception as e:
            logger.error(f"Error obteniendo ventas: {e}")
            raise DatabaseError("Error al obtener ventas")
    
    @staticmethod
    def obtener_por_id(venta_id: int):
        """Obtener venta por ID"""
        try:
            query = "SELECT * FROM ventas WHERE id = ?"
            result = db.execute_query(query, (venta_id,))
            
            if not result:
                return None
            
            venta_data = dict(result[0])
            venta = Venta(
                id=venta_data['id'],
                numero_boleta=venta_data['numero_boleta'],
                fecha=datetime.fromisoformat(venta_data['fecha']) if venta_data['fecha'] else None,
                cliente_nombre=venta_data['cliente_nombre'],
                cliente_rut=venta_data['cliente_rut'],
                subtotal=venta_data['subtotal'],
                iva=venta_data['iva'],
                total=venta_data['total'],
                usuario_id=venta_data['usuario_id'],
                created_at=datetime.fromisoformat(venta_data['created_at']) if venta_data['created_at'] else None
            )
            
            # Obtener detalles
            detalles_query = "SELECT * FROM detalle_ventas WHERE venta_id = ?"
            detalles_results = db.execute_query(detalles_query, (venta_id,))
            
            for detalle_row in detalles_results:
                detalle_data = dict(detalle_row)
                detalle = DetalleVenta(
                    id=detalle_data['id'],
                    venta_id=detalle_data['venta_id'],
                    producto_id=detalle_data['producto_id'],
                    cantidad=detalle_data['cantidad'],
                    precio_unitario=detalle_data['precio_unitario'],
                    total_linea=detalle_data['total_linea']
                )
                venta.agregar_detalle(detalle)
            
            return venta
            
        except Exception as e:
            logger.error(f"Error obteniendo venta {venta_id}: {e}")
            raise DatabaseError("Error al obtener venta")
    
    @staticmethod
    def crear_venta(venta: Venta):
        """Crear nueva venta"""
        conn = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Validaciones
            if not venta.detalles:
                raise ValidationError("La venta debe tener al menos un producto")
            
            # Verificar stock disponible
            for detalle in venta.detalles:
                producto = ProductoService.obtener_por_id(detalle.producto_id)
                if not producto:
                    raise ValidationError(f"Producto ID {detalle.producto_id} no encontrado")
                
                if producto.stock_actual < detalle.cantidad:
                    raise InsufficientStockError(
                        f"Stock insuficiente para {producto.nombre}. "
                        f"Stock actual: {producto.stock_actual}, solicitado: {detalle.cantidad}"
                    )
            
            # Generar número de boleta
            if not venta.numero_boleta:
                venta.numero_boleta = VentaService._generar_numero_boleta()
            
            # Calcular totales
            venta.calcular_totales()
            
            # Insertar venta
            query_venta = """
                INSERT INTO ventas 
                (numero_boleta, fecha, cliente_nombre, cliente_rut, subtotal, iva, total, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params_venta = (
                venta.numero_boleta,
                venta.fecha or datetime.now(),
                venta.cliente_nombre,
                venta.cliente_rut,
                venta.subtotal,
                venta.iva,
                venta.total,
                venta.usuario_id
            )
            
            cursor.execute(query_venta, params_venta)
            venta_id = cursor.lastrowid
            
            # Insertar detalles y actualizar stock
            for detalle in venta.detalles:
                detalle.venta_id = venta_id
                detalle.calcular_total()
                
                query_detalle = """
                    INSERT INTO detalle_ventas 
                    (venta_id, producto_id, cantidad, precio_unitario, total_linea)
                    VALUES (?, ?, ?, ?, ?)
                """
                params_detalle = (
                    detalle.venta_id,
                    detalle.producto_id,
                    detalle.cantidad,
                    detalle.precio_unitario,
                    detalle.total_linea
                )
                cursor.execute(query_detalle, params_detalle)
                
                # Actualizar stock y registrar movimiento
                producto = ProductoService.obtener_por_id(detalle.producto_id)
                nuevo_stock = producto.stock_actual - detalle.cantidad
                
                ProductoService.actualizar_stock(detalle.producto_id, nuevo_stock)
                
                InventarioService.registrar_movimiento(
                    producto_id=detalle.producto_id,
                    tipo="salida",
                    cantidad=detalle.cantidad,
                    cantidad_anterior=producto.stock_actual,
                    cantidad_nueva=nuevo_stock,
                    motivo=f"Venta #{venta.numero_boleta}",
                    referencia_id=venta_id,
                    referencia_tipo="venta",
                    usuario_id=venta.usuario_id
                )
            
            conn.commit()
            logger.info(f"Venta creada: {venta.numero_boleta}")
            return venta_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creando venta: {e}")
            if isinstance(e, (ValidationError, InsufficientStockError)):
                raise
            raise DatabaseError("Error al crear venta")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def _generar_numero_boleta():
        """Generar número de boleta único"""
        try:
            # Formato: B-YYYYMMDD-XXXX
            fecha_actual = datetime.now().strftime("%Y%m%d")
            query = "SELECT COUNT(*) as count FROM ventas WHERE strftime('%Y%m%d', fecha) = ?"
            result = db.execute_query(query, (fecha_actual,))
            count = result[0]['count'] + 1 if result else 1
            
            return f"B-{fecha_actual}-{count:04d}"
        except Exception as e:
            logger.error(f"Error generando número de boleta: {e}")
            return f"B-{datetime.now().strftime('%Y%m%d')}-0001"
    
    @staticmethod
    def obtener_ventas_por_fecha(fecha_inicio: datetime, fecha_fin: datetime):
        """Obtener ventas por rango de fechas"""
        try:
            query = """
                SELECT * FROM ventas 
                WHERE fecha BETWEEN ? AND ? 
                ORDER BY fecha DESC
            """
            params = (fecha_inicio, fecha_fin)
            results = db.execute_query(query, params)
            
            ventas = []
            for row in results:
                venta_data = dict(row)
                venta = Venta(
                    id=venta_data['id'],
                    numero_boleta=venta_data['numero_boleta'],
                    fecha=datetime.fromisoformat(venta_data['fecha']) if venta_data['fecha'] else None,
                    cliente_nombre=venta_data['cliente_nombre'],
                    cliente_rut=venta_data['cliente_rut'],
                    subtotal=venta_data['subtotal'],
                    iva=venta_data['iva'],
                    total=venta_data['total'],
                    usuario_id=venta_data['usuario_id']
                )
                ventas.append(venta)
            
            return ventas
            
        except Exception as e:
            logger.error(f"Error obteniendo ventas por fecha: {e}")
            raise DatabaseError("Error al obtener ventas por fecha")
    
    @staticmethod
    def obtener_resumen_ventas(fecha_inicio: datetime, fecha_fin: datetime):
        """Obtener resumen de ventas por período"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_ventas,
                    SUM(total) as total_ingresos,
                    SUM(subtotal) as total_subtotal,
                    SUM(iva) as total_iva,
                    AVG(total) as promedio_venta
                FROM ventas 
                WHERE fecha BETWEEN ? AND ?
            """
            result = db.execute_query(query, (fecha_inicio, fecha_fin))
            
            if result and result[0]['total_ventas']:
                return dict(result[0])
            else:
                return {
                    'total_ventas': 0,
                    'total_ingresos': 0.0,
                    'total_subtotal': 0.0,
                    'total_iva': 0.0,
                    'promedio_venta': 0.0
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo resumen de ventas: {e}")
            raise DatabaseError("Error al obtener resumen de ventas")