# Task 0010: Frontend Core Setup

## Overview
Configure the Next.js project structure, API client, state management with Zustand, TypeScript types, React Query, and Zod validation schemas.

## Subtasks

### 10.1 Configure Next.js project structure
- Set up App Router directory structure per Section 5.1
- Configure `next.config.js` with API proxy settings
- Create `tailwind.config.js` with design system colors
- Reference: Section 5.1 (Project Structure), Appendix A (Color Palette)

### 10.2 Set up API client
- Create `lib/api-client.ts` with Axios/fetch wrapper
- Configure base URL, interceptors for auth tokens
- Handle token refresh on 401 responses
- Reference: Section 5.1 (Frontend lib structure)

### 10.3 Set up Zustand stores
- Create `stores/auth-store.ts` with user state and auth actions
- Create `stores/evaluation-store.ts` with wizard and processing state per Section 5.4
- Create `stores/ui-store.ts` for UI state (sidebar, modals)
- Reference: Section 5.4 (State Management)

### 10.4 Create TypeScript type definitions
- Create `types/api.ts` with API response types
- Create `types/evaluation.ts` with evaluation-related types
- Create `types/vendor.ts` and `types/user.ts`
- Reference: Section 5.1 (Frontend types structure)

### 10.5 Set up React Query
- Configure QueryClient with default options
- Create query hooks for API endpoints
- Reference: Section 3.1 (Frontend Stack - TanStack Query)

### 10.6 Create Zod validation schemas
- Create `lib/validations.ts` with form validation schemas
- Include login, evaluation config, document upload schemas
- Reference: Section 5.1 (Frontend lib structure)

## References
- Section 3.1 (Frontend Stack)
- Section 5.1 (Project Structure)
- Section 5.4 (State Management)
- Appendix A (Color Palette)
