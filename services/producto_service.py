from config.database import db
from models.producto import Producto
from core.logger import logger
from core.exceptions import DatabaseError


class ProductoService:
    """Servicio mínimo para productos requerido por otros servicios."""

    @staticmethod
    def obtener_por_id(producto_id: int):
        try:
            query = "SELECT * FROM productos WHERE id = ?"
            result = db.execute_query(query, (producto_id,))
            if not result:
                return None
            data = dict(result[0])
            return Producto.from_dict(data)
        except Exception as e:
            logger.error(f"Error obteniendo producto {producto_id}: {e}")
            raise DatabaseError("Error al obtener producto")

    @staticmethod
    def actualizar_stock(producto_id: int, nuevo_stock: int):
        try:
            query = "UPDATE productos SET stock_actual = ? WHERE id = ?"
            db.execute_query(query, (nuevo_stock, producto_id))
            return True
        except Exception as e:
            logger.error(f"Error actualizando stock producto {producto_id}: {e}")
            raise DatabaseError("Error al actualizar stock")

    @staticmethod
    def obtener_todos(activos_only: bool = True):
        try:
            if activos_only:
                query = "SELECT * FROM productos WHERE activo = 1 ORDER BY nombre"
                results = db.execute_query(query)
            else:
                query = "SELECT * FROM productos ORDER BY nombre"
                results = db.execute_query(query)

            productos = []
            for row in results:
                productos.append(Producto.from_dict(dict(row)))
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            raise DatabaseError("Error al obtener productos")

    @staticmethod
    def obtener_productos_bajo_stock():
        try:
            query = "SELECT * FROM productos WHERE stock_actual <= stock_minimo AND activo = 1 ORDER BY stock_actual ASC"
            results = db.execute_query(query)
            productos = [Producto.from_dict(dict(r)) for r in results]
            return productos
        except Exception as e:
            logger.error(f"Error obteniendo productos bajo stock: {e}")
            raise DatabaseError("Error al obtener productos bajo stock")
