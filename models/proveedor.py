from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Proveedor:
    """Modelo de proveedor"""
    id: Optional[int] = None
    nombre: str = ""
    rut: str = ""
    direccion: str = ""
    telefono: str = ""
    email: str = ""
    producto_principal: str = ""
    activo: bool = True
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'rut': self.rut,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'producto_principal': self.producto_principal,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Proveedor':
        """Crear desde diccionario"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            rut=data.get('rut', ''),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            producto_principal=data.get('producto_principal', ''),
            activo=bool(data.get('activo', True)),
            created_at=created_at
        )