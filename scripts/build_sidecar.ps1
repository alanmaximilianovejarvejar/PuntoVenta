$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Desktop = Join-Path $Root "desktop"
$Sidecar = Join-Path $Desktop "sidecar"
$Binaries = Join-Path $Desktop "src-tauri\binaries"

Set-Location $Root

if (-not (Test-Path $Python)) {
    Write-Host "No existe .venv. Ejecuta primero .\scripts\bootstrap.ps1"
    exit 1
}

& $Python manage.py collectstatic --noinput

$AddData = @(
    "$Root\cauloti_pos;cauloti_pos",
    "$Root\core;core",
    "$Root\users;users",
    "$Root\products;products",
    "$Root\sales;sales",
    "$Root\inventory;inventory",
    "$Root\templates;templates",
    "$Root\static;static",
    "$Root\staticfiles;staticfiles"
)

$Args = @(
    "-m", "PyInstaller",
    "$Sidecar\server.py",
    "--name", "cauloti_server",
    "--onefile",
    "--noconsole",
    "--clean",
    "--distpath", "$Sidecar\dist",
    "--workpath", "$Sidecar\build",
    "--specpath", "$Sidecar"
)

foreach ($Item in $AddData) {
    $Args += @("--add-data", $Item)
}

& $Python @Args

New-Item -ItemType Directory -Force -Path $Binaries | Out-Null

$Triple = "x86_64-pc-windows-msvc"
if (Get-Command rustc -ErrorAction SilentlyContinue) {
    $Detected = (& rustc --print host-tuple) 2>$null
    if (-not $Detected) {
        $HostLine = (& rustc -Vv | Select-String "host:")
        if ($HostLine) {
            $Detected = $HostLine.Line.Split(" ")[1]
        }
    }
    if ($Detected) {
        $Triple = $Detected.Trim()
    }
}

$Source = Join-Path $Sidecar "dist\cauloti_server.exe"
$Target = Join-Path $Binaries "cauloti_server-$Triple.exe"
Copy-Item -Force $Source $Target

Write-Host "Sidecar listo: $Target"

