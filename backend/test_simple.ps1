# Simple Backend API Test Script
Write-Host "=== RepoTwin Backend API Tests ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: GET /api/health" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
    Write-Host "Success: Health check passed" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Simple Analyze (AGENTS.md compliant)
Write-Host "Test 2: POST /api/analyze" -ForegroundColor Yellow
$analyzeBody = @{
    repositoryName = "UniMarket"
    changeRequest = "Add reservation flow before purchase"
    mode = "demo"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" -Method Post -Body $analyzeBody -ContentType "application/json"
    Write-Host "Success: Analyze endpoint passed" -ForegroundColor Green
    Write-Host "Analysis ID: $($response.analysisId)" -ForegroundColor Gray
    Write-Host "Status: $($response.status)" -ForegroundColor Gray
    $analysisId = $response.analysisId
} catch {
    Write-Host "Failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Get Demo Analysis Results
if ($analysisId) {
    Write-Host "Test 3: GET /api/demo/$analysisId/results" -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/demo/$analysisId/results" -Method Get
        Write-Host "Success: Got Shadow PR results" -ForegroundColor Green
        Write-Host "Repository: $($response.repository.name)" -ForegroundColor Gray
        Write-Host "Affected Files: $($response.affectedFiles.Count)" -ForegroundColor Gray
        Write-Host "Risk Score: $($response.riskScore.overall)/100" -ForegroundColor Gray
    } catch {
        Write-Host "Failed: $_" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Visit http://localhost:8000/docs for API documentation" -ForegroundColor Gray

# Made with Bob
