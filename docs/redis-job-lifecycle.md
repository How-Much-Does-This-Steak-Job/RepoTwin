# Redis Job Lifecycle Documentation

## Overview

RepoTwin uses Redis as the primary storage for analysis job state, progress tracking, and result caching. This document defines the complete Redis-based job lifecycle, key structure, TTL strategy, and fallback behavior.

## Job Lifecycle States

```
┌─────────┐
│ QUEUED  │ ← Job created, waiting to start
└────┬────┘
     │
     ▼
┌─────────┐
│ RUNNING │ ← Analysis in progress
└────┬────┘
     │
     ├──────────────┐
     ▼              ▼
┌───────────┐  ┌─────────┐
│ COMPLETED │  │ FAILED  │
└───────────┘  └─────────┘
     │              │
     ▼              ▼
┌─────────────────────┐
│ EXPIRED (after TTL) │
└─────────────────────┘
```

### State Definitions

| State | Description | Next States | TTL |
|-------|-------------|-------------|-----|
| `queued` | Job created, waiting to start | `running`, `failed` | 1 hour |
| `running` | Analysis in progress | `completed`, `failed` | 1 hour |
| `completed` | Analysis finished successfully | `expired` | 24 hours |
| `failed` | Analysis failed with error | `expired` | 24 hours |
| `cancelled` | User cancelled the job | `expired` | 1 hour |

## Redis Key Structure

### Key Naming Convention

All keys follow this pattern:

```
{namespace}:{entity}:{id}:{attribute}
```

### Analysis Job Keys

#### 1. Job Status

**Key**: `analysis:{analysis_id}:status`

**Value**: JSON string

**TTL**: 1 hour (queued/running), 24 hours (completed/failed)

**Example**:
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "created_at": "2026-05-16T04:00:00Z",
  "updated_at": "2026-05-16T04:02:30Z",
  "started_at": "2026-05-16T04:00:01Z",
  "completed_at": null,
  "error_message": null
}
```

#### 2. Job Progress

**Key**: `analysis:{analysis_id}:progress`

**Value**: JSON string

**TTL**: 1 hour

**Example**:
```json
{
  "progress_percent": 65,
  "current_step": "Calculating blast radius",
  "message": "Analyzing impact propagation with IBM Bob-assisted analysis",
  "estimated_time_remaining": 120,
  "timestamp": "2026-05-16T04:02:30Z"
}
```

#### 3. Job Result

**Key**: `analysis:{analysis_id}:result`

**Value**: JSON string (complete Shadow PR)

**TTL**: 24 hours

**Example**:
```json
{
  "summary": { ... },
  "affected_files": [ ... ],
  "impact_radius": { ... },
  "risk_assessment": { ... },
  "regression_analysis": { ... },
  "implementation_plan": { ... },
  "test_recommendations": { ... }
}
```

#### 4. Job Metadata

**Key**: `analysis:{analysis_id}:metadata`

**Value**: JSON string

**TTL**: 24 hours

**Example**:
```json
{
  "repo_id": "660e8400-e29b-41d4-a716-446655440000",
  "repo_name": "UniMarket",
  "change_description": "Add reservation flow before purchase",
  "target_branch": "main",
  "mode": "demo",
  "selected_files": ["src/models/listing.py"],
  "context_files": ["src/models/transaction.py"]
}
```

#### 5. Job Error

**Key**: `analysis:{analysis_id}:error`

**Value**: JSON string

**TTL**: 24 hours

**Example**:
```json
{
  "error_code": "ANALYSIS_FAILED",
  "error_message": "IBM watsonx.ai API timeout",
  "error_details": "Request timed out after 300 seconds",
  "timestamp": "2026-05-16T04:05:00Z",
  "stack_trace": null
}
```

### Repository Cache Keys

#### 1. Repository Summary

**Key**: `repo:{repo_name}:summary`

**Value**: JSON string

**TTL**: 1 hour

**Example**:
```json
{
  "name": "UniMarket",
  "description": "Android marketplace app",
  "total_files": 387,
  "total_lines": 45230,
  "languages": ["Kotlin", "Java", "XML"],
  "last_updated": "2026-05-16T04:00:00Z"
}
```

#### 2. Dependency Graph

**Key**: `repo:{repo_name}:dependencies`

**Value**: JSON string (NetworkX graph data)

**TTL**: 1 hour

**Example**:
```json
{
  "nodes": [ ... ],
  "edges": [ ... ],
  "stats": {
    "total_nodes": 387,
    "total_edges": 1243
  }
}
```

### Demo Scenario Keys

#### 1. Demo Analysis Cache

**Key**: `demo:{repo_name}:{scenario_slug}`

**Value**: JSON string (complete Shadow PR)

**TTL**: No expiration (permanent cache)

**Example Key**: `demo:unimarket:reservation-flow`

**Example Value**: Contents of `data/sample-shadow-pr.json`

### Session Keys

#### 1. Active Analysis Set

**Key**: `active:analyses`

**Value**: Redis Set of analysis IDs

**TTL**: No expiration

**Purpose**: Track all currently running analyses

**Operations**:
```python
# Add to active set
await redis.sadd("active:analyses", analysis_id)

# Remove from active set
await redis.srem("active:analyses", analysis_id)

# Get all active
active_ids = await redis.smembers("active:analyses")
```

#### 2. Repository Analysis History

**Key**: `repo:{repo_id}:analyses`

**Value**: Redis Sorted Set (score = timestamp)

**TTL**: 7 days

**Purpose**: Track analysis history per repository

**Operations**:
```python
# Add analysis
await redis.zadd(
    f"repo:{repo_id}:analyses",
    {analysis_id: timestamp}
)

# Get recent analyses
recent = await redis.zrevrange(
    f"repo:{repo_id}:analyses",
    0, 9  # Last 10
)
```

## Redis Operations

### Job Creation Flow

```python
async def create_analysis_job(
    analysis_id: str,
    repo_id: str,
    change_description: str,
    mode: str = "demo"
) -> None:
    """Create new analysis job in Redis."""
    
    # 1. Store job status
    status = {
        "analysis_id": analysis_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
        "error_message": None
    }
    await redis.setex(
        f"analysis:{analysis_id}:status",
        3600,  # 1 hour TTL
        json.dumps(status)
    )
    
    # 2. Store job metadata
    metadata = {
        "repo_id": repo_id,
        "change_description": change_description,
        "mode": mode,
        "target_branch": "main"
    }
    await redis.setex(
        f"analysis:{analysis_id}:metadata",
        86400,  # 24 hours TTL
        json.dumps(metadata)
    )
    
    # 3. Initialize progress
    progress = {
        "progress_percent": 0,
        "current_step": "Waiting to start",
        "message": "Job queued",
        "timestamp": datetime.utcnow().isoformat()
    }
    await redis.setex(
        f"analysis:{analysis_id}:progress",
        3600,  # 1 hour TTL
        json.dumps(progress)
    )
    
    # 4. Add to active set
    await redis.sadd("active:analyses", analysis_id)
    
    # 5. Add to repository history
    await redis.zadd(
        f"repo:{repo_id}:analyses",
        {analysis_id: time.time()}
    )
```

### Progress Update Flow

```python
async def update_progress(
    analysis_id: str,
    progress_percent: int,
    current_step: str,
    message: str
) -> None:
    """Update analysis progress."""
    
    # 1. Update progress
    progress = {
        "progress_percent": progress_percent,
        "current_step": current_step,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    await redis.setex(
        f"analysis:{analysis_id}:progress",
        3600,  # 1 hour TTL
        json.dumps(progress)
    )
    
    # 2. Update status timestamp
    status_key = f"analysis:{analysis_id}:status"
    status_json = await redis.get(status_key)
    if status_json:
        status = json.loads(status_json)
        status["updated_at"] = datetime.utcnow().isoformat()
        
        # Update to running if still queued
        if status["status"] == "queued":
            status["status"] = "running"
            status["started_at"] = datetime.utcnow().isoformat()
        
        await redis.setex(status_key, 3600, json.dumps(status))
```

### Job Completion Flow

```python
async def complete_analysis(
    analysis_id: str,
    result: dict
) -> None:
    """Mark analysis as completed and store result."""
    
    # 1. Store result
    await redis.setex(
        f"analysis:{analysis_id}:result",
        86400,  # 24 hours TTL
        json.dumps(result)
    )
    
    # 2. Update status
    status_key = f"analysis:{analysis_id}:status"
    status_json = await redis.get(status_key)
    if status_json:
        status = json.loads(status_json)
        status["status"] = "completed"
        status["updated_at"] = datetime.utcnow().isoformat()
        status["completed_at"] = datetime.utcnow().isoformat()
        
        await redis.setex(
            status_key,
            86400,  # 24 hours TTL
            json.dumps(status)
        )
    
    # 3. Update progress to 100%
    progress = {
        "progress_percent": 100,
        "current_step": "Completed",
        "message": "Shadow PR ready",
        "timestamp": datetime.utcnow().isoformat()
    }
    await redis.setex(
        f"analysis:{analysis_id}:progress",
        86400,  # 24 hours TTL
        json.dumps(progress)
    )
    
    # 4. Remove from active set
    await redis.srem("active:analyses", analysis_id)
```

### Job Failure Flow

```python
async def fail_analysis(
    analysis_id: str,
    error_code: str,
    error_message: str,
    error_details: str = None
) -> None:
    """Mark analysis as failed."""
    
    # 1. Store error
    error = {
        "error_code": error_code,
        "error_message": error_message,
        "error_details": error_details,
        "timestamp": datetime.utcnow().isoformat()
    }
    await redis.setex(
        f"analysis:{analysis_id}:error",
        86400,  # 24 hours TTL
        json.dumps(error)
    )
    
    # 2. Update status
    status_key = f"analysis:{analysis_id}:status"
    status_json = await redis.get(status_key)
    if status_json:
        status = json.loads(status_json)
        status["status"] = "failed"
        status["updated_at"] = datetime.utcnow().isoformat()
        status["completed_at"] = datetime.utcnow().isoformat()
        status["error_message"] = error_message
        
        await redis.setex(
            status_key,
            86400,  # 24 hours TTL
            json.dumps(status)
        )
    
    # 3. Remove from active set
    await redis.srem("active:analyses", analysis_id)
```

## TTL Strategy

### Time-to-Live Rules

| Key Type | TTL | Reason |
|----------|-----|--------|
| Job status (queued/running) | 1 hour | Short-lived, active jobs |
| Job status (completed/failed) | 24 hours | Allow result retrieval |
| Job progress | 1 hour | Only needed during execution |
| Job result | 24 hours | Cache for repeated access |
| Job metadata | 24 hours | Needed for result context |
| Job error | 24 hours | Debugging information |
| Repository summary | 1 hour | Frequently updated |
| Dependency graph | 1 hour | Expensive to compute |
| Demo scenarios | No expiration | Permanent cache |
| Active analyses set | No expiration | Managed manually |
| Repository history | 7 days | Historical tracking |

### TTL Extension

For long-running analyses, extend TTL periodically:

```python
async def extend_job_ttl(analysis_id: str) -> None:
    """Extend TTL for long-running job."""
    keys = [
        f"analysis:{analysis_id}:status",
        f"analysis:{analysis_id}:progress",
        f"analysis:{analysis_id}:metadata"
    ]
    
    for key in keys:
        await redis.expire(key, 3600)  # Extend by 1 hour
```

## In-Memory Fallback

When Redis is unavailable, the backend falls back to in-memory storage.

### MemoryStore Implementation

```python
class MemoryStore:
    """In-memory fallback for Redis."""
    
    def __init__(self):
        self._data: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._lock = asyncio.Lock()
    
    async def setex(self, key: str, ttl: int, value: str) -> None:
        """Set key with expiration."""
        async with self._lock:
            expires_at = time.time() + ttl if ttl else None
            self._data[key] = (value, expires_at)
    
    async def get(self, key: str) -> Optional[str]:
        """Get key value."""
        async with self._lock:
            if key not in self._data:
                return None
            
            value, expires_at = self._data[key]
            
            # Check expiration
            if expires_at and time.time() > expires_at:
                del self._data[key]
                return None
            
            return value
    
    async def delete(self, key: str) -> None:
        """Delete key."""
        async with self._lock:
            self._data.pop(key, None)
    
    async def sadd(self, key: str, *values: str) -> None:
        """Add to set."""
        async with self._lock:
            if key not in self._data:
                self._data[key] = (set(), None)
            
            current_set, expires_at = self._data[key]
            current_set.update(values)
            self._data[key] = (current_set, expires_at)
```

### Fallback Detection

```python
async def get_store() -> Union[RedisStore, MemoryStore]:
    """Get storage backend with fallback."""
    try:
        redis_store = RedisStore()
        await redis_store.ping()
        logger.info("Using Redis storage")
        return redis_store
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}. Using in-memory fallback")
        return MemoryStore()
```

## Monitoring and Cleanup

### Cleanup Stale Jobs

```python
async def cleanup_stale_jobs() -> None:
    """Clean up jobs stuck in running state."""
    
    # Get all active analyses
    active_ids = await redis.smembers("active:analyses")
    
    for analysis_id in active_ids:
        status_json = await redis.get(f"analysis:{analysis_id}:status")
        if not status_json:
            # Status expired, remove from active set
            await redis.srem("active:analyses", analysis_id)
            continue
        
        status = json.loads(status_json)
        
        # Check if stuck in running state
        if status["status"] == "running":
            updated_at = datetime.fromisoformat(status["updated_at"])
            age = datetime.utcnow() - updated_at
            
            if age.total_seconds() > 3600:  # 1 hour timeout
                await fail_analysis(
                    analysis_id,
                    "TIMEOUT",
                    "Analysis timed out after 1 hour"
                )
```

### Monitoring Metrics

Track these Redis metrics:

1. **Key Count**: Total keys in Redis
2. **Memory Usage**: Redis memory consumption
3. **Hit Rate**: Cache hit vs miss ratio
4. **Active Jobs**: Count of running analyses
5. **TTL Distribution**: Keys by TTL bucket

## Best Practices

### 1. Always Set TTL

Never create keys without TTL (except permanent caches):

```python
# ❌ Bad: No TTL
await redis.set(key, value)

# ✅ Good: With TTL
await redis.setex(key, 3600, value)
```

### 2. Use Atomic Operations

Use Redis transactions for multi-key updates:

```python
async with redis.pipeline() as pipe:
    pipe.setex(f"analysis:{id}:status", 3600, status_json)
    pipe.setex(f"analysis:{id}:progress", 3600, progress_json)
    await pipe.execute()
```

### 3. Handle Missing Keys

Always check for None:

```python
status_json = await redis.get(key)
if status_json is None:
    raise AnalysisNotFoundError(f"Analysis {id} not found")
```

### 4. Serialize Consistently

Always use JSON for complex data:

```python
# ✅ Good: JSON serialization
await redis.setex(key, ttl, json.dumps(data))
data = json.loads(await redis.get(key))
```

### 5. Log Redis Operations

Log all Redis failures:

```python
try:
    await redis.setex(key, ttl, value)
except RedisError as e:
    logger.error(f"Redis operation failed: {e}")
    # Fall back to memory store
```

## References

- [Redis Documentation](https://redis.io/documentation)
- [Redis Best Practices](https://redis.io/topics/best-practices)
- [Python Redis Client](https://redis-py.readthedocs.io/)
- [AGENTS.md](../AGENTS.md) - Project guidelines