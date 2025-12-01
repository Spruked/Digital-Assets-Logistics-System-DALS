Write-Host "🔒 FORCE-LOADING FULL DALS STACK (IONOS + PROD) ..." -ForegroundColor Cyan

docker-compose -f docker-compose.yml `
               -f docker-compose.ionos.yml `
               -f docker-compose.prod.yml down -v

Start-Sleep -Seconds 2

docker-compose -f docker-compose.yml `
               -f docker-compose.ionos.yml `
               -f docker-compose.prod.yml up -d --build

Write-Host ""
Write-Host "✅ FULL DALS STACK IS NOW RUNNING" -ForegroundColor Green
Write-Host "🌐 API:        http://localhost:8003"
Write-Host "📊 Dashboard:  http://localhost:8008"
Write-Host "🧠 UCM:        http://localhost:8081/health"
Write-Host ""
Write-Host "No minimal stack. No dev reloader. No Copilot chaos." -ForegroundColor Yellow
