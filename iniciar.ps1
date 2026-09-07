$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host 'Iniciando Clinica Aurora...' -ForegroundColor Cyan

$docker = Get-Command docker -ErrorAction SilentlyContinue
$dockerAvailable = $false
if ($docker) {
    docker info *> $null
    $dockerAvailable = ($LASTEXITCODE -eq 0)
}
if ($dockerAvailable) {
    Write-Host 'Docker encontrado: reconstruindo e iniciando os servicos automaticamente.' -ForegroundColor Green
    docker compose up --build
    exit $LASTEXITCODE
}

Write-Host 'Docker nao encontrado. Iniciando em modo local...' -ForegroundColor Yellow
$frontendPath = Join-Path $projectRoot 'frontend'
$backendPath = Join-Path $projectRoot 'backend'

python -c "import fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Instalando dependencias do backend...' -ForegroundColor Yellow
    python -m pip install -r (Join-Path $backendPath 'requirements.txt')
}

if (-not (Test-Path (Join-Path $frontendPath 'node_modules\.bin\react-scripts.cmd'))) {
    Push-Location $frontendPath
    npm install
    Pop-Location
}

$backend = Start-Process powershell -ArgumentList '-NoExit', '-Command', "Set-Location '$backendPath'; uvicorn app.main:app --reload --port 8000" -PassThru
$frontend = Start-Process powershell -ArgumentList '-NoExit', '-Command', "Set-Location '$frontendPath'; npm start" -PassThru

Write-Host "Backend iniciado (PID $($backend.Id)) em http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend iniciado (PID $($frontend.Id)) em http://localhost:3000" -ForegroundColor Green
Write-Host 'Para encerrar, feche as duas janelas do PowerShell.'
