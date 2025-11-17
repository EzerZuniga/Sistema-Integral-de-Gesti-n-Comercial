import logging
import sys
from pathlib import Path
from datetime import datetime
from config.environment import env

class Logger:
    """Sistema de logging para la aplicación"""
    
    def __init__(self):
        self._setup_logging()
    
    def _setup_logging(self):
        """Configurar el sistema de logging"""
        # Crear logger principal
        self.logger = logging.getLogger('doña_rosa')
        self.logger.setLevel(logging.DEBUG if env.debug else logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        # Handler para archivo
        log_file = env.logs_path / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Agregar handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def critical(self, message):
        self.logger.critical(message)

# Instancia global
logger = Logger()