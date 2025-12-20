# Task 0019: Testing

## Overview
Set up testing infrastructure and write tests for both backend and frontend including authentication, evaluations, agents, and component tests.

## Subtasks

### 19.1 Set up backend testing infrastructure
- Create `tests/conftest.py` with pytest fixtures
- Configure test database (SQLite in-memory)
- Create test client factory
- Reference: Section 6.1 (tests directory)

### 19.2 Write authentication tests
- Create `tests/test_auth.py`
- Test registration, login, token refresh, logout endpoints
- Test RBAC permission checks
- Reference: Section 6.1 (test_auth.py)

### 19.3 Write evaluation endpoint tests
- Create `tests/test_evaluations.py`
- Test CRUD operations, workflow transitions
- Test results endpoints
- Reference: Section 6.1 (test_evaluations.py)

### 19.4 Write agent unit tests
- Create `tests/test_agents.py`
- Test individual agent functionality with mock LLM responses
- Test orchestrator workflow
- Reference: Section 6.1 (test_agents.py)

### 19.5 Set up frontend testing
- Configure Jest and React Testing Library
- Create test utilities for component testing
- Reference: Section 3.1 (Frontend Stack)

### 19.6 Write frontend component tests
- Test wizard components
- Test results view components
- Test form validation
- Reference: Section 5 (Frontend Specification)

## References
- Section 3.1 (Frontend Stack)
- Section 5 (Frontend Specification)
- Section 6.1 (tests directory)
