# Task 0013: Frontend Dashboard

## Overview
Create the dashboard layout, page, and all dashboard components including stats cards, quick actions, activity chart, and recent evaluations.

## Subtasks

### 13.1 Create dashboard layout
- Create `app/(dashboard)/layout.tsx` with header, sidebar
- Implement protected route with auth check
- Reference: Section 5.1 (Dashboard group routes)

### 13.2 Implement dashboard page
- Create `app/(dashboard)/dashboard/page.tsx`
- Add welcome header with user greeting
- Reference: Section 5.2.2 (Dashboard Page)

### 13.3 Create dashboard stat cards component
- Create `components/dashboard/stats-cards.tsx`
- Display Active Evaluations, Completed, Pending Review, Total Vendors
- Reference: Section 5.2.2 (Stats Cards)

### 13.4 Create quick actions component
- Create `components/dashboard/quick-actions.tsx`
- Add buttons: New Evaluation, Upload Documents, View Reports
- Reference: Section 5.2.2 (Quick Actions)

### 13.5 Create activity chart component
- Create `components/dashboard/activity-chart.tsx` using Recharts
- Display 30-day activity bar chart
- Reference: Section 5.2.2 (Activity Chart)

### 13.6 Create recent evaluations component
- Create `components/dashboard/recent-evaluations.tsx`
- Display table with Reference ID, Title, Date, Status, Actions
- Reference: Section 5.2.2 (Recent Evaluations)

## References
- Section 5.1 (Dashboard group routes)
- Section 5.2.2 (Dashboard Page)
- Section 5.2.2 (Stats Cards)
- Section 5.2.2 (Quick Actions)
- Section 5.2.2 (Activity Chart)
- Section 5.2.2 (Recent Evaluations)
