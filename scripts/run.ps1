$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

Set-Location $Root

if (-not (Test-Path $Python)) {
    Write-Host "No existe .venv. Ejecuta primero .\scripts\bootstrap.ps1"
    exit 1
}

& $Python manage.py runserver 127.0.0.1:8000

