from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Producto:
    """Modelo de producto"""
    id: Optional[int] = None
    codigo: str = ""
    nombre: str = ""
    descripcion: str = ""
    categoria: str = ""
    precio_compra: float = 0.0
    precio_venta: float = 0.0
    stock_actual: int = 0
    stock_minimo: int = 10
    stock_maximo: int = 100
    proveedor_id: Optional[int] = None
    activo: bool = True
    created_at: Optional[datetime] = None
    
    @property
    def margen_ganancia(self) -> float:
        """Calcular margen de ganancia"""
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0.0
    
    @property
    def necesita_reposicion(self) -> bool:
        """Verificar si necesita reposición"""
        return self.stock_actual <= self.stock_minimo
    
    @property
    def sobre_stock(self) -> bool:
        """Verificar si tiene exceso de stock"""
        return self.stock_actual > self.stock_maximo
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'precio_compra': self.precio_compra,
            'precio_venta': self.precio_venta,
            'stock_actual': self.stock_actual,
            'stock_minimo': self.stock_minimo,
            'stock_maximo': self.stock_maximo,
            'proveedor_id': self.proveedor_id,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Producto':
        """Crear desde diccionario"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            id=data.get('id'),
            codigo=data.get('codigo', ''),
            nombre=data.get('nombre', ''),
            descripcion=data.get('descripcion', ''),
            categoria=data.get('categoria', ''),
            precio_compra=float(data.get('precio_compra', 0)),
            precio_venta=float(data.get('precio_venta', 0)),
            stock_actual=int(data.get('stock_actual', 0)),
            stock_minimo=int(data.get('stock_minimo', 10)),
            stock_maximo=int(data.get('stock_maximo', 100)),
            proveedor_id=data.get('proveedor_id'),
            activo=bool(data.get('activo', True)),
            created_at=created_at
        )