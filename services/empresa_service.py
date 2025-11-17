from config.database import db
from core.exceptions import DatabaseError, ValidationError
from core.logger import logger
from core.security import security

class EmpresaService:
    """Servicio para gestión de empresa"""
    
    @staticmethod
    def obtener_empresa():
        """Obtener datos de la empresa"""
        try:
            query = "SELECT * FROM empresas LIMIT 1"
            result = db.execute_query(query)
            return dict(result[0]) if result else None
        except Exception as e:
            logger.error(f"Error obteniendo empresa: {e}")
            raise DatabaseError("Error al obtener datos de la empresa")
    
    @staticmethod
    def crear_empresa(nombre: str, rut: str, direccion: str = "", telefono: str = "", email: str = ""):
        """Crear nueva empresa"""
        try:
            # Validaciones
            if not nombre or not rut:
                raise ValidationError("Nombre y RUT son obligatorios")
            
            if not security.validate_rut(rut):
                raise ValidationError("RUT inválido")
            
            # Verificar si ya existe una empresa
            empresa_existente = EmpresaService.obtener_empresa()
            if empresa_existente:
                raise ValidationError("Ya existe una empresa registrada")
            
            query = """
                INSERT INTO empresas (nombre, rut, direccion, telefono, email)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (nombre, rut, direccion, telefono, email)
            db.execute_query(query, params)
            
            logger.info(f"Empresa creada: {nombre}")
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creando empresa: {e}")
            raise DatabaseError("Error al crear empresa")
    
    @staticmethod
    def actualizar_empresa(empresa_id: int, **kwargs):
        """Actualizar datos de la empresa"""
        try:
            campos = []
            valores = []
            
            for campo, valor in kwargs.items():
                if valor is not None:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
            
            if not campos:
                raise ValidationError("No hay datos para actualizar")
            
            valores.append(empresa_id)
            query = f"UPDATE empresas SET {', '.join(campos)} WHERE id = ?"
            db.execute_query(query, valores)
            
            logger.info("Empresa actualizada correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando empresa: {e}")
            raise DatabaseError("Error al actualizar empresa")