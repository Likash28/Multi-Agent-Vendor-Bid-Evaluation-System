# Task 0003: Authentication & Security

## Overview
Implement the complete authentication and security layer including JWT handling, RBAC, security headers, and audit logging.

## Subtasks

### 3.1 Implement password hashing and JWT utilities
- Create `app/core/security.py` with bcrypt password hashing
- Implement `create_access_token()` and `create_refresh_token()` functions
- Add token verification and decoding
- Reference: Section 10.1 (Authentication & Authorization)

### 3.2 Implement authentication middleware and guards
- Create `app/core/auth.py` with `get_current_user` dependency
- Implement `get_current_user_ws` for WebSocket authentication
- Add token refresh logic
- Reference: Section 10.1 (Authentication & Authorization)

### 3.3 Implement Role-Based Access Control (RBAC)
- Define Permission enum with all permissions from Section 10.2
- Create ROLE_PERMISSIONS mapping for officer, evaluator, admin roles
- Implement `require_permission` decorator
- Reference: Section 10.2 (Role-Based Access Control)

### 3.4 Create authentication API endpoints
- Implement `POST /api/v1/auth/register` endpoint
- Implement `POST /api/v1/auth/login` endpoint with JWT token generation
- Implement `POST /api/v1/auth/logout` endpoint
- Implement `POST /api/v1/auth/refresh` endpoint
- Implement `GET /api/v1/auth/me` endpoint
- Reference: Section 9.1 (Authentication Endpoints)

### 3.5 Implement password reset flow
- Implement `POST /api/v1/auth/forgot-password` endpoint
- Implement `POST /api/v1/auth/reset-password` endpoint
- Reference: Section 9.1 (Password Reset endpoints)

### 3.6 Add security headers middleware
- Create `app/core/middleware.py` with SecurityHeadersMiddleware
- Add X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS headers
- Reference: Section 10.4 (Security Headers)

### 3.7 Implement audit logging service
- Create `app/services/audit_service.py` with async logging functionality
- Log entity changes, actor, IP address, user agent
- Reference: Section 10.3 (Audit Logging)

## References
- Section 9.1 (Authentication Endpoints)
- Section 10.1 (Authentication & Authorization)
- Section 10.2 (Role-Based Access Control)
- Section 10.3 (Audit Logging)
- Section 10.4 (Security Headers)
