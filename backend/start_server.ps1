# Start RepoTwin Backend Server
# This script starts the FastAPI backend with uvicorn

Write-Host "=== Starting RepoTwin Backend Server ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the backend directory
if (-not (Test-Path "app/main.py")) {
    Write-Host "Error: Must run from backend directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found, using defaults" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file" -ForegroundColor Green
    }
}

Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Made with Bob
