# UI/UX DESIGN SPECIFICATION
## Multi-Agent Vendor Bid Evaluation System for Indian Government Procurement

**Design Tool:** Google Stitch
**Version:** 1.0
**Date:** 2025-12-20

---

## TABLE OF CONTENTS

1. [Design System](#1-design-system)
2. [User Roles & Personas](#2-user-roles--personas)
3. [Information Architecture](#3-information-architecture)
4. [User Flows](#4-user-flows)
5. [Page Designs](#5-page-designs)
6. [Component Library](#6-component-library)
7. [Responsive Breakpoints](#7-responsive-breakpoints)

---

## 1. DESIGN SYSTEM

### 1.1 Color Palette

```
PRIMARY COLORS (Government Blue Theme):
├── Primary-900:    #1a365d  (Darkest - Headers, Important text)
├── Primary-800:    #2a4365  (Navigation background)
├── Primary-700:    #2c5282  (Primary buttons)
├── Primary-600:    #2b6cb0  (Button hover)
├── Primary-500:    #3182ce  (Links, Interactive elements)
├── Primary-100:    #ebf8ff  (Light backgrounds)
└── Primary-50:     #f7fafc  (Page backgrounds)

SECONDARY COLORS (Saffron Accent - Indian Flag):
├── Secondary-600:  #dd6b20  (Accent, CTAs)
├── Secondary-500:  #ed8936  (Hover states)
└── Secondary-100:  #feebc8  (Accent backgrounds)

SEMANTIC COLORS:
├── Success-600:    #38a169  (Qualified, Pass, Complete)
├── Success-100:    #c6f6d5  (Success backgrounds)
├── Warning-600:    #d69e2e  (Pending, Review needed)
├── Warning-100:    #fefcbf  (Warning backgrounds)
├── Error-600:      #e53e3e  (Disqualified, Fail, Error)
├── Error-100:      #fed7d7  (Error backgrounds)
└── Info-600:       #3182ce  (Information, Tips)

NEUTRAL COLORS:
├── Gray-900:       #1a202c  (Primary text)
├── Gray-700:       #4a5568  (Secondary text)
├── Gray-500:       #a0aec0  (Placeholder, Disabled)
├── Gray-300:       #e2e8f0  (Borders)
├── Gray-100:       #f7fafc  (Backgrounds)
└── White:          #ffffff  (Cards, Modals)
```

### 1.2 Typography

```
FONT FAMILY:
├── Primary:   'Inter', sans-serif (UI elements)
├── Heading:   'Poppins', sans-serif (Headings)
└── Mono:      'JetBrains Mono', monospace (Code, IDs)

TYPE SCALE:
├── Display:   48px / 56px line-height / 700 weight
├── H1:        36px / 44px line-height / 600 weight
├── H2:        30px / 38px line-height / 600 weight
├── H3:        24px / 32px line-height / 600 weight
├── H4:        20px / 28px line-height / 500 weight
├── Body-L:    18px / 28px line-height / 400 weight
├── Body:      16px / 24px line-height / 400 weight
├── Body-S:    14px / 20px line-height / 400 weight
├── Caption:   12px / 16px line-height / 400 weight
└── Overline:  10px / 16px line-height / 600 weight / UPPERCASE
```

### 1.3 Spacing System

```
BASE UNIT: 4px

SPACING SCALE:
├── xs:   4px   (Tight spacing)
├── sm:   8px   (Compact elements)
├── md:   16px  (Standard spacing)
├── lg:   24px  (Section spacing)
├── xl:   32px  (Large sections)
├── 2xl:  48px  (Page sections)
└── 3xl:  64px  (Major divisions)
```

### 1.4 Border Radius

```
├── none:   0px
├── sm:     4px   (Buttons, inputs)
├── md:     8px   (Cards)
├── lg:     12px  (Modals)
├── xl:     16px  (Large cards)
└── full:   9999px (Avatars, badges)
```

### 1.5 Shadows

```
├── sm:    0 1px 2px rgba(0,0,0,0.05)
├── md:    0 4px 6px rgba(0,0,0,0.1)
├── lg:    0 10px 15px rgba(0,0,0,0.1)
├── xl:    0 20px 25px rgba(0,0,0,0.15)
└── inner: inset 0 2px 4px rgba(0,0,0,0.05)
```

---

## 2. USER ROLES & PERSONAS

### 2.1 User Roles

```
┌─────────────────────────────────────────────────────────────────┐
│  ROLE 1: PROCUREMENT OFFICER (Primary User)                    │
├─────────────────────────────────────────────────────────────────┤
│  Access: Full system access                                     │
│  Actions:                                                       │
│  • Upload tender documents                                      │
│  • Upload vendor bids                                           │
│  • Run AI evaluation                                            │
│  • Review results                                               │
│  • Generate reports                                             │
│  • Export audit trail                                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ROLE 2: EVALUATION COMMITTEE MEMBER                           │
├─────────────────────────────────────────────────────────────────┤
│  Access: View and review                                        │
│  Actions:                                                       │
│  • View evaluation results                                      │
│  • Add comments/notes                                           │
│  • Approve/flag scores                                          │
│  • View audit trail                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ROLE 3: ADMINISTRATOR                                          │
├─────────────────────────────────────────────────────────────────┤
│  Access: System configuration                                   │
│  Actions:                                                       │
│  • Manage users                                                 │
│  • Configure evaluation parameters                              │
│  • View system logs                                             │
│  • Manage templates                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ROLE 4: AUDITOR (Read-Only)                                    │
├─────────────────────────────────────────────────────────────────┤
│  Access: Complete audit trail                                   │
│  Actions:                                                       │
│  • View all evaluations                                         │
│  • Export audit reports                                         │
│  • View decision history                                        │
│  • No edit capabilities                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. INFORMATION ARCHITECTURE

### 3.1 Site Map

```
🏠 ROOT
├── 🔐 AUTHENTICATION
│   ├── Login Page
│   ├── Forgot Password
│   ├── Reset Password
│   └── MFA Verification
│
├── 📊 DASHBOARD
│   ├── Overview Cards
│   ├── Recent Evaluations
│   ├── Quick Actions
│   └── Activity Feed
│
├── 📋 EVALUATIONS
│   ├── All Evaluations (List)
│   ├── New Evaluation (Wizard)
│   │   ├── Step 1: Tender Upload
│   │   ├── Step 2: Bids Upload
│   │   ├── Step 3: Configuration
│   │   ├── Step 4: Review & Run
│   │   └── Step 5: Processing
│   ├── Evaluation Detail
│   │   ├── Summary Tab
│   │   ├── Compliance Tab
│   │   ├── Technical Scores Tab
│   │   ├── Financial Scores Tab
│   │   ├── Comparison Matrix Tab
│   │   └── Audit Trail Tab
│   └── Export/Reports
│
├── 📁 DOCUMENT LIBRARY
│   ├── Tenders
│   ├── Vendor Bids
│   └── Templates
│
├── 📈 REPORTS
│   ├── Evaluation Reports
│   ├── Audit Reports
│   └── Analytics
│
├── ⚙️ SETTINGS
│   ├── Profile
│   ├── Preferences
│   ├── Notifications
│   └── Security
│
└── 👥 ADMIN (Admin only)
    ├── User Management
    ├── System Configuration
    ├── Scoring Templates
    └── System Logs
```

---

## 4. USER FLOWS

### 4.1 Primary Flow: Complete Bid Evaluation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRIMARY USER FLOW: BID EVALUATION                         │
└─────────────────────────────────────────────────────────────────────────────┘

[LOGIN] ──► [DASHBOARD] ──► [NEW EVALUATION]
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: UPLOAD TENDER                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  📄 Drag & Drop or Browse                                               ││
│  │  ─────────────────────────────                                          ││
│  │  Supported: PDF, DOCX, TXT                                              ││
│  │  Max size: 50MB                                                         ││
│  │                                                                         ││
│  │  [Upload Tender Document]                                               ││
│  │                                                                         ││
│  │  ✓ Tender ID auto-extracted: GEM/2024/B/12345                          ││
│  │  ✓ Organization: Ministry of Electronics                               ││
│  │  ✓ Category: IT Hardware                                                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                [Next →]      │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: UPLOAD VENDOR BIDS                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  📁 Upload Multiple Bids                                                ││
│  │  ─────────────────────────────                                          ││
│  │                                                                         ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐       ││
│  │  │ 📄 Vendor_1  │ │ 📄 Vendor_2  │ │ 📄 Vendor_3  │ │  + Add   │       ││
│  │  │   TechPro    │ │  BudgetIT    │ │  Premium     │ │  More    │       ││
│  │  │   ✓ Ready    │ │   ✓ Ready    │ │   ✓ Ready    │ │          │       ││
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────┘       ││
│  │                                                                         ││
│  │  Total Bids: 3                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                          [← Back]  [Next →]                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: CONFIGURATION                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Evaluation Method                                                       ││
│  │  ○ L1 (Lowest Price)                                                    ││
│  │  ● QCBS (Quality & Cost Based)                                          ││
│  │  ○ Two-Stage Bidding                                                    ││
│  │                                                                         ││
│  │  QCBS Configuration:                                                     ││
│  │  Technical Weight: [70%] ────●────────── Financial Weight: [30%]        ││
│  │                                                                         ││
│  │  Qualification Threshold: [50%] minimum technical score                 ││
│  │                                                                         ││
│  │  ☑ Enable compliance verification                                       ││
│  │  ☑ Generate detailed justifications                                     ││
│  │  ☐ Enable cartel detection (Beta)                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                          [← Back]  [Next →]                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: REVIEW & CONFIRM                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  📋 Evaluation Summary                                                   ││
│  │  ─────────────────────────                                              ││
│  │                                                                         ││
│  │  Tender:        GEM/2024/B/12345 - IT Hardware Procurement              ││
│  │  Vendors:       3 bids uploaded                                         ││
│  │  Method:        QCBS (70:30)                                            ││
│  │  Threshold:     50% minimum technical score                             ││
│  │                                                                         ││
│  │  Estimated Time: ~5-10 minutes                                          ││
│  │                                                                         ││
│  │  ⚠️ Once started, evaluation cannot be cancelled.                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                          [← Back]  [🚀 Start Evaluation]     │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: PROCESSING (Live Updates)                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                                                                         ││
│  │  🔄 Evaluation in Progress                                              ││
│  │  ═══════════════════════════════════════════════════════ 75%           ││
│  │                                                                         ││
│  │  ✅ Step 1: Tender Parsing                          Complete            ││
│  │  ✅ Step 2: Bid Analysis (3/3 vendors)              Complete            ││
│  │  ✅ Step 3: Compliance Verification                 Complete            ││
│  │  🔄 Step 4: Technical Scoring                       In Progress...      ││
│  │  ⏳ Step 5: Financial Scoring                       Pending             ││
│  │  ⏳ Step 6: Report Generation                       Pending             ││
│  │                                                                         ││
│  │  ┌─────────────────────────────────────────────────────────────────┐   ││
│  │  │ 📝 Live Log                                                     │   ││
│  │  │ 14:32:05 - Analyzing TechPro Solutions bid...                   │   ││
│  │  │ 14:32:08 - Scoring technical criterion T1...                    │   ││
│  │  │ 14:32:12 - Awarded 28/30 marks for spec compliance              │   ││
│  │  └─────────────────────────────────────────────────────────────────┘   ││
│  │                                                                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                          [RESULTS PAGE]
```

---

## 5. PAGE DESIGNS

### 5.1 LOGIN PAGE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │                             │  │                                     │  │
│  │                             │  │    🏛️ Government of India           │  │
│  │                             │  │                                     │  │
│  │    [HERO IMAGE]             │  │    Vendor Bid Evaluation System     │  │
│  │    Government Building      │  │    ─────────────────────────────    │  │
│  │    or                       │  │                                     │  │
│  │    Abstract Pattern         │  │    Welcome back! Please sign in     │  │
│  │    with Indian colors       │  │    to continue.                     │  │
│  │                             │  │                                     │  │
│  │                             │  │    ┌─────────────────────────────┐  │  │
│  │                             │  │    │ 📧 Email Address            │  │  │
│  │                             │  │    │ officer@gov.in              │  │  │
│  │                             │  │    └─────────────────────────────┘  │  │
│  │                             │  │                                     │  │
│  │                             │  │    ┌─────────────────────────────┐  │  │
│  │                             │  │    │ 🔒 Password                 │  │  │
│  │                             │  │    │ ••••••••••           👁️    │  │  │
│  │                             │  │    └─────────────────────────────┘  │  │
│  │                             │  │                                     │  │
│  │                             │  │    ☐ Remember me for 30 days       │  │
│  │                             │  │                                     │  │
│  │                             │  │    ┌─────────────────────────────┐  │  │
│  │                             │  │    │      🔐 Sign In             │  │  │
│  │                             │  │    └─────────────────────────────┘  │  │
│  │                             │  │                                     │  │
│  │                             │  │    Forgot password?                 │  │
│  │                             │  │                                     │  │
│  │                             │  │    ─────────── or ───────────       │  │
│  │                             │  │                                     │  │
│  │                             │  │    ┌─────────────────────────────┐  │  │
│  │                             │  │    │  🔑 Sign in with SSO        │  │  │
│  │                             │  │    └─────────────────────────────┘  │  │
│  │                             │  │                                     │  │
│  └─────────────────────────────┘  └─────────────────────────────────────┘  │
│                                                                             │
│  © 2024 Government of India | Privacy Policy | Terms of Service            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Login Page Specifications:**
- Split layout: 50% hero image, 50% login form
- Hero: Abstract geometric pattern with saffron/blue gradient
- Government emblem at top of form
- Email validation with @gov.in suggestion
- Password visibility toggle
- SSO option for government SSO integration
- Mobile: Stack vertically, hide hero image

---

### 5.2 DASHBOARD

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 🏛️ BidEval   📊 Dashboard  📋 Evaluations  📁 Documents  📈 Reports   │ │
│ │                                                    🔔 3  👤 Officer ▼  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  👋 Good morning, Procurement Officer!                                │  │
│  │  Here's your evaluation overview for December 2024                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌───────────┐  │
│  │  📊 ACTIVE      │ │  ✅ COMPLETED   │ │  ⏳ PENDING     │ │ 📄 TOTAL  │  │
│  │  Evaluations    │ │  This Month     │ │  Review         │ │ Vendors   │  │
│  │                 │ │                 │ │                 │ │           │  │
│  │     3           │ │     12          │ │     2           │ │    47     │  │
│  │   ↑ 2 new       │ │   ↑ 4 from Nov  │ │                 │ │           │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ └───────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────┐ ┌───────────────────────────┐│
│  │  🚀 QUICK ACTIONS                         │ │  📋 RECENT EVALUATIONS    ││
│  │  ─────────────────                        │ │  ─────────────────────    ││
│  │                                           │ │                           ││
│  │  ┌─────────────────────────────────────┐  │ │  ┌───────────────────────┐││
│  │  │  ➕ New Evaluation                  │  │ │  │ GEM/2024/B/12345      │││
│  │  │  Start a new bid evaluation         │  │ │  │ IT Hardware           │││
│  │  └─────────────────────────────────────┘  │ │  │ 🔄 In Progress (75%)  │││
│  │                                           │ │  │ 3 vendors • QCBS      │││
│  │  ┌─────────────────────────────────────┐  │ │  └───────────────────────┘││
│  │  │  📤 Upload Documents                │  │ │                           ││
│  │  │  Add tenders or bid documents       │  │ │  ┌───────────────────────┐││
│  │  └─────────────────────────────────────┘  │ │  │ CPPP/2024/IT/8821     │││
│  │                                           │ │  │ Software Services     │││
│  │  ┌─────────────────────────────────────┐  │ │  │ ✅ Completed          │││
│  │  │  📊 View Reports                    │  │ │  │ 5 vendors • L1        │││
│  │  │  Access evaluation reports          │  │ │  └───────────────────────┘││
│  │  └─────────────────────────────────────┘  │ │                           ││
│  │                                           │ │  ┌───────────────────────┐││
│  │                                           │ │  │ STATE/MH/2024/1001    │││
│  │                                           │ │  │ Road Construction     │││
│  │                                           │ │  │ ⏳ Pending Review     │││
│  │                                           │ │  │ 8 vendors • QCBS      │││
│  │                                           │ │  └───────────────────────┘││
│  └───────────────────────────────────────────┘ └───────────────────────────┘│
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  📈 EVALUATION ACTIVITY (Last 30 Days)                                │  │
│  │  ─────────────────────────────────────                                │  │
│  │                                                                       │  │
│  │     ▓▓▓▓▓▓▓▓                                                          │  │
│  │     ▓▓▓▓▓▓▓▓▓▓▓▓                                                      │  │
│  │     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                                │  │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                          │  │
│  │  ─────────────────────────────────────────────────────────────────    │  │
│  │  Week 1      Week 2       Week 3       Week 4                         │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## COMPLETE PAGE LIST

The full specification includes detailed wireframes for:

1. **Login Page** - Split layout with government branding
2. **Dashboard** - Overview cards, quick actions, recent evaluations
3. **New Evaluation Wizard**
   - Step 1: Tender Upload (drag-drop, AI extraction preview)
   - Step 2: Bids Upload (multi-file, auto-detection)
   - Step 3: Configuration (method selection, thresholds)
   - Step 4: Review & Confirm
   - Step 5: Processing (live progress, activity log)
4. **Evaluation Results**
   - Summary Tab (rankings, score distribution)
   - Compliance Tab (document checks, eligibility)
   - Technical Scores Tab (detailed justifications)
   - Financial Scores Tab (L1 calculation)
   - Comparison Matrix Tab (side-by-side)
   - Audit Trail Tab (complete decision log)
5. **Evaluations List** - Search, filter, status badges
6. **Settings Page** - Profile, preferences, admin sections

---

## 6. COMPONENT LIBRARY

### 6.1 Buttons

```
PRIMARY BUTTON:
┌─────────────────────────┐
│  🚀 Start Evaluation    │  bg: Primary-700, text: white
└─────────────────────────┘  hover: Primary-600, radius: 4px

SECONDARY BUTTON:
┌─────────────────────────┐
│     Cancel              │  bg: white, border: Gray-300
└─────────────────────────┘  text: Gray-700, hover: Gray-50

GHOST BUTTON:
┌─────────────────────────┐
│     View Details →      │  bg: transparent, text: Primary-500
└─────────────────────────┘  hover: Primary-100

DANGER BUTTON:
┌─────────────────────────┐
│     Delete              │  bg: Error-600, text: white
└─────────────────────────┘  hover: Error-700
```

### 6.2 Status Badges

```
✅ COMPLETE      bg: Success-100, text: Success-600, radius: full
🔄 IN PROGRESS   bg: Info-100, text: Info-600
⏳ PENDING       bg: Warning-100, text: Warning-600
❌ DISQUALIFIED  bg: Error-100, text: Error-600
✓ QUALIFIED     bg: Success-100, text: Success-600
```

### 6.3 Cards

```
EVALUATION CARD:
┌─────────────────────────────────────────────────────────┐
│  GEM/2024/B/12345                            ✅ Complete│
│  ───────────────────────────────────────────────────────│
│  IT Hardware Procurement                                │
│  Ministry of Electronics & IT                           │
│                                                         │
│  Method: QCBS  │  Vendors: 3  │  Winner: TechPro       │
│                                                         │
│  [View Results]  [Export PDF]  [···]                   │
└─────────────────────────────────────────────────────────┘
bg: white, border: Gray-200, radius: 8px, shadow: sm
```

---

## 7. RESPONSIVE BREAKPOINTS

```
MOBILE:      320px - 767px    (Single column, stacked layout)
TABLET:      768px - 1023px   (Two column, condensed nav)
DESKTOP:     1024px - 1439px  (Full layout, sidebar nav)
LARGE:       1440px+          (Wide layout, expanded content)

MOBILE ADAPTATIONS:
- Hamburger menu for navigation
- Full-width cards
- Stacked form fields
- Bottom sheet for modals
- Simplified tables (card view)
- Touch-friendly buttons (min 44px)
```

---

## 8. ACCESSIBILITY (WCAG 2.1 AA)

```
├── Color contrast ratio: minimum 4.5:1 for text
├── Focus indicators: visible outline on all interactive elements
├── Keyboard navigation: full keyboard accessibility
├── Screen reader: ARIA labels on all elements
├── Touch targets: minimum 44x44px
└── Error messages: associated with form fields
```

---

## 9. ANIMATIONS

```
TRANSITIONS:
├── Duration: 150ms-300ms for micro-interactions
├── Easing: ease-out for most transitions
├── Page transitions: 300ms fade
└── Modal: 200ms slide-up + fade

SPECIFIC ANIMATIONS:
├── Button hover: 150ms background color
├── Card hover: 200ms shadow + transform
├── Progress bar: 300ms width transition
├── Dropdown: 200ms slide-down + fade
└── Toast notifications: 300ms slide-in from right
```

---

**END OF UI/UX DESIGN SPECIFICATION**

This document provides comprehensive design specifications for implementing the Multi-Agent Vendor Bid Evaluation System in Google Stitch. All pages, components, and interactions are defined for a complete end-to-end user experience from login through evaluation completion.
