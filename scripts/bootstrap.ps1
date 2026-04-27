$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"

Set-Location $Root

if (-not (Test-Path $VenvPython)) {
    python -m venv .venv
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt
& $VenvPython manage.py makemigrations
& $VenvPython manage.py migrate
& $VenvPython manage.py seed_demo
& $VenvPython manage.py collectstatic --noinput

Write-Host "Punto de Venta Cauloti listo."
Write-Host "Ejecuta: .\scripts\run.ps1"

