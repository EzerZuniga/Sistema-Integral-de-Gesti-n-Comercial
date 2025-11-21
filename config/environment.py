import os
from pathlib import Path

class Environment:
    """Configuración del entorno de la aplicación"""
    
    def __init__(self):
        self.mode = os.getenv('APP_MODE', 'development')
        self.debug = self.mode == 'development'
        self.base_dir = Path(__file__).parent.parent
        
    @property
    def database_path(self):
        return self.base_dir / 'data' / 'bodega.db'

    @property
    def database_type(self):
        """Tipo de base de datos: 'sqlite' (por defecto) o 'mysql'"""
        return os.getenv('APP_DB_TYPE', 'sqlite').lower()

    # Parámetros para MySQL (si se usa)
    @property
    def mysql_host(self):
        return os.getenv('APP_DB_HOST', 'localhost')

    @property
    def mysql_port(self):
        try:
            return int(os.getenv('APP_DB_PORT', '3306'))
        except Exception:
            return 3306

    @property
    def mysql_user(self):
        return os.getenv('APP_DB_USER', 'root')

    @property
    def mysql_password(self):
        return os.getenv('APP_DB_PASSWORD', '')

    @property
    def mysql_database(self):
        return os.getenv('APP_DB_NAME', 'donarosa')
    
    @property
    def logs_path(self):
        return self.base_dir / 'data' / 'logs'
    
    @property
    def backups_path(self):
        return self.base_dir / 'data' / 'backups'

# Instancia global
env = Environment()