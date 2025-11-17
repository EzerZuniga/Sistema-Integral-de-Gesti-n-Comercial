from config.database import db
from models.inventario import InventarioMovimiento
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from datetime import datetime

class InventarioService:
    """Servicio para gestión de inventario"""
    
    @staticmethod
    def registrar_movimiento(
        producto_id: int,
        tipo: str,
        cantidad: int,
        cantidad_anterior: int,
        cantidad_nueva: int,
        motivo: str = "",
        referencia_id: int = None,
        referencia_tipo: str = None,
        usuario_id: int = None
    ):
        """Registrar movimiento de inventario"""
        try:
            # Validaciones
            if tipo not in ['entrada', 'salida', 'ajuste']:
                raise ValidationError("Tipo de movimiento inválido")
            
            if cantidad <= 0:
                raise ValidationError("La cantidad debe ser mayor a cero")
            
            query = """
                INSERT INTO inventario_movimientos 
                (producto_id, tipo, cantidad, cantidad_anterior, cantidad_nueva, 
                 motivo, referencia_id, referencia_tipo, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                producto_id, tipo, cantidad, cantidad_anterior, cantidad_nueva,
                motivo, referencia_id, referencia_tipo, usuario_id
            )
            
            movimiento_id = db.execute_query(query, params)
            logger.info(f"Movimiento de inventario registrado: {tipo} para producto {producto_id}")
            return movimiento_id
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error registrando movimiento de inventario: {e}")
            raise DatabaseError("Error al registrar movimiento de inventario")
    
    @staticmethod
    def obtener_movimientos_por_producto(producto_id: int, limit: int = 100):
        """Obtener movimientos de inventario por producto"""
        try:
            query = """
                SELECT im.*, p.nombre as producto_nombre, u.nombre as usuario_nombre
                FROM inventario_movimientos im
                LEFT JOIN productos p ON im.producto_id = p.id
                LEFT JOIN usuarios u ON im.usuario_id = u.id
                WHERE im.producto_id = ?
                ORDER BY im.created_at DESC
                LIMIT ?
            """
            results = db.execute_query(query, (producto_id, limit))
            
            movimientos = []
            for row in results:
                movimiento_data = dict(row)
                movimiento = InventarioMovimiento(
                    id=movimiento_data['id'],
                    producto_id=movimiento_data['producto_id'],
                    tipo=movimiento_data['tipo'],
                    cantidad=movimiento_data['cantidad'],
                    cantidad_anterior=movimiento_data['cantidad_anterior'],
                    cantidad_nueva=movimiento_data['cantidad_nueva'],
                    motivo=movimiento_data['motivo'],
                    referencia_id=movimiento_data['referencia_id'],
                    referencia_tipo=movimiento_data['referencia_tipo'],
                    usuario_id=movimiento_data['usuario_id'],
                    created_at=datetime.fromisoformat(movimiento_data['created_at']) if movimiento_data['created_at'] else None
                )
                movimientos.append(movimiento)
            
            return movimientos
            
        except Exception as e:
            logger.error(f"Error obteniendo movimientos para producto {producto_id}: {e}")
            raise DatabaseError("Error al obtener movimientos de inventario")
    
    @staticmethod
    def obtener_movimientos_por_fecha(fecha_inicio: datetime, fecha_fin: datetime):
        """Obtener movimientos por rango de fechas"""
        try:
            query = """
                SELECT im.*, p.nombre as producto_nombre, p.codigo as producto_codigo,
                       u.nombre as usuario_nombre
                FROM inventario_movimientos im
                LEFT JOIN productos p ON im.producto_id = p.id
                LEFT JOIN usuarios u ON im.usuario_id = u.id
                WHERE im.created_at BETWEEN ? AND ?
                ORDER BY im.created_at DESC
            """
            params = (fecha_inicio, fecha_fin)
            results = db.execute_query(query, params)
            
            movimientos = []
            for row in results:
                movimiento_data = dict(row)
                movimiento = InventarioMovimiento(
                    id=movimiento_data['id'],
                    producto_id=movimiento_data['producto_id'],
                    tipo=movimiento_data['tipo'],
                    cantidad=movimiento_data['cantidad'],
                    cantidad_anterior=movimiento_data['cantidad_anterior'],
                    cantidad_nueva=movimiento_data['cantidad_nueva'],
                    motivo=movimiento_data['motivo'],
                    referencia_id=movimiento_data['referencia_id'],
                    referencia_tipo=movimiento_data['referencia_tipo'],
                    usuario_id=movimiento_data['usuario_id'],
                    created_at=datetime.fromisoformat(movimiento_data['created_at']) if movimiento_data['created_at'] else None
                )
                movimientos.append(movimiento)
            
            return movimientos
            
        except Exception as e:
            logger.error(f"Error obteniendo movimientos por fecha: {e}")
            raise DatabaseError("Error al obtener movimientos por fecha")
    
    @staticmethod
    def ajustar_stock(producto_id: int, nueva_cantidad: int, motivo: str, usuario_id: int):
        """Ajustar stock de producto manualmente"""
        conn = None
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Obtener stock actual
            query_stock = "SELECT stock_actual FROM productos WHERE id = ?"
            result = cursor.execute(query_stock, (producto_id,)).fetchone()
            
            if not result:
                raise ValidationError("Producto no encontrado")
            
            stock_actual = result['stock_actual']
            
            if nueva_cantidad < 0:
                raise ValidationError("El stock no puede ser negativo")
            
            # Calcular diferencia
            diferencia = nueva_cantidad - stock_actual
            
            if diferencia == 0:
                logger.info("No hay diferencia en el ajuste de stock")
                return True
            
            # Actualizar stock
            query_update = "UPDATE productos SET stock_actual = ? WHERE id = ?"
            cursor.execute(query_update, (nueva_cantidad, producto_id))
            
            # Registrar movimiento
            tipo = "ajuste"
            InventarioService.registrar_movimiento(
                producto_id=producto_id,
                tipo=tipo,
                cantidad=abs(diferencia),
                cantidad_anterior=stock_actual,
                cantidad_nueva=nueva_cantidad,
                motivo=motivo,
                usuario_id=usuario_id
            )
            
            conn.commit()
            logger.info(f"Stock ajustado para producto {producto_id}: {stock_actual} -> {nueva_cantidad}")
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error ajustando stock: {e}")
            if isinstance(e, ValidationError):
                raise
            raise DatabaseError("Error al ajustar stock")
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def obtener_kpi_inventario():
        """Obtener KPIs del inventario"""
        try:
            # Productos bajo stock mínimo
            query_bajo_stock = """
                SELECT COUNT(*) as count 
                FROM productos 
                WHERE stock_actual <= stock_minimo AND activo = 1
            """
            result_bajo_stock = db.execute_query(query_bajo_stock)
            bajo_stock = result_bajo_stock[0]['count'] if result_bajo_stock else 0
            
            # Productos sobre stock máximo
            query_sobre_stock = """
                SELECT COUNT(*) as count 
                FROM productos 
                WHERE stock_actual > stock_maximo AND activo = 1
            """
            result_sobre_stock = db.execute_query(query_sobre_stock)
            sobre_stock = result_sobre_stock[0]['count'] if result_sobre_stock else 0
            
            # Valor total del inventario
            query_valor = """
                SELECT SUM(stock_actual * precio_compra) as valor_total 
                FROM productos 
                WHERE activo = 1
            """
            result_valor = db.execute_query(query_valor)
            valor_total = result_valor[0]['valor_total'] if result_valor and result_valor[0]['valor_total'] else 0.0
            
            # Productos sin stock
            query_sin_stock = """
                SELECT COUNT(*) as count 
                FROM productos 
                WHERE stock_actual = 0 AND activo = 1
            """
            result_sin_stock = db.execute_query(query_sin_stock)
            sin_stock = result_sin_stock[0]['count'] if result_sin_stock else 0
            
            return {
                'bajo_stock': bajo_stock,
                'sobre_stock': sobre_stock,
                'sin_stock': sin_stock,
                'valor_total': valor_total,
                'total_productos': bajo_stock + sobre_stock + sin_stock
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo KPIs de inventario: {e}")
            raise DatabaseError("Error al obtener KPIs de inventario")