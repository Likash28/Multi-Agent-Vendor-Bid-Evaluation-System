# Task 0012: Frontend Authentication Pages

## Overview
Create authentication layout, login page, and authentication hook.

## Subtasks

### 12.1 Create auth layout
- Create `app/(auth)/layout.tsx` with split layout (branding + form)
- Reference: Section 5.2.1 (Login Page)

### 12.2 Implement login page
- Create `app/(auth)/login/page.tsx`
- Add email/password form with validation
- Implement "Remember Me" checkbox
- Add forgot password link
- Handle JWT token storage
- Reference: Section 5.2.1 (Login Page)

### 12.3 Create auth hook
- Create `hooks/use-auth.ts` for authentication logic
- Implement login, logout, token refresh
- Manage auth state persistence
- Reference: Section 5.1 (Frontend hooks)

## References
- Section 5.1 (Frontend hooks)
- Section 5.2.1 (Login Page)
