# Task 0006: Pydantic Schemas

## Overview
Create all Pydantic schemas for request/response validation across authentication, evaluations, documents, vendors, bids, and reports.

## Subtasks

### 6.1 Create authentication schemas
- Create `app/schemas/auth.py` with UserCreate, UserLogin, TokenResponse, UserResponse
- Reference: Section 9.1 (Authentication Endpoints)

### 6.2 Create evaluation schemas
- Create `app/schemas/evaluation.py` with EvaluationMethod enum
- Implement EvaluationConfig with weight validation (must sum to 100%)
- Create EvaluationCreate, EvaluationSummary, VendorScore, EvaluationResults schemas
- Reference: Section 9.6 (Schema Definitions)

### 6.3 Create document schemas
- Create `app/schemas/document.py` with DocumentUpload, DocumentDetail schemas
- Reference: Section 9.3 (Document Endpoints)

### 6.4 Create vendor and bid schemas
- Create `app/schemas/vendor.py` with VendorDetail, VendorList schemas
- Create `app/schemas/bid.py` with BidCreate, BidDetail schemas
- Reference: Section 9.4 (Vendor Endpoints)

### 6.5 Create report schemas
- Create `app/schemas/report.py` with export-related schemas
- Reference: Section 9.2 (Export endpoint)

## References
- Section 9.1 (Authentication Endpoints)
- Section 9.2 (Export endpoint)
- Section 9.3 (Document Endpoints)
- Section 9.4 (Vendor Endpoints)
- Section 9.6 (Schema Definitions)
