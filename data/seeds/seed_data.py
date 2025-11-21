from config.database import db
from core.security import security
from core.logger import logger
from datetime import datetime, date

class SeedData:
    """Clase para cargar datos iniciales en la base de datos"""
    
    @staticmethod
    def cargar_datos_iniciales():
        """Cargar todos los datos iniciales"""
        try:
            # Verificar si ya existen datos
            if SeedData._existen_datos():
                logger.info("Ya existen datos en la base de datos, omitiendo carga inicial")
                return
            
            logger.info("Cargando datos iniciales...")
            
            # Cargar datos en orden
            SeedData._cargar_empresa()
            SeedData._cargar_usuarios()
            SeedData._cargar_proveedores()
            SeedData._cargar_trabajadores()
            SeedData._cargar_productos()
            
            logger.info("Datos iniciales cargados exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {e}")
            raise
    
    @staticmethod
    def _existen_datos() -> bool:
        """Verificar si ya existen datos en la base de datos"""
        try:
            # Verificar si existe la empresa
            query = "SELECT COUNT(*) as count FROM empresas"
            result = db.execute_query(query)
            return result[0]['count'] > 0 if result else False
        except Exception:
            return False
    
    @staticmethod
    def _cargar_empresa():
        """Cargar datos de la empresa"""
        query = """
            INSERT INTO empresas (nombre, rut, direccion, telefono, email)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            "Bodega Doña Rosa",
            "76234567-8",
            "Av. Principal 123, Santiago",
            "+56 2 2345 6789",
            "contacto@bodegadonarosa.cl"
        )
        db.execute_query(query, params)
        logger.info("Datos de empresa cargados")
    
    @staticmethod
    def _cargar_usuarios():
        """Cargar usuarios iniciales"""
        usuarios = [
            {
                'username': 'admin',
                'password': 'admin123',
                'nombre': 'Administrador',
                'email': 'admin@bodegadonarosa.cl',
                'rol': 'admin'
            },
            {
                'username': 'trabajador',
                'password': 'trabajador123',
                'nombre': 'Trabajador Principal',
                'email': 'ventas@bodegadonarosa.cl',
                'rol': 'trabajador'
            }
        ]
        
        for usuario_data in usuarios:
            password_hash = security.hash_password(usuario_data['password'])
            query = """
                INSERT INTO usuarios (username, password_hash, nombre, email, rol)
                VALUES (?, ?, ?, ?, ?)
            """
            params = (
                usuario_data['username'],
                password_hash,
                usuario_data['nombre'],
                usuario_data['email'],
                usuario_data['rol']
            )
            db.execute_query(query, params)
        
        logger.info("Usuarios iniciales cargados")
    
    @staticmethod
    def _cargar_proveedores():
        """Cargar proveedores iniciales"""
        proveedores = [
            {
                'nombre': 'Distribuidora Alimentos S.A.',
                'rut': '12345678-9',
                'direccion': 'Av. Industrial 456, Santiago',
                'telefono': '+56 2 2456 7890',
                'email': 'ventas@dalimentos.cl',
                'producto_principal': 'Abarrotes'
            },
            {
                'nombre': 'Lácteos Frescos Ltda.',
                'rut': '23456789-0',
                'direccion': 'Camino La lechera 789, Rancagua',
                'telefono': '+56 72 2789 0123',
                'email': 'pedidos@lacteosfrescos.cl',
                'producto_principal': 'Lácteos'
            },
            {
                'nombre': 'Bebidas Nacionales S.A.',
                'rut': '34567890-1',
                'direccion': 'Av. del Vino 321, Curicó',
                'telefono': '+56 75 2901 2345',
                'email': 'contacto@bebidasnacionales.cl',
                'producto_principal': 'Bebidas'
            }
        ]
        
        for proveedor_data in proveedores:
            query = """
                INSERT INTO proveedores (nombre, rut, direccion, telefono, email, producto_principal)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                proveedor_data['nombre'],
                proveedor_data['rut'],
                proveedor_data['direccion'],
                proveedor_data['telefono'],
                proveedor_data['email'],
                proveedor_data['producto_principal']
            )
            db.execute_query(query, params)
        
        logger.info("Proveedores iniciales cargados")
    
    @staticmethod
    def _cargar_trabajadores():
        """Cargar trabajadores iniciales"""
        trabajadores = [
            {
                'rut': '11222333-4',
                'nombre': 'María',
                'apellido': 'González',
                'cargo': 'Dueña',
                'telefono': '+56 9 8765 4321',
                'email': 'maria.gonzalez@bodegadonarosa.cl',
                'salario': 850000,
                'fecha_contratacion': date(2020, 1, 15)
            },
            {
                'rut': '22333444-5',
                'nombre': 'Pedro',
                'apellido': 'Martínez',
                'cargo': 'Vendedor',
                'telefono': '+56 9 7654 3210',
                'email': 'pedro.martinez@bodegadonarosa.cl',
                'salario': 450000,
                'fecha_contratacion': date(2021, 3, 1)
            },
            {
                'rut': '33444555-6',
                'nombre': 'Ana',
                'apellido': 'Silva',
                'cargo': 'Cajera',
                'telefono': '+56 9 6543 2109',
                'email': 'ana.silva@bodegadonarosa.cl',
                'salario': 420000,
                'fecha_contratacion': date(2021, 6, 15)
            }
        ]
        
        for trabajador_data in trabajadores:
            query = """
                INSERT INTO trabajadores 
                (rut, nombre, apellido, cargo, telefono, email, salario, fecha_contratacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                trabajador_data['rut'],
                trabajador_data['nombre'],
                trabajador_data['apellido'],
                trabajador_data['cargo'],
                trabajador_data['telefono'],
                trabajador_data['email'],
                trabajador_data['salario'],
                trabajador_data['fecha_contratacion']
            )
            db.execute_query(query, params)
        
        logger.info("Trabajadores iniciales cargados")
    
    @staticmethod
    def _cargar_productos():
        """Cargar productos iniciales"""
        productos = [
            {
                'codigo': 'ARROZ-001',
                'nombre': 'Arroz Grado 1',
                'descripcion': 'Arroz grano largo 1kg',
                'categoria': 'Abarrotes',
                'precio_compra': 800,
                'precio_venta': 1200,
                'stock_actual': 50,
                'stock_minimo': 10,
                'stock_maximo': 100,
                'proveedor_id': 1
            },
            {
                'codigo': 'LECHE-001',
                'nombre': 'Leche Entera',
                'descripcion': 'Leche entera 1L',
                'categoria': 'Lácteos',
                'precio_compra': 600,
                'precio_venta': 850,
                'stock_actual': 30,
                'stock_minimo': 15,
                'stock_maximo': 80,
                'proveedor_id': 2
            },
            {
                'codigo': 'AZUCAR-001',
                'nombre': 'Azúcar Rubia',
                'descripcion': 'Azúcar rubia 1kg',
                'categoria': 'Abarrotes',
                'precio_compra': 700,
                'precio_venta': 950,
                'stock_actual': 40,
                'stock_minimo': 8,
                'stock_maximo': 60,
                'proveedor_id': 1
            },
            {
                'codigo': 'ACEITE-001',
                'nombre': 'Aceite Vegetal',
                'descripcion': 'Aceite vegetal 1L',
                'categoria': 'Abarrotes',
                'precio_compra': 1200,
                'precio_venta': 1800,
                'stock_actual': 25,
                'stock_minimo': 5,
                'stock_maximo': 40,
                'proveedor_id': 1
            },
            {
                'codigo': 'COCA-001',
                'nombre': 'Coca-Cola',
                'descripcion': 'Coca-Cola 1.5L',
                'categoria': 'Bebidas',
                'precio_compra': 800,
                'precio_venta': 1200,
                'stock_actual': 35,
                'stock_minimo': 12,
                'stock_maximo': 50,
                'proveedor_id': 3
            }
        ]
        
        for producto_data in productos:
            query = """
                INSERT INTO productos 
                (codigo, nombre, descripcion, categoria, precio_compra, precio_venta,
                 stock_actual, stock_minimo, stock_maximo, proveedor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                producto_data['codigo'],
                producto_data['nombre'],
                producto_data['descripcion'],
                producto_data['categoria'],
                producto_data['precio_compra'],
                producto_data['precio_venta'],
                producto_data['stock_actual'],
                producto_data['stock_minimo'],
                producto_data['stock_maximo'],
                producto_data['proveedor_id']
            )
            db.execute_query(query, params)
        
        logger.info("Productos iniciales cargados")

# Ejecutar carga de datos si se ejecuta directamente
if __name__ == "__main__":
    SeedData.cargar_datos_iniciales()