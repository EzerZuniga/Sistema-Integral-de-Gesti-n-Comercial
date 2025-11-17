from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class DetalleCompra:
    """Modelo de detalle de compra"""
    id: Optional[int] = None
    compra_id: Optional[int] = None
    producto_id: int = 0
    cantidad: int = 0
    precio_unitario: float = 0.0
    total_linea: float = 0.0
    
    def calcular_total(self):
        """Calcular total de la línea"""
        self.total_linea = self.cantidad * self.precio_unitario

@dataclass
class Compra:
    """Modelo de compra"""
    id: Optional[int] = None
    numero_factura: str = ""
    fecha: Optional[datetime] = None
    proveedor_id: int = 0
    subtotal: float = 0.0
    iva: float = 0.0
    total: float = 0.0
    usuario_id: int = 0
    created_at: Optional[datetime] = None
    detalles: List[DetalleCompra] = field(default_factory=list)
    
    def agregar_detalle(self, detalle: DetalleCompra):
        """Agregar detalle a la compra"""
        detalle.compra_id = self.id
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
            'numero_factura': self.numero_factura,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'proveedor_id': self.proveedor_id,
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