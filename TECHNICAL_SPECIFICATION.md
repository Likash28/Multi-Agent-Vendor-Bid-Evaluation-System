# Technical Specification Document
## Multi-Agent Vendor Bid Evaluation System (GovProcure)

**Version:** 1.1
**Date:** December 2025
**Status:** Revised (Gap Analysis Updates)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Frontend Specification](#5-frontend-specification)
6. [Backend Specification (FastAPI)](#6-backend-specification-fastapi)
7. [Database Design](#7-database-design)
8. [Multi-Agent AI System](#8-multi-agent-ai-system)
9. [API Specification](#9-api-specification)
10. [Security & Compliance](#10-security--compliance)
11. [Deployment Architecture](#11-deployment-architecture)

---

## 1. Executive Summary

### 1.1 Purpose
The Multi-Agent Vendor Bid Evaluation System (GovProcure) is a government procurement platform designed to automate and streamline the vendor bid evaluation process using AI-powered multi-agent systems. The platform enables transparent, efficient, and compliant procurement for government organizations.

### 1.2 Key Features
- **Secure JWT Authentication** with role-based access control
- **AI-Powered Document Analysis** for tender and bid processing
- **Multi-Agent Evaluation System** for technical, financial, and compliance scoring
- **Real-time Processing** with live progress updates
- **Comprehensive Reporting** with audit trails and export capabilities
- **Comparison Matrix** for side-by-side vendor analysis

### 1.3 Target Users
- Procurement Officers
- Evaluation Committee Members
- Department Administrators
- Audit Personnel

### 1.4 Stakeholder Decisions (Gap Analysis - Dec 2025)

The following decisions were resolved during gap analysis to clarify ambiguous requirements:

| Decision | Resolution | Rationale |
|----------|------------|-----------|
| **Tie-breaking** | Earliest submission wins | When vendors have identical total scores, the vendor who submitted first is ranked higher |
| **Qualification Threshold** | 75 points is a **hard cutoff** | Bids scoring below 75 in technical evaluation are disqualified and excluded from financial evaluation |
| **Winner Recommendation** | System **recommends winner** with justification | The system explicitly identifies the recommended vendor with detailed AI-generated justification |
| **Scope** | Hackathon demo (MVP) | SQLite database, local file storage, minimal AWS infrastructure (~$60/month) |
| **LLM Provider** | AWS Bedrock (Claude Sonnet 4.5) | Model ID: `anthropic.claude-sonnet-4-5-20250929-v1:0` |

---

## 2. System Overview

### 2.1 Application Modules

| Module | Description |
|--------|-------------|
| **Authentication** | Login, JWT tokens, session management |
| **Dashboard** | KPIs, activity metrics, recent evaluations |
| **Evaluation Wizard** | Multi-step bid evaluation workflow |
| **Document Processing** | Upload, parse, and extract document data |
| **AI Evaluation Engine** | Multi-agent scoring and analysis |
| **Results & Reports** | Summary, compliance, technical, financial views |
| **Vendor Management** | Vendor registry and history |
| **Administration** | User management, settings, audit logs |

### 2.2 User Flows

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Login     │────▶│  Dashboard  │────▶│  New Eval   │────▶│  Upload     │
│   (JWT)     │     │   (Home)    │     │   Wizard    │     │  Tender     │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
│  Results    │◀────│  Processing │◀────│   Review    │◀────│  Upload     │
│  Summary    │     │  (Live)     │     │  & Confirm  │     │  Vendor Bids│
└──────┬──────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  Results Views: Compliance | Technical | Financial |    │
│                 Comparison Matrix | Export Report       │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### 3.1 Frontend Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **Next.js 14+** | React Framework | SSR/SSG, App Router, excellent performance |
| **TypeScript** | Type Safety | Robust codebase, better DX |
| **Tailwind CSS** | Styling | Utility-first, rapid development |
| **shadcn/ui** | Component Library | Accessible, customizable, modern design |
| **React Query (TanStack)** | Data Fetching | Caching, background updates, optimistic UI |
| **Zustand** | State Management | Lightweight, simple API |
| **React Hook Form** | Form Handling | Performance, validation |
| **Zod** | Schema Validation | Type-safe validation |
| **Recharts** | Data Visualization | Charts, graphs for dashboard |
| **Socket.io Client** | Real-time Updates | Live processing updates |

### 3.2 Backend Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| **FastAPI** | Web Framework | Async, fast, auto-documentation |
| **Python 3.11+** | Runtime | AI/ML ecosystem, typing support |
| **SQLAlchemy 2.0** | ORM | Async support, type hints |
| **SQLite** | Database (POC) | Simple, file-based, no setup required |
| **BackgroundTasks** | Async Processing | FastAPI built-in, no external dependencies |
| **Local File System** | Document Storage | Simple uploads directory for POC |
| **Alembic** | Migrations | Database version control |

> **Note:** For production, migrate to PostgreSQL, add Redis for caching, and Celery for heavy background tasks.

### 3.3 AI/ML Stack

| Technology | Purpose |
|------------|---------|
| **LangChain** | Agent orchestration |
| **AWS Bedrock** | LLM provider (managed, scalable) |
| **Claude Sonnet 4.5** | Primary LLM (`anthropic.claude-sonnet-4-5-20250929-v1:0`) |
| **LangChain-AWS** | `ChatBedrockConverse` wrapper for Bedrock integration |
| **LangGraph** | Multi-agent workflows |
| **PyMuPDF / pdfplumber** | PDF extraction |
| **python-docx** | DOCX parsing |
| **Sentence Transformers** | Document embeddings |
| **ChromaDB / Pinecone** | Vector storage (optional) |

> **Note:** AWS Bedrock provides managed LLM access with automatic scaling, no API key management, and enterprise security. Temperature is set to 0.2 for consistent scoring.

### 3.4 Infrastructure (POC - AWS EC2 Minimal)

| Technology | Purpose |
|------------|---------|
| **AWS EC2** | Single instance hosting everything |
| **SQLite** | File-based database (no external DB needed) |
| **Local File Storage** | Documents stored on EC2 volume |
| **PM2** | Process manager for Node.js & Python |
| **Caddy** | Reverse proxy with auto SSL |

> **Note:** This is a minimal POC setup (~$60/month). For production, add PostgreSQL, Redis, Celery, and S3.

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Next.js Frontend (SSR)                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │   │
│  │  │Dashboard │ │Evaluation│ │ Results  │ │   Admin Panel    │   │   │
│  │  │  Module  │ │  Wizard  │ │  Views   │ │                  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS / WSS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY LAYER                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    NGINX (Load Balancer / SSL)                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                              │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Application Server                   │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │    │
│  │  │   Auth   │ │Evaluation│ │ Document │ │     Vendor       │  │    │
│  │  │  Router  │ │  Router  │ │  Router  │ │     Router       │  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │    │
│  │  │  Report  │ │  Admin   │ │ WebSocket│ │     Health       │  │    │
│  │  │  Router  │ │  Router  │ │  Handler │ │     Router       │  │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐
│    WORKER LAYER      │ │   CACHE LAYER    │ │     STORAGE LAYER        │
│  ┌────────────────┐  │ │  ┌────────────┐  │ │  ┌────────────────────┐  │
│  │ Celery Workers │  │ │  │   Redis    │  │ │  │    PostgreSQL      │  │
│  │  ┌──────────┐  │  │ │  │  - Cache   │  │ │  │   - Core Data      │  │
│  │  │ Document │  │  │ │  │  - Session │  │ │  │   - Evaluations    │  │
│  │  │ Processor│  │  │ │  │  - Queue   │  │ │  │   - Audit Logs     │  │
│  │  └──────────┘  │  │ │  │  - Pub/Sub │  │ │  └────────────────────┘  │
│  │  ┌──────────┐  │  │ │  └────────────┘  │ │  ┌────────────────────┐  │
│  │  │   AI     │  │  │ └──────────────────┘ │  │    MinIO / S3      │  │
│  │  │ Evaluator│  │  │                      │  │   - Documents      │  │
│  │  └──────────┘  │  │                      │  │   - Reports        │  │
│  │  ┌──────────┐  │  │                      │  └────────────────────┘  │
│  │  │  Report  │  │  │                      │  ┌────────────────────┐  │
│  │  │Generator │  │  │                      │  │  ChromaDB/Pinecone │  │
│  │  └──────────┘  │  │                      │  │  - Vector Store    │  │
│  └────────────────┘  │                      │  └────────────────────┘  │
└──────────────────────┘                      └──────────────────────────┘
```

### 4.2 Component Interaction Flow

```
User Request ──▶ Next.js SSR ──▶ FastAPI ──▶ Service Layer ──▶ Repository
                                    │              │
                                    │              ▼
                                    │         PostgreSQL
                                    │
                                    ├──▶ Celery Task ──▶ AI Agents ──▶ Results
                                    │
                                    └──▶ WebSocket ──▶ Real-time Updates
```

---

## 5. Frontend Specification

### 5.1 Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth group routes
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/              # Protected routes
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── evaluations/
│   │   │   ├── page.tsx          # List evaluations
│   │   │   ├── new/
│   │   │   │   └── page.tsx      # New evaluation wizard
│   │   │   └── [id]/
│   │   │       ├── page.tsx      # Evaluation details
│   │   │       ├── processing/
│   │   │       │   └── page.tsx  # Live processing view
│   │   │       └── results/
│   │   │           ├── page.tsx  # Results summary
│   │   │           ├── compliance/
│   │   │           ├── technical/
│   │   │           ├── financial/
│   │   │           └── comparison/
│   │   ├── vendors/
│   │   │   └── page.tsx
│   │   ├── reports/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── api/                      # API routes (if needed)
│   ├── layout.tsx                # Root layout
│   └── globals.css
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── form.tsx
│   │   ├── input.tsx
│   │   ├── progress.tsx
│   │   ├── select.tsx
│   │   ├── slider.tsx
│   │   ├── table.tsx
│   │   ├── tabs.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   ├── footer.tsx
│   │   └── breadcrumb.tsx
│   ├── dashboard/
│   │   ├── stats-cards.tsx
│   │   ├── activity-chart.tsx
│   │   ├── recent-evaluations.tsx
│   │   └── quick-actions.tsx
│   ├── evaluation/
│   │   ├── wizard/
│   │   │   ├── step-indicator.tsx
│   │   │   ├── upload-tender.tsx
│   │   │   ├── upload-bids.tsx
│   │   │   ├── evaluation-config.tsx
│   │   │   └── review-confirm.tsx
│   │   ├── processing/
│   │   │   ├── workflow-steps.tsx
│   │   │   ├── live-log.tsx
│   │   │   └── progress-indicator.tsx
│   │   └── results/
│   │       ├── summary-view.tsx
│   │       ├── compliance-view.tsx
│   │       ├── technical-scores.tsx
│   │       ├── financial-scores.tsx
│   │       ├── comparison-matrix.tsx
│   │       └── vendor-ranking.tsx
│   └── shared/
│       ├── file-upload.tsx
│       ├── data-table.tsx
│       ├── status-badge.tsx
│       ├── score-display.tsx
│       └── export-button.tsx
├── hooks/
│   ├── use-auth.ts
│   ├── use-evaluation.ts
│   ├── use-websocket.ts
│   └── use-file-upload.ts
├── lib/
│   ├── api-client.ts             # Axios/fetch wrapper
│   ├── auth.ts                   # Auth utilities
│   ├── utils.ts                  # General utilities
│   └── validations.ts            # Zod schemas
├── stores/
│   ├── auth-store.ts
│   ├── evaluation-store.ts
│   └── ui-store.ts
├── types/
│   ├── api.ts
│   ├── evaluation.ts
│   ├── vendor.ts
│   └── user.ts
├── styles/
│   └── globals.css
├── public/
│   └── assets/
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

### 5.2 Page Specifications

#### 5.2.1 Login Page
**Route:** `/login`

| Component | Description |
|-----------|-------------|
| Split Layout | Left: Branding panel (gradient), Right: Login form |
| Government Logo | GOI Procurement branding |
| Email Input | Email format validation |
| Password Input | Secure password field |
| Remember Me | Checkbox for persistent session |
| Forgot Password | Link to password recovery |
| Sign In Button | Primary action button (JWT authentication) |
| Footer | Ministry attribution, links |

#### 5.2.2 Dashboard Page
**Route:** `/dashboard`

| Component | Description |
|-----------|-------------|
| Welcome Header | User greeting, last updated timestamp |
| Stats Cards | 4 KPI cards (Active Evaluations, Completed, Pending Review, Total Vendors) |
| Quick Actions | New Evaluation, Upload Documents, View Reports buttons |
| Activity Chart | Bar chart showing 30-day activity |
| Recent Evaluations | Table with Reference ID, Project Title, Date, Status, Actions |
| Search Bar | Global search for tenders/IDs |

#### 5.2.3 New Evaluation Wizard
**Route:** `/evaluations/new`

**Step 1: Upload Tender**
- Step indicator (1-4)
- File upload zone (PDF, DOCX, TXT - max 50MB)
- Uploaded file preview with metadata
- Auto-extraction status
- Tender ID, Organization, Category fields

**Step 2: Upload Vendor Bids**
- Drag & drop zone for multiple files
- Uploaded bids list with vendor names
- Status indicators (Ready, Processing)
- Add More button

**Step 3: Evaluation Configuration**
- Evaluation Method selection:
  - **L1 (Lowest Price)**: Winner is the vendor with the lowest bid meeting all technical requirements
  - **QCBS (Quality & Cost Based Selection)** - Recommended: Weighted scoring combining technical (70%) and financial (30%) scores
  - **Two-Stage Bidding**: Sequential evaluation where Stage 1 (technical) qualifies vendors for Stage 2 (financial)
- Weight Configuration slider (Technical vs Financial)
- Qualification Threshold input
- Advanced Settings:
  - AI compliance verification (checkbox)
  - Generate detailed justifications (checkbox)
  - Cartel detection analysis (checkbox, Beta)

**Step 4: Review & Confirm**
- Tender Information summary
- Evaluation Parameters summary
- Estimated Processing Time display
- Irreversible Action warning
- Start Evaluation button

#### 5.2.4 Processing Page (Live Updates)
**Route:** `/evaluations/[id]/processing`

| Component | Description |
|-----------|-------------|
| Progress Bar | Overall completion percentage |
| Workflow Steps | Vertical stepper (Tender Parsing, Bid Analysis, Compliance Verification, Technical Scoring, Financial Scoring, Report Generation) |
| Live System Log | Terminal-style log with timestamps and agent messages |
| Estimated Time | Remaining time display |

#### 5.2.5 Results Pages

**Summary View** (`/evaluations/[id]/results`)
- Stats row (Total Bids, Qualified, Disqualified, Eval Method)
- Preferred Bidder card with score and justification
- Vendor Score Distribution chart
- Detailed Rankings table
- Recommended Next Steps

**Compliance View** (`/evaluations/[id]/results/compliance`)
- Participating/Qualified/Disqualified vendors count
- Filter by vendor/status
- Vendor compliance cards with:
  - Document checklist (GST, Bank Guarantee, etc.)
  - Pass/Fail badges
  - AI Notes with justification
  - View Document links

**Technical Scores** (`/evaluations/[id]/results/technical`)
- Vendor selector dropdown
- Score summary (percentage + Qualified/Disqualified)
- Detailed Breakdown sections:
  - Previous Experience
  - Technical Team Expertise
  - Proposed Methodology
- AI Justification for each section

**Financial Evaluation** (`/evaluations/[id]/results/financial`)
- L1 Winner highlight
- Winning Quote and Financial Score
- Scoring Methodology explanation
- Vendor Comparison table (Rank, Details, Quote, Adjustments, Score)

**Comparison Matrix** (`/evaluations/[id]/results/comparison`)
- View options (columns, filters)
- Highlight Differences toggle
- Side-by-side vendor comparison
- Categories: Evaluation Parameters, Mandatory Compliance, Technical Evaluation, Financial Bid
- Status indicators (Verified, Failed, Omitted)
- Winner highlight

### 5.3 Component Library (shadcn/ui)

```
Required Components:
├── Accordion
├── Alert
├── Avatar
├── Badge
├── Button
├── Card
├── Checkbox
├── Dialog
├── Dropdown Menu
├── Form
├── Input
├── Label
├── Progress
├── Radio Group
├── Select
├── Separator
├── Slider
├── Switch
├── Table
├── Tabs
├── Textarea
├── Toast
├── Tooltip
└── Custom Components:
    ├── File Upload Zone
    ├── Step Indicator
    ├── Score Ring
    ├── Status Badge
    └── Live Log Terminal
```

### 5.4 State Management

```typescript
// stores/evaluation-store.ts
interface EvaluationState {
  // Wizard state
  currentStep: number;
  tenderDocument: File | null;
  tenderMetadata: TenderMetadata | null;
  vendorBids: VendorBid[];
  evaluationConfig: EvaluationConfig;

  // Processing state
  processingStatus: ProcessingStatus;
  workflowSteps: WorkflowStep[];
  logs: LogEntry[];

  // Results state
  results: EvaluationResults | null;

  // Actions
  setCurrentStep: (step: number) => void;
  uploadTender: (file: File) => Promise<void>;
  addVendorBid: (file: File) => Promise<void>;
  removeVendorBid: (id: string) => void;
  updateConfig: (config: Partial<EvaluationConfig>) => void;
  startEvaluation: () => Promise<void>;
  subscribeToUpdates: (evaluationId: string) => void;
}
```

---

## 6. Backend Specification (FastAPI)

### 6.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Settings & configuration
│   ├── dependencies.py           # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py         # API router aggregator
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── evaluations.py    # Evaluation CRUD & workflow
│   │   │   ├── documents.py      # Document upload & processing
│   │   │   ├── vendors.py        # Vendor management
│   │   │   ├── reports.py        # Report generation
│   │   │   └── admin.py          # Admin endpoints
│   │   └── websocket.py          # WebSocket handlers
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, hashing, encryption
│   │   ├── auth.py               # Auth middleware, guards
│   │   └── exceptions.py         # Custom exceptions
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py               # Base model class
│   │   ├── user.py
│   │   ├── evaluation.py
│   │   ├── document.py
│   │   ├── vendor.py
│   │   ├── bid.py
│   │   ├── score.py
│   │   └── audit_log.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── evaluation.py
│   │   ├── document.py
│   │   ├── vendor.py
│   │   ├── bid.py
│   │   └── report.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── evaluation_service.py
│   │   ├── document_service.py
│   │   ├── vendor_service.py
│   │   └── report_service.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── evaluation_repo.py
│   │   ├── document_repo.py
│   │   ├── vendor_repo.py
│   │   └── user_repo.py
│   │
│   ├── agents/                   # Multi-Agent AI System
│   │   ├── __init__.py
│   │   ├── orchestrator.py       # Main orchestration agent
│   │   ├── document_parser.py    # Document extraction agent
│   │   ├── compliance_agent.py   # Compliance verification
│   │   ├── technical_agent.py    # Technical evaluation
│   │   ├── financial_agent.py    # Financial analysis
│   │   ├── comparison_agent.py   # Cross-vendor comparison
│   │   └── report_agent.py       # Report generation
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py
│       ├── pdf_parser.py
│       ├── docx_parser.py
│       └── validators.py
│
├── migrations/                   # Alembic migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_evaluations.py
│   └── test_agents.py
│
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── Dockerfile
```

### 6.2 Core Application Setup

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.api.websocket import websocket_router
from app.config import settings
from app.core.exceptions import setup_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_redis()
    yield
    # Shutdown
    await close_connections()

app = FastAPI(
    title="GovProcure API",
    description="Multi-Agent Vendor Bid Evaluation System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/ws")

# Exception handlers
setup_exception_handlers(app)
```

### 6.3 Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "GovProcure"
    DEBUG: bool = False
    SECRET_KEY: str

    # Database (SQLite)
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/govprocure.db"

    # File Storage (local)
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # JWT Authentication
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI/LLM (AWS Bedrock)
    AWS_BEDROCK_REGION: str = "us-east-1"
    AWS_BEDROCK_MODEL_ID: str = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    LLM_TEMPERATURE: float = 0.2
    LLM_TIMEOUT: int = 120  # seconds

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

### 6.4 Service Layer Pattern

```python
# app/services/evaluation_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evaluation import Evaluation, EvaluationStatus
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationConfig,
    EvaluationResponse
)
from app.repositories.evaluation_repo import EvaluationRepository
from app.agents.orchestrator import EvaluationOrchestrator

class EvaluationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EvaluationRepository(db)

    async def create_evaluation(
        self,
        data: EvaluationCreate,
        user_id: str
    ) -> Evaluation:
        """Create a new evaluation."""
        evaluation = await self.repo.create(
            tender_id=data.tender_id,
            tender_document_id=data.tender_document_id,
            config=data.config.model_dump(),
            created_by=user_id,
            status=EvaluationStatus.DRAFT
        )
        return evaluation

    async def add_vendor_bids(
        self,
        evaluation_id: str,
        bid_ids: List[str]
    ) -> None:
        """Add vendor bids to evaluation."""
        await self.repo.add_bids(evaluation_id, bid_ids)

    async def start_evaluation(
        self,
        evaluation_id: str,
        background_tasks: BackgroundTasks
    ) -> Evaluation:
        """Start the evaluation process using FastAPI BackgroundTasks."""
        evaluation = await self.repo.get_by_id(evaluation_id)

        if evaluation.status != EvaluationStatus.DRAFT:
            raise ValueError("Evaluation already started")

        # Update status
        await self.repo.update_status(
            evaluation_id,
            EvaluationStatus.PROCESSING
        )

        # Trigger background processing (no Celery needed)
        background_tasks.add_task(
            self._process_evaluation,
            evaluation_id
        )

        return evaluation

    async def _process_evaluation(self, evaluation_id: str):
        """Background task to process evaluation."""
        orchestrator = EvaluationOrchestrator(config={})
        # ... run evaluation and update results

    async def get_results(
        self,
        evaluation_id: str
    ) -> EvaluationResponse:
        """Get evaluation results."""
        evaluation = await self.repo.get_with_results(evaluation_id)
        return EvaluationResponse.from_orm(evaluation)
```

---

## 7. Database Design

### 7.1 Entity Relationship Diagram

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Users     │     │ Departments  │     │    Roles     │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id (PK)      │────▶│ id (PK)      │     │ id (PK)      │
│ email        │     │ name         │     │ name         │
│ password_hash│     │ code         │     │ permissions  │
│ name         │     │ ministry     │     └──────────────┘
│ department_id│     └──────────────┘            │
│ role_id      │◀────────────────────────────────┘
│ is_active    │
│ created_at   │
└──────┬───────┘
       │
       │ created_by
       ▼
┌──────────────────┐     ┌──────────────────┐
│   Evaluations    │     │    Documents     │
├──────────────────┤     ├──────────────────┤
│ id (PK)          │     │ id (PK)          │
│ reference_id     │     │ filename         │
│ title            │     │ file_path        │
│ tender_doc_id(FK)│────▶│ file_type        │
│ department_id    │     │ file_size        │
│ config (JSONB)   │     │ mime_type        │
│ status           │     │ extracted_data   │
│ created_by (FK)  │     │ uploaded_by      │
│ created_at       │     │ uploaded_at      │
│ started_at       │     └──────────────────┘
│ completed_at     │
└────────┬─────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐     ┌──────────────────┐
│      Bids        │     │     Vendors      │
├──────────────────┤     ├──────────────────┤
│ id (PK)          │     │ id (PK)          │
│ evaluation_id(FK)│     │ name             │
│ vendor_id (FK)   │────▶│ registration_no  │
│ document_id (FK) │     │ gstin            │
│ bid_amount       │     │ address          │
│ submitted_at     │     │ contact_email    │
│ status           │     │ contact_phone    │
└────────┬─────────┘     │ is_verified      │
         │               └──────────────────┘
         │ 1:N
         ▼
┌──────────────────────────────────────────────────────────┐
│                         Scores                            │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                   │
│ bid_id (FK)                                               │
│ evaluation_id (FK)                                        │
│ score_type (compliance | technical | financial)           │
│ total_score                                               │
│ max_score                                                 │
│ breakdown (JSONB)                                         │
│ justification (TEXT)                                      │
│ ai_reasoning (JSONB)                                      │
│ is_qualified                                              │
│ scored_at                                                 │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                     Audit Logs                            │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                   │
│ entity_type                                               │
│ entity_id                                                 │
│ action                                                    │
│ actor_id (FK)                                             │
│ changes (JSONB)                                           │
│ ip_address                                                │
│ user_agent                                                │
│ created_at                                                │
└──────────────────────────────────────────────────────────┘
```

### 7.2 SQLAlchemy Models

```python
# app/models/evaluation.py
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from app.models.base import Base

class EvaluationStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EvaluationMethod(str, enum.Enum):
    L1 = "l1"           # Lowest Price - winner is lowest bid meeting technical requirements
    QCBS = "qcbs"       # Quality & Cost Based Selection - weighted scoring
    TWO_STAGE = "two_stage"  # Two-Stage Bidding - see below

"""
Two-Stage Bidding Process (Added in v1.1):
=========================================
Stage 1 (Technical Qualification):
  1. All vendors submit technical proposals only
  2. Technical evaluation against tender criteria
  3. Vendors scoring >= qualification_threshold proceed to Stage 2
  4. Vendors below threshold are eliminated

Stage 2 (Financial Bidding):
  1. Only qualified vendors are invited to submit financial bids
  2. Financial bids evaluated using L1 method
  3. Winner is lowest bidder among qualified vendors

Key Difference from QCBS:
  - QCBS: Technical and financial scores are weighted and combined
  - Two-Stage: Technical is pass/fail, then L1 among qualified vendors
"""

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)

    tender_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))

    # Configuration stored as JSONB
    config = Column(JSONB, nullable=False, default={})
    # {
    #   "method": "qcbs",
    #   "technical_weight": 70,
    #   "financial_weight": 30,
    #   "qualification_threshold": 75,
    #   "enable_compliance_check": true,
    #   "enable_justifications": true,
    #   "enable_cartel_detection": false
    # }

    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.DRAFT)

    # Processing metadata
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_logs = Column(JSONB, default=[])

    # Results summary
    results_summary = Column(JSONB)
    winner_bid_id = Column(UUID(as_uuid=True), ForeignKey("bids.id"), nullable=True)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tender_document = relationship("Document", foreign_keys=[tender_document_id])
    bids = relationship("Bid", back_populates="evaluation")
    scores = relationship("Score", back_populates="evaluation")
    created_by_user = relationship("User", foreign_keys=[created_by])
    winner_bid = relationship("Bid", foreign_keys=[winner_bid_id])
```

### 7.3 Data Normalization Rules (Added in v1.1)

The following normalization rules ensure consistent data handling across the system:

| Field | Storage Format | Display Format | Validation |
|-------|---------------|----------------|------------|
| **Currency (INR)** | Integer (paisa) | ₹X.XX or ₹X Cr | Store ₹2 Cr as `20000000000` paisa |
| **Timestamps** | UTC (ISO 8601) | IST (+05:30) | Always store UTC, display as IST |
| **Financial Year** | String (FY format) | FY25, FY26 | Regex: `^FY\d{2}$` |
| **Bid Amount** | Decimal(15,2) | ₹X,XX,XXX.XX | Normalize to INR; max 15 digits |
| **Phone Numbers** | String (E.164) | +91-XXXXX-XXXXX | Validate Indian format |
| **GSTIN** | String (15 chars) | XX-XXXXXXX-XXXX | Validate checksum |

```python
# app/utils/normalization.py

def normalize_currency_to_paisa(amount: str) -> int:
    """Convert human-readable currency to paisa (smallest unit).

    Examples:
        '₹2 Cr' -> 20000000000 (paisa)
        '₹50 Lakh' -> 5000000000 (paisa)
        '₹1,25,000' -> 12500000 (paisa)
    """
    # Implementation handles Cr, Lakh, and comma-separated formats
    pass

def display_currency(paisa: int, short: bool = False) -> str:
    """Convert paisa to human-readable format.

    Examples:
        20000000000 -> '₹2 Cr' (short=True) or '₹2,00,00,000' (short=False)
    """
    pass

def utc_to_ist(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to IST (+05:30) for display."""
    return utc_dt + timedelta(hours=5, minutes=30)
```

### 7.4 Database Indexes

```sql
-- Performance indexes
CREATE INDEX idx_evaluations_status ON evaluations(status);
CREATE INDEX idx_evaluations_department ON evaluations(department_id);
CREATE INDEX idx_evaluations_created_at ON evaluations(created_at DESC);
CREATE INDEX idx_evaluations_reference ON evaluations(reference_id);

CREATE INDEX idx_bids_evaluation ON bids(evaluation_id);
CREATE INDEX idx_bids_vendor ON bids(vendor_id);
CREATE INDEX idx_bids_status ON bids(status);

CREATE INDEX idx_scores_bid ON scores(bid_id);
CREATE INDEX idx_scores_evaluation ON scores(evaluation_id);
CREATE INDEX idx_scores_type ON scores(score_type);

CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- Full-text search
CREATE INDEX idx_evaluations_title_fts ON evaluations
USING gin(to_tsvector('english', title));

CREATE INDEX idx_vendors_name_fts ON vendors
USING gin(to_tsvector('english', name));
```

---

## 8. Multi-Agent AI System

### 8.1 Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR AGENT                                │
│                   (Manages workflow & coordination)                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DOCUMENT      │    │   COMPLIANCE    │    │   TECHNICAL     │
│   PARSER        │    │   AGENT         │    │   AGENT         │
│                 │    │                 │    │                 │
│ - Extract text  │    │ - Verify docs   │    │ - Score tech    │
│ - Parse tables  │    │ - Check GST     │    │   criteria      │
│ - Identify      │    │ - Bank guarantee│    │ - Experience    │
│   sections      │    │ - Past perf.    │    │ - Team eval     │
└─────────────────┘    └─────────────────┘    │ - Methodology   │
                                              └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FINANCIAL     │    │   COMPARISON    │    │   REPORT        │
│   AGENT         │    │   AGENT         │    │   AGENT         │
│                 │    │                 │    │                 │
│ - Parse quotes  │    │ - Cross-vendor  │    │ - Generate      │
│ - Calculate L1  │    │   analysis      │    │   summaries     │
│ - Adjustments   │    │ - Cartel detect │    │ - Create PDF    │
│ - Normalize     │    │   (Beta/Advis.) │    │ - Audit trail   │
└─────────────────┘    └─────────────────┘    └─────────────────┘

> **Cartel Detection (Beta - Advisory Only):**
> - Flags suspicious patterns for **human review only**
> - Does NOT automatically disqualify vendors
> - Detected patterns: identical pricing, bid rotation, cover bidding, unusual price clustering
> - All flags require manual verification before any action
> - False positive rate is expected; treat as investigative leads, not conclusions
```

### 8.2 Orchestrator Implementation

```python
# app/agents/orchestrator.py
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrockConverse
from app.agents.document_parser import DocumentParserAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.technical_agent import TechnicalAgent
from app.agents.financial_agent import FinancialAgent
from app.agents.comparison_agent import ComparisonAgent
from app.agents.report_agent import ReportAgent
from app.services.bedrock_llm_service import bedrock_llm_service

class EvaluationState:
    """State object passed between agents."""
    tender_data: Dict[str, Any]
    vendor_bids: List[Dict[str, Any]]
    compliance_results: Dict[str, Any]
    technical_scores: Dict[str, Any]
    financial_scores: Dict[str, Any]
    comparison_matrix: Dict[str, Any]
    final_report: Dict[str, Any]
    logs: List[str]
    current_step: str
    error: str | None

    # Error Recovery (Added in v1.1)
    retry_count: int = 0
    max_retries: int = 3
    failed_step: str | None = None
    partial_results_saved: bool = False

"""
Error Recovery Workflow (Added in v1.1):
=======================================
When LLM fails during evaluation:

1. Retry with exponential backoff:
   - Attempt 1: Immediate retry
   - Attempt 2: Wait 2 seconds
   - Attempt 3: Wait 4 seconds

2. If all retries fail:
   - Save partial results to database
   - Set evaluation status to FAILED
   - Log detailed error with stack trace
   - Send notification to user

3. Manual recovery options:
   - Restart from failed step (preserves completed work)
   - Restart entire evaluation
   - Cancel evaluation

4. Partial results are preserved:
   - Completed agent outputs saved before failure
   - Resume capability from last successful checkpoint
"""

class EvaluationOrchestrator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Use AWS Bedrock with Claude Sonnet 4.5
        self.llm = bedrock_llm_service.get_bedrock_client(
            model_id="anthropic.claude-sonnet-4-5-20250929-v1:0"
        )

        # Initialize agents
        self.document_parser = DocumentParserAgent(self.llm)
        self.compliance_agent = ComplianceAgent(self.llm)
        self.technical_agent = TechnicalAgent(self.llm)
        self.financial_agent = FinancialAgent(self.llm)
        self.comparison_agent = ComparisonAgent(self.llm)
        self.report_agent = ReportAgent(self.llm)

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(EvaluationState)

        # Add nodes
        workflow.add_node("parse_tender", self._parse_tender)
        workflow.add_node("parse_bids", self._parse_bids)
        workflow.add_node("compliance_check", self._compliance_check)
        workflow.add_node("technical_evaluation", self._technical_evaluation)
        workflow.add_node("financial_evaluation", self._financial_evaluation)
        workflow.add_node("comparison_analysis", self._comparison_analysis)
        workflow.add_node("generate_report", self._generate_report)

        # Define edges
        workflow.add_edge("parse_tender", "parse_bids")
        workflow.add_edge("parse_bids", "compliance_check")
        workflow.add_conditional_edges(
            "compliance_check",
            self._should_continue_after_compliance,
            {
                "continue": "technical_evaluation",
                "end": END
            }
        )
        workflow.add_edge("technical_evaluation", "financial_evaluation")
        workflow.add_edge("financial_evaluation", "comparison_analysis")
        workflow.add_edge("comparison_analysis", "generate_report")
        workflow.add_edge("generate_report", END)

        workflow.set_entry_point("parse_tender")

        return workflow.compile()

    async def run(
        self,
        tender_document: bytes,
        vendor_bid_documents: List[bytes],
        progress_callback: callable = None
    ) -> Dict[str, Any]:
        """Execute the full evaluation workflow."""
        initial_state = EvaluationState(
            tender_data={},
            vendor_bids=[],
            compliance_results={},
            technical_scores={},
            financial_scores={},
            comparison_matrix={},
            final_report={},
            logs=[],
            current_step="starting",
            error=None
        )

        # Inject documents
        initial_state.tender_data["raw_document"] = tender_document
        initial_state.vendor_bids = [
            {"raw_document": doc} for doc in vendor_bid_documents
        ]

        # Run workflow with progress updates
        async for state in self.workflow.astream(initial_state):
            if progress_callback:
                await progress_callback(state)

        return state

    async def _parse_tender(self, state: EvaluationState) -> EvaluationState:
        """Parse tender document."""
        state.current_step = "tender_parsing"
        state.logs.append(f"[{self._timestamp()}] Starting tender document parsing...")

        result = await self.document_parser.parse_tender(
            state.tender_data["raw_document"]
        )

        state.tender_data.update(result)
        state.logs.append(f"[{self._timestamp()}] Tender parsing complete. Extracted {len(result.get('sections', []))} sections.")

        return state

    async def _compliance_check(self, state: EvaluationState) -> EvaluationState:
        """Run compliance verification for all bids."""
        state.current_step = "compliance_verification"
        state.logs.append(f"[{self._timestamp()}] Starting compliance verification...")

        results = {}
        for bid in state.vendor_bids:
            vendor_id = bid.get("vendor_id")
            result = await self.compliance_agent.verify(
                bid=bid,
                tender_requirements=state.tender_data.get("requirements", [])
            )
            results[vendor_id] = result

            status = "PASS" if result["is_compliant"] else "FAIL"
            state.logs.append(
                f"[{self._timestamp()}] AGENT_1: {bid['vendor_name']} compliance: {status}"
            )

        state.compliance_results = results
        return state

    # ... additional methods for other steps
```

### 8.3 Technical Evaluation Agent

```python
# app/agents/technical_agent.py
from typing import Dict, Any, List
from langchain_aws import ChatBedrockConverse
from langchain.prompts import ChatPromptTemplate

class TechnicalAgent:
    def __init__(self, llm: ChatBedrockConverse):
        self.llm = llm
        self.evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical evaluator for government procurement.

            Evaluate the vendor's technical proposal against the criteria provided.
            For each criterion, provide:
            1. A score (0-100)
            2. A detailed justification with specific references to the proposal
            3. Strengths and weaknesses identified

            Be objective, fair, and base all assessments on documented evidence."""),
            ("user", """
            ## Tender Requirements
            {tender_requirements}

            ## Technical Criteria (with weights)
            {criteria}

            ## Vendor Technical Proposal
            {proposal}

            Evaluate this proposal and provide scores for each criterion.
            """)
        ])

    async def evaluate(
        self,
        bid: Dict[str, Any],
        tender_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate technical proposal."""

        criteria = self._get_technical_criteria(tender_data)

        # Run LLM evaluation
        response = await self.llm.ainvoke(
            self.evaluation_prompt.format(
                tender_requirements=tender_data.get("requirements", ""),
                criteria=self._format_criteria(criteria),
                proposal=bid.get("technical_proposal", "")
            )
        )

        # Parse structured response
        scores = self._parse_scores(response.content)

        # Calculate weighted total
        total_score = self._calculate_weighted_score(scores, criteria)

        return {
            "vendor_id": bid.get("vendor_id"),
            "vendor_name": bid.get("vendor_name"),
            "total_score": total_score,
            "max_score": 100,
            "is_qualified": total_score >= config.get("qualification_threshold", 75),
            "breakdown": scores,
            "ai_reasoning": {
                "model": "anthropic.claude-sonnet-4-5-20250929-v1:0",
                "provider": "aws_bedrock",
                "timestamp": self._timestamp(),
                "raw_response": response.content
            }
        }

    def _get_technical_criteria(self, tender_data: Dict) -> List[Dict]:
        """Extract technical evaluation criteria."""
        default_criteria = [
            {"name": "Previous Government Projects Experience", "weight": 20, "max_score": 100},
            {"name": "Technical Team Expertise", "weight": 25, "max_score": 100},
            {"name": "Proposed Methodology", "weight": 30, "max_score": 100},
            {"name": "Quality Assurance Plan", "weight": 15, "max_score": 100},
            {"name": "Delivery Timeline", "weight": 10, "max_score": 100}
        ]
        return tender_data.get("technical_criteria", default_criteria)
```

### 8.4 Real-time Progress Updates (WebSocket)

```python
# app/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
import json
import asyncio
from app.core.auth import get_current_user_ws

websocket_router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, evaluation_id: str):
        await websocket.accept()
        if evaluation_id not in self.active_connections:
            self.active_connections[evaluation_id] = []
        self.active_connections[evaluation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, evaluation_id: str):
        if evaluation_id in self.active_connections:
            self.active_connections[evaluation_id].remove(websocket)

    async def broadcast(self, evaluation_id: str, message: dict):
        if evaluation_id in self.active_connections:
            for connection in self.active_connections[evaluation_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

@websocket_router.websocket("/evaluation/{evaluation_id}")
async def evaluation_progress(
    websocket: WebSocket,
    evaluation_id: str
):
    await manager.connect(websocket, evaluation_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, evaluation_id)

# Progress callback used by orchestrator
async def send_progress_update(evaluation_id: str, state: dict):
    """Send progress update to all connected clients."""
    message = {
        "type": "progress",
        "step": state.get("current_step"),
        "logs": state.get("logs", [])[-5:],  # Last 5 logs
        "progress_percent": calculate_progress(state),
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(evaluation_id, message)
```

---

## 9. API Specification

### 9.1 Authentication Endpoints (JWT)

```yaml
POST /api/v1/auth/register
  Request:
    email: string
    password: string
    name: string
    department: string
  Response:
    id: uuid
    email: string
    message: "Registration successful"

POST /api/v1/auth/login
  Request:
    email: string
    password: string
  Response:
    access_token: string
    refresh_token: string
    token_type: "bearer"
    user: UserResponse

POST /api/v1/auth/logout
  Headers: Authorization: Bearer <token>
  Response: { message: "Logged out successfully" }

POST /api/v1/auth/refresh
  Request:
    refresh_token: string
  Response:
    access_token: string
    token_type: "bearer"

GET /api/v1/auth/me
  Headers: Authorization: Bearer <token>
  Response: UserResponse

# Password Reset (Added in v1.1)
POST /api/v1/auth/forgot-password
  Request:
    email: string
  Response:
    message: "Password reset email sent"

POST /api/v1/auth/reset-password
  Request:
    token: string
    new_password: string
  Response:
    message: "Password reset successful"
```

### 9.2 Evaluation Endpoints

```yaml
# List evaluations
GET /api/v1/evaluations
  Query:
    status: string (optional)
    page: int (default: 1)
    limit: int (default: 20)
  Response:
    items: EvaluationSummary[]
    total: int
    page: int
    pages: int

# Create evaluation
POST /api/v1/evaluations
  Request:
    tender_document_id: uuid
    title: string
    config: EvaluationConfig
  Response:
    id: uuid
    reference_id: string
    status: "draft"

# Get evaluation details
GET /api/v1/evaluations/{id}
  Response: EvaluationDetail

# Add vendor bids
POST /api/v1/evaluations/{id}/bids
  Request:
    bids: [
      { vendor_id: uuid, document_id: uuid }
    ]
  Response: { added: int }

# Update configuration
PATCH /api/v1/evaluations/{id}/config
  Request: EvaluationConfig
  Response: EvaluationDetail

# Start evaluation
POST /api/v1/evaluations/{id}/start
  Response:
    id: uuid
    status: "processing"
    estimated_time_seconds: int

# Get results
GET /api/v1/evaluations/{id}/results
  Response: EvaluationResults

# Get compliance results
GET /api/v1/evaluations/{id}/results/compliance
  Response: ComplianceResults

# Get technical scores
GET /api/v1/evaluations/{id}/results/technical
  Query: vendor_id: uuid (optional)
  Response: TechnicalScores

# Get financial scores
GET /api/v1/evaluations/{id}/results/financial
  Response: FinancialScores

# Get comparison matrix
GET /api/v1/evaluations/{id}/results/comparison
  Response: ComparisonMatrix

# Export report
GET /api/v1/evaluations/{id}/export
  Query: format: "pdf" | "xlsx"
  Response: Binary file

# Cancel evaluation (Added in v1.1)
POST /api/v1/evaluations/{id}/cancel
  Request:
    reason: string (optional)
  Response:
    id: uuid
    status: "cancelled"
    cancelled_at: datetime
    cancelled_by: uuid

# Approve evaluation results (Added in v1.1)
POST /api/v1/evaluations/{id}/approve
  Request:
    approver_notes: string (optional)
  Response:
    id: uuid
    status: "approved"
    approved_at: datetime
    approved_by: uuid
```

### 9.3 Document Endpoints

```yaml
# Upload document
POST /api/v1/documents/upload
  Request: multipart/form-data
    file: File
    type: "tender" | "bid"
    metadata: JSON
  Response:
    id: uuid
    filename: string
    file_size: int
    extracted_data: object

# Get document
GET /api/v1/documents/{id}
  Response: DocumentDetail

# Download document
GET /api/v1/documents/{id}/download
  Response: Binary file
```

### 9.4 Vendor Endpoints

```yaml
# List vendors
GET /api/v1/vendors
  Query:
    search: string
    verified: boolean
    page: int
    limit: int
  Response: VendorList

# Get vendor details
GET /api/v1/vendors/{id}
  Response: VendorDetail

# Get vendor history
GET /api/v1/vendors/{id}/history
  Response: VendorBidHistory
```

### 9.5 Admin Endpoints (Added in v1.1)

```yaml
# List users
GET /api/v1/admin/users
  Query:
    role: string (optional)
    department_id: uuid (optional)
    page: int
    limit: int
  Response: UserList

# Create user
POST /api/v1/admin/users
  Request:
    email: string
    password: string
    name: string
    role: "officer" | "evaluator" | "admin"
    department_id: uuid
  Response: UserDetail

# Update user
PATCH /api/v1/admin/users/{id}
  Request:
    name: string (optional)
    role: string (optional)
    is_active: boolean (optional)
  Response: UserDetail

# Delete user
DELETE /api/v1/admin/users/{id}
  Response: { message: "User deleted" }

# Get audit logs
GET /api/v1/admin/audit-logs
  Query:
    entity_type: string (optional)
    entity_id: uuid (optional)
    actor_id: uuid (optional)
    from_date: datetime (optional)
    to_date: datetime (optional)
    page: int
    limit: int
  Response:
    items: AuditLog[]
    total: int

# List departments
GET /api/v1/departments
  Response:
    items: Department[]
    total: int
```

### 9.6 Schema Definitions

```python
# app/schemas/evaluation.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class EvaluationMethod(str, Enum):
    L1 = "l1"
    QCBS = "qcbs"
    TWO_STAGE = "two_stage"

class EvaluationConfig(BaseModel):
    method: EvaluationMethod = EvaluationMethod.QCBS
    technical_weight: int = Field(70, ge=0, le=100)
    financial_weight: int = Field(30, ge=0, le=100)
    qualification_threshold: int = Field(75, ge=0, le=100)  # Hard cutoff per gap analysis
    enable_compliance_check: bool = True
    enable_justifications: bool = True
    enable_cartel_detection: bool = False  # Beta feature - advisory only

    # Weight Validation (Added in v1.1)
    @model_validator(mode='after')
    def validate_weights_sum_to_100(self):
        """Ensure technical + financial weights equal 100%."""
        if self.technical_weight + self.financial_weight != 100:
            raise ValueError(
                f"Weights must sum to 100 (got {self.technical_weight} + {self.financial_weight} = "
                f"{self.technical_weight + self.financial_weight})"
            )
        return self

class EvaluationCreate(BaseModel):
    tender_document_id: UUID
    title: str = Field(..., min_length=10, max_length=500)
    config: EvaluationConfig = EvaluationConfig()

class EvaluationSummary(BaseModel):
    id: UUID
    reference_id: str
    title: str
    status: str
    created_at: datetime
    vendor_count: int

    class Config:
        from_attributes = True

class VendorScore(BaseModel):
    vendor_id: UUID
    vendor_name: str
    compliance_status: str
    technical_score: Optional[float]
    financial_score: Optional[float]
    total_score: Optional[float]
    rank: Optional[int]
    is_winner: bool = False

class EvaluationResults(BaseModel):
    evaluation_id: UUID
    status: str
    method: EvaluationMethod
    total_bids: int
    qualified_bids: int
    disqualified_bids: int
    winner: Optional[VendorScore]
    rankings: List[VendorScore]
    score_distribution: Dict[str, Any]
    processing_time_seconds: int
    completed_at: datetime
```

---

## 10. Security & Compliance

### 10.1 Authentication & Authorization

```python
# app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

### 10.2 Role-Based Access Control

```python
# app/core/auth.py
from enum import Enum
from functools import wraps
from fastapi import HTTPException, Depends

class Permission(str, Enum):
    VIEW_EVALUATIONS = "view_evaluations"
    CREATE_EVALUATION = "create_evaluation"
    START_EVALUATION = "start_evaluation"
    VIEW_RESULTS = "view_results"
    EXPORT_REPORTS = "export_reports"
    MANAGE_VENDORS = "manage_vendors"
    ADMIN = "admin"

ROLE_PERMISSIONS = {
    "officer": [
        Permission.VIEW_EVALUATIONS,
        Permission.CREATE_EVALUATION,
        Permission.START_EVALUATION,
        Permission.VIEW_RESULTS,
        Permission.EXPORT_REPORTS,
    ],
    "evaluator": [
        Permission.VIEW_EVALUATIONS,
        Permission.VIEW_RESULTS,
    ],
    "admin": [
        Permission.ADMIN,
        # ... all permissions
    ]
}

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user = Depends(get_current_user), **kwargs):
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
            if Permission.ADMIN not in user_permissions and permission not in user_permissions:
                raise HTTPException(status_code=403, detail="Permission denied")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

### 10.3 Audit Logging

```python
# app/services/audit_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from typing import Any, Dict

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_id: str,
        changes: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(log)
        await self.db.commit()

# Usage in endpoints
@router.post("/{id}/start")
async def start_evaluation(
    id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    audit: AuditService = Depends(get_audit_service)
):
    # ... start evaluation
    await audit.log(
        entity_type="evaluation",
        entity_id=str(id),
        action="started",
        actor_id=str(current_user.id),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
```

### 10.4 Security Headers & HTTPS

```python
# app/core/middleware.py
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
```

---

## 11. Deployment Architecture (AWS EC2 - Minimal POC)

### 11.1 AWS Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    EC2 Instance (t3.medium)                      │   │
│  │                                                                   │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │                   Caddy (Reverse Proxy)                   │   │   │
│  │  │                     :80, :443 (SSL)                       │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  │                              │                                   │   │
│  │              ┌───────────────┴───────────────┐                  │   │
│  │              ▼                               ▼                  │   │
│  │  ┌──────────────────────┐      ┌──────────────────────┐        │   │
│  │  │      Next.js         │      │      FastAPI         │        │   │
│  │  │       (PM2)          │      │       (PM2)          │        │   │
│  │  │       :3000          │      │       :8000          │        │   │
│  │  └──────────────────────┘      └──────────────────────┘        │   │
│  │                                          │                      │   │
│  │                        ┌─────────────────┴─────────────────┐   │   │
│  │                        ▼                                   ▼   │   │
│  │            ┌──────────────────────┐      ┌──────────────────┐  │   │
│  │            │       SQLite         │      │   File Storage   │  │   │
│  │            │     (database)       │      │   /var/uploads   │  │   │
│  │            └──────────────────────┘      └──────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 11.2 AWS Resources Required

| Resource | Specification | Purpose | Estimated Cost (POC) |
|----------|---------------|---------|---------------------|
| **EC2** | t3.medium (2 vCPU, 4GB RAM) | Everything runs here | **~$30/month** |

> **Note:** Use EC2 public IP directly for POC. No Redis/Celery needed - uses FastAPI BackgroundTasks.

### 11.3 EC2 Server Setup

```bash
#!/bin/bash
# setup-ec2.sh - Run on fresh Ubuntu 22.04 EC2 instance

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install PM2 globally
sudo npm install -g pm2

# Install Caddy (reverse proxy with automatic HTTPS)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Create application directories
sudo mkdir -p /var/www/govprocure
sudo mkdir -p /var/www/govprocure/data        # SQLite database
sudo mkdir -p /var/www/govprocure/uploads     # Document uploads
sudo chown -R ubuntu:ubuntu /var/www/govprocure

# Clone repository (replace with your repo)
cd /var/www/govprocure
git clone https://github.com/your-org/govprocure.git .

echo "Base setup complete. Configure application next."
```

### 11.4 Application Deployment Scripts

**Backend Setup:**
```bash
#!/bin/bash
# deploy-backend.sh

cd /var/www/govprocure/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'fastapi',
      script: 'venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      cwd: '/var/www/govprocure/backend',
      env: {
        NODE_ENV: 'production',
      },
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_memory_restart: '500M',
    }
  ]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
```

**Frontend Setup:**
```bash
#!/bin/bash
# deploy-frontend.sh

cd /var/www/govprocure/frontend

# Install dependencies
npm ci

# Build production
npm run build

# Create PM2 config
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'nextjs',
      script: 'npm',
      args: 'start',
      cwd: '/var/www/govprocure/frontend',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      instances: 1,
      autorestart: true,
      max_memory_restart: '512M',
    }
  ]
};
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
```

### 11.5 Caddy Configuration (Reverse Proxy)

```bash
# /etc/caddy/Caddyfile

yourdomain.gov.in {
    # Frontend (Next.js)
    handle /* {
        reverse_proxy localhost:3000
    }

    # API routes
    handle /api/* {
        reverse_proxy localhost:8000
    }

    # WebSocket for real-time updates
    handle /ws/* {
        reverse_proxy localhost:8000
    }

    # Health check endpoint
    handle /health {
        reverse_proxy localhost:8000
    }

    # Enable compression
    encode gzip

    # Security headers
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
    }

    # Logs
    log {
        output file /var/log/caddy/access.log
        format json
    }
}
```

### 11.6 PM2 Process Management

```bash
# Useful PM2 commands

# View all processes
pm2 list

# View logs
pm2 logs

# Monitor resources
pm2 monit

# Restart all
pm2 restart all

# Reload without downtime
pm2 reload all

# Setup startup script (auto-start on reboot)
pm2 startup
pm2 save
```

### 11.7 Environment Configuration

```bash
# .env.example (AWS EC2 Minimal POC)

# Application
APP_NAME=GovProcure
DEBUG=false
SECRET_KEY=your-secret-key-here

# Database (SQLite - local file)
DATABASE_URL=sqlite+aiosqlite:///var/www/govprocure/data/govprocure.db

# File Storage (local directory)
UPLOAD_DIR=/var/www/govprocure/uploads
MAX_UPLOAD_SIZE_MB=50

# JWT Authentication
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI/LLM
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
LLM_MODEL=gpt-4-turbo

# CORS (use EC2 public IP for POC)
ALLOWED_ORIGINS=["http://your-ec2-public-ip", "http://localhost:3000"]

# Frontend Environment (.env.local)
NEXT_PUBLIC_API_URL=http://your-ec2-public-ip/api
NEXT_PUBLIC_WS_URL=ws://your-ec2-public-ip/ws
```

### 11.8 AWS Security Group Configuration

```
# EC2 Security Group (sg-ec2-govprocure)
Inbound Rules:
  - HTTP (80)      : 0.0.0.0/0        # Application access
  - HTTPS (443)    : 0.0.0.0/0        # Application access (if using SSL)
  - SSH (22)       : Your IP only     # Admin access

# No other security groups needed - everything runs on EC2
```

### 11.9 Backup Script (Important for SQLite)

```bash
#!/bin/bash
# backup.sh - Run daily via cron

BACKUP_DIR="/var/www/govprocure/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup SQLite database
sqlite3 /var/www/govprocure/data/govprocure.db ".backup '$BACKUP_DIR/db_$DATE.sqlite'"

# Backup uploads directory
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/govprocure/uploads

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Add to crontab (runs daily at 2 AM)
# crontab -e
0 2 * * * /var/www/govprocure/backup.sh >> /var/log/govprocure-backup.log 2>&1
```

---

## Appendix A: UI Component Reference

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | #1E40AF | Buttons, links, active states |
| Primary Light | #3B82F6 | Hover states, highlights |
| Success | #10B981 | Completed, passed, verified |
| Warning | #F59E0B | Pending, in progress |
| Error | #EF4444 | Failed, disqualified, errors |
| Background | #F8FAFC | Page background |
| Card | #FFFFFF | Card backgrounds |
| Border | #E2E8F0 | Borders, dividers |
| Text Primary | #1E293B | Primary text |
| Text Secondary | #64748B | Secondary text, labels |

### Typography

| Style | Size | Weight | Line Height |
|-------|------|--------|-------------|
| H1 | 30px | 700 | 36px |
| H2 | 24px | 600 | 32px |
| H3 | 20px | 600 | 28px |
| H4 | 16px | 600 | 24px |
| Body | 14px | 400 | 20px |
| Small | 12px | 400 | 16px |
| Caption | 11px | 500 | 14px |

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **L1** | Lowest Price method - winner is vendor with lowest price meeting technical criteria |
| **QCBS** | Quality and Cost Based Selection - weighted scoring of technical and financial bids |
| **RFP** | Request for Proposal |
| **RFQ** | Request for Quotation |
| **GeM** | Government e-Marketplace |
| **GSTIN** | Goods and Services Tax Identification Number |
| **Jan Parichay** | Government of India SSO authentication system |

---

**Document Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | - | Initial draft |
| 1.1 | Dec 2025 | - | Gap analysis updates (see below) |

### Version 1.1 Changes (December 2025)

Based on comprehensive gap analysis, the following updates were made:

**Stakeholder Decisions:**
- Tie-breaking: Earliest submission wins
- Qualification threshold (75): Hard cutoff
- Winner recommendation: System recommends with justification
- LLM provider: AWS Bedrock (Claude Sonnet 4.5)

**New API Endpoints:**
- Password reset: `POST /auth/forgot-password`, `POST /auth/reset-password`
- Admin endpoints: User CRUD, audit logs
- Evaluation workflow: `POST /evaluations/{id}/cancel`, `POST /evaluations/{id}/approve`
- Reference data: `GET /departments`

**Technical Improvements:**
- Data normalization rules (currency, timezone, FY format)
- Two-Stage Bidding method explained
- Cartel Detection clarified as Beta/advisory only
- Error recovery workflow for LLM failures
- Weight validation (must sum to 100%)

---

*End of Technical Specification Document*
