Param(
    [string]$ProjectRoot = (Resolve-Path "$PSScriptRoot/../..").Path,
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
Set-Location $ProjectRoot

Write-Host "[1/4] Installing build tools..."
& $PythonExe -m pip install --upgrade pip pyinstaller

Write-Host "[2/4] Cleaning old build artifacts..."
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "literature-manager.spec") { Remove-Item -Force "literature-manager.spec" }

Write-Host "[3/4] Building EXE with PyInstaller..."
& $PythonExe -m PyInstaller `
  --noconfirm `
  --clean `
  --name "literature-manager" `
  --onedir `
  --console `
  literature_manager.py

Write-Host "[4/4] Done. Output folder: dist/literature-manager"
Write-Host "You can run: dist/literature-manager/literature-manager.exe --help"
