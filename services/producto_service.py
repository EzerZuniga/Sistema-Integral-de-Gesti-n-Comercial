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

    @staticmethod
    def crear_producto(producto: Producto):
        """Insertar un nuevo producto en la base de datos y retornar su id."""
        try:
            query = """
                INSERT INTO productos (
                    codigo, nombre, descripcion, categoria,
                    precio_compra, precio_venta, stock_actual,
                    stock_minimo, stock_maximo, proveedor_id, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                producto.codigo,
                producto.nombre,
                producto.descripcion,
                producto.categoria,
                producto.precio_compra,
                producto.precio_venta,
                producto.stock_actual,
                producto.stock_minimo,
                producto.stock_maximo,
                producto.proveedor_id,
                1 if producto.activo else 0
            )
            new_id = db.execute_query(query, params)
            logger.info(f"Producto creado con id {new_id}")
            return new_id
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            raise DatabaseError("Error al crear producto")

    @staticmethod
    def actualizar_producto(producto_id: int, **fields):
        """Actualizar campos de un producto. Campos pasados como kwargs."""
        try:
            if not fields:
                return True

            # Mapear campos permitidos a columnas
            allowed = {
                'codigo': 'codigo',
                'nombre': 'nombre',
                'descripcion': 'descripcion',
                'categoria': 'categoria',
                'precio_compra': 'precio_compra',
                'precio_venta': 'precio_venta',
                'stock_actual': 'stock_actual',
                'stock_minimo': 'stock_minimo',
                'stock_maximo': 'stock_maximo',
                'proveedor_id': 'proveedor_id',
                'activo': 'activo'
            }

            set_clauses = []
            params = []
            for key, value in fields.items():
                if key in allowed:
                    set_clauses.append(f"{allowed[key]} = ?")
                    # Ensure boolean is stored as int
                    if key == 'activo':
                        params.append(1 if value else 0)
                    else:
                        params.append(value)

            if not set_clauses:
                return True

            query = f"UPDATE productos SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(producto_id)

            db.execute_query(query, tuple(params))
            logger.info(f"Producto {producto_id} actualizado: {fields}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando producto {producto_id}: {e}")
            raise DatabaseError("Error al actualizar producto")
