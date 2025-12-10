# Friction - Startup Script (PowerShell)
# This script starts the backend server

Write-Host "🚀 Starting Friction Backend Server..." -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: backend directory not found. Make sure you're in the project root." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Warning: backend\.env file not found!" -ForegroundColor Yellow
    Write-Host "Please configure your database connection in backend\.env" -ForegroundColor Yellow
    Write-Host "See CONNECTION_GUIDE.md for instructions." -ForegroundColor Yellow
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "backend\venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv backend\venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
& backend\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
pip install -r backend\requirements.txt

# Start the server
Write-Host "" -ForegroundColor White
Write-Host "✨ Starting backend server on http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "❤️  Health Check: http://localhost:8000/health" -ForegroundColor Green
Write-Host "" -ForegroundColor White
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White

Set-Location backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
