# Backend Analysis Architecture

## Overview

The RepoTwin backend is a FastAPI-based Python service that powers the Shadow PR analysis platform. It transforms natural-language change requests into comprehensive impact analyses, helping developers understand the blast radius of code changes before implementation.

## Core Responsibilities

The backend is responsible for:

1. **Analysis Job Management**: Creating, tracking, and managing analysis jobs through their lifecycle
2. **Repository Context Loading**: Understanding repository structure and dependencies
3. **Impact Analysis**: Using IBM Bob (watsonx.ai) to analyze code changes and predict impacts
4. **Risk Assessment**: Calculating risk scores and identifying potential issues
5. **Result Storage**: Persisting analysis results in Redis with fallback to in-memory storage
6. **API Contract**: Providing stable REST endpoints for frontend consumption
7. **Demo Mode**: Serving pre-computed IBM Bob-assisted analyses for demonstration
8. **Live Mode**: Supporting future real-time repository analysis

## Architecture Principles

### 1. Separation of Concerns

The backend follows a layered architecture:

- **API Layer** (`app/api/`): HTTP endpoints and request/response handling
- **Service Layer** (`app/services/`): Business logic and orchestration
- **Core Layer** (`app/core/`): Analysis engines and IBM Bob integration
- **Storage Layer** (`app/redis/`, `app/models/`): Data persistence
- **Schema Layer** (`app/schemas/`): Request/response contracts

### 2. Redis-First with Graceful Fallback

- Primary storage: Redis for job state, progress, and results
- Fallback: In-memory storage when Redis is unavailable
- No hard dependency on Redis for local development

### 3. IBM Bob Integration

- IBM watsonx.ai (Bob) powers the core analysis engine
- Mock client available for development without credentials
- Circuit breaker pattern for resilience
- Retry logic for transient failures

### 4. Async-First Design

- FastAPI with async/await throughout
- Non-blocking I/O for all external calls
- Background tasks for long-running analyses
- WebSocket support for real-time progress updates

## Analysis Pipeline

The analysis pipeline follows these stages:

```
1. Request Validation
   ↓
2. Job Creation (Redis/Memory)
   ↓
3. Repository Context Resolution
   ↓
4. Demo Mode Check
   ├─→ Demo: Load sample-shadow-pr.json
   └─→ Live: Perform analysis
   ↓
5. IBM Bob Analysis
   ├─→ Affected Files Detection
   ├─→ Blast Radius Calculation
   ├─→ Risk Assessment
   ├─→ Regression Analysis
   ├─→ Implementation Plan
   └─→ Test Recommendations
   ↓
6. Result Storage (Redis/Memory)
   ↓
7. Response Generation
```

## Progress Stages

Analysis jobs report progress through these stages:

| Stage | Progress | Description |
|-------|----------|-------------|
| Queued | 0% | Job created, waiting to start |
| Initializing | 10% | Reading change request and validating |
| Loading Context | 25% | Loading repository metadata |
| Mapping Modules | 45% | Identifying affected modules |
| Calculating Blast Radius | 65% | Analyzing impact propagation |
| Building Regression Pack | 85% | Generating test recommendations |
| Finalizing | 95% | Preparing Shadow PR result |
| Completed | 100% | Analysis ready |

## Error Handling Strategy

### Error Categories

1. **Validation Errors** (400): Invalid request parameters
2. **Not Found Errors** (404): Analysis or repository not found
3. **Analysis Errors** (500): IBM Bob or processing failures
4. **Rate Limit Errors** (429): Too many requests
5. **Service Errors** (503): Redis or external service unavailable

### Error Response Format

```json
{
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Unable to analyze the requested change.",
    "details": "Optional safe details for debugging"
  }
}
```

**Security Note**: Never expose stack traces, credentials, or internal paths in error responses.

## Performance Considerations

### Caching Strategy

- **Repository Metadata**: 1 hour TTL
- **Dependency Graphs**: 1 hour TTL
- **Analysis Results**: 24 hours TTL
- **Demo Scenarios**: No expiration (permanent cache)

### Resource Limits

- Max repository size: 500 MB
- Max files per analysis: 50
- Max context size: 100,000 characters
- Analysis timeout: 300 seconds (5 minutes)
- Rate limit: 100 requests/minute per client

### Optimization Techniques

1. **Lazy Loading**: Load repository data only when needed
2. **Incremental Analysis**: Cache intermediate results
3. **Parallel Processing**: Analyze multiple files concurrently
4. **Result Streaming**: Stream progress updates via WebSocket
5. **Connection Pooling**: Reuse Redis and database connections

## Security Considerations

### API Security

- CORS configured for frontend origins only
- Rate limiting per client IP
- Request size limits
- Input validation on all endpoints

### Data Security

- No credentials stored in Redis
- Sensitive data encrypted at rest
- API keys loaded from environment only
- No logging of sensitive information

### IBM Bob Security

- API keys never logged or exposed
- Circuit breaker prevents credential leakage
- Fallback to mock client in development
- Rate limiting to prevent abuse

## Scalability Design

### Horizontal Scaling

The backend is designed for horizontal scaling:

1. **Stateless API**: No session state in application
2. **External State**: All state in Redis/PostgreSQL
3. **Load Balancing**: Any instance can handle any request
4. **Background Jobs**: Can be distributed via Celery (optional)

### Vertical Scaling

Resource-intensive operations:

1. **Code Parsing**: CPU-bound, benefits from more cores
2. **Graph Analysis**: Memory-bound, needs sufficient RAM
3. **IBM Bob Calls**: Network-bound, benefits from connection pooling

## Monitoring and Observability

### Logging Strategy

- **Structured Logging**: JSON format for machine parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context**: Include analysis_id, repo_id in all logs
- **No Secrets**: Never log credentials or sensitive data

### Metrics to Track

1. **Request Metrics**: Rate, latency, error rate
2. **Analysis Metrics**: Duration, success rate, failure reasons
3. **IBM Bob Metrics**: API calls, token usage, error rate
4. **Redis Metrics**: Hit rate, connection pool usage
5. **Resource Metrics**: CPU, memory, disk usage

### Health Checks

- **Liveness** (`/health/live`): Is the service running?
- **Readiness** (`/health/ready`): Can it handle requests?
- **Health** (`/api/health`): Detailed component status

## Deployment Architecture

### Development Environment

```
FastAPI (localhost:8000)
├─→ Redis (localhost:6379) [optional]
├─→ PostgreSQL (localhost:5432) [optional]
└─→ IBM watsonx.ai [optional, uses mock]
```

### Production Environment

```
Load Balancer
├─→ FastAPI Instance 1
├─→ FastAPI Instance 2
└─→ FastAPI Instance N
    ├─→ Redis Cluster
    ├─→ PostgreSQL Primary/Replica
    └─→ IBM watsonx.ai
```

## Technology Stack

### Core Framework

- **FastAPI**: Modern async web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server with high performance

### Storage

- **Redis**: Job state, progress, caching
- **PostgreSQL**: Persistent data (optional for MVP)
- **SQLAlchemy**: ORM with async support

### Analysis

- **IBM watsonx.ai**: AI-powered impact analysis
- **NetworkX**: Dependency graph analysis
- **Tree-sitter**: Code parsing for multiple languages

### Utilities

- **Tenacity**: Retry logic with exponential backoff
- **Circuit Breaker**: Fault tolerance for external services
- **Structlog**: Structured logging
- **HTTPX**: Async HTTP client

## Future Enhancements

### Phase 2 Features

1. **Real Repository Analysis**: Clone and analyze actual repositories
2. **GitHub Integration**: Direct repository access via API
3. **Incremental Analysis**: Track changes over time
4. **Team Collaboration**: Share analyses across team
5. **Custom Rules**: User-defined impact rules

### Phase 3 Features

1. **ML-Based Predictions**: Learn from historical changes
2. **Auto-Fix Suggestions**: Propose code changes
3. **CI/CD Integration**: Run analyses in pipelines
4. **Multi-Repository**: Analyze changes across repos
5. **Advanced Visualization**: Interactive dependency graphs

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [IBM watsonx.ai Documentation](https://www.ibm.com/products/watsonx-ai)
- [Redis Documentation](https://redis.io/documentation)
- [NetworkX Documentation](https://networkx.org/)
- [AGENTS.md](../AGENTS.md) - Project guidelines