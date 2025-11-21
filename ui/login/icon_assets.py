import os
import base64

# Pequeños placeholders PNG (1x1 transparent) en base64. Se usan como fallback para iconos.
USER_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)
LOCK_PNG_B64 = USER_PNG_B64
EYE_PNG_B64 = USER_PNG_B64

ICONS = {
    'user.png': USER_PNG_B64,
    'lock.png': LOCK_PNG_B64,
    'eye.png': EYE_PNG_B64,
}


def ensure_icons(base_path=None):
    """Crea archivos PNG en `assets/icons/` si no existen.

    Devuelve el directorio donde se escribieron los iconos.
    """
    if base_path is None:
        base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons')

    try:
        os.makedirs(base_path, exist_ok=True)
    except Exception:
        # si no podemos crear directorio, devolvemos None
        return None

    for name, b64 in ICONS.items():
        path = os.path.join(base_path, name)
        try:
            if not os.path.exists(path):
                with open(path, 'wb') as f:
                    f.write(base64.b64decode(b64))
        except Exception:
            # ignorar errores de escritura
            pass

    return base_path
