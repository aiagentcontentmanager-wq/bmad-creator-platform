# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BMAD (Blueprint-Manifest-Agents-Deployment) is a multi-agent AI orchestration platform for content creation, recruitment, and social media management. It uses FastAPI as the API layer, SQLite for local persistence, Redis for caching/rate-limiting, and integrates with local (Ollama) and remote (OpenRouter) AI providers.

Documentation is primarily in German.

## Build & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server (development)
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Run the model orchestrator standalone
python -m src.model_orchestrator

# Run with Docker
docker-compose up --build
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_model_orchestrator.py -v

# Run a specific test
python -m pytest tests/test_model_orchestrator.py::TestModelOrchestrator::test_execute_task_success -v
```

Tests use `pytest` with `asyncio` support. Async test functions are standard pytest functions using `asyncio.run()` or fixtures.

## Architecture

### Layer Structure

The system follows a layered architecture:

- **API Layer** (`src/api/main.py`) — FastAPI application with JWT auth, endpoints for users, managers, agents, tasks, and supervisor health.
- **Agents** (`src/agents/`) — Autonomous agents managed by a SupervisorAgent parent. Key agents: SupervisorAgent, RecruiterAgent, CommunicationService.
- **Model Orchestrator** (`src/model_orchestrator.py`) — Routes tasks to AI providers (Ollama, OpenRouter) with round-robin selection, quota management, and retry logic.
- **Security** (`src/security/`) — Four modules forming a pipeline: input sanitization → prompt building → provider call → output validation. Also includes Redis-based rate limiting.
- **Auth** (`src/auth/auth.py`) — JWT-based authentication with bcrypt password hashing, role-based access (admin, manager).
- **Database** (`src/database/`) — SQLite with manual schema initialization. Tables: users, managers, model_manager, recruitment_funnel, communications, communication_templates. Migrations in `src/database/migrations/`.
- **Communication** (`src/database/communication_database.py`, `src/agents/communication_service.py`) — Multi-channel communication (email, SMS, WhatsApp, etc.) with template support.

### Security Pipeline

All AI task execution flows through a security pipeline in `ModelOrchestrator.execute_task()`:

1. `PromptInjectionDetector.detect()` — blocks prompt injection via regex patterns
2. `SecurePromptBuilder.build_secure_prompt()` — wraps user input with immutable system delimiters
3. `AIOutputValidator.validate()` — redacts leaked API keys, credentials, paths from AI output
4. `AIRateLimiter.check_limit()` — Redis-based sliding window rate limiting (50 req/15 min)

### Agent Hierarchy

```
SupervisorAgent (parent)
├── ContentAgent
├── AnalyticsAgent
├── GovernanceAgent
├── RecruiterAgent
└── ModelOrchestrator
```

The SupervisorAgent handles registration, health checks, policy evaluation, and automatic restart of degraded agents.

### Configuration

- `config/config.yaml` — Model paths and default parameters
- `docker-compose.yml` — Redis 7 + app service on port 8000
- Environment variables: `ENV`, `LOG_LEVEL`, `REDIS_URL`, `SUPABASE_URL`, `SUPABASE_KEY`

### Key Data Flow

User request → JWT auth → API endpoint → SupervisorAgent (policy check) → ModelOrchestrator → (injection check → secure prompt → provider call → output validation) → response

## Tech Stack

- **Python 3.9+** with FastAPI, Uvicorn
- **SQLite** (`bmad.db`) for local persistence
- **Redis** for caching and rate limiting
- **JWT (PyJWT)** for authentication, **bcrypt** for password hashing
- **Pydantic** for input validation
- **pytest** for testing
- **Docker** + docker-compose for containerized deployment
