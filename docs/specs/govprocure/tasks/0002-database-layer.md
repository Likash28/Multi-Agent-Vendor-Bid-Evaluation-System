# Task 0002: Database Layer

## Overview
Create the complete database layer including SQLAlchemy models, migrations, and data normalization utilities.

## Subtasks

### 2.1 Create SQLAlchemy base model and database connection
- Create `app/models/base.py` with declarative base
- Create `app/dependencies.py` with async database session dependency
- Configure SQLite with aiosqlite for async operations
- Reference: Section 7 (Database Design)

### 2.2 Implement User and Role models
- Create `app/models/user.py` with User model (id, email, password_hash, name, department_id, role_id, is_active, created_at)
- Create `app/models/role.py` with Role model (id, name, permissions)
- Create `app/models/department.py` with Department model (id, name, code, ministry)
- Reference: Section 7.1 (ERD - Users, Departments, Roles)

### 2.3 Implement Document model
- Create `app/models/document.py` with fields: id, filename, file_path, file_type, file_size, mime_type, extracted_data (JSON), uploaded_by, uploaded_at
- Reference: Section 7.1 (ERD - Documents)

### 2.4 Implement Evaluation model
- Create `app/models/evaluation.py` with EvaluationStatus enum (DRAFT, PROCESSING, COMPLETED, FAILED, CANCELLED)
- Create EvaluationMethod enum (L1, QCBS, TWO_STAGE)
- Implement Evaluation model with all fields from Section 7.2
- Reference: Section 7.2 (SQLAlchemy Models)

### 2.5 Implement Vendor and Bid models
- Create `app/models/vendor.py` with Vendor model (id, name, registration_no, gstin, address, contact_email, contact_phone, is_verified)
- Create `app/models/bid.py` with Bid model (id, evaluation_id, vendor_id, document_id, bid_amount, submitted_at, status)
- Reference: Section 7.1 (ERD - Vendors, Bids)

### 2.6 Implement Score and AuditLog models
- Create `app/models/score.py` with Score model (id, bid_id, evaluation_id, score_type, total_score, max_score, breakdown, justification, ai_reasoning, is_qualified, scored_at)
- Create `app/models/audit_log.py` with AuditLog model
- Reference: Section 7.1 (ERD - Scores, Audit Logs)

### 2.7 Set up Alembic migrations
- Initialize Alembic with async SQLAlchemy support
- Create initial migration for all models
- Add database indexes defined in Section 7.4
- Reference: Section 7.4 (Database Indexes)

### 2.8 Implement data normalization utilities
- Create `app/utils/normalization.py` with currency conversion functions (paisa storage)
- Implement UTC to IST timezone conversion
- Add GSTIN and phone number validation
- Reference: Section 7.3 (Data Normalization Rules)

## References
- Section 7 (Database Design)
- Section 7.1 (ERD)
- Section 7.2 (SQLAlchemy Models)
- Section 7.3 (Data Normalization Rules)
- Section 7.4 (Database Indexes)
