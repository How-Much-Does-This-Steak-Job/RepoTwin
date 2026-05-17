# Backend Testing Guide

## Overview

This guide provides instructions for testing the RepoTwin backend API endpoints to ensure AGENTS.md compliance and proper integration with the frontend.

## Prerequisites

1. **Python 3.12+** installed
2. **Dependencies installed**: `pip install -r requirements.txt`
3. **Environment configured**: `.env` file created from `.env.example`
4. **Sample data available**: `data/sample-shadow-pr.json` exists

## Quick Start

### 1. Start the Backend Server

```powershell
cd backend
.\start_server.ps1
```

Or manually:

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### 2. Run Automated Tests

```powershell
cd backend
.\test_endpoints.ps1
```

### 3. Access API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Manual Testing

### Test 1: Health Check

**Endpoint**: `GET /api/health`

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Test 2: Root Endpoint

**Endpoint**: `GET /`

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
```

**Expected Response**:
```json
{
  "name": "RepoTwin by Bob",
  "version": "0.1.0",
  "status": "running",
  "docs": "/docs"
}
```

### Test 3: Simple Analyze (AGENTS.md Compliant)

**Endpoint**: `POST /api/analyze`

This is the primary endpoint specified in AGENTS.md.

```powershell
$body = @{
    repositoryName = "UniMarket"
    changeRequest = "Add reservation flow before purchase"
    mode = "demo"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

**Expected Response**:
```json
{
  "analysisId": "analysis_abc123",
  "status": "completed",
  "message": "Demo analysis completed successfully"
}
```

### Test 4: Full Analysis Creation

**Endpoint**: `POST /api/analysis`

```powershell
$body = @{
    repository_name = "UniMarket"
    repository_url = "https://github.com/example/unimarket"
    change_request = "Add reservation flow before purchase"
    context = "User wants to reserve items before completing purchase"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/analysis" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

$analysisId = $response.id
```

**Expected Response**:
```json
{
  "id": "uuid-here",
  "repository_name": "UniMarket",
  "status": "pending",
  "created_at": "2026-05-17T02:00:00Z"
}
```

### Test 5: Get Analysis Status

**Endpoint**: `GET /api/analysis/{id}`

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analysis/$analysisId" -Method Get
```

**Expected Response**:
```json
{
  "id": "uuid-here",
  "status": "processing",
  "progress": 65,
  "message": "Analyzing code structure..."
}
```

### Test 6: Get Analysis Progress

**Endpoint**: `GET /api/analysis/{id}/progress`

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analysis/$analysisId/progress" -Method Get
```

**Expected Response**:
```json
{
  "analysis_id": "uuid-here",
  "status": "processing",
  "progress": 75,
  "current_step": "Calculating blast radius",
  "total_steps": 8,
  "completed_steps": 6
}
```

### Test 7: Get Analysis Results

**Endpoint**: `GET /api/analysis/{id}/results`

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analysis/$analysisId/results" -Method Get
```

**Expected Response**: Full Shadow PR object (see `types/shadow-pr.ts`)

### Test 8: Delete Analysis

**Endpoint**: `DELETE /api/analysis/{id}`

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/analysis/$analysisId" -Method Delete
```

**Expected Response**:
```json
{
  "message": "Analysis deleted successfully"
}
```

## Testing Demo Mode

Demo mode returns pre-computed Shadow PR data from `data/sample-shadow-pr.json`.

### Verify Demo Data Loading

```powershell
# Test simple analyze in demo mode
$body = @{
    repositoryName = "UniMarket"
    changeRequest = "Add reservation flow"
    mode = "demo"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

# Get the results
$analysisId = $response.analysisId
Start-Sleep -Seconds 1

$results = Invoke-RestMethod -Uri "http://localhost:8000/api/analysis/$analysisId/results" -Method Get

# Verify key fields exist
Write-Host "Summary: $($results.summary.title)"
Write-Host "Affected Files: $($results.affected_files.Count)"
Write-Host "Risk Score: $($results.risk_score.overall_score)"
```

## Testing with cURL (Alternative)

If you prefer cURL:

```bash
# Health check
curl http://localhost:8000/api/health

# Simple analyze
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"repositoryName":"UniMarket","changeRequest":"Add reservation flow","mode":"demo"}'

# Full analysis
curl -X POST http://localhost:8000/api/analysis \
  -H "Content-Type: application/json" \
  -d '{"repository_name":"UniMarket","repository_url":"https://github.com/example/unimarket","change_request":"Add reservation flow"}'
```

## Common Issues

### Issue 1: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue 2: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Ensure you're in the `backend` directory and dependencies are installed:
```powershell
cd backend
pip install -r requirements.txt
```

### Issue 3: Sample Data Not Found

**Error**: `Demo data file not found`

**Solution**: Verify `data/sample-shadow-pr.json` exists:
```powershell
# From project root
Test-Path data/sample-shadow-pr.json

# If missing, check frontend/data/
Test-Path frontend/data/sample-shadow-pr.json
```

### Issue 4: Database Connection Error

**Error**: `Could not connect to database`

**Solution**: The backend should work without Postgres. Check `.env`:
```env
# Optional: Set to false to skip database
USE_DATABASE=false
```

### Issue 5: Redis Connection Error

**Error**: `Could not connect to Redis`

**Solution**: Redis is optional. The backend falls back to in-memory storage:
```env
# Optional: Set to false to skip Redis
USE_REDIS=false
```

## Validation Checklist

Use this checklist to verify backend readiness:

- [ ] Server starts without errors
- [ ] Health endpoint returns 200
- [ ] Root endpoint returns app info
- [ ] `/api/analyze` accepts demo requests
- [ ] `/api/analyze` returns valid analysisId
- [ ] Demo mode loads sample Shadow PR data
- [ ] Results endpoint returns complete Shadow PR object
- [ ] API documentation accessible at `/docs`
- [ ] No credentials in logs or responses
- [ ] CORS allows frontend origin
- [ ] Error responses include proper error codes

## Integration with Frontend

### Frontend API Client

The frontend uses `lib/api.ts` to communicate with the backend:

```typescript
// Example frontend usage
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    repositoryName: 'UniMarket',
    changeRequest: 'Add reservation flow',
    mode: 'demo'
  })
});

const data = await response.json();
console.log('Analysis ID:', data.analysisId);
```

### Testing Frontend Connection

1. Start backend: `cd backend && .\start_server.ps1`
2. Start frontend: `cd frontend && pnpm dev`
3. Navigate to: http://localhost:3000/demo
4. Submit a change request
5. Verify results display correctly

## Performance Testing

### Load Test with PowerShell

```powershell
# Simple load test - 10 concurrent requests
1..10 | ForEach-Object -Parallel {
    $body = @{
        repositoryName = "UniMarket"
        changeRequest = "Test request $_"
        mode = "demo"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:8000/api/analyze" `
        -Method Post `
        -Body $body `
        -ContentType "application/json"
} -ThrottleLimit 10
```

### Expected Performance

- Health check: < 10ms
- Demo analyze: < 100ms
- Full analysis (with IBM Bob): 5-30 seconds
- Results retrieval: < 50ms

## Next Steps

After backend testing is complete:

1. **Frontend Integration**: Test end-to-end demo flow
2. **Dashboard Validation**: Verify all Shadow PR sections render
3. **IBM Bob Evidence**: Export task sessions to `bob_sessions/`
4. **Documentation**: Update README with deployment instructions
5. **Final QA**: Complete submission checklist

## Support

For issues or questions:
- Check `docs/api-contract.md` for API specifications
- Review `AGENTS.md` for project guidelines
- Check backend logs for detailed error messages
- Verify `.env` configuration matches `.env.example`