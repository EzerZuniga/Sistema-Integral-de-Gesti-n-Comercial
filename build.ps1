param(
    [switch]$Clean
)

# Ejecutar desde la raíz del proyecto
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ProjectRoot

if ($Clean) {
    Write-Host "Limpiando artefactos previos..."
    Remove-Item -Recurse -Force .\dist, .\build, .\main.spec -ErrorAction SilentlyContinue
}

Write-Host "Creando/activando entorno virtual .venv si es necesario..."
if (-not (Test-Path ".\\.venv\\Scripts\\Activate.ps1")) {
    python -m venv .venv
}

Write-Host "Activando entorno virtual..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Actualizando pip e instalando PyInstaller..."
python -m pip install --upgrade pip
pip install pyinstaller

Write-Host "Ejecutando PyInstaller para generar el .exe (esto puede tardar)..."
pyinstaller --noconfirm --onefile --windowed --name "DonaRosa" --add-data "assets;assets" --add-data "data;data" main.py

if (Test-Path ".\dist\DonaRosa.exe") {
    Write-Host "Build completado. Ejecutable generado en: .\\dist\\DonaRosa.exe"
} else {
    Write-Host "Build finalizado pero no encontré el ejecutable. Revisa la salida de PyInstaller para errores." -ForegroundColor Yellow
}
