# API Contract Documentation

## Overview

This document defines the complete REST API contract between the RepoTwin frontend and backend. All endpoints follow RESTful conventions and return JSON responses.

**Base URL**: `http://localhost:8000/api`

**Content Type**: `application/json`

## Authentication

Currently, the API does not require authentication for MVP. Future versions will implement:
- API key authentication
- JWT tokens for user sessions
- Rate limiting per API key

## Common Response Formats

### Success Response

```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2026-05-16T04:00:00Z",
    "version": "1.0.0"
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Optional additional context"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `ANALYSIS_FAILED` | 500 | Analysis processing failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `SERVICE_UNAVAILABLE` | 503 | External service unavailable |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Health Endpoints

### GET /api/health

Basic health check endpoint.

**Response**: `200 OK`

```json
{
  "status": "ok",
  "service": "repotwin"
}
```

### GET /api/health/ready

Readiness probe for Kubernetes deployments.

**Response**: `200 OK`

```json
{
  "ready": true
}
```

### GET /api/health/live

Liveness probe for Kubernetes deployments.

**Response**: `200 OK`

```json
{
  "alive": true
}
```

## Analysis Endpoints

### POST /api/analysis

Create a new analysis job.

**Request Body**:

```json
{
  "repo_id": "uuid",
  "change_description": "Add reservation flow before purchase",
  "target_branch": "main",
  "mode": "demo",
  "selected_files": ["src/main.py"],
  "context_files": ["src/utils.py"]
}
```

**Request Schema**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repo_id` | UUID | Yes | Repository identifier |
| `change_description` | string | Yes | Natural language description (10-5000 chars) |
| `target_branch` | string | No | Target branch (default: "main") |
| `mode` | enum | No | "demo" or "live" (default: "demo") |
| `selected_files` | string[] | No | Files to focus analysis on |
| `context_files` | string[] | No | Additional context files |

**Response**: `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "repo_id": "660e8400-e29b-41d4-a716-446655440000",
  "change_description": "Add reservation flow before purchase",
  "target_branch": "main",
  "status": "queued",
  "progress_percent": 0,
  "current_step": null,
  "created_at": "2026-05-16T04:00:00Z",
  "updated_at": "2026-05-16T04:00:00Z",
  "started_at": null,
  "completed_at": null,
  "error_message": null
}
```

**Error Responses**:

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Repository not found
- `500 Internal Server Error`: Analysis creation failed

### GET /api/analysis

List all analyses with optional filtering.

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_id` | UUID | No | Filter by repository |
| `status` | enum | No | Filter by status (pending, running, completed, failed) |
| `skip` | integer | No | Number of records to skip (default: 0) |
| `limit` | integer | No | Max records to return (default: 100, max: 1000) |

**Response**: `200 OK`

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "repo_id": "660e8400-e29b-41d4-a716-446655440000",
      "change_description": "Add reservation flow",
      "status": "completed",
      "progress_percent": 100,
      "created_at": "2026-05-16T04:00:00Z",
      "completed_at": "2026-05-16T04:05:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### GET /api/analysis/{analysis_id}

Get analysis details by ID.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `analysis_id` | UUID | Analysis identifier |

**Response**: `200 OK`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "repo_id": "660e8400-e29b-41d4-a716-446655440000",
  "change_description": "Add reservation flow before purchase",
  "target_branch": "main",
  "status": "completed",
  "progress_percent": 100,
  "current_step": "Completed",
  "created_at": "2026-05-16T04:00:00Z",
  "updated_at": "2026-05-16T04:05:00Z",
  "started_at": "2026-05-16T04:00:01Z",
  "completed_at": "2026-05-16T04:05:00Z",
  "error_message": null
}
```

**Error Responses**:

- `404 Not Found`: Analysis not found

### GET /api/analysis/{analysis_id}/progress

Get real-time analysis progress.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `analysis_id` | UUID | Analysis identifier |

**Response**: `200 OK`

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress_percent": 65,
  "current_step": "Calculating blast radius",
  "message": "Analyzing impact propagation with IBM Bob-assisted analysis",
  "estimated_time_remaining": 120
}
```

**Status Values**:

| Status | Description |
|--------|-------------|
| `queued` | Job created, waiting to start |
| `running` | Analysis in progress |
| `completed` | Analysis finished successfully |
| `failed` | Analysis failed with error |
| `cancelled` | Analysis cancelled by user |

**Progress Stages**:

| Stage | Progress | Current Step |
|-------|----------|--------------|
| Queued | 0% | "Waiting to start" |
| Initializing | 10% | "Reading change request" |
| Loading Context | 25% | "Loading repository context" |
| Mapping Modules | 45% | "Mapping affected modules" |
| Calculating Blast Radius | 65% | "Calculating blast radius" |
| Building Regression Pack | 85% | "Building regression pack" |
| Finalizing | 95% | "Preparing Shadow PR" |
| Completed | 100% | "Shadow PR ready" |

### GET /api/analysis/{analysis_id}/results

Get complete analysis results (Shadow PR).

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `analysis_id` | UUID | Analysis identifier |

**Response**: `200 OK`

```json
{
  "summary": {
    "title": "Impact Analysis: Add Reservation Flow",
    "overview": "This change affects 12 files across 3 modules with medium risk level.",
    "key_points": [
      "12 files require modifications",
      "Primary impact on transaction lifecycle",
      "Test coverage should be increased",
      "Documentation updates needed"
    ]
  },
  "affected_files": [
    {
      "path": "src/models/listing.py",
      "impact_level": "direct",
      "change_type": "modification",
      "reasoning": "Listing state model needs reservation status",
      "lines_added": 25,
      "lines_removed": 10,
      "complexity_change": "increased",
      "risk_factors": ["State machine complexity", "Database migration"]
    }
  ],
  "impact_radius": {
    "category": "medium",
    "metrics": {
      "files_affected": 12,
      "files_direct": 4,
      "files_indirect": 8,
      "functions_affected": 28,
      "classes_affected": 6,
      "tests_affected": 8,
      "percentage_of_codebase": 3.2
    }
  },
  "risk_assessment": {
    "overall_level": "medium",
    "score": 65,
    "factors": [
      {
        "name": "State Machine Complexity",
        "level": "high",
        "likelihood": "high",
        "impact": "high",
        "description": "Adding reservation state increases state machine complexity",
        "mitigation": "Add comprehensive state transition tests"
      }
    ]
  },
  "regression_analysis": {
    "breaking_changes": [
      {
        "type": "api_signature",
        "file": "src/api/listings.py",
        "line": 42,
        "description": "Purchase endpoint now requires reservation_id",
        "migration": "Update all purchase calls to include reservation_id",
        "severity": "high"
      }
    ],
    "behavior_changes": [
      {
        "type": "logic",
        "file": "src/services/transaction.py",
        "description": "Purchase flow now checks reservation status",
        "impact": "Existing direct purchases will fail without reservation"
      }
    ]
  },
  "implementation_plan": {
    "phases": [
      {
        "phase": 1,
        "name": "Update Data Models",
        "description": "Add reservation fields to Listing and Transaction models",
        "files": ["src/models/listing.py", "src/models/transaction.py"],
        "estimated_effort": "2 hours",
        "checkpoints": ["Database migration created", "Model tests pass"]
      },
      {
        "phase": 2,
        "name": "Implement Reservation API",
        "description": "Create reservation endpoints and business logic",
        "files": ["src/api/reservations.py", "src/services/reservation.py"],
        "estimated_effort": "4 hours",
        "checkpoints": ["API tests pass", "Integration tests pass"]
      }
    ],
    "total_estimated_effort": "12 hours",
    "rollback_strategy": "Database migration rollback + feature flag disable",
    "prerequisites": ["Database backup", "Staging environment ready"]
  },
  "test_recommendations": {
    "existing_tests_to_update": [
      {
        "path": "tests/test_purchase.py",
        "changes": "Add reservation_id to all purchase test cases",
        "priority": "high"
      }
    ],
    "new_tests_needed": [
      {
        "type": "integration",
        "description": "Test complete reservation → purchase flow",
        "priority": "high"
      },
      {
        "type": "unit",
        "description": "Test reservation expiration logic",
        "priority": "medium"
      }
    ],
    "coverage_gaps": [
      {
        "area": "Reservation state transitions",
        "current_coverage": 0,
        "target_coverage": 90
      }
    ]
  }
}
```

**Error Responses**:

- `404 Not Found`: Analysis not found or not completed
- `500 Internal Server Error`: Failed to retrieve results

### DELETE /api/analysis/{analysis_id}

Delete an analysis.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `analysis_id` | UUID | Analysis identifier |

**Response**: `204 No Content`

**Error Responses**:

- `404 Not Found`: Analysis not found

### WebSocket /api/analysis/{analysis_id}/ws

Real-time analysis progress updates via WebSocket.

**Connection**: `ws://localhost:8000/api/analysis/{analysis_id}/ws`

**Messages Received**:

```json
{
  "type": "progress",
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "progress_percent": 65,
    "message": "Calculating blast radius"
  }
}
```

```json
{
  "type": "completed",
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed"
  }
}
```

```json
{
  "type": "error",
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "error": "Analysis failed: timeout"
  }
}
```

## Repository Endpoints

### GET /api/repos

List repositories (future implementation).

**Response**: `200 OK`

```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "name": "UniMarket",
      "url": "https://github.com/example/unimarket",
      "default_branch": "main",
      "created_at": "2026-05-16T04:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /api/repos

Register a new repository (future implementation).

**Request Body**:

```json
{
  "name": "UniMarket",
  "url": "https://github.com/example/unimarket",
  "default_branch": "main"
}
```

**Response**: `201 Created`

## Rate Limiting

**Limits**:
- 100 requests per minute per IP address
- 10 concurrent analyses per repository

**Headers**:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1620000000
```

**Error Response**: `429 Too Many Requests`

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": "Limit: 100 requests/minute"
  }
}
```

## CORS Configuration

**Allowed Origins**:
- `http://localhost:3000` (development)
- `http://127.0.0.1:3000` (development)
- Production frontend URL (configured via environment)

**Allowed Methods**: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`

**Allowed Headers**: `Content-Type`, `Authorization`

## Versioning

**Current Version**: `v1`

**Version Header**: `X-API-Version: 1.0.0`

Future versions will use URL versioning: `/api/v2/analysis`

## Demo Mode vs Live Mode

### Demo Mode (`mode: "demo"`)

- Returns pre-computed IBM Bob-assisted analysis
- Uses `data/sample-shadow-pr.json`
- Instant response (simulated progress)
- No external API calls
- Perfect for demonstrations and testing

### Live Mode (`mode: "live"`)

- Performs real-time analysis
- Calls IBM watsonx.ai API
- Actual progress tracking
- May take 2-5 minutes
- Requires valid API credentials

## Frontend Integration Example

### TypeScript API Client

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create analysis
const createAnalysis = async (data: AnalysisCreate) => {
  const response = await api.post('/analysis', data);
  return response.data;
};

// Poll for progress
const getProgress = async (analysisId: string) => {
  const response = await api.get(`/analysis/${analysisId}/progress`);
  return response.data;
};

// Get results
const getResults = async (analysisId: string) => {
  const response = await api.get(`/analysis/${analysisId}/results`);
  return response.data;
};
```

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Create analysis
curl -X POST http://localhost:8000/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "660e8400-e29b-41d4-a716-446655440000",
    "change_description": "Add reservation flow",
    "mode": "demo"
  }'

# Get progress
curl http://localhost:8000/api/analysis/{analysis_id}/progress

# Get results
curl http://localhost:8000/api/analysis/{analysis_id}/results
```

### Using HTTPie

```bash
# Create analysis
http POST localhost:8000/api/analysis \
  repo_id="660e8400-e29b-41d4-a716-446655440000" \
  change_description="Add reservation flow" \
  mode="demo"
```

## OpenAPI Documentation

Interactive API documentation available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [REST API Best Practices](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [AGENTS.md](../AGENTS.md) - Project guidelines