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
    def logs_path(self):
        return self.base_dir / 'data' / 'logs'
    
    @property
    def backups_path(self):
        return self.base_dir / 'data' / 'backups'

# Instancia global
env = Environment()