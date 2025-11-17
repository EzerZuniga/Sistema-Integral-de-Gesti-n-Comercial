import hashlib
import secrets
import string
from .logger import logger

class Security:
    """Manejo de seguridad y cifrado"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashear contraseña usando SHA-256 con salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verificar contraseña contra hash"""
        try:
            salt, stored_hash = hashed_password.split('$')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return secrets.compare_digest(password_hash, stored_hash)
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
    
    @staticmethod
    def generate_random_password(length=8) -> str:
        """Generar contraseña aleatoria segura"""
        characters = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    def validate_rut(rut: str) -> bool:
        """Validar formato de RUT chileno"""
        try:
            rut = rut.upper().replace(".", "").replace("-", "")
            if not rut or len(rut) < 2:
                return False
            
            cuerpo = rut[:-1]
            dv = rut[-1]
            
            if not cuerpo.isdigit():
                return False
            
            # Calcular dígito verificador
            suma = 0
            multiplo = 2
            
            for c in reversed(cuerpo):
                suma += int(c) * multiplo
                multiplo = multiplo + 1 if multiplo < 7 else 2
            
            resto = suma % 11
            dv_calculado = str(11 - resto) if resto != 0 else "0"
            dv_calculado = "K" if dv_calculado == "10" else dv_calculado
            
            return dv == dv_calculado
            
        except Exception:
            return False
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitizar entrada de texto para prevenir inyecciones"""
        if not text:
            return text
        # Remover caracteres potencialmente peligrosos
        dangerous_chars = [';', '"', "'", '\\', '<', '>', '&', '|']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text.strip()

# Instancia global
security = Security()