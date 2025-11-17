from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class InventarioMovimiento:
    """Modelo de movimiento de inventario"""
    id: Optional[int] = None
    producto_id: int = 0
    tipo: str = ""  # entrada, salida, ajuste
    cantidad: int = 0
    cantidad_anterior: int = 0
    cantidad_nueva: int = 0
    motivo: str = ""
    referencia_id: Optional[int] = None
    referencia_tipo: Optional[str] = None  # venta, compra
    usuario_id: int = 0
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'tipo': self.tipo,
            'cantidad': self.cantidad,
            'cantidad_anterior': self.cantidad_anterior,
            'cantidad_nueva': self.cantidad_nueva,
            'motivo': self.motivo,
            'referencia_id': self.referencia_id,
            'referencia_tipo': self.referencia_tipo,
            'usuario_id': self.usuario_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }