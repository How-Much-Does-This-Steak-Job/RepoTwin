# Backend Folder Structure

## Current Structure

The RepoTwin backend follows a clean, layered FastAPI architecture:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration and settings
│   │
│   ├── api/                       # API Layer - HTTP endpoints
│   │   ├── __init__.py
│   │   ├── router.py              # Main API router
│   │   ├── health.py              # Health check endpoints
│   │   ├── analysis.py            # Analysis endpoints (TO BE ENHANCED)
│   │   └── repos.py               # Repository endpoints
│   │
│   ├── services/                  # Service Layer - Business logic
│   │   ├── __init__.py
│   │   ├── repo_service.py        # Repository operations
│   │   ├── analysis_service.py    # [TO ADD] Analysis orchestration
│   │   └── demo_service.py        # [TO ADD] Demo mode handler
│   │
│   ├── redis/                     # [TO ADD] Redis Layer
│   │   ├── __init__.py
│   │   ├── client.py              # Redis client and connection
│   │   ├── store.py               # Redis storage operations
│   │   └── memory_store.py        # In-memory fallback
│   │
│   ├── core/                      # Core Layer - Analysis engines
│   │   ├── __init__.py
│   │   ├── ibm_bob.py             # IBM watsonx.ai integration
│   │   ├── impact_engine.py       # Dependency graph analysis
│   │   ├── code_parser.py         # Code parsing utilities
│   │   └── risk_calculator.py     # Risk scoring logic
│   │
│   ├── models/                    # Data Models - Database ORM
│   │   ├── __init__.py
│   │   └── database.py            # Database configuration
│   │
│   ├── schemas/                   # Schemas - Request/Response contracts
│   │   ├── __init__.py
│   │   ├── analysis.py            # Analysis schemas
│   │   ├── repository.py          # Repository schemas
│   │   └── common.py              # Common/shared schemas
│   │
│   └── utils/                     # [TO ADD] Utilities
│       ├── __init__.py
│       ├── logging.py             # Logging configuration
│       └── errors.py              # Error handling utilities
│
├── tests/                         # Test Suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_code_parser.py
│   ├── test_ibm_bob.py
│   ├── test_impact_engine.py
│   ├── test_repo_analyzer.py
│   ├── test_analysis_service.py   # [TO ADD]
│   └── test_redis_store.py        # [TO ADD]
│
├── Dockerfile                     # Docker container definition
├── requirements.txt               # Python dependencies
└── README.md                      # Backend documentation
```

## Layer Responsibilities

### 1. API Layer (`app/api/`)

**Purpose**: Handle HTTP requests and responses

**Files**:
- `router.py`: Aggregate all API routers
- `health.py`: Health check endpoints
- `analysis.py`: Analysis CRUD and job management endpoints
- `repos.py`: Repository management endpoints

**Responsibilities**:
- Request validation (via Pydantic)
- Response serialization
- HTTP status codes
- Error handling at HTTP level
- Background task scheduling

**Example**:
```python
@router.post("/analyses", response_model=Analysis)
async def create_analysis(data: AnalysisCreate):
    """Create new analysis job."""
    return await analysis_service.create_analysis(data)
```

### 2. Service Layer (`app/services/`)

**Purpose**: Orchestrate business logic and coordinate between layers

**Files**:
- `repo_service.py`: Repository operations (existing)
- `analysis_service.py`: Analysis job orchestration (TO ADD)
- `demo_service.py`: Demo mode data loading (TO ADD)

**Responsibilities**:
- Business logic implementation
- Coordinate between core engines and storage
- Transaction management
- Job lifecycle management
- Progress tracking

**Example**:
```python
class AnalysisService:
    async def create_analysis(self, data: AnalysisCreate) -> Analysis:
        # 1. Create job in Redis
        # 2. Start background analysis
        # 3. Return job metadata
        pass
```

### 3. Redis Layer (`app/redis/`) [TO ADD]

**Purpose**: Manage Redis connections and data operations

**Files**:
- `client.py`: Redis client initialization and connection pooling
- `store.py`: Redis-backed storage operations
- `memory_store.py`: In-memory fallback implementation

**Responsibilities**:
- Redis connection management
- Job state persistence
- Progress tracking
- Result caching
- TTL management
- Graceful fallback to memory

**Example**:
```python
class RedisStore:
    async def set_analysis_status(self, analysis_id: str, status: dict):
        await self.redis.setex(
            f"analysis:{analysis_id}:status",
            ttl=3600,
            value=json.dumps(status)
        )
```

### 4. Core Layer (`app/core/`)

**Purpose**: Implement analysis algorithms and AI integration

**Files**:
- `ibm_bob.py`: IBM watsonx.ai client and prompts (existing)
- `impact_engine.py`: Dependency graph analysis (existing)
- `code_parser.py`: Multi-language code parsing (existing)
- `risk_calculator.py`: Risk scoring algorithms (existing)

**Responsibilities**:
- AI-powered analysis via IBM Bob
- Dependency graph construction
- Impact radius calculation
- Risk assessment
- Code parsing and understanding

**Example**:
```python
async def analyze_impact(
    repository_context: str,
    change_description: str,
) -> AnalysisResults:
    # Use IBM Bob to analyze impact
    pass
```

### 5. Schema Layer (`app/schemas/`)

**Purpose**: Define data contracts and validation rules

**Files**:
- `analysis.py`: Analysis-related schemas (existing)
- `repository.py`: Repository schemas (existing)
- `common.py`: Shared schemas (existing)

**Responsibilities**:
- Request validation
- Response serialization
- Type safety
- API contract enforcement
- Documentation generation

**Example**:
```python
class AnalysisCreate(BaseModel):
    repo_id: UUID
    change_description: str = Field(..., min_length=10)
    mode: AnalysisMode = AnalysisMode.DEMO
```

### 6. Models Layer (`app/models/`)

**Purpose**: Database ORM models (optional for MVP)

**Files**:
- `database.py`: Database configuration (existing)

**Note**: PostgreSQL is optional for MVP. Redis handles most storage needs.

### 7. Utils Layer (`app/utils/`) [TO ADD]

**Purpose**: Shared utilities and helpers

**Files**:
- `logging.py`: Structured logging configuration
- `errors.py`: Custom exceptions and error handlers

## File Naming Conventions

### Python Files

- **Modules**: `snake_case.py` (e.g., `analysis_service.py`)
- **Classes**: `PascalCase` (e.g., `AnalysisService`)
- **Functions**: `snake_case` (e.g., `create_analysis`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ANALYSIS_TIMEOUT`)

### Test Files

- **Pattern**: `test_<module_name>.py`
- **Example**: `test_analysis_service.py`

## Import Conventions

### Absolute Imports

Always use absolute imports from `app`:

```python
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisCreate
from app.redis.store import RedisStore
```

### Layer Dependencies

Follow these dependency rules:

```
API Layer
  ↓ (can import)
Service Layer
  ↓ (can import)
Core Layer + Redis Layer
  ↓ (can import)
Schema Layer + Models Layer
```

**Never**:
- Core layer importing from Service layer
- Schema layer importing from API layer
- Circular dependencies between layers

## Configuration Management

### Environment Variables

All configuration via `app/config.py`:

```python
class Settings(BaseSettings):
    # Application
    app_name: str = "RepoTwin"
    
    # Redis
    redis_url: RedisDsn = "redis://localhost:6379/0"
    
    # IBM watsonx.ai
    watsonx_api_key: Optional[str] = None
```

### Loading Order

1. Default values in `Settings` class
2. `.env` file (development)
3. Environment variables (production)

## Testing Structure

### Test Organization

```
tests/
├── unit/                  # Unit tests (fast, isolated)
│   ├── test_redis_store.py
│   └── test_analysis_service.py
│
├── integration/           # Integration tests (slower, external deps)
│   ├── test_api_endpoints.py
│   └── test_ibm_bob_integration.py
│
└── fixtures/              # Test data and fixtures
    ├── sample_repos.py
    └── mock_responses.py
```

### Test Naming

- **Pattern**: `test_<function>_<scenario>_<expected>`
- **Example**: `test_create_analysis_with_demo_mode_returns_job`

## Adding New Features

### Checklist for New Endpoints

1. **Schema** (`app/schemas/`): Define request/response models
2. **Service** (`app/services/`): Implement business logic
3. **API** (`app/api/`): Create endpoint handler
4. **Router** (`app/api/router.py`): Register endpoint
5. **Tests** (`tests/`): Add unit and integration tests
6. **Docs**: Update API documentation

### Example: Adding New Endpoint

```python
# 1. Schema (app/schemas/analysis.py)
class AnalysisCancel(BaseModel):
    reason: Optional[str] = None

# 2. Service (app/services/analysis_service.py)
async def cancel_analysis(self, analysis_id: UUID, reason: str):
    # Implementation
    pass

# 3. API (app/api/analysis.py)
@router.post("/{analysis_id}/cancel")
async def cancel_analysis(analysis_id: UUID, data: AnalysisCancel):
    await analysis_service.cancel_analysis(analysis_id, data.reason)
    return {"status": "cancelled"}

# 4. Test (tests/test_analysis_service.py)
async def test_cancel_analysis_updates_status():
    # Test implementation
    pass
```

## Code Quality Standards

### Type Hints

Always use type hints:

```python
async def create_analysis(
    data: AnalysisCreate,
    background_tasks: BackgroundTasks,
) -> Analysis:
    pass
```

### Docstrings

Use Google-style docstrings:

```python
async def analyze_impact(repo_id: UUID) -> AnalysisResults:
    """Analyze impact of code change.
    
    Args:
        repo_id: Repository UUID
        
    Returns:
        Analysis results with affected files
        
    Raises:
        AnalysisError: If analysis fails
    """
    pass
```

### Error Handling

Use custom exceptions:

```python
class AnalysisError(Exception):
    """Base exception for analysis errors."""
    pass

class AnalysisNotFoundError(AnalysisError):
    """Analysis not found."""
    pass
```

## Development Workflow

### Local Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run Redis (optional)
docker run --name repotwin-redis -p 6379:6379 -d redis:latest

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_analysis_service.py

# Specific test
pytest tests/test_analysis_service.py::test_create_analysis
```

### Code Formatting

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type check
mypy app/
```

## Migration Path

### Current State → Target State

**Phase 1: Redis Integration**
- Add `app/redis/` layer
- Implement `RedisStore` and `MemoryStore`
- Update `analysis_service.py` to use Redis

**Phase 2: Enhanced Analysis**
- Enhance `analysis.py` endpoints
- Add demo mode support
- Implement progress tracking

**Phase 3: Testing & Polish**
- Add comprehensive tests
- Add error handling
- Add logging and monitoring

## References

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Python Project Structure](https://docs.python-guide.org/writing/structure/)
- [AGENTS.md](../AGENTS.md) - Project guidelines