# Task 0005: API Endpoints (FastAPI Routers)

## Overview
Implement all FastAPI API routers for documents, evaluations, vendors, admin, and health check.

## Subtasks

### 5.1 Create API router aggregator
- Create `app/api/v1/router.py` to combine all routers
- Create `app/api/v1/__init__.py`
- Reference: Section 6.1 (Backend Structure)

### 5.2 Implement document endpoints
- Create `app/api/v1/documents.py` router
- Implement `POST /api/v1/documents/upload` with multipart form handling
- Implement `GET /api/v1/documents/{id}` endpoint
- Implement `GET /api/v1/documents/{id}/download` endpoint
- Reference: Section 9.3 (Document Endpoints)

### 5.3 Implement evaluation endpoints
- Create `app/api/v1/evaluations.py` router
- Implement `GET /api/v1/evaluations` with pagination and filtering
- Implement `POST /api/v1/evaluations` to create evaluation
- Implement `GET /api/v1/evaluations/{id}` endpoint
- Implement `POST /api/v1/evaluations/{id}/bids` to add vendor bids
- Implement `PATCH /api/v1/evaluations/{id}/config` endpoint
- Reference: Section 9.2 (Evaluation Endpoints)

### 5.4 Implement evaluation workflow endpoints
- Implement `POST /api/v1/evaluations/{id}/start` to trigger background processing
- Implement `POST /api/v1/evaluations/{id}/cancel` endpoint
- Implement `POST /api/v1/evaluations/{id}/approve` endpoint
- Reference: Section 9.2 (Evaluation Endpoints)

### 5.5 Implement evaluation results endpoints
- Implement `GET /api/v1/evaluations/{id}/results` endpoint
- Implement `GET /api/v1/evaluations/{id}/results/compliance` endpoint
- Implement `GET /api/v1/evaluations/{id}/results/technical` with optional vendor_id filter
- Implement `GET /api/v1/evaluations/{id}/results/financial` endpoint
- Implement `GET /api/v1/evaluations/{id}/results/comparison` endpoint
- Implement `GET /api/v1/evaluations/{id}/export` with format query parameter
- Reference: Section 9.2 (Evaluation Endpoints)

### 5.6 Implement vendor endpoints
- Create `app/api/v1/vendors.py` router
- Implement `GET /api/v1/vendors` with search, pagination
- Implement `GET /api/v1/vendors/{id}` endpoint
- Implement `GET /api/v1/vendors/{id}/history` endpoint
- Reference: Section 9.4 (Vendor Endpoints)

### 5.7 Implement admin endpoints
- Create `app/api/v1/admin.py` router
- Implement user CRUD endpoints (GET, POST, PATCH, DELETE)
- Implement `GET /api/v1/admin/audit-logs` with filtering
- Implement `GET /api/v1/departments` endpoint
- Reference: Section 9.5 (Admin Endpoints)

### 5.8 Implement health check endpoint
- Create `app/api/v1/health.py` router
- Return application health status
- Reference: Section 4.1 (High-Level Architecture - Health Router)

## References
- Section 4.1 (High-Level Architecture)
- Section 6.1 (Backend Structure)
- Section 9.2 (Evaluation Endpoints)
- Section 9.3 (Document Endpoints)
- Section 9.4 (Vendor Endpoints)
- Section 9.5 (Admin Endpoints)
