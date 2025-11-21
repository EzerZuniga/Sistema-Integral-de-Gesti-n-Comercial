class DoñaRosaException(Exception):
    """Excepción base para la aplicación"""
    pass

class AuthenticationError(DoñaRosaException):
    """Error de autenticación"""
    pass

class DatabaseError(DoñaRosaException):
    """Error de base de datos"""
    pass

class ValidationError(DoñaRosaException):
    """Error de validación de datos"""
    pass

class BusinessLogicError(DoñaRosaException):
    """Error de lógica de negocio"""
    pass

class AuthorizationError(DoñaRosaException):
    """Error de autorización / permisos"""
    pass

class InsufficientStockError(BusinessLogicError):
    """Error por stock insuficiente"""
    pass

class AuthorizationError(DoñaRosaException):
    """Error de autorización / permisos"""
    pass