# Backend Redis Analysis Implementation TODO

## Overview

This TODO list tracks the implementation of Redis-backed analysis job management for RepoTwin. The backend member should work through these tasks sequentially, confirming completion of each before moving to the next.

**Branch**: `feature/backend-redis-analysis`

**Estimated Effort**: 12-16 hours

**Dependencies**: 
- Redis running locally or via Docker
- Existing FastAPI backend structure
- IBM watsonx.ai credentials (optional for demo mode)

## Phase 1: Redis Infrastructure (3-4 hours)

### 1.1 Redis Client Setup

- [ ] Create `backend/app/redis/__init__.py`
- [ ] Create `backend/app/redis/client.py`
  - [ ] Implement Redis connection with connection pooling
  - [ ] Add health check method (`ping()`)
  - [ ] Add graceful connection handling
  - [ ] Add logging for connection events
  - [ ] Handle connection errors gracefully
- [ ] Update `backend/app/config.py`
  - [ ] Add `redis_url` configuration
  - [ ] Add `redis_pool_size` configuration
  - [ ] Add `redis_enabled` flag for fallback control
- [ ] Test Redis connection locally

**Acceptance Criteria**:
- Redis client connects successfully
- Connection pooling works
- Health check returns True when Redis is available
- Logs connection status appropriately

### 1.2 Redis Store Implementation

- [ ] Create `backend/app/redis/store.py`
  - [ ] Implement `RedisStore` class
  - [ ] Add `set_analysis_status()` method
  - [ ] Add `get_analysis_status()` method
  - [ ] Add `set_analysis_progress()` method
  - [ ] Add `get_analysis_progress()` method
  - [ ] Add `set_analysis_result()` method
  - [ ] Add `get_analysis_result()` method
  - [ ] Add `set_analysis_metadata()` method
  - [ ] Add `get_analysis_metadata()` method
  - [ ] Add `set_analysis_error()` method
  - [ ] Add `get_analysis_error()` method
  - [ ] Add `delete_analysis()` method
  - [ ] Add `add_to_active_set()` method
  - [ ] Add `remove_from_active_set()` method
  - [ ] Add `get_active_analyses()` method
  - [ ] Implement proper TTL for each key type
  - [ ] Add error handling for all operations
  - [ ] Add logging for all operations

**Acceptance Criteria**:
- All CRUD operations work correctly
- TTL is set appropriately for each key type
- Errors are handled and logged
- Keys follow documented naming convention

### 1.3 In-Memory Fallback

- [ ] Create `backend/app/redis/memory_store.py`
  - [ ] Implement `MemoryStore` class with same interface as `RedisStore`
  - [ ] Add thread-safe dictionary storage
  - [ ] Implement TTL expiration logic
  - [ ] Add cleanup method for expired keys
  - [ ] Match all `RedisStore` methods
- [ ] Create `backend/app/redis/factory.py`
  - [ ] Implement `get_store()` factory function
  - [ ] Add Redis availability check
  - [ ] Return `RedisStore` if available, else `MemoryStore`
  - [ ] Log which store is being used
- [ ] Test fallback behavior when Redis is unavailable

**Acceptance Criteria**:
- `MemoryStore` implements same interface as `RedisStore`
- TTL expiration works correctly
- Factory correctly detects Redis availability
- Fallback is transparent to calling code

## Phase 2: Analysis Service Layer (4-5 hours)

### 2.1 Analysis Service Core

- [ ] Create `backend/app/services/analysis_service.py`
  - [ ] Implement `AnalysisService` class
  - [ ] Add `create_analysis()` method
  - [ ] Add `get_analysis()` method
  - [ ] Add `list_analyses()` method
  - [ ] Add `get_analysis_progress()` method
  - [ ] Add `get_analysis_results()` method
  - [ ] Add `delete_analysis()` method
  - [ ] Add `cancel_analysis()` method
  - [ ] Integrate with Redis store
  - [ ] Add proper error handling
  - [ ] Add logging for all operations

**Acceptance Criteria**:
- Service methods work with both Redis and memory store
- Proper error handling for missing analyses
- UUID generation for new analyses
- Timestamps are ISO 8601 format

### 2.2 Background Analysis Execution

- [ ] Add `_execute_analysis()` private method to `AnalysisService`
  - [ ] Update status to "running"
  - [ ] Update progress through stages (10%, 25%, 45%, 65%, 85%, 95%, 100%)
  - [ ] Call appropriate analysis mode (demo or live)
  - [ ] Store final result in Redis
  - [ ] Update status to "completed" or "failed"
  - [ ] Remove from active set
  - [ ] Handle errors and store error details
- [ ] Integrate with FastAPI `BackgroundTasks`
- [ ] Add timeout handling (5 minutes)
- [ ] Add progress update intervals (every 2 seconds)

**Acceptance Criteria**:
- Analysis runs in background without blocking API
- Progress updates are stored in Redis
- Timeout is enforced
- Errors are caught and stored properly

### 2.3 Demo Mode Service

- [ ] Create `backend/app/services/demo_service.py`
  - [ ] Implement `DemoService` class
  - [ ] Add `load_demo_scenario()` method
  - [ ] Add `get_demo_result()` method
  - [ ] Load from `data/sample-shadow-pr.json`
  - [ ] Cache demo results in Redis (permanent TTL)
  - [ ] Simulate realistic progress delays
- [ ] Create `data/sample-shadow-pr.json` if missing
  - [ ] Use IBM Bob to generate realistic UniMarket reservation flow analysis
  - [ ] Include all required Shadow PR fields
  - [ ] Ensure JSON is valid and complete

**Acceptance Criteria**:
- Demo mode loads sample data correctly
- Demo results are cached in Redis
- Progress simulation feels realistic (2-5 seconds total)
- Sample data is comprehensive and realistic

## Phase 3: API Endpoints (3-4 hours)

### 3.1 Update Analysis Endpoints

- [ ] Update `backend/app/api/analysis.py`
  - [ ] Update `create_analysis()` endpoint
    - [ ] Validate request with Pydantic
    - [ ] Call `analysis_service.create_analysis()`
    - [ ] Schedule background task
    - [ ] Return 201 with analysis metadata
  - [ ] Update `get_analysis()` endpoint
    - [ ] Call `analysis_service.get_analysis()`
    - [ ] Return 404 if not found
  - [ ] Update `list_analyses()` endpoint
    - [ ] Support filtering by repo_id and status
    - [ ] Support pagination (skip/limit)
    - [ ] Return list with total count
  - [ ] Update `get_analysis_progress()` endpoint
    - [ ] Call `analysis_service.get_analysis_progress()`
    - [ ] Return current progress state
  - [ ] Update `get_analysis_results()` endpoint
    - [ ] Call `analysis_service.get_analysis_results()`
    - [ ] Return 404 if not completed
    - [ ] Return complete Shadow PR
  - [ ] Update `delete_analysis()` endpoint
    - [ ] Call `analysis_service.delete_analysis()`
    - [ ] Return 204 on success
  - [ ] Keep WebSocket endpoint for future enhancement

**Acceptance Criteria**:
- All endpoints return correct status codes
- Request validation works via Pydantic
- Error responses follow documented format
- Endpoints work with both Redis and memory store

### 3.2 Error Handling

- [ ] Create `backend/app/utils/errors.py`
  - [ ] Define `AnalysisError` base exception
  - [ ] Define `AnalysisNotFoundError` exception
  - [ ] Define `AnalysisTimeoutError` exception
  - [ ] Define `AnalysisValidationError` exception
- [ ] Add FastAPI exception handlers in `backend/app/main.py`
  - [ ] Handle `AnalysisNotFoundError` → 404
  - [ ] Handle `AnalysisValidationError` → 400
  - [ ] Handle `AnalysisTimeoutError` → 500
  - [ ] Handle generic `AnalysisError` → 500
  - [ ] Return consistent error format
- [ ] Never expose stack traces in production

**Acceptance Criteria**:
- Custom exceptions are raised appropriately
- Exception handlers return correct status codes
- Error responses match documented format
- No sensitive information in error messages

### 3.3 Request/Response Validation

- [ ] Update `backend/app/schemas/analysis.py`
  - [ ] Add `AnalysisMode` enum if missing
  - [ ] Ensure `AnalysisCreate` has all required fields
  - [ ] Add field validators for `change_description` length
  - [ ] Add field validators for `target_branch` format
  - [ ] Ensure all response models match API contract
- [ ] Test validation with invalid requests
- [ ] Test validation with edge cases

**Acceptance Criteria**:
- Invalid requests return 400 with clear error message
- Field validators work correctly
- Response models serialize correctly

## Phase 4: Testing (2-3 hours)

### 4.1 Unit Tests

- [ ] Create `backend/tests/test_redis_store.py`
  - [ ] Test all `RedisStore` methods
  - [ ] Test TTL expiration
  - [ ] Test error handling
  - [ ] Mock Redis client
- [ ] Create `backend/tests/test_memory_store.py`
  - [ ] Test all `MemoryStore` methods
  - [ ] Test TTL expiration
  - [ ] Test thread safety
- [ ] Create `backend/tests/test_analysis_service.py`
  - [ ] Test `create_analysis()`
  - [ ] Test `get_analysis()`
  - [ ] Test `get_analysis_progress()`
  - [ ] Test `get_analysis_results()`
  - [ ] Test error cases
  - [ ] Mock Redis store
- [ ] Create `backend/tests/test_demo_service.py`
  - [ ] Test demo scenario loading
  - [ ] Test demo result caching
  - [ ] Test progress simulation

**Acceptance Criteria**:
- All unit tests pass
- Code coverage > 80%
- Tests are isolated and fast
- Mocks are used appropriately

### 4.2 Integration Tests

- [ ] Create `backend/tests/integration/test_analysis_api.py`
  - [ ] Test complete analysis flow (create → progress → results)
  - [ ] Test demo mode end-to-end
  - [ ] Test error cases (not found, invalid input)
  - [ ] Test pagination
  - [ ] Test filtering
- [ ] Use pytest fixtures for test data
- [ ] Use TestClient from FastAPI
- [ ] Test with both Redis and memory store

**Acceptance Criteria**:
- Integration tests pass
- Tests cover happy path and error cases
- Tests work with both storage backends

### 4.3 Manual Testing

- [ ] Test with Redis running
  - [ ] Create demo analysis
  - [ ] Poll progress endpoint
  - [ ] Retrieve results
  - [ ] Verify Redis keys are created
  - [ ] Verify TTL is set correctly
- [ ] Test with Redis stopped
  - [ ] Verify fallback to memory store
  - [ ] Verify same functionality works
  - [ ] Check logs for fallback message
- [ ] Test error cases
  - [ ] Invalid UUID
  - [ ] Missing analysis
  - [ ] Invalid change description
- [ ] Test with curl or Postman
- [ ] Test with frontend (if available)

**Acceptance Criteria**:
- All manual tests pass
- Fallback works seamlessly
- Error messages are clear
- API matches documented contract

## Phase 5: Documentation & Polish (1-2 hours)

### 5.1 Code Documentation

- [ ] Add docstrings to all public methods
  - [ ] Use Google-style docstrings
  - [ ] Document parameters and return types
  - [ ] Document exceptions raised
- [ ] Add inline comments for complex logic
- [ ] Add type hints to all functions
- [ ] Run `mypy` for type checking

**Acceptance Criteria**:
- All public methods have docstrings
- Type hints are complete
- `mypy` passes with no errors

### 5.2 Backend README

- [ ] Create or update `backend/README.md`
  - [ ] Add setup instructions
  - [ ] Add Redis setup instructions
  - [ ] Add environment variables documentation
  - [ ] Add API endpoint examples
  - [ ] Add testing instructions
  - [ ] Add troubleshooting section
- [ ] Add code examples for common operations

**Acceptance Criteria**:
- README is clear and complete
- Setup instructions work for new developers
- Examples are accurate

### 5.3 Environment Configuration

- [ ] Update `.env.example`
  - [ ] Add `REDIS_URL` with default value
  - [ ] Add `REDIS_POOL_SIZE` with default value
  - [ ] Add comments explaining each variable
- [ ] Document required vs optional variables
- [ ] Add example for Docker Redis setup

**Acceptance Criteria**:
- `.env.example` is complete
- Comments are helpful
- Defaults are sensible

## Phase 6: Deployment Preparation (1 hour)

### 6.1 Docker Support

- [ ] Update `backend/Dockerfile` if needed
  - [ ] Ensure Redis client libraries are installed
  - [ ] Add health check command
- [ ] Create `docker-compose.yml` for local development
  - [ ] Add FastAPI service
  - [ ] Add Redis service
  - [ ] Add volume for Redis persistence
  - [ ] Add network configuration
- [ ] Test Docker setup locally

**Acceptance Criteria**:
- Docker build succeeds
- Docker Compose starts all services
- Services can communicate
- Health checks work

### 6.2 Production Readiness

- [ ] Add logging configuration
  - [ ] Use structured logging (JSON format)
  - [ ] Add request ID to all logs
  - [ ] Add analysis ID to analysis logs
  - [ ] Never log sensitive data
- [ ] Add monitoring hooks
  - [ ] Log analysis duration
  - [ ] Log Redis operation latency
  - [ ] Log error rates
- [ ] Add rate limiting (optional for MVP)
- [ ] Add request size limits
- [ ] Review security considerations

**Acceptance Criteria**:
- Logging is comprehensive and structured
- No sensitive data in logs
- Monitoring metrics are tracked
- Security best practices followed

## Verification Checklist

Before marking this task as complete, verify:

- [ ] All Redis operations work correctly
- [ ] In-memory fallback works when Redis is unavailable
- [ ] All API endpoints return correct responses
- [ ] Error handling is comprehensive
- [ ] Unit tests pass with >80% coverage
- [ ] Integration tests pass
- [ ] Manual testing confirms functionality
- [ ] Documentation is complete
- [ ] Code follows project style guide
- [ ] No secrets or credentials in code
- [ ] Logs are structured and helpful
- [ ] Docker setup works
- [ ] `.env.example` is updated
- [ ] README is updated
- [ ] Code is ready for code review

## Commands Reference

### Start Redis Locally

```bash
docker run --name repotwin-redis -p 6379:6379 -d redis:latest
```

### Stop Redis

```bash
docker stop repotwin-redis
docker rm repotwin-redis
```

### Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests

```bash
cd backend
pytest
pytest --cov=app --cov-report=html
pytest tests/test_redis_store.py -v
```

### Check Types

```bash
cd backend
mypy app/
```

### Format Code

```bash
cd backend
black app/ tests/
ruff check app/ tests/
```

### Test API with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Create analysis
curl -X POST http://localhost:8000/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "660e8400-e29b-41d4-a716-446655440000",
    "change_description": "Add reservation flow before purchase",
    "mode": "demo"
  }'

# Get progress (replace {id} with actual analysis ID)
curl http://localhost:8000/api/analysis/{id}/progress

# Get results
curl http://localhost:8000/api/analysis/{id}/results
```

## Notes

- Use `pnpm` for any Node.js commands (not npm or yarn)
- Never commit credentials or API keys
- Follow AGENTS.md guidelines
- Keep Redis keys following documented naming convention
- Ensure TTL is set for all temporary keys
- Test both Redis and memory store paths
- Document any deviations from the plan
- Ask for clarification if requirements are unclear

## References

- [Backend Architecture](../../backend-analysis-architecture.md)
- [Backend Structure](../../backend-structure.md)
- [API Contract](../../api-contract.md)
- [Redis Job Lifecycle](../../redis-job-lifecycle.md)
- [AGENTS.md](../../../AGENTS.md)