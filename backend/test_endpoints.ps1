# Backend API Test Script for RepoTwin
# Tests all AGENTS.md compliant endpoints

Write-Host "=== RepoTwin Backend API Tests ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: GET /api/health" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Root endpoint
Write-Host "Test 2: GET /" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
    Write-Host "✓ Root endpoint passed" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Root endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: Simple Analyze (AGENTS.md compliant)
Write-Host "Test 3: POST /api/analyze (AGENTS.md endpoint)" -ForegroundColor Yellow
$analyzeBody = @{
    repositoryName = "UniMarket"
    changeRequest = "Add reservation flow before purchase"
    mode = "demo"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" -Method Post -Body $analyzeBody -ContentType "application/json"
    Write-Host "✓ Simple analyze passed" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
    $analysisId = $response.analysisId
} catch {
    Write-Host "✗ Simple analyze failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Full Analysis Creation
Write-Host "Test 4: POST /api/analysis (full endpoint)" -ForegroundColor Yellow
$fullAnalysisBody = @{
    repository_name = "UniMarket"
    repository_url = "https://github.com/example/unimarket"
    change_request = "Add reservation flow before purchase"
    context = "User wants to reserve items before completing purchase"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analysis" -Method Post -Body $fullAnalysisBody -ContentType "application/json"
    Write-Host "✓ Full analysis creation passed" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
    $fullAnalysisId = $response.id
} catch {
    Write-Host "✗ Full analysis creation failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: Get Analysis Status (if we have an ID)
if ($fullAnalysisId) {
    Write-Host "Test 5: GET /api/analysis/$fullAnalysisId" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analysis/$fullAnalysisId" -Method Get
        Write-Host "✓ Get analysis passed" -ForegroundColor Green
        Write-Host "Status: $($response.status)" -ForegroundColor Gray
    } catch {
        Write-Host "✗ Get analysis failed: $_" -ForegroundColor Red
    }
    Write-Host ""

    # Test 6: Get Analysis Results
    Write-Host "Test 6: GET /api/analysis/$fullAnalysisId/results" -ForegroundColor Yellow
    Start-Sleep -Seconds 2  # Wait for processing
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/analysis/$fullAnalysisId/results" -Method Get
        Write-Host "✓ Get results passed" -ForegroundColor Green
        Write-Host "Result keys: $($response.PSObject.Properties.Name -join ', ')" -ForegroundColor Gray
    } catch {
        Write-Host "✗ Get results failed: $_" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 7: OpenAPI Docs
Write-Host "Test 7: GET /docs (OpenAPI documentation)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method Get
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ OpenAPI docs accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ OpenAPI docs failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host "All critical endpoints tested." -ForegroundColor Green
Write-Host "Visit http://localhost:8000/docs for interactive API documentation" -ForegroundColor Gray

# Made with Bob
