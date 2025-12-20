# Task 0014: Frontend Evaluation Wizard

## Overview
Create the complete 4-step evaluation wizard including upload tender, upload vendor bids, evaluation configuration, review & confirm, and related hooks.

## Subtasks

### 14.1 Create evaluation wizard page
- Create `app/(dashboard)/evaluations/new/page.tsx`
- Implement 4-step wizard flow with step indicator
- Reference: Section 5.2.3 (New Evaluation Wizard)

### 14.2 Create step indicator component
- Create `components/evaluation/wizard/step-indicator.tsx`
- Display steps 1-4 with active/completed states
- Reference: Section 5.2.3 (Step 1 - Step indicator)

### 14.3 Implement Step 1: Upload Tender
- Create `components/evaluation/wizard/upload-tender.tsx`
- Add file upload zone (PDF, DOCX, TXT - max 50MB)
- Display file preview and metadata
- Show auto-extraction status
- Reference: Section 5.2.3 (Step 1: Upload Tender)

### 14.4 Implement Step 2: Upload Vendor Bids
- Create `components/evaluation/wizard/upload-bids.tsx`
- Add multi-file drag & drop zone
- Display uploaded bids list with vendor names
- Show status indicators (Ready, Processing)
- Reference: Section 5.2.3 (Step 2: Upload Vendor Bids)

### 14.5 Implement Step 3: Evaluation Configuration
- Create `components/evaluation/wizard/evaluation-config.tsx`
- Add evaluation method selection (L1, QCBS, Two-Stage)
- Add weight configuration sliders (Technical vs Financial)
- Add qualification threshold input
- Add advanced settings checkboxes (AI compliance, justifications, cartel detection)
- Reference: Section 5.2.3 (Step 3: Evaluation Configuration)

### 14.6 Implement Step 4: Review & Confirm
- Create `components/evaluation/wizard/review-confirm.tsx`
- Display tender and configuration summary
- Show estimated processing time
- Add irreversible action warning
- Implement "Start Evaluation" button
- Reference: Section 5.2.3 (Step 4: Review & Confirm)

### 14.7 Create evaluation hook
- Create `hooks/use-evaluation.ts` with wizard state management
- Implement tender upload, bid management, config update actions
- Reference: Section 5.4 (State Management - EvaluationState)

### 14.8 Create file upload hook
- Create `hooks/use-file-upload.ts` for file handling
- Implement upload progress, validation, error handling
- Reference: Section 5.1 (Frontend hooks)

## References
- Section 5.1 (Frontend hooks)
- Section 5.2.3 (New Evaluation Wizard)
- Section 5.4 (State Management)
