# Environment Configuration

## Overview

This document defines the required environment variables for the RepoTwin backend. The backend member should update `.env.example` with these configurations.

## Required .env.example Updates

The `.env.example` file should be updated to include Redis configuration. Here's the complete recommended configuration:

```bash
# ============================================================================
# IBM watsonx.ai Configuration
# ============================================================================

# IBM watsonx.ai API Key (required for live mode, optional for demo mode)
WATSONX_API_KEY=your-api-key-here

# IBM watsonx.ai Project ID (optional)
WATSONX_PROJECT_ID=

# IBM watsonx.ai API URL
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Model Configuration
WATSONX_MODEL_ID=ibm-granite-13b-chat-v2
WATSONX_MAX_TOKENS=4096
WATSONX_TEMPERATURE=0.1
WATSONX_TOP_P=0.9

# ============================================================================
# Redis Configuration
# ============================================================================

# Redis connection URL
# Format: redis://[username:password@]host:port/database
# Local development: redis://localhost:6379/0
# Docker: redis://repotwin-redis:6379/0
REDIS_URL=redis://localhost:6379/0

# Redis connection pool size
REDIS_POOL_SIZE=20

# Enable/disable Redis (set to false to force in-memory fallback)
REDIS_ENABLED=true

# ============================================================================
# Database Configuration (Optional for MVP)
# ============================================================================

# PostgreSQL connection details
POSTGRES_USER=repotwin
POSTGRES_PASSWORD=repotwin123
POSTGRES_DB=repotwin
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Full database URL (alternative to individual settings)
# DATABASE_URL=postgresql+asyncpg://repotwin:repotwin123@localhost:5432/repotwin

# ============================================================================
# Application Configuration
# ============================================================================

# Application name
APP_NAME=RepoTwin

# Application version
APP_VERSION=1.0.0

# Environment (development, staging, production)
ENVIRONMENT=development

# Debug mode (true/false)
DEBUG=false

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log format (json, text)
LOG_FORMAT=json

# ============================================================================
# Server Configuration
# ============================================================================

# Server host
HOST=0.0.0.0

# Server port
PORT=8000

# Number of worker processes
WORKERS=1

# Enable auto-reload (development only)
RELOAD=true

# ============================================================================
# Security Configuration
# ============================================================================

# Secret key for JWT tokens (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-change-this-in-production

# Access token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Refresh token expiration (days)
REFRESH_TOKEN_EXPIRE_DAYS=7

# JWT algorithm
ALGORITHM=HS256

# ============================================================================
# CORS Configuration
# ============================================================================

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Allowed origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ============================================================================
# Analysis Configuration
# ============================================================================

# Maximum context size for analysis (characters)
ANALYSIS_MAX_CONTEXT_SIZE=100000

# Analysis timeout (seconds)
ANALYSIS_TIMEOUT_SECONDS=300

# Maximum files per analysis
MAX_FILES_PER_ANALYSIS=50

# ============================================================================
# Caching Configuration
# ============================================================================

# Repository metadata cache TTL (seconds)
CACHE_TTL_REPOSITORY=3600

# Dependency graph cache TTL (seconds)
CACHE_TTL_DEPENDENCY_GRAPH=3600

# Analysis results cache TTL (seconds)
CACHE_TTL_ANALYSIS_RESULTS=86400

# ============================================================================
# Git Configuration
# ============================================================================

# Git clone timeout (seconds)
GIT_CLONE_TIMEOUT=300

# Maximum repository size (MB)
GIT_MAX_REPO_SIZE_MB=500

# Git storage path
GIT_STORAGE_PATH=/tmp/repotwin/repos

# ============================================================================
# Rate Limiting
# ============================================================================

# Requests per minute per client
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# watsonx.ai rate limit per minute
WATSONX_RATE_LIMIT_PER_MINUTE=100
```

## Environment-Specific Configurations

### Development (.env)

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
RELOAD=true
REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:3000
```

### Docker Compose (.env.docker)

```bash
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
REDIS_URL=redis://repotwin-redis:6379/0
POSTGRES_HOST=repotwin-postgres
DATABASE_URL=postgresql+asyncpg://repotwin:repotwin123@repotwin-postgres:5432/repotwin
```

### Production (.env.production)

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
LOG_FORMAT=json
REDIS_URL=redis://production-redis:6379/0
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/repotwin
SECRET_KEY=<strong-random-key>
WATSONX_API_KEY=<production-api-key>
ALLOWED_ORIGINS=https://repotwin.example.com
```

## Redis Setup Commands

### Local Development

```bash
# Start Redis with Docker
docker run --name repotwin-redis -p 6379:6379 -d redis:latest

# Stop Redis
docker stop repotwin-redis

# Remove Redis container
docker rm repotwin-redis

# View Redis logs
docker logs repotwin-redis

# Connect to Redis CLI
docker exec -it repotwin-redis redis-cli
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: repotwin-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  backend:
    build: ./backend
    container_name: repotwin-backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - ./backend:/app

volumes:
  redis_data:
```

## Configuration Validation

### Required Variables

These variables MUST be set:

- `WATSONX_API_KEY` (for live mode)
- `SECRET_KEY` (for production)
- `REDIS_URL` (if Redis is enabled)

### Optional Variables

These variables have sensible defaults:

- `REDIS_ENABLED` (default: true)
- `REDIS_POOL_SIZE` (default: 20)
- `LOG_LEVEL` (default: INFO)
- `ENVIRONMENT` (default: development)

### Validation Script

```python
# backend/app/utils/config_validator.py

import os
import sys
from typing import List, Tuple

def validate_config() -> Tuple[bool, List[str]]:
    """Validate environment configuration."""
    errors = []
    
    # Check required variables for production
    if os.getenv("ENVIRONMENT") == "production":
        required = [
            "SECRET_KEY",
            "WATSONX_API_KEY",
            "REDIS_URL",
        ]
        
        for var in required:
            if not os.getenv(var):
                errors.append(f"Missing required variable: {var}")
    
    # Validate Redis URL format
    redis_url = os.getenv("REDIS_URL")
    if redis_url and not redis_url.startswith("redis://"):
        errors.append("REDIS_URL must start with redis://")
    
    # Validate log level
    log_level = os.getenv("LOG_LEVEL", "INFO")
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_levels)}")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    valid, errors = validate_config()
    if not valid:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("Configuration is valid")
```

## Security Best Practices

### Never Commit

❌ **DO NOT** commit these to version control:

- Actual API keys
- Production passwords
- Secret keys
- Database credentials
- Personal tokens

### Use Strong Values

✅ **DO** use strong, random values for:

```bash
# Generate secret key
openssl rand -hex 32

# Generate password
openssl rand -base64 32
```

### Environment-Specific Files

Create separate `.env` files for each environment:

```
.env                    # Local development (gitignored)
.env.example           # Template (committed)
.env.docker            # Docker Compose (gitignored)
.env.production        # Production (never committed)
.env.test              # Testing (committed, no secrets)
```

### .gitignore

Ensure `.gitignore` includes:

```
.env
.env.local
.env.*.local
.env.docker
.env.production
*.pem
*.key
```

## Troubleshooting

### Redis Connection Issues

**Problem**: `ConnectionError: Error connecting to Redis`

**Solutions**:
1. Check Redis is running: `docker ps | grep redis`
2. Check Redis URL is correct in `.env`
3. Test connection: `redis-cli -h localhost -p 6379 ping`
4. Check firewall/network settings
5. Enable fallback: `REDIS_ENABLED=false`

### Missing Environment Variables

**Problem**: `KeyError: 'WATSONX_API_KEY'`

**Solutions**:
1. Copy `.env.example` to `.env`
2. Fill in required values
3. Restart the application
4. Check variable names match exactly

### Permission Issues

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solutions**:
1. Check file permissions: `ls -la .env`
2. Fix permissions: `chmod 600 .env`
3. Check directory permissions
4. Run with appropriate user

## References

- [Backend Architecture](./backend-analysis-architecture.md)
- [Redis Job Lifecycle](./redis-job-lifecycle.md)
- [AGENTS.md](../AGENTS.md)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Redis Configuration](https://redis.io/docs/management/config/)