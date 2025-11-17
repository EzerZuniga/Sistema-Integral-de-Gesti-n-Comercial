from .environment import env

class Settings:
    """Configuración general de la aplicación"""
    
    # Configuración de la aplicación
    APP_NAME = "Doña Rosa - Sistema de Gestión"
    APP_VERSION = "1.0.0"
    COMPANY_NAME = "Bodega Doña Rosa"
    
    # Configuración de la base de datos
    DATABASE_URL = f"sqlite:///{env.database_path}"
    
    # Configuración de la UI
    WINDOW_SIZE = "1200x800"
    THEME = "default"  # default, dark
    
    # Configuración de seguridad
    SESSION_TIMEOUT = 3600  # 1 hora en segundos
    MAX_LOGIN_ATTEMPTS = 3
    
    # Configuración de negocio
    IVA_PERCENT = 0.19  # 19% IVA
    STOCK_MINIMO = 10
    STOCK_MAXIMO = 100

# Instancia global
settings = Settings()