import sqlite3
from pathlib import Path
from .environment import env
from core.logger import logger

# Intentar importar driver MySQL (PyMySQL). Si no está disponible, seguiremos usando sqlite.
try:
    import pymysql
    from pymysql.cursors import DictCursor
    _HAS_PYMYSQL = True
except Exception:
    pymysql = None
    DictCursor = None
    _HAS_PYMYSQL = False

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
            # Soporte para MySQL vía variables de entorno
            if env.database_type == 'mysql' and _HAS_PYMYSQL:
                # Intentar conectar al servidor MySQL y crear la base de datos si no existe
                logger.info("Usando MySQL como backend de datos")
                conn = pymysql.connect(host=env.mysql_host, port=env.mysql_port,
                                       user=env.mysql_user, password=env.mysql_password,
                                       cursorclass=DictCursor, autocommit=True)
                try:
                    cur = conn.cursor()
                    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{env.mysql_database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                    logger.info(f"Verificando base de datos MySQL: {env.mysql_database}")
                finally:
                    conn.close()
                # Crear tablas si es necesario (no tenemos un archivo .db para comprobar)
                self._create_tables()
            else:
                # SQLite por defecto
                if not env.database_path.exists():
                    logger.info("Creando nueva base de datos SQLite...")
                    self._create_tables()
                else:
                    logger.info("Base de datos SQLite encontrada")
                
        except Exception as e:
            logger.error(f"Error al crear base de datos: {e}")
            raise
    
    def _create_tables(self):
        """Crear las tablas iniciales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Tabla de empresas
            # SQL compatible tanto para SQLite como para MySQL (con leves diferencias manejadas por el DBMS)
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
                    rol TEXT NOT NULL,
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
            
            # Para MySQL commit lo maneja el cursor/connection según autocommit
            try:
                conn.commit()
            except Exception:
                pass
            conn.close()
            logger.info("Tablas creadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error al crear tablas: {e}")
            raise
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            if env.database_type == 'mysql' and _HAS_PYMYSQL:
                # Conectar a la base de datos MySQL y devolver connection con DictCursor
                conn = pymysql.connect(host=env.mysql_host,
                                       port=env.mysql_port,
                                       user=env.mysql_user,
                                       password=env.mysql_password,
                                       database=env.mysql_database,
                                       cursorclass=DictCursor,
                                       autocommit=False)
                return conn
            else:
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

            # PyMySQL usa %s como placeholder; sqlite3 usa ? -- asumimos que las consultas
            # en el código usan ? (sqlite). Para compatibilidad simple, si usamos MySQL
            # convertimos placeholders '?' -> '%s' en el query.
            use_mysql = env.database_type == 'mysql' and _HAS_PYMYSQL
            if use_mysql:
                # Reemplazar todos los '?' por '%s' salvo si ya hay '%s'
                if '?' in query:
                    query = query.replace('?', '%s')

            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                # En MySQL con DictCursor obtenemos dicts; en sqlite Row -> sqlite.Row
                rows = cursor.fetchall()
                # Normalizar a lista de dicts
                if isinstance(rows, list):
                    result = [dict(r) if not isinstance(r, dict) else r for r in rows]
                else:
                    result = rows
            else:
                conn.commit()
                try:
                    result = cursor.lastrowid
                except Exception:
                    result = None

            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Error en consulta: {e}")
            raise

# Instancia global de base de datos
db = Database()