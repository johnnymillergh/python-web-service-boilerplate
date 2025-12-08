# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup & Installation
```bash
# Install dependencies with test group
uv sync --extra test --extra dev

# Install mypy type stubs
uv run mypy --install-types

# Setup pre-commit hooks
uv run pre-commit install -t pre-commit
uv run pre-commit install -t pre-push
```

### Running the Application
```bash
# Development server with auto-reload
fastapi dev src/python_web_service_boilerplate/__main__.py

# Direct module execution
PYTHONPATH=$(pwd) uv run python src/python_web_service_boilerplate/__main__.py

# Using uvicorn directly
uvicorn python_web_service_boilerplate.__main__:app --host localhost --port 8080 --reload
```

### Testing
```bash
# Run all tests with coverage
uv run pytest --cov --cov-report html --cov-fail-under=80 --capture=no --log-cli-level=INFO

# Run with parallel execution
uv run pytest -n auto

# Run specific test file
pytest tests/common/test_debounce_throttle.py

# Run with pattern matching
pytest tests/common/test_debounce_throttle.py -k 'test_debounce'

# Benchmark tests only
uv run pytest --capture=no --log-cli-level=ERROR -n 0 --benchmark-only

# Run with verbose logging
uv run pytest --log-cli-level=DEBUG --capture=no
```

### Code Quality
```bash
# Check and fix imports
uv run ruff check --select I --fix

# Lint all code
uv run ruff check

# Format code
uv run ruff format

# Type checking
uv run mypy
```

### Database Operations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Reset database (development only)
# Drop and recreate all tables
```

### Docker
```bash
# Start with docker-compose
docker-compose up --build

# Database only
docker-compose up db
```

## Project Architecture

### Core Structure
The application follows a layered architecture with clear separation of concerns:

```
src/python_web_service_boilerplate/
├── __main__.py              # Application entry point
├── alembic/                 # Database migrations
├── common/                  # Shared utilities
│   ├── middleware.py        # TraceIDMiddleware
│   ├── router_loader.py     # Auto-discovers and includes routers
│   ├── profiling.py         # Performance profiling utilities
│   └── common_function.py   # Shared helper functions
├── configuration/           # Configuration modules
│   ├── application.py       # Pydantic Settings, pyproject.toml loader
│   ├── database.py          # SQLModel/SQLAlchemy async setup
│   ├── loguru.py            # Logging configuration
│   ├── apscheduler.py       # Job scheduler config
│   └── thread_pool.py       # Thread pool configuration
├── core/                    # Domain layer (business logic)
│   ├── auth/                # Authentication & authorization
│   │   ├── models.py        # User model
│   │   ├── service.py       # Business logic
│   │   ├── repository.py    # Data access
│   │   ├── router.py        # API endpoints
│   │   ├── middleware.py    # AuthMiddleware
│   │   ├── decorators.py    # require_scopes
│   │   └── schemas.py       # Pydantic schemas
│   └── startup_log/         # Startup/shutdown tracking
├── resources/               # Static resources (.env files)
└── demo/                    # Example/demo scripts
```

### Key Architecture Patterns

1. **Router Auto-Discovery** (`common/router_loader.py:53`)
   - Automatically scans all modules for `APIRouter` instances
   - Scopes are extracted via AST parsing from `@require_scopes` decorators
   - All routers in the `core/` directory are automatically included

2. **Configuration** (`configuration/application.py:41`)
   - Uses Pydantic Settings with environment variable support
   - Supports nested configuration with `__` delimiter (e.g., `DATABASE__HOST`)
   - Loads `.env` file from `resources/` directory
   - Reads version from `pyproject.toml` at runtime

3. **Database Layer** (`configuration/database.py:16`)
   - Async-first with SQLModel/SQLAlchemy
   - Supports both PostgreSQL (production) and SQLite (development)
   - Automatic fallback to SQLite in offline environments
   - Connection pooling with pre-ping and LIFO strategy

4. **Authentication** (`core/auth/`)
   - JWT-based authentication via python-jose
   - Scopes-based authorization (extracted dynamically)
   - Middleware checks all requests (can be selective via decorators)
   - Users are soft-deleted with `deleted` flag

5. **Lifespan Management** (`__main__.py:53`)
   - Startup: Configures all components, creates startup log entry
   - Shutdown: Updates shutdown time, cleanup resources
   - Tracked timing and logging throughout lifecycle

### Data Models

#### Core Models
- **User** (`core/auth/models.py:15`): Primary user model with audit fields
  - Uses `get_login_user()` for created_by/updated_by tracking
  - Soft delete via `Deleted` enum
  - Scopes stored as comma-separated string

#### Common Models
- **Deleted** enum: `Y`/`N` for soft deletes
- All models include: `created_at`, `updated_at`, `created_by`, `updated_by`, `deleted`

### Configuration Settings

Environment variables (all case-insensitive, underscore-separated):
- `DATABASE__HOST`, `DATABASE__PORT`, `DATABASE__USERNAME`, `DATABASE__PASSWORD`, `DATABASE__DB_NAME`
- `DATABASE__SQL_LOG_ENABLED` - Enable SQL query logging
- `OFFLINE=true` - Switch to SQLite (development)
- Custom log levels via `LOGGER__<NAME>` pattern

See `resources/.env.example` for all available settings.

### Testing Framework

**Test Structure** (`tests/`):
- Pytest with async support (`pytest-asyncio`)
- Test client configured in `conftest.py`
- Coverage threshold: 80%
- Parallel execution with `pytest-xdist`
- HTML coverage reports in `build/.pytest_report/`

**Test Fixtures** (`conftest.py`):
- `pytest_user`: Creates test user with admin scope
- `test_client`: FastAPI TestClient instance
- `pytest_user_token`: JWT token for authenticated requests

### Database Migrations

**Alembic Setup** (`alembic.ini`):
- Migrations in `alembic/versions/`
- Auto-generated migrations: `alembic revision --autogenerate`
- Upgrade to latest: `alembic upgrade head`
- Downgrade: `alembic downgrade -1`

### Development Workflow

1. **Local Development**:
   - SQLite database in `data/{module_name}.db`
   - Auto-reload enabled via `fastapi dev`
   - Pre-commit hooks run: ruff check/format, mypy, pytest

2. **Production**:
   - PostgreSQL database (psycopg3 + asyncpg)
   - Docker deployment with multi-stage build
   - Health checks configured

### Dependencies Overview

**Core Stack**:
- FastAPI 0.118.0 (web framework)
- SQLModel 0.0.25 + SQLAlchemy 2.0.43 async (ORM)
- Alembic 1.16.5 (migrations)
- PostgreSQL/SQLite (databases)
- orjson 3.11.3 (fast JSON serialization)

**Security**:
- python-jose (JWT)
- passlib[bcrypt] (password hashing)

**Configuration**:
- pydantic 2.11.10 + pydantic-settings 2.11.0
- Pydantic Settings for environment variables

**Development**:
- uv (dependency management)
- ruff 0.12.11 (linting + formatting)
- mypy 1.17.1 (type checking)
- pytest 8.4.1 + plugins (testing)

**Operations**:
- loguru 0.7.3 (logging)
- APScheduler 3.11.0 (job scheduling)
- uvicorn 0.37.0 (ASGI server)

## Key Implementation Details

### Router Inclusion Process
Routers are auto-discovered from the `core/` package. Each router can use `@require_scopes({"scope"})` decorator, and scopes are automatically extracted and logged during startup.

### Database Configuration
The application supports both PostgreSQL and SQLite:
- Production: PostgreSQL with connection pooling
- Development: SQLite (automatic when `offline_environment()` returns True)
- JSON serialization via orjson with numpy and UTC support

### Middleware Stack
1. `AuthMiddleware` - Authenticates requests and checks scopes
2. `TraceIDMiddleware` - Adds request tracing IDs

### Logging
- Centralized via loguru
- Configurable log levels per logger
- SQLAlchemy engine logging can be enabled
- Startup/shutdown logs tracked in database

## API Endpoints

**Core Routes**:
- `GET /hello` - Health check (requires `user:read` scope)
- `GET /health` - Basic health status
- All other routes auto-loaded from `core/*/router.py` files

## CI/CD

**GitHub Actions** (`.github/workflows/python-ci-with-uv.yml`):
- Python 3.13 testing
- Pre-commit hook validation
- Docker image publishing

## Important Files

- `pyproject.toml` - Package configuration, dependencies, tool settings
- `Dockerfile` - Multi-stage build for production
- `docker-compose.yml` - Local development with PostgreSQL
- `.pre-commit-config.yaml` - Pre-commit hooks (ruff, mypy, pytest)
- `resources/.env` - Environment variables
- `alembic.ini` - Database migration configuration
- `.coveragerc` - Coverage reporting configuration

## Pre-commit Hooks

Configured hooks (run on commit):
- Ruff fix imports
- Ruff check and fix
- Ruff format
- mypy type checking
- pytest unit tests

Additional hook for pre-push:
- pytest with coverage (fails under 80%)

## Development Tips

- Use `PYTHONPATH=$(pwd)` when running scripts directly
- Offline mode (SQLite) activates automatically when not connected to network
- All database tables auto-created on startup if they don't exist
- Scope extraction is automatic - just add `@require_scopes` decorators
- Pre-commit hooks ensure code quality before each commit
