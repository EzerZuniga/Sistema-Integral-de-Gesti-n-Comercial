from app.controller import BaseController

class LoginController(BaseController):
    """Controlador para la vista de login"""
    
    def _load_initial_data(self):
        """Cargar datos iniciales para el login"""
        # No se necesitan datos iniciales para el login
        pass
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Autenticar usuario"""
        from core.auth import AuthService
        try:
            user = AuthService.login(username, password)
            return user is not None
        except Exception:
            return False