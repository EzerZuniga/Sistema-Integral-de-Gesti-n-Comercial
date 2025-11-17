from config.database import db
from models.proveedor import Proveedor
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from core.security import security
from core.utils import utils

class ProveedorService:
    """Servicio para gestión de proveedores"""
    
    @staticmethod
    def obtener_todos(activos_only: bool = True):
        """Obtener todos los proveedores"""
        try:
            if activos_only:
                query = "SELECT * FROM proveedores WHERE activo = 1 ORDER BY nombre"
            else:
                query = "SELECT * FROM proveedores ORDER BY nombre"
            
            results = db.execute_query(query)
            return [Proveedor.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error obteniendo proveedores: {e}")
            raise DatabaseError("Error al obtener proveedores")
    
    @staticmethod
    def obtener_por_id(proveedor_id: int):
        """Obtener proveedor por ID"""
        try:
            query = "SELECT * FROM proveedores WHERE id = ?"
            result = db.execute_query(query, (proveedor_id,))
            return Proveedor.from_dict(dict(result[0])) if result else None
        except Exception as e:
            logger.error(f"Error obteniendo proveedor {proveedor_id}: {e}")
            raise DatabaseError("Error al obtener proveedor")
    
    @staticmethod
    def crear_proveedor(proveedor: Proveedor):
        """Crear nuevo proveedor"""
        try:
            # Validaciones
            if not proveedor.nombre or not proveedor.rut:
                raise ValidationError("Nombre y RUT son obligatorios")
            
            if not security.validate_rut(proveedor.rut):
                raise ValidationError("RUT inválido")
            
            if proveedor.email and not utils.validate_email(proveedor.email):
                raise ValidationError("Email inválido")
            
            # Verificar si el RUT ya existe
            query_check = "SELECT id FROM proveedores WHERE rut = ?"
            existing = db.execute_query(query_check, (proveedor.rut,))
            if existing:
                raise ValidationError("Ya existe un proveedor con este RUT")
            
            query = """
                INSERT INTO proveedores 
                (nombre, rut, direccion, telefono, email, producto_principal, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                proveedor.nombre, proveedor.rut, proveedor.direccion,
                proveedor.telefono, proveedor.email, proveedor.producto_principal,
                proveedor.activo
            )
            
            proveedor_id = db.execute_query(query, params)
            logger.info(f"Proveedor creado: {proveedor.nombre}")
            return proveedor_id
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            raise DatabaseError("Error al crear proveedor")
    
    @staticmethod
    def actualizar_proveedor(proveedor_id: int, **kwargs):
        """Actualizar proveedor"""
        try:
            campos = []
            valores = []
            
            for campo, valor in kwargs.items():
                if valor is not None:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos:
                raise ValidationError("No hay datos para actualizar")
            
            valores.append(proveedor_id)
            query = f"UPDATE proveedores SET {', '.join(campos)} WHERE id = ?"
            db.execute_query(query, valores)
            
            logger.info(f"Proveedor {proveedor_id} actualizado")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando proveedor {proveedor_id}: {e}")
            raise DatabaseError("Error al actualizar proveedor")
    
    @staticmethod
    def desactivar_proveedor(proveedor_id: int):
        """Desactivar proveedor (eliminación lógica)"""
        try:
            query = "UPDATE proveedores SET activo = 0 WHERE id = ?"
            db.execute_query(query, (proveedor_id,))
            logger.info(f"Proveedor {proveedor_id} desactivado")
            return True
        except Exception as e:
            logger.error(f"Error desactivando proveedor {proveedor_id}: {e}")
            raise DatabaseError("Error al desactivar proveedor")
    
    @staticmethod
    def buscar_por_nombre(nombre: str):
        """Buscar proveedores por nombre"""
        try:
            query = "SELECT * FROM proveedores WHERE nombre LIKE ? ORDER BY nombre"
            params = (f"%{nombre}%",)
            results = db.execute_query(query, params)
            return [Proveedor.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error buscando proveedores: {e}")
            raise DatabaseError("Error al buscar proveedores")