# GovProcure Implementation Tasks

## Multi-Agent Vendor Bid Evaluation System

Based on: [Technical Specification v1.1](/TECHNICAL_SPECIFICATION.md)

---

## 1. Project Setup & Infrastructure

- [ ] 1.1 Initialize backend project structure
  - Create FastAPI project with the directory structure defined in Section 6.1
  - Set up Python 3.11+ virtual environment
  - Create `requirements.txt` with dependencies: FastAPI, SQLAlchemy 2.0, Pydantic, python-jose, passlib, aiosqlite, alembic
  - Reference: Section 3.2 (Backend Stack), Section 6.1 (Project Structure)

- [ ] 1.2 Initialize frontend project structure
  - Create Next.js 14+ project with App Router
  - Configure TypeScript, Tailwind CSS, and ESLint
  - Install core dependencies: React Query (TanStack), Zustand, React Hook Form, Zod, Recharts, Socket.io-client
  - Set up shadcn/ui component library
  - Reference: Section 3.1 (Frontend Stack), Section 5.1 (Project Structure)

- [ ] 1.3 Configure application settings and environment
  - Create `app/config.py` with Pydantic BaseSettings for all configuration options
  - Create `.env.example` with all required environment variables
  - Configure database URL, JWT settings, AWS Bedrock settings, upload directory
  - Reference: Section 6.3 (Configuration), Section 11.7 (Environment Configuration)

- [ ] 1.4 Set up FastAPI application entry point
  - Create `app/main.py` with lifespan context manager
  - Configure CORS middleware with allowed origins
  - Set up exception handlers
  - Include API routers and WebSocket router
  - Reference: Section 6.2 (Core Application Setup)

---

## 2. Database Layer

- [ ] 2.1 Create SQLAlchemy base model and database connection
  - Create `app/models/base.py` with declarative base
  - Create `app/dependencies.py` with async database session dependency
  - Configure SQLite with aiosqlite for async operations
  - Reference: Section 7 (Database Design)

- [ ] 2.2 Implement User and Role models
  - Create `app/models/user.py` with User model (id, email, password_hash, name, department_id, role_id, is_active, created_at)
  - Create `app/models/role.py` with Role model (id, name, permissions)
  - Create `app/models/department.py` with Department model (id, name, code, ministry)
  - Reference: Section 7.1 (ERD - Users, Departments, Roles)

- [ ] 2.3 Implement Document model
  - Create `app/models/document.py` with fields: id, filename, file_path, file_type, file_size, mime_type, extracted_data (JSON), uploaded_by, uploaded_at
  - Reference: Section 7.1 (ERD - Documents)

- [ ] 2.4 Implement Evaluation model
  - Create `app/models/evaluation.py` with EvaluationStatus enum (DRAFT, PROCESSING, COMPLETED, FAILED, CANCELLED)
  - Create EvaluationMethod enum (L1, QCBS, TWO_STAGE)
  - Implement Evaluation model with all fields from Section 7.2
  - Reference: Section 7.2 (SQLAlchemy Models)

- [ ] 2.5 Implement Vendor and Bid models
  - Create `app/models/vendor.py` with Vendor model (id, name, registration_no, gstin, address, contact_email, contact_phone, is_verified)
  - Create `app/models/bid.py` with Bid model (id, evaluation_id, vendor_id, document_id, bid_amount, submitted_at, status)
  - Reference: Section 7.1 (ERD - Vendors, Bids)

- [ ] 2.6 Implement Score and AuditLog models
  - Create `app/models/score.py` with Score model (id, bid_id, evaluation_id, score_type, total_score, max_score, breakdown, justification, ai_reasoning, is_qualified, scored_at)
  - Create `app/models/audit_log.py` with AuditLog model
  - Reference: Section 7.1 (ERD - Scores, Audit Logs)

- [ ] 2.7 Set up Alembic migrations
  - Initialize Alembic with async SQLAlchemy support
  - Create initial migration for all models
  - Add database indexes defined in Section 7.4
  - Reference: Section 7.4 (Database Indexes)

- [ ] 2.8 Implement data normalization utilities
  - Create `app/utils/normalization.py` with currency conversion functions (paisa storage)
  - Implement UTC to IST timezone conversion
  - Add GSTIN and phone number validation
  - Reference: Section 7.3 (Data Normalization Rules)

---

## 3. Authentication & Security

- [ ] 3.1 Implement password hashing and JWT utilities
  - Create `app/core/security.py` with bcrypt password hashing
  - Implement `create_access_token()` and `create_refresh_token()` functions
  - Add token verification and decoding
  - Reference: Section 10.1 (Authentication & Authorization)

- [ ] 3.2 Implement authentication middleware and guards
  - Create `app/core/auth.py` with `get_current_user` dependency
  - Implement `get_current_user_ws` for WebSocket authentication
  - Add token refresh logic
  - Reference: Section 10.1 (Authentication & Authorization)

- [ ] 3.3 Implement Role-Based Access Control (RBAC)
  - Define Permission enum with all permissions from Section 10.2
  - Create ROLE_PERMISSIONS mapping for officer, evaluator, admin roles
  - Implement `require_permission` decorator
  - Reference: Section 10.2 (Role-Based Access Control)

- [ ] 3.4 Create authentication API endpoints
  - Implement `POST /api/v1/auth/register` endpoint
  - Implement `POST /api/v1/auth/login` endpoint with JWT token generation
  - Implement `POST /api/v1/auth/logout` endpoint
  - Implement `POST /api/v1/auth/refresh` endpoint
  - Implement `GET /api/v1/auth/me` endpoint
  - Reference: Section 9.1 (Authentication Endpoints)

- [ ] 3.5 Implement password reset flow
  - Implement `POST /api/v1/auth/forgot-password` endpoint
  - Implement `POST /api/v1/auth/reset-password` endpoint
  - Reference: Section 9.1 (Password Reset endpoints)

- [ ] 3.6 Add security headers middleware
  - Create `app/core/middleware.py` with SecurityHeadersMiddleware
  - Add X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS headers
  - Reference: Section 10.4 (Security Headers)

- [ ] 3.7 Implement audit logging service
  - Create `app/services/audit_service.py` with async logging functionality
  - Log entity changes, actor, IP address, user agent
  - Reference: Section 10.3 (Audit Logging)

---

## 4. Core Backend Services

- [ ] 4.1 Create base repository pattern
  - Create `app/repositories/base.py` with generic CRUD operations
  - Implement async methods: get_by_id, get_all, create, update, delete
  - Reference: Section 6.4 (Service Layer Pattern)

- [ ] 4.2 Implement user repository and service
  - Create `app/repositories/user_repo.py`
  - Create `app/services/auth_service.py` with user authentication logic
  - Reference: Section 6.1 (Backend Structure)

- [ ] 4.3 Implement document repository and service
  - Create `app/repositories/document_repo.py`
  - Create `app/services/document_service.py` with upload and retrieval logic
  - Implement local file storage in configured UPLOAD_DIR
  - Reference: Section 6.1 (Backend Structure), Section 9.3 (Document Endpoints)

- [ ] 4.4 Implement vendor repository and service
  - Create `app/repositories/vendor_repo.py`
  - Create `app/services/vendor_service.py` with vendor management logic
  - Reference: Section 9.4 (Vendor Endpoints)

- [ ] 4.5 Implement evaluation repository and service
  - Create `app/repositories/evaluation_repo.py` with specialized queries
  - Create `app/services/evaluation_service.py` with full evaluation workflow logic
  - Implement create, add bids, start evaluation, get results methods
  - Reference: Section 6.4 (Service Layer Pattern)

- [ ] 4.6 Implement report service
  - Create `app/services/report_service.py` with PDF/XLSX export functionality
  - Reference: Section 9.2 (Export report endpoint)

---

## 5. API Endpoints (FastAPI Routers)

- [ ] 5.1 Create API router aggregator
  - Create `app/api/v1/router.py` to combine all routers
  - Create `app/api/v1/__init__.py`
  - Reference: Section 6.1 (Backend Structure)

- [ ] 5.2 Implement document endpoints
  - Create `app/api/v1/documents.py` router
  - Implement `POST /api/v1/documents/upload` with multipart form handling
  - Implement `GET /api/v1/documents/{id}` endpoint
  - Implement `GET /api/v1/documents/{id}/download` endpoint
  - Reference: Section 9.3 (Document Endpoints)

- [ ] 5.3 Implement evaluation endpoints
  - Create `app/api/v1/evaluations.py` router
  - Implement `GET /api/v1/evaluations` with pagination and filtering
  - Implement `POST /api/v1/evaluations` to create evaluation
  - Implement `GET /api/v1/evaluations/{id}` endpoint
  - Implement `POST /api/v1/evaluations/{id}/bids` to add vendor bids
  - Implement `PATCH /api/v1/evaluations/{id}/config` endpoint
  - Reference: Section 9.2 (Evaluation Endpoints)

- [ ] 5.4 Implement evaluation workflow endpoints
  - Implement `POST /api/v1/evaluations/{id}/start` to trigger background processing
  - Implement `POST /api/v1/evaluations/{id}/cancel` endpoint
  - Implement `POST /api/v1/evaluations/{id}/approve` endpoint
  - Reference: Section 9.2 (Evaluation Endpoints)

- [ ] 5.5 Implement evaluation results endpoints
  - Implement `GET /api/v1/evaluations/{id}/results` endpoint
  - Implement `GET /api/v1/evaluations/{id}/results/compliance` endpoint
  - Implement `GET /api/v1/evaluations/{id}/results/technical` with optional vendor_id filter
  - Implement `GET /api/v1/evaluations/{id}/results/financial` endpoint
  - Implement `GET /api/v1/evaluations/{id}/results/comparison` endpoint
  - Implement `GET /api/v1/evaluations/{id}/export` with format query parameter
  - Reference: Section 9.2 (Evaluation Endpoints)

- [ ] 5.6 Implement vendor endpoints
  - Create `app/api/v1/vendors.py` router
  - Implement `GET /api/v1/vendors` with search, pagination
  - Implement `GET /api/v1/vendors/{id}` endpoint
  - Implement `GET /api/v1/vendors/{id}/history` endpoint
  - Reference: Section 9.4 (Vendor Endpoints)

- [ ] 5.7 Implement admin endpoints
  - Create `app/api/v1/admin.py` router
  - Implement user CRUD endpoints (GET, POST, PATCH, DELETE)
  - Implement `GET /api/v1/admin/audit-logs` with filtering
  - Implement `GET /api/v1/departments` endpoint
  - Reference: Section 9.5 (Admin Endpoints)

- [ ] 5.8 Implement health check endpoint
  - Create `app/api/v1/health.py` router
  - Return application health status
  - Reference: Section 4.1 (High-Level Architecture - Health Router)

---

## 6. Pydantic Schemas

- [ ] 6.1 Create authentication schemas
  - Create `app/schemas/auth.py` with UserCreate, UserLogin, TokenResponse, UserResponse
  - Reference: Section 9.1 (Authentication Endpoints)

- [ ] 6.2 Create evaluation schemas
  - Create `app/schemas/evaluation.py` with EvaluationMethod enum
  - Implement EvaluationConfig with weight validation (must sum to 100%)
  - Create EvaluationCreate, EvaluationSummary, VendorScore, EvaluationResults schemas
  - Reference: Section 9.6 (Schema Definitions)

- [ ] 6.3 Create document schemas
  - Create `app/schemas/document.py` with DocumentUpload, DocumentDetail schemas
  - Reference: Section 9.3 (Document Endpoints)

- [ ] 6.4 Create vendor and bid schemas
  - Create `app/schemas/vendor.py` with VendorDetail, VendorList schemas
  - Create `app/schemas/bid.py` with BidCreate, BidDetail schemas
  - Reference: Section 9.4 (Vendor Endpoints)

- [ ] 6.5 Create report schemas
  - Create `app/schemas/report.py` with export-related schemas
  - Reference: Section 9.2 (Export endpoint)

---

## 7. Document Processing Utilities

- [ ] 7.1 Implement PDF parsing utility
  - Create `app/utils/pdf_parser.py` using PyMuPDF or pdfplumber
  - Extract text, tables, and sections from PDF documents
  - Reference: Section 3.3 (AI/ML Stack)

- [ ] 7.2 Implement DOCX parsing utility
  - Create `app/utils/docx_parser.py` using python-docx
  - Extract text and structured content from DOCX files
  - Reference: Section 3.3 (AI/ML Stack)

- [ ] 7.3 Create file utilities
  - Create `app/utils/file_utils.py` with file validation, size checking
  - Implement file type detection (PDF, DOCX, TXT)
  - Validate max 50MB upload size
  - Reference: Section 6.1 (Backend Structure)

- [ ] 7.4 Create validators
  - Create `app/utils/validators.py` with GSTIN validation, phone number validation
  - Add financial year format validation
  - Reference: Section 7.3 (Data Normalization Rules)

---

## 8. Multi-Agent AI System

- [ ] 8.1 Set up AWS Bedrock LLM service
  - Create `app/services/bedrock_llm_service.py`
  - Configure ChatBedrockConverse with Claude Sonnet 4.5 model
  - Set temperature to 0.2 for consistent scoring
  - Implement connection and error handling
  - Reference: Section 3.3 (AI/ML Stack), Section 8.2 (Orchestrator - LLM setup)

- [ ] 8.2 Create EvaluationState class
  - Create `app/agents/__init__.py` with EvaluationState dataclass
  - Include all state fields: tender_data, vendor_bids, compliance_results, technical_scores, financial_scores, comparison_matrix, final_report, logs, current_step, error
  - Add error recovery fields: retry_count, max_retries, failed_step, partial_results_saved
  - Reference: Section 8.2 (EvaluationState class)

- [ ] 8.3 Implement Document Parser Agent
  - Create `app/agents/document_parser.py`
  - Implement `parse_tender()` method to extract requirements, sections, criteria from tender documents
  - Implement `parse_bid()` method to extract vendor proposal content
  - Reference: Section 8.1 (Agent Architecture - Document Parser)

- [ ] 8.4 Implement Compliance Agent
  - Create `app/agents/compliance_agent.py`
  - Implement `verify()` method to check document compliance (GST, Bank Guarantee, etc.)
  - Return compliance status, document checklist, AI notes with justification
  - Reference: Section 8.1 (Agent Architecture - Compliance Agent), Section 5.2.5 (Compliance View)

- [ ] 8.5 Implement Technical Evaluation Agent
  - Create `app/agents/technical_agent.py`
  - Implement technical criteria evaluation with LLM prompts from Section 8.3
  - Score against: Previous Experience, Technical Team, Methodology, QA Plan, Timeline
  - Calculate weighted total score and qualification status (threshold = 75)
  - Reference: Section 8.3 (Technical Evaluation Agent)

- [ ] 8.6 Implement Financial Evaluation Agent
  - Create `app/agents/financial_agent.py`
  - Parse bid amounts and normalize to paisa
  - Calculate L1 winner (lowest price method)
  - Apply financial scoring formula for QCBS method
  - Reference: Section 8.1 (Agent Architecture - Financial Agent)

- [ ] 8.7 Implement Comparison Agent
  - Create `app/agents/comparison_agent.py`
  - Perform cross-vendor analysis and generate comparison matrix
  - Implement cartel detection (Beta - advisory only, flag patterns for human review)
  - Reference: Section 8.1 (Agent Architecture - Comparison Agent)

- [ ] 8.8 Implement Report Agent
  - Create `app/agents/report_agent.py`
  - Generate evaluation summaries with AI-generated justifications
  - Prepare data for PDF report export
  - Include winner recommendation with detailed justification
  - Reference: Section 8.1 (Agent Architecture - Report Agent)

- [ ] 8.9 Implement Orchestrator Agent with LangGraph
  - Create `app/agents/orchestrator.py` with EvaluationOrchestrator class
  - Build LangGraph StateGraph with all workflow nodes
  - Define edges and conditional routing (e.g., skip financial if no qualified bids)
  - Implement progress callback for WebSocket updates
  - Reference: Section 8.2 (Orchestrator Implementation)

- [ ] 8.10 Implement error recovery workflow
  - Add retry logic with exponential backoff (3 attempts)
  - Save partial results on failure
  - Enable restart from failed step
  - Reference: Section 8.2 (Error Recovery Workflow)

---

## 9. WebSocket Real-time Updates

- [ ] 9.1 Implement WebSocket connection manager
  - Create `app/api/websocket.py` with ConnectionManager class
  - Manage active connections per evaluation_id
  - Implement connect, disconnect, broadcast methods
  - Reference: Section 8.4 (Real-time Progress Updates)

- [ ] 9.2 Implement WebSocket endpoint for evaluation progress
  - Create `/ws/evaluation/{evaluation_id}` endpoint
  - Handle ping/pong for connection keep-alive
  - Authenticate WebSocket connections
  - Reference: Section 8.4 (WebSocket handlers)

- [ ] 9.3 Implement progress callback
  - Create `send_progress_update()` function for orchestrator integration
  - Broadcast step, logs, progress percentage, timestamp
  - Reference: Section 8.4 (Progress callback)

---

## 10. Frontend Core Setup

- [ ] 10.1 Configure Next.js project structure
  - Set up App Router directory structure per Section 5.1
  - Configure `next.config.js` with API proxy settings
  - Create `tailwind.config.js` with design system colors
  - Reference: Section 5.1 (Project Structure), Appendix A (Color Palette)

- [ ] 10.2 Set up API client
  - Create `lib/api-client.ts` with Axios/fetch wrapper
  - Configure base URL, interceptors for auth tokens
  - Handle token refresh on 401 responses
  - Reference: Section 5.1 (Frontend lib structure)

- [ ] 10.3 Set up Zustand stores
  - Create `stores/auth-store.ts` with user state and auth actions
  - Create `stores/evaluation-store.ts` with wizard and processing state per Section 5.4
  - Create `stores/ui-store.ts` for UI state (sidebar, modals)
  - Reference: Section 5.4 (State Management)

- [ ] 10.4 Create TypeScript type definitions
  - Create `types/api.ts` with API response types
  - Create `types/evaluation.ts` with evaluation-related types
  - Create `types/vendor.ts` and `types/user.ts`
  - Reference: Section 5.1 (Frontend types structure)

- [ ] 10.5 Set up React Query
  - Configure QueryClient with default options
  - Create query hooks for API endpoints
  - Reference: Section 3.1 (Frontend Stack - TanStack Query)

- [ ] 10.6 Create Zod validation schemas
  - Create `lib/validations.ts` with form validation schemas
  - Include login, evaluation config, document upload schemas
  - Reference: Section 5.1 (Frontend lib structure)

---

## 11. Frontend UI Components

- [ ] 11.1 Install and configure shadcn/ui components
  - Install base shadcn/ui setup with Tailwind CSS
  - Add required components: Button, Card, Dialog, Input, Form, Select, Slider, Table, Tabs, Progress, Badge, Toast, etc.
  - Reference: Section 5.3 (Component Library)

- [ ] 11.2 Create layout components
  - Create `components/layout/header.tsx` with user menu, notifications
  - Create `components/layout/sidebar.tsx` with navigation links
  - Create `components/layout/footer.tsx` with ministry attribution
  - Create `components/layout/breadcrumb.tsx`
  - Reference: Section 5.1 (Frontend components structure)

- [ ] 11.3 Create shared utility components
  - Create `components/shared/file-upload.tsx` with drag-and-drop zone
  - Create `components/shared/data-table.tsx` for tabular data
  - Create `components/shared/status-badge.tsx` for status indicators
  - Create `components/shared/score-display.tsx` with score ring visualization
  - Create `components/shared/export-button.tsx`
  - Reference: Section 5.1 (Shared components)

- [ ] 11.4 Create custom components
  - Create Step Indicator component for wizard
  - Create Live Log Terminal component for processing view
  - Create Score Ring component for score visualization
  - Reference: Section 5.3 (Custom Components)

---

## 12. Frontend Authentication Pages

- [ ] 12.1 Create auth layout
  - Create `app/(auth)/layout.tsx` with split layout (branding + form)
  - Reference: Section 5.2.1 (Login Page)

- [ ] 12.2 Implement login page
  - Create `app/(auth)/login/page.tsx`
  - Add email/password form with validation
  - Implement "Remember Me" checkbox
  - Add forgot password link
  - Handle JWT token storage
  - Reference: Section 5.2.1 (Login Page)

- [ ] 12.3 Create auth hook
  - Create `hooks/use-auth.ts` for authentication logic
  - Implement login, logout, token refresh
  - Manage auth state persistence
  - Reference: Section 5.1 (Frontend hooks)

---

## 13. Frontend Dashboard

- [ ] 13.1 Create dashboard layout
  - Create `app/(dashboard)/layout.tsx` with header, sidebar
  - Implement protected route with auth check
  - Reference: Section 5.1 (Dashboard group routes)

- [ ] 13.2 Implement dashboard page
  - Create `app/(dashboard)/dashboard/page.tsx`
  - Add welcome header with user greeting
  - Reference: Section 5.2.2 (Dashboard Page)

- [ ] 13.3 Create dashboard stat cards component
  - Create `components/dashboard/stats-cards.tsx`
  - Display Active Evaluations, Completed, Pending Review, Total Vendors
  - Reference: Section 5.2.2 (Stats Cards)

- [ ] 13.4 Create quick actions component
  - Create `components/dashboard/quick-actions.tsx`
  - Add buttons: New Evaluation, Upload Documents, View Reports
  - Reference: Section 5.2.2 (Quick Actions)

- [ ] 13.5 Create activity chart component
  - Create `components/dashboard/activity-chart.tsx` using Recharts
  - Display 30-day activity bar chart
  - Reference: Section 5.2.2 (Activity Chart)

- [ ] 13.6 Create recent evaluations component
  - Create `components/dashboard/recent-evaluations.tsx`
  - Display table with Reference ID, Title, Date, Status, Actions
  - Reference: Section 5.2.2 (Recent Evaluations)

---

## 14. Frontend Evaluation Wizard

- [ ] 14.1 Create evaluation wizard page
  - Create `app/(dashboard)/evaluations/new/page.tsx`
  - Implement 4-step wizard flow with step indicator
  - Reference: Section 5.2.3 (New Evaluation Wizard)

- [ ] 14.2 Create step indicator component
  - Create `components/evaluation/wizard/step-indicator.tsx`
  - Display steps 1-4 with active/completed states
  - Reference: Section 5.2.3 (Step 1 - Step indicator)

- [ ] 14.3 Implement Step 1: Upload Tender
  - Create `components/evaluation/wizard/upload-tender.tsx`
  - Add file upload zone (PDF, DOCX, TXT - max 50MB)
  - Display file preview and metadata
  - Show auto-extraction status
  - Reference: Section 5.2.3 (Step 1: Upload Tender)

- [ ] 14.4 Implement Step 2: Upload Vendor Bids
  - Create `components/evaluation/wizard/upload-bids.tsx`
  - Add multi-file drag & drop zone
  - Display uploaded bids list with vendor names
  - Show status indicators (Ready, Processing)
  - Reference: Section 5.2.3 (Step 2: Upload Vendor Bids)

- [ ] 14.5 Implement Step 3: Evaluation Configuration
  - Create `components/evaluation/wizard/evaluation-config.tsx`
  - Add evaluation method selection (L1, QCBS, Two-Stage)
  - Add weight configuration sliders (Technical vs Financial)
  - Add qualification threshold input
  - Add advanced settings checkboxes (AI compliance, justifications, cartel detection)
  - Reference: Section 5.2.3 (Step 3: Evaluation Configuration)

- [ ] 14.6 Implement Step 4: Review & Confirm
  - Create `components/evaluation/wizard/review-confirm.tsx`
  - Display tender and configuration summary
  - Show estimated processing time
  - Add irreversible action warning
  - Implement "Start Evaluation" button
  - Reference: Section 5.2.3 (Step 4: Review & Confirm)

- [ ] 14.7 Create evaluation hook
  - Create `hooks/use-evaluation.ts` with wizard state management
  - Implement tender upload, bid management, config update actions
  - Reference: Section 5.4 (State Management - EvaluationState)

- [ ] 14.8 Create file upload hook
  - Create `hooks/use-file-upload.ts` for file handling
  - Implement upload progress, validation, error handling
  - Reference: Section 5.1 (Frontend hooks)

---

## 15. Frontend Processing View

- [ ] 15.1 Create processing page
  - Create `app/(dashboard)/evaluations/[id]/processing/page.tsx`
  - Display overall progress bar
  - Reference: Section 5.2.4 (Processing Page)

- [ ] 15.2 Create workflow steps component
  - Create `components/evaluation/processing/workflow-steps.tsx`
  - Display vertical stepper with all evaluation stages
  - Show step status (pending, active, completed)
  - Reference: Section 5.2.4 (Workflow Steps)

- [ ] 15.3 Create live log component
  - Create `components/evaluation/processing/live-log.tsx`
  - Display terminal-style log with timestamps and agent messages
  - Auto-scroll to latest entries
  - Reference: Section 5.2.4 (Live System Log)

- [ ] 15.4 Create progress indicator component
  - Create `components/evaluation/processing/progress-indicator.tsx`
  - Display remaining time estimate
  - Reference: Section 5.2.4 (Estimated Time)

- [ ] 15.5 Create WebSocket hook
  - Create `hooks/use-websocket.ts` for real-time updates
  - Connect to `/ws/evaluation/{id}` endpoint
  - Handle progress messages and update UI state
  - Reference: Section 8.4 (WebSocket - Frontend integration)

---

## 16. Frontend Results Views

- [ ] 16.1 Create results summary page
  - Create `app/(dashboard)/evaluations/[id]/results/page.tsx`
  - Display stats row (Total Bids, Qualified, Disqualified, Eval Method)
  - Add preferred bidder card with score and justification
  - Include vendor score distribution chart
  - Show detailed rankings table
  - Reference: Section 5.2.5 (Summary View)

- [ ] 16.2 Create summary view component
  - Create `components/evaluation/results/summary-view.tsx`
  - Reference: Section 5.2.5 (Summary View)

- [ ] 16.3 Create compliance results page
  - Create `app/(dashboard)/evaluations/[id]/results/compliance/page.tsx`
  - Display vendor compliance cards with document checklists
  - Show Pass/Fail badges and AI notes
  - Reference: Section 5.2.5 (Compliance View)

- [ ] 16.4 Create compliance view component
  - Create `components/evaluation/results/compliance-view.tsx`
  - Reference: Section 5.2.5 (Compliance View)

- [ ] 16.5 Create technical scores page
  - Create `app/(dashboard)/evaluations/[id]/results/technical/page.tsx`
  - Add vendor selector dropdown
  - Display score breakdown by criteria
  - Show AI justification for each section
  - Reference: Section 5.2.5 (Technical Scores)

- [ ] 16.6 Create technical scores component
  - Create `components/evaluation/results/technical-scores.tsx`
  - Reference: Section 5.2.5 (Technical Scores)

- [ ] 16.7 Create financial evaluation page
  - Create `app/(dashboard)/evaluations/[id]/results/financial/page.tsx`
  - Highlight L1 winner
  - Display vendor comparison table with ranks, quotes, adjustments
  - Reference: Section 5.2.5 (Financial Evaluation)

- [ ] 16.8 Create financial scores component
  - Create `components/evaluation/results/financial-scores.tsx`
  - Reference: Section 5.2.5 (Financial Evaluation)

- [ ] 16.9 Create comparison matrix page
  - Create `app/(dashboard)/evaluations/[id]/results/comparison/page.tsx`
  - Implement side-by-side vendor comparison
  - Add "Highlight Differences" toggle
  - Show winner highlight
  - Reference: Section 5.2.5 (Comparison Matrix)

- [ ] 16.10 Create comparison matrix component
  - Create `components/evaluation/results/comparison-matrix.tsx`
  - Reference: Section 5.2.5 (Comparison Matrix)

- [ ] 16.11 Create vendor ranking component
  - Create `components/evaluation/results/vendor-ranking.tsx`
  - Display final rankings with tie-breaking by earliest submission
  - Reference: Section 1.4 (Tie-breaking decision)

---

## 17. Frontend Vendor & Reports Pages

- [ ] 17.1 Create vendors list page
  - Create `app/(dashboard)/vendors/page.tsx`
  - Display vendor list with search and filters
  - Show verification status
  - Reference: Section 5.1 (Vendors route)

- [ ] 17.2 Create reports page
  - Create `app/(dashboard)/reports/page.tsx`
  - Display list of generated reports
  - Implement export functionality (PDF, XLSX)
  - Reference: Section 5.1 (Reports route)

---

## 18. Frontend Evaluations List Page

- [ ] 18.1 Create evaluations list page
  - Create `app/(dashboard)/evaluations/page.tsx`
  - Display evaluations table with pagination
  - Add status filters
  - Implement search by reference ID
  - Reference: Section 5.1 (Evaluations route)

- [ ] 18.2 Create evaluation details page
  - Create `app/(dashboard)/evaluations/[id]/page.tsx`
  - Display evaluation details and configuration
  - Show current status and actions
  - Reference: Section 5.1 (Evaluation [id] route)

---

## 19. Testing

- [ ] 19.1 Set up backend testing infrastructure
  - Create `tests/conftest.py` with pytest fixtures
  - Configure test database (SQLite in-memory)
  - Create test client factory
  - Reference: Section 6.1 (tests directory)

- [ ] 19.2 Write authentication tests
  - Create `tests/test_auth.py`
  - Test registration, login, token refresh, logout endpoints
  - Test RBAC permission checks
  - Reference: Section 6.1 (test_auth.py)

- [ ] 19.3 Write evaluation endpoint tests
  - Create `tests/test_evaluations.py`
  - Test CRUD operations, workflow transitions
  - Test results endpoints
  - Reference: Section 6.1 (test_evaluations.py)

- [ ] 19.4 Write agent unit tests
  - Create `tests/test_agents.py`
  - Test individual agent functionality with mock LLM responses
  - Test orchestrator workflow
  - Reference: Section 6.1 (test_agents.py)

- [ ] 19.5 Set up frontend testing
  - Configure Jest and React Testing Library
  - Create test utilities for component testing
  - Reference: Section 3.1 (Frontend Stack)

- [ ] 19.6 Write frontend component tests
  - Test wizard components
  - Test results view components
  - Test form validation
  - Reference: Section 5 (Frontend Specification)

---

## 20. Integration & Final Assembly

- [ ] 20.1 Wire up frontend to backend API
  - Connect all API calls to backend endpoints
  - Handle loading states and error responses
  - Implement toast notifications for success/error
  - Reference: Section 4.2 (Component Interaction Flow)

- [ ] 20.2 End-to-end workflow integration
  - Verify complete evaluation flow from upload to results
  - Test WebSocket real-time updates during processing
  - Verify all result views display correctly
  - Reference: Section 2.2 (User Flows)

- [ ] 20.3 Implement error handling and recovery UI
  - Add error boundaries in React
  - Display user-friendly error messages
  - Implement retry options for failed evaluations
  - Reference: Section 8.2 (Error Recovery Workflow)

- [ ] 20.4 Performance optimization
  - Implement React Query caching strategies
  - Optimize large document handling
  - Add loading skeletons for async operations
  - Reference: Section 3.1 (React Query - caching)

- [ ] 20.5 Final API documentation
  - Verify FastAPI auto-generated OpenAPI docs
  - Add comprehensive endpoint descriptions
  - Reference: Section 9 (API Specification)

---

## Summary

This implementation plan covers all aspects of the GovProcure Multi-Agent Vendor Bid Evaluation System:

- **Backend**: 57 tasks covering database, authentication, services, API endpoints, and AI agents
- **Frontend**: 45 tasks covering UI components, pages, state management, and real-time updates
- **Testing**: 6 tasks for backend and frontend testing
- **Integration**: 5 tasks for final assembly and optimization

Total: **113 implementation tasks**

Each task references specific sections of the Technical Specification v1.1 for detailed requirements.
