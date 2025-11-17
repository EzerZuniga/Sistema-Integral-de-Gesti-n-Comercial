import sqlite3
from pathlib import Path
from .environment import env
from core.logger import logger

class Database:
    """Manejador de base de datos SQLite"""
    
    def __init__(self):
        self._create_database()
    
    def _create_database(self):
        """Crear la base de datos y directorios necesarios"""
        try:
            # Crear directorios si no existen
            env.logs_path.mkdir(parents=True, exist_ok=True)
            env.backups_path.mkdir(parents=True, exist_ok=True)
            env.database_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not env.database_path.exists():
                logger.info("Creando nueva base de datos...")
                self._create_tables()
            else:
                logger.info("Base de datos encontrada")
                
        except Exception as e:
            logger.error(f"Error al crear base de datos: {e}")
            raise
    
    def _create_tables(self):
        """Crear las tablas iniciales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Tabla de empresas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empresas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    rut TEXT UNIQUE NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    email TEXT,
                    rol TEXT NOT NULL, -- admin, vendedor
                    activo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de trabajadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trabajadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rut TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    cargo TEXT NOT NULL,
                    telefono TEXT,
                    email TEXT,
                    salario REAL,
                    fecha_contratacion DATE,
                    activo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de proveedores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    rut TEXT UNIQUE NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT,
                    producto_principal TEXT,
                    activo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de productos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    categoria TEXT NOT NULL,
                    precio_compra REAL NOT NULL,
                    precio_venta REAL NOT NULL,
                    stock_actual INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 10,
                    stock_maximo INTEGER DEFAULT 100,
                    proveedor_id INTEGER,
                    activo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proveedor_id) REFERENCES proveedores (id)
                )
            ''')
            
            # Tabla de ventas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_boleta TEXT UNIQUE NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cliente_nombre TEXT,
                    cliente_rut TEXT,
                    subtotal REAL NOT NULL,
                    iva REAL NOT NULL,
                    total REAL NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de detalle_ventas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    total_linea REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas (id),
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            ''')
            
            # Tabla de compras
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_factura TEXT UNIQUE NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    proveedor_id INTEGER NOT NULL,
                    subtotal REAL NOT NULL,
                    iva REAL NOT NULL,
                    total REAL NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proveedor_id) REFERENCES proveedores (id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de detalle_compras
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_compras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    compra_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    total_linea REAL NOT NULL,
                    FOREIGN KEY (compra_id) REFERENCES compras (id),
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            ''')
            
            # Tabla de inventario_movimientos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventario_movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL, -- entrada, salida, ajuste
                    cantidad INTEGER NOT NULL,
                    cantidad_anterior INTEGER NOT NULL,
                    cantidad_nueva INTEGER NOT NULL,
                    motivo TEXT,
                    referencia_id INTEGER, -- id de venta/compra
                    referencia_tipo TEXT, -- venta, compra
                    usuario_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (producto_id) REFERENCES productos (id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Tablas creadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error al crear tablas: {e}")
            raise
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            conn = sqlite3.connect(env.database_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise
    
    def execute_query(self, query, params=()):
        """Ejecutar consulta y retornar resultados"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
            
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error en consulta: {e}")
            raise

# Instancia global de base de datos
db = Database()