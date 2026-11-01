# IntelliInteraction Unified Runner
# This script builds the frontend and starts the backend on port 8000.

Write-Host "--- 1. Building Frontend (Next.js) ---" -ForegroundColor Cyan
Set-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend Build Failed"; exit }
Set-Location ..

Write-Host "--- 2. Syncing Assets to Backend ---" -ForegroundColor Cyan
if (Test-Path backend/static) { Remove-Item -Path backend/static/* -Recurse -Force }
else { New-Item -ItemType Directory -Path backend/static }
Copy-Item -Path frontend/out/* -Destination backend/static/ -Recurse -Force

Write-Host "--- 3. Starting Unified Backend on http://localhost:8000 ---" -ForegroundColor Cyan
Set-Location backend
python -m app.main
