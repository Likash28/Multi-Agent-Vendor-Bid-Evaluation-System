# Task 0015: Frontend Processing View

## Overview
Create the processing page with workflow steps, live log, progress indicator, and WebSocket integration for real-time updates.

## Subtasks

### 15.1 Create processing page
- Create `app/(dashboard)/evaluations/[id]/processing/page.tsx`
- Display overall progress bar
- Reference: Section 5.2.4 (Processing Page)

### 15.2 Create workflow steps component
- Create `components/evaluation/processing/workflow-steps.tsx`
- Display vertical stepper with all evaluation stages
- Show step status (pending, active, completed)
- Reference: Section 5.2.4 (Workflow Steps)

### 15.3 Create live log component
- Create `components/evaluation/processing/live-log.tsx`
- Display terminal-style log with timestamps and agent messages
- Auto-scroll to latest entries
- Reference: Section 5.2.4 (Live System Log)

### 15.4 Create progress indicator component
- Create `components/evaluation/processing/progress-indicator.tsx`
- Display remaining time estimate
- Reference: Section 5.2.4 (Estimated Time)

### 15.5 Create WebSocket hook
- Create `hooks/use-websocket.ts` for real-time updates
- Connect to `/ws/evaluation/{id}` endpoint
- Handle progress messages and update UI state
- Reference: Section 8.4 (WebSocket - Frontend integration)

## References
- Section 5.2.4 (Processing Page)
- Section 5.2.4 (Workflow Steps)
- Section 5.2.4 (Live System Log)
- Section 5.2.4 (Estimated Time)
- Section 8.4 (WebSocket - Frontend integration)
