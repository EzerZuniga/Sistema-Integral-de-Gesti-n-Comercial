# do-a-rosa-management-system
Sistema de gestión para la bodega “Doña Rosa”, diseñado para controlar inventario, registrar ventas, generar reportes y administrar productos de forma rápida y eficiente. Desarrollado en Python.

## Nueva estructura implementada

doña-rosa-bodega/
	- `src/`
		- `core/` (config, database, security, utils)
		- `ui/`
			- `login/` (`login_view.py`)
			- `main/` (`main_window.py`, `menu_config.py`)
			- `components/` (`styles.py`)
		- `modules/` (stubs para `inventario`, `usuarios`, etc.)
		- `app.py` (entrypoint del paquete)
	- `data/` (base de datos `bodega.db`, `usuarios_bodega.json`)
	- `assets/`
	- `run.py` (launcher raíz)

## Cómo ejecutar

1. (Opcional) Crear y activar un entorno virtual.
2. Instalar dependencias (solo si las necesitas, p.ej. `matplotlib`):

```powershell
python -m pip install matplotlib
```

3. Ejecutar la app desde la raíz:

```powershell
python run.py
```

Notas:
- He reutilizado tu código existente: la lógica de login y la interfaz principal están copiadas a `src/ui/*` y adaptadas para usar rutas centrales en `src/core/config.py`.
- No eliminé los archivos originales en la raíz; si quieres que borre los archivos raíz antiguos (para evitar duplicados) lo hago en la siguiente iteración.

Si quieres que complete más componentes (por ejemplo, todas las vistas en `src/ui/views_*`, separar componentes `buttons/dialogs/tables` o mover `assets/` dentro de `src/`), dime y lo hago. También puedo ejecutar la app aquí para comprobar arranque (necesito confirmación para abrir ventanas en tu máquina).
