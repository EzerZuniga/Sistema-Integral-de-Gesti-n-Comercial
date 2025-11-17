from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class Trabajador:
    """Modelo de trabajador"""
    id: Optional[int] = None
    rut: str = ""
    nombre: str = ""
    apellido: str = ""
    cargo: str = ""
    telefono: str = ""
    email: str = ""
    salario: float = 0.0
    fecha_contratacion: Optional[date] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    
    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'rut': self.rut,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'cargo': self.cargo,
            'telefono': self.telefono,
            'email': self.email,
            'salario': self.salario,
            'fecha_contratacion': self.fecha_contratacion.isoformat() if self.fecha_contratacion else None,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Trabajador':
        """Crear desde diccionario"""
        fecha_contratacion = None
        if data.get('fecha_contratacion'):
            fecha_contratacion = date.fromisoformat(data['fecha_contratacion'])
        
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            id=data.get('id'),
            rut=data.get('rut', ''),
            nombre=data.get('nombre', ''),
            apellido=data.get('apellido', ''),
            cargo=data.get('cargo', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            salario=float(data.get('salario', 0)),
            fecha_contratacion=fecha_contratacion,
            activo=bool(data.get('activo', True)),
            created_at=created_at
        )