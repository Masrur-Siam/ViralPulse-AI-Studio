Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Starting OmniCut AI Video Studio...              " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] .venv not found!" -ForegroundColor Red
    Exit 1
}

Start-Process "http://127.0.0.1:8899"
& $VenvPython -m omnicut.main
