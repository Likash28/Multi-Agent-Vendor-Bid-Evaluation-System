# Task 0004: Core Backend Services

## Overview
Implement the repository pattern and core backend services for users, documents, vendors, evaluations, and reports.

## Subtasks

### 4.1 Create base repository pattern
- Create `app/repositories/base.py` with generic CRUD operations
- Implement async methods: get_by_id, get_all, create, update, delete
- Reference: Section 6.4 (Service Layer Pattern)

### 4.2 Implement user repository and service
- Create `app/repositories/user_repo.py`
- Create `app/services/auth_service.py` with user authentication logic
- Reference: Section 6.1 (Backend Structure)

### 4.3 Implement document repository and service
- Create `app/repositories/document_repo.py`
- Create `app/services/document_service.py` with upload and retrieval logic
- Implement local file storage in configured UPLOAD_DIR
- Reference: Section 6.1 (Backend Structure), Section 9.3 (Document Endpoints)

### 4.4 Implement vendor repository and service
- Create `app/repositories/vendor_repo.py`
- Create `app/services/vendor_service.py` with vendor management logic
- Reference: Section 9.4 (Vendor Endpoints)

### 4.5 Implement evaluation repository and service
- Create `app/repositories/evaluation_repo.py` with specialized queries
- Create `app/services/evaluation_service.py` with full evaluation workflow logic
- Implement create, add bids, start evaluation, get results methods
- Reference: Section 6.4 (Service Layer Pattern)

### 4.6 Implement report service
- Create `app/services/report_service.py` with PDF/XLSX export functionality
- Reference: Section 9.2 (Export report endpoint)

## References
- Section 6.1 (Backend Structure)
- Section 6.4 (Service Layer Pattern)
- Section 9.2 (Export report endpoint)
- Section 9.3 (Document Endpoints)
- Section 9.4 (Vendor Endpoints)
