from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class DetalleVenta:
    """Modelo de detalle de venta"""
    id: Optional[int] = None
    venta_id: Optional[int] = None
    producto_id: int = 0
    cantidad: int = 0
    precio_unitario: float = 0.0
    total_linea: float = 0.0
    
    def calcular_total(self):
        """Calcular total de la línea"""
        self.total_linea = self.cantidad * self.precio_unitario

@dataclass
class Venta:
    """Modelo de venta"""
    id: Optional[int] = None
    numero_boleta: str = ""
    fecha: Optional[datetime] = None
    cliente_nombre: str = ""
    cliente_rut: str = ""
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    usuario_id: int = 0
    created_at: Optional[datetime] = None
    detalles: List[DetalleVenta] = field(default_factory=list)
    
    def agregar_detalle(self, detalle: DetalleVenta):
        """Agregar detalle a la venta"""
        detalle.venta_id = self.id
        self.detalles.append(detalle)
    
    def calcular_totales(self, iva_percent: float = 0.19):
        """Calcular subtotal, IVA y total"""
        self.subtotal = sum(detalle.total_linea for detalle in self.detalles)
        self.iva = self.subtotal * iva_percent
        self.total = self.subtotal + self.iva
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'numero_boleta': self.numero_boleta,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'cliente_nombre': self.cliente_nombre,
            'cliente_rut': self.cliente_rut,
            'subtotal': self.subtotal,
            'iva': self.iva,
            'total': self.total,
            'usuario_id': self.usuario_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'detalles': [{
                'id': detalle.id,
                'producto_id': detalle.producto_id,
                'cantidad': detalle.cantidad,
                'precio_unitario': detalle.precio_unitario,
                'total_linea': detalle.total_linea
            } for detalle in self.detalles]
        }