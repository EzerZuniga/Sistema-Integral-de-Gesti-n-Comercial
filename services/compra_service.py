from config.database import db
from models.compra import Compra, DetalleCompra
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from services.inventario_service import InventarioService
from services.producto_service import ProductoService
from datetime import datetime

class CompraService:
    """Servicio para gestión de compras"""
    
    @staticmethod
    def obtener_todas():
        """Obtener todas las compras"""
        try:
            query = """
                SELECT c.*, p.nombre as proveedor_nombre, u.nombre as usuario_nombre 
                FROM compras c 
                LEFT JOIN proveedores p ON c.proveedor_id = p.id 
                LEFT JOIN usuarios u ON c.usuario_id = u.id 
                ORDER BY c.fecha DESC
            """
            results = db.execute_query(query)
            compras = []
            
            for row in results:
                compra_data = dict(row)
                compra = Compra(
                    id=compra_data['id'],
                    numero_factura=compra_data['numero_factura'],
                    fecha=datetime.fromisoformat(compra_data['fecha']) if compra_data['fecha'] else None,
                    proveedor_id=compra_data['proveedor_id'],
                    subtotal=compra_data['subtotal'],
                    iva=compra_data['iva'],
                    total=compra_data['total'],
                    usuario_id=compra_data['usuario_id'],
                    created_at=datetime.fromisoformat(compra_data['created_at']) if compra_data['created_at'] else None
                )
                
                # Obtener detalles
                detalles_query = """
                    SELECT dc.*, p.nombre as producto_nombre, p.codigo as producto_codigo
                    FROM detalle_compras dc 
                    LEFT JOIN productos p ON dc.producto_id = p.id 
                    WHERE dc.compra_id = ?
                """
                detalles_results = db.execute_query(detalles_query, (compra.id,))
                
                for detalle_row in detalles_results:
                    detalle_data = dict(detalle_row)
                    detalle = DetalleCompra(
                        id=detalle_data['id'],
                        compra_id=detalle_data['compra_id'],
                        producto_id=detalle_data['producto_id'],
                        cantidad=detalle_data['cantidad'],
                        precio_unitario=detalle_data['precio_unitario'],
                        total_linea=detalle_data['total_linea']
                    )
                    compra.agregar_detalle(detalle)
                
                compras.append(compra)
            
            return compras
            
        except Exception as e:
            logger.error(f"Error obteniendo compras: {e}")
            raise DatabaseError("Error al obtener compras")
    
    @staticmethod
    def obtener_por_id(compra_id: int):
        """Obtener compra por ID"""
        try:
            query = "SELECT * FROM compras WHERE id = ?"
            result = db.execute_query(query, (compra_id,))
            
            if not result:
                return None
            
            compra_data = dict(result[0])
            compra = Compra(
                id=compra_data['id'],
                numero_factura=compra_data['numero_factura'],
                fecha=datetime.fromisoformat(compra_data['fecha']) if compra_data['fecha'] else None,
                proveedor_id=compra_data['proveedor_id'],
                subtotal=compra_data['subtotal'],
                iva=compra_data['iva'],
                total=compra_data['total'],
                usuario_id=compra_data['usuario_id'],
                created_at=datetime.fromisoformat(compra_data['created_at']) if compra_data['created_at'] else None
            )
            
            # Obtener detalles
            detalles_query = "SELECT * FROM detalle_compras WHERE compra_id = ?"
            detalles_results = db.execute_query(detalles_query, (compra_id,))
            
            for detalle_row in detalles_results:
                detalle_data = dict(detalle_row)
                detalle = DetalleCompra(
                    id=detalle_data['id'],
                    compra_id=detalle_data['compra_id'],
                    producto_id=detalle_data['producto_id'],
                    cantidad=detalle_data['cantidad'],
                    precio_unitario=detalle_data['precio_unitario'],
                    total_linea=detalle_data['total_linea']
                )
                compra.agregar_detalle(detalle)
            
            return compra
            
        except Exception as e:
            logger.error(f"Error obteniendo compra {compra_id}: {e}")
            raise DatabaseError("Error al obtener compra")
    
    @staticmethod
    def crear_compra(compra: Compra):
        """Crear nueva compra"""
        conn = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Validaciones
            if not compra.detalles:
                raise ValidationError("La compra debe tener al menos un producto")
            
            # Generar número de factura
            if not compra.numero_factura:
                compra.numero_factura = CompraService._generar_numero_factura()
            
            # Calcular totales
            compra.calcular_totales()
            
            # Insertar compra
            query_compra = """
                INSERT INTO compras 
                (numero_factura, fecha, proveedor_id, subtotal, iva, total, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params_compra = (
                compra.numero_factura,
                compra.fecha or datetime.now(),
                compra.proveedor_id,
                compra.subtotal,
                compra.iva,
                compra.total,
                compra.usuario_id
            )
            
            cursor.execute(query_compra, params_compra)
            compra_id = cursor.lastrowid
            
            # Insertar detalles y actualizar stock
            for detalle in compra.detalles:
                detalle.compra_id = compra_id
                detalle.calcular_total()
                
                query_detalle = """
                    INSERT INTO detalle_compras 
                    (compra_id, producto_id, cantidad, precio_unitario, total_linea)
                    VALUES (?, ?, ?, ?, ?)
                """
                params_detalle = (
                    detalle.compra_id,
                    detalle.producto_id,
                    detalle.cantidad,
                    detalle.precio_unitario,
                    detalle.total_linea
                )
                cursor.execute(query_detalle, params_detalle)
                
                # Actualizar stock y registrar movimiento
                producto = ProductoService.obtener_por_id(detalle.producto_id)
                nuevo_stock = producto.stock_actual + detalle.cantidad
                
                ProductoService.actualizar_stock(detalle.producto_id, nuevo_stock)
                
                InventarioService.registrar_movimiento(
                    producto_id=detalle.producto_id,
                    tipo="entrada",
                    cantidad=detalle.cantidad,
                    cantidad_anterior=producto.stock_actual,
                    cantidad_nueva=nuevo_stock,
                    motivo=f"Compra #{compra.numero_factura}",
                    referencia_id=compra_id,
                    referencia_tipo="compra",
                    usuario_id=compra.usuario_id
                )
            
            conn.commit()
            logger.info(f"Compra creada: {compra.numero_factura}")
            return compra_id
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creando compra: {e}")
            if isinstance(e, ValidationError):
                raise
            raise DatabaseError("Error al crear compra")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def _generar_numero_factura():
        """Generar número de factura único"""
        try:
            # Formato: F-YYYYMMDD-XXXX
            fecha_actual = datetime.now().strftime("%Y%m%d")
            query = "SELECT COUNT(*) as count FROM compras WHERE strftime('%Y%m%d', fecha) = ?"
            result = db.execute_query(query, (fecha_actual,))
            count = result[0]['count'] + 1 if result else 1
            
            return f"F-{fecha_actual}-{count:04d}"
        except Exception as e:
            logger.error(f"Error generando número de factura: {e}")
            return f"F-{datetime.now().strftime('%Y%m%d')}-0001"
    
    @staticmethod
    def obtener_compras_por_proveedor(proveedor_id: int):
        """Obtener compras por proveedor"""
        try:
            query = """
                SELECT * FROM compras 
                WHERE proveedor_id = ? 
                ORDER BY fecha DESC
            """
            results = db.execute_query(query, (proveedor_id,))
            
            compras = []
            for row in results:
                compra_data = dict(row)
                compra = Compra(
                    id=compra_data['id'],
                    numero_factura=compra_data['numero_factura'],
                    fecha=datetime.fromisoformat(compra_data['fecha']) if compra_data['fecha'] else None,
                    proveedor_id=compra_data['proveedor_id'],
                    subtotal=compra_data['subtotal'],
                    iva=compra_data['iva'],
                    total=compra_data['total'],
                    usuario_id=compra_data['usuario_id']
                )
                compras.append(compra)
            
            return compras
            
        except Exception as e:
            logger.error(f"Error obteniendo compras por proveedor: {e}")
            raise DatabaseError("Error al obtener compras por proveedor")