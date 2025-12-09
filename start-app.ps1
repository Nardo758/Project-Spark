# Friction - Complete Startup Script (PowerShell)
# This script starts both backend and frontend servers

Write-Host "🚀 Starting Friction Application (Backend + Frontend)..." -ForegroundColor Cyan
Write-Host "" -ForegroundColor White

# Start backend in a new window
Write-Host "📡 Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "start-backend.ps1"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "🌐 Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "start-frontend.ps1"

Write-Host "" -ForegroundColor White
Write-Host "✅ Application started!" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "🔗 Frontend: http://localhost:5500" -ForegroundColor Cyan
Write-Host "🔗 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🔗 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "Close the server windows to stop the application." -ForegroundColor Yellow
