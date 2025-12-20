# GovProcure Frontend

Multi-Agent Vendor Bid Evaluation System - Frontend Application

## Technology Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Real-time**: Socket.io Client
- **Charts**: Recharts

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Configure environment variables:

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

3. Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                      # Next.js app directory
│   ├── (auth)/              # Authentication pages (grouped route)
│   │   ├── login/           # Login page
│   │   ├── register/        # Registration page
│   │   └── forgot-password/ # Password reset page
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page (redirects)
│   ├── providers.tsx        # React Query provider
│   └── globals.css          # Global styles
├── components/              # React components
│   └── ui/                  # shadcn/ui components
│       ├── button.tsx
│       ├── input.tsx
│       ├── card.tsx
│       ├── form.tsx
│       ├── label.tsx
│       └── alert.tsx
├── hooks/                   # Custom React hooks
│   ├── use-auth.ts         # Authentication hook
│   ├── use-evaluations.ts  # Evaluations data hook
│   └── use-websocket.ts    # WebSocket hook
├── lib/                     # Utility libraries
│   ├── api.ts              # Axios instance with interceptors
│   ├── auth.ts             # Auth utilities (token management)
│   └── utils.ts            # Helper functions
├── stores/                  # Zustand state stores
│   ├── auth-store.ts       # Authentication state
│   └── evaluation-store.ts # Evaluation state
├── types/                   # TypeScript type definitions
│   ├── api.ts              # API types
│   └── index.ts            # Type exports
└── package.json            # Dependencies and scripts
```

## Core Features

### Authentication

- **Login**: Email/password authentication with JWT tokens
- **Registration**: User account creation with validation
- **Password Reset**: Forgot password functionality
- **Token Management**: Automatic token refresh on 401 errors
- **Protected Routes**: Route guards for authenticated pages

### State Management

- **Zustand Stores**: Lightweight state management
  - `auth-store`: User authentication state
  - `evaluation-store`: Evaluation data and operations
- **React Query**: Server state caching and synchronization
- **Persistent Storage**: Auth state persisted to localStorage

### API Integration

- **Axios Instance**: Configured with base URL and interceptors
- **Request Interceptor**: Auto-inject auth tokens
- **Response Interceptor**: Handle errors and token refresh
- **Type Safety**: Full TypeScript support for API calls

### Real-time Updates

- **WebSocket Hook**: Connect to evaluation processing updates
- **Auto-reconnect**: Exponential backoff reconnection strategy
- **Event Handlers**: Progress, logs, agent updates, completion

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types

## Authentication Flow

1. User enters credentials on login page
2. Frontend sends POST request to `/api/auth/login`
3. Backend validates and returns JWT token + user data
4. Token stored in localStorage via `setToken()`
5. Axios interceptor adds token to all subsequent requests
6. On 401 error, attempt token refresh automatically
7. If refresh fails, redirect to login page

## Type Safety

All API interactions are fully typed:

- Request/Response types in `types/api.ts`
- Form validation with Zod schemas
- TypeScript strict mode enabled
- Path aliases configured (`@/*`)

## Styling

- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality component library
- **CSS Variables**: Theme customization via CSS variables
- **Dark Mode**: Support for dark mode (configured)
- **Responsive**: Mobile-first responsive design

## Best Practices

- TypeScript strict mode for type safety
- Zod validation for forms and API data
- React Hook Form for performant forms
- Error boundaries for error handling
- Loading states for async operations
- Proper error messages for users
- Token refresh for seamless auth
- WebSocket reconnection handling

## Next Steps

To extend the frontend:

1. Add dashboard pages in `app/(dashboard)/`
2. Create evaluation pages for creating/viewing evaluations
3. Add vendor management pages
4. Implement results visualization with Recharts
5. Add real-time processing status displays
6. Create reports and comparison views

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API base URL
- `NEXT_PUBLIC_WS_URL`: WebSocket server URL

## License

Proprietary - GovProcure
