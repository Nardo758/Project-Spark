# Friction - Frontend Startup Script (PowerShell)
# This script starts a simple HTTP server for the frontend

Write-Host "🌐 Starting Friction Frontend Server..." -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "index.html")) {
    Write-Host "❌ Error: index.html not found. Make sure you're in the project root." -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please install Python." -ForegroundColor Red
    Write-Host "Alternatively, use VS Code Live Server extension." -ForegroundColor Yellow
    exit 1
}

Write-Host "" -ForegroundColor White
Write-Host "✨ Starting frontend server on http://localhost:5500" -ForegroundColor Green
Write-Host "🏠 Homepage: http://localhost:5500/index.html" -ForegroundColor Green
Write-Host "🔐 Sign in: http://localhost:5500/signin.html" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "⚠️  Make sure backend is running on http://localhost:8000" -ForegroundColor Yellow
Write-Host "   Run './start-backend.ps1' in another terminal" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White

# Start Python HTTP server
python -m http.server 5500
