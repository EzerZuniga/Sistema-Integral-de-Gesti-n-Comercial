from functools import wraps
from core.auth import AuthService
from core.exceptions import AuthorizationError


def requires_role(required_role: str):
    """Decorador que asegura que el usuario autenticado tenga el rol requerido.

    Lanza AuthorizationError si no está autenticado o no tiene el rol.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = AuthService.get_current_user()
            if not user:
                raise AuthorizationError("No autenticado")
            if user.rol != required_role:
                raise AuthorizationError("Acceso denegado: se requiere rol '%s'" % required_role)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def requires_permission(permission: str):
    """Decorador que asegura que el usuario tenga permiso para una acción.

    Se basa en `AuthService.has_permission`.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not AuthService.has_permission(permission):
                raise AuthorizationError(f"Permisos insuficientes: {permission}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
