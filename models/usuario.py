from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Usuario:
    """Modelo de usuario del sistema"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    nombre: str = ""
    email: str = ""
    rol: str = "trabajador"  # admin, trabajador
    activo: bool = True
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'username': self.username,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """Crear desde diccionario"""
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            nombre=data.get('nombre', ''),
            email=data.get('email', ''),
            rol=data.get('rol', 'trabajador'),
            activo=bool(data.get('activo', True)),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )