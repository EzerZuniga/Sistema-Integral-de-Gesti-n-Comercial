from config.database import db
from models.usuario import Usuario
from core.exceptions import AuthenticationError, ValidationError
from core.logger import logger
from core.security import security
from datetime import datetime

class AuthService:
    """Servicio de autenticación y gestión de usuarios"""
    
    _current_user = None
    
    @classmethod
    def login(cls, username: str, password: str) -> Usuario:
        """Iniciar sesión"""
        try:
            if not username or not password:
                raise AuthenticationError("Usuario y contraseña son requeridos")
            
            # Buscar usuario
            query = "SELECT * FROM usuarios WHERE username = ? AND activo = 1"
            result = db.execute_query(query, (username,))
            
            if not result:
                raise AuthenticationError("Usuario o contraseña incorrectos")
            
            usuario_data = dict(result[0])
            
            # Verificar contraseña
            if not security.verify_password(password, usuario_data['password_hash']):
                raise AuthenticationError("Usuario o contraseña incorrectos")
            
            # Crear objeto usuario
            usuario = Usuario(
                id=usuario_data['id'],
                username=usuario_data['username'],
                password_hash=usuario_data['password_hash'],
                nombre=usuario_data['nombre'],
                email=usuario_data['email'],
                rol=usuario_data['rol'],
                activo=usuario_data['activo'],
                created_at=datetime.fromisoformat(usuario_data['created_at']) if usuario_data['created_at'] else None
            )
            
            cls._current_user = usuario
            logger.info(f"Usuario {username} ha iniciado sesión")
            return usuario
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error en login: {e}")
            raise AuthenticationError("Error al iniciar sesión")
    
    @classmethod
    def logout(cls):
        """Cerrar sesión"""
        if cls._current_user:
            logger.info(f"Usuario {cls._current_user.username} ha cerrado sesión")
            cls._current_user = None
    
    @classmethod
    def get_current_user(cls) -> Usuario:
        """Obtener usuario actual"""
        return cls._current_user
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """Verificar si hay usuario autenticado"""
        return cls._current_user is not None
    
    @classmethod
    def has_permission(cls, permission: str) -> bool:
        """Verificar si el usuario actual tiene un permiso"""
        if not cls._current_user:
            return False
        
        if cls._current_user.rol == 'admin':
            return True
        
        # Permisos para vendedor
        vendedor_permissions = ['ventas', 'consulta']
        return permission in vendedor_permissions
    
    @classmethod
    def cambiar_password(cls, current_password: str, new_password: str) -> bool:
        """Cambiar contraseña del usuario actual"""
        try:
            if not cls._current_user:
                raise AuthenticationError("No hay usuario autenticado")
            
            # Verificar contraseña actual
            if not security.verify_password(current_password, cls._current_user.password_hash):
                raise AuthenticationError("Contraseña actual incorrecta")
            
            # Validar nueva contraseña
            if len(new_password) < 6:
                raise ValidationError("La nueva contraseña debe tener al menos 6 caracteres")
            
            # Hashear nueva contraseña
            new_password_hash = security.hash_password(new_password)
            
            # Actualizar en base de datos
            query = "UPDATE usuarios SET password_hash = ? WHERE id = ?"
            db.execute_query(query, (new_password_hash, cls._current_user.id))
            
            # Actualizar en objeto usuario
            cls._current_user.password_hash = new_password_hash
            
            logger.info(f"Contraseña cambiada para usuario {cls._current_user.username}")
            return True
            
        except (AuthenticationError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            raise AuthenticationError("Error al cambiar contraseña")
    
    @classmethod
    def crear_usuario(cls, usuario: Usuario, password: str) -> int:
        """Crear nuevo usuario (solo admin)"""
        try:
            if not cls._current_user or cls._current_user.rol != 'admin':
                raise AuthenticationError("No tiene permisos para crear usuarios")
            
            # Validaciones
            if not usuario.username or not password:
                raise ValidationError("Usuario y contraseña son obligatorios")
            
            if len(password) < 6:
                raise ValidationError("La contraseña debe tener al menos 6 caracteres")
            
            if usuario.email and not security.validate_email(usuario.email):
                raise ValidationError("Email inválido")
            
            # Verificar si el usuario ya existe
            query_check = "SELECT id FROM usuarios WHERE username = ?"
            existing = db.execute_query(query_check, (usuario.username,))
            if existing:
                raise ValidationError("El nombre de usuario ya existe")
            
            # Hashear contraseña
            password_hash = security.hash_password(password)
            usuario.password_hash = password_hash
            
            # Insertar usuario
            query = """
                INSERT INTO usuarios 
                (username, password_hash, nombre, email, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                usuario.username,
                usuario.password_hash,
                usuario.nombre,
                usuario.email,
                usuario.rol,
                usuario.activo
            )
            
            usuario_id = db.execute_query(query, params)
            logger.info(f"Usuario creado: {usuario.username} por {cls._current_user.username}")
            return usuario_id
            
        except (AuthenticationError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise DatabaseError("Error al crear usuario")
    
    @classmethod
    def obtener_usuarios(cls):
        """Obtener todos los usuarios (solo admin)"""
        try:
            if not cls._current_user or cls._current_user.rol != 'admin':
                raise AuthenticationError("No tiene permisos para ver usuarios")
            
            query = "SELECT * FROM usuarios ORDER BY username"
            results = db.execute_query(query)
            
            usuarios = []
            for row in results:
                usuario_data = dict(row)
                usuario = Usuario(
                    id=usuario_data['id'],
                    username=usuario_data['username'],
                    nombre=usuario_data['nombre'],
                    email=usuario_data['email'],
                    rol=usuario_data['rol'],
                    activo=usuario_data['activo'],
                    created_at=datetime.fromisoformat(usuario_data['created_at']) if usuario_data['created_at'] else None
                )
                usuarios.append(usuario)
            
            return usuarios
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}")
            raise DatabaseError("Error al obtener usuarios")