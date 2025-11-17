from config.database import db
from models.trabajador import Trabajador
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from core.security import security
from core.utils import utils

class TrabajadorService:
    """Servicio para gestión de trabajadores"""
    
    @staticmethod
    def obtener_todos(activos_only: bool = True):
        """Obtener todos los trabajadores"""
        try:
            if activos_only:
                query = "SELECT * FROM trabajadores WHERE activo = 1 ORDER BY nombre, apellido"
            else:
                query = "SELECT * FROM trabajadores ORDER BY nombre, apellido"
            
            results = db.execute_query(query)
            return [Trabajador.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error obteniendo trabajadores: {e}")
            raise DatabaseError("Error al obtener trabajadores")
    
    @staticmethod
    def obtener_por_id(trabajador_id: int):
        """Obtener trabajador por ID"""
        try:
            query = "SELECT * FROM trabajadores WHERE id = ?"
            result = db.execute_query(query, (trabajador_id,))
            return Trabajador.from_dict(dict(result[0])) if result else None
        except Exception as e:
            logger.error(f"Error obteniendo trabajador {trabajador_id}: {e}")
            raise DatabaseError("Error al obtener trabajador")
    
    @staticmethod
    def crear_trabajador(trabajador: Trabajador):
        """Crear nuevo trabajador"""
        try:
            # Validaciones
            if not trabajador.rut or not trabajador.nombre or not trabajador.apellido:
                raise ValidationError("RUT, nombre y apellido son obligatorios")
            
            if not security.validate_rut(trabajador.rut):
                raise ValidationError("RUT inválido")
            
            if trabajador.email and not utils.validate_email(trabajador.email):
                raise ValidationError("Email inválido")
            
            # Verificar si el RUT ya existe
            query_check = "SELECT id FROM trabajadores WHERE rut = ?"
            existing = db.execute_query(query_check, (trabajador.rut,))
            if existing:
                raise ValidationError("Ya existe un trabajador con este RUT")
            
            query = """
                INSERT INTO trabajadores 
                (rut, nombre, apellido, cargo, telefono, email, salario, fecha_contratacion, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                trabajador.rut, trabajador.nombre, trabajador.apellido, trabajador.cargo,
                trabajador.telefono, trabajador.email, trabajador.salario,
                trabajador.fecha_contratacion, trabajador.activo
            )
            
            trabajador_id = db.execute_query(query, params)
            logger.info(f"Trabajador creado: {trabajador.nombre} {trabajador.apellido}")
            return trabajador_id
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creando trabajador: {e}")
            raise DatabaseError("Error al crear trabajador")
    
    @staticmethod
    def actualizar_trabajador(trabajador_id: int, **kwargs):
        """Actualizar trabajador"""
        try:
            campos = []
            valores = []
            
            for campo, valor in kwargs.items():
                if valor is not None:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos:
                raise ValidationError("No hay datos para actualizar")
            
            valores.append(trabajador_id)
            query = f"UPDATE trabajadores SET {', '.join(campos)} WHERE id = ?"
            db.execute_query(query, valores)
            
            logger.info(f"Trabajador {trabajador_id} actualizado")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando trabajador {trabajador_id}: {e}")
            raise DatabaseError("Error al actualizar trabajador")
    
    @staticmethod
    def desactivar_trabajador(trabajador_id: int):
        """Desactivar trabajador (eliminación lógica)"""
        try:
            query = "UPDATE trabajadores SET activo = 0 WHERE id = ?"
            db.execute_query(query, (trabajador_id,))
            logger.info(f"Trabajador {trabajador_id} desactivado")
            return True
        except Exception as e:
            logger.error(f"Error desactivando trabajador {trabajador_id}: {e}")
            raise DatabaseError("Error al desactivar trabajador")
    
    @staticmethod
    def buscar_por_nombre(nombre: str):
        """Buscar trabajadores por nombre"""
        try:
            query = "SELECT * FROM trabajadores WHERE nombre LIKE ? OR apellido LIKE ? ORDER BY nombre"
            params = (f"%{nombre}%", f"%{nombre}%")
            results = db.execute_query(query, params)
            return [Trabajador.from_dict(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Error buscando trabajadores: {e}")
            raise DatabaseError("Error al buscar trabajadores")