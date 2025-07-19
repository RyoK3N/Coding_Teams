# AgentForge - Multi-Agent Software Generation Platform

## Overview

AgentForge is a full-stack web application that provides a platform for multi-agent software generation. Users can submit software development requests through prompts, and the system orchestrates multiple specialized AI agents to collaboratively generate code, documentation, and tests. The platform features real-time monitoring of agent activities, live log streaming, artifact management, and a comprehensive code editor interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **UI Library**: Shadcn/UI components built on Radix UI primitives
- **Styling**: Tailwind CSS with CSS variables for theming
- **State Management**: React hooks and context for local state, TanStack Query for server state
- **Routing**: Wouter for lightweight client-side routing
- **Build Tool**: Vite with custom configuration for development and production

### Backend Architecture
- **Runtime**: Node.js with Express.js server
- **Database**: PostgreSQL with Drizzle ORM
- **Database Provider**: Neon serverless PostgreSQL
- **Real-time Communication**: WebSocket integration for live updates
- **API Pattern**: RESTful endpoints with WebSocket subscriptions

### Data Layer
- **ORM**: Drizzle with schema definitions in TypeScript
- **Database Schema**: 
  - `users` - User authentication and management
  - `sessions` - Project sessions with prompts and metadata
  - `agents` - Individual agent instances with status tracking
  - `agentEvents` - Event log for all agent activities
  - `artifacts` - Generated code files and documentation
- **Migration Strategy**: Schema-first with Drizzle Kit for migrations

## Key Components

### Session Management
- **Project Sessions**: Each software request creates a unique session with tracking
- **Session Status**: Tracks progress through pending → running → completed/failed states
- **Metrics Collection**: Aggregates task counts, completion times, and success rates

### Agent Orchestration
- **Multi-Agent System**: Principal Engineer, Python Specialist, Test Specialist
- **Status Tracking**: Real-time monitoring of agent states (idle, running, succeeded, failed)
- **Progress Monitoring**: Granular progress tracking for each agent's tasks

### Real-time Communication
- **WebSocket Service**: Custom WebSocket implementation for bidirectional communication
- **Event Streaming**: Structured events for task updates, logs, and artifact creation
- **Session Subscriptions**: Clients subscribe to specific session updates

### UI Components
- **Agent Cards**: Visual representation of each agent with logs and artifacts
- **File Explorer**: Hierarchical view of generated project structure
- **Code Editor**: Monaco-style editor with syntax highlighting and diff capabilities
- **Metrics Dashboard**: Real-time analytics and progress visualization

## Data Flow

### Session Creation Flow
1. User submits prompt via form with validation
2. Backend creates session record with unique ID
3. Default agents are automatically created for the session
4. WebSocket subscription established for real-time updates
5. User redirected to session monitoring page

### Agent Event Flow
1. Agents emit structured events during execution
2. Events stored in database with sequence numbers
3. WebSocket broadcasts events to subscribed clients
4. Frontend updates UI components reactively
5. Metrics aggregated and displayed in real-time

### Artifact Management Flow
1. Agents generate code files and documentation
2. Artifacts stored with metadata (file path, content, language)
3. File explorer builds hierarchical tree structure
4. Code editor provides syntax highlighting and editing capabilities
5. Download functionality packages all artifacts

## External Dependencies

### Core Dependencies
- **@neondatabase/serverless**: Serverless PostgreSQL client
- **drizzle-orm**: Type-safe ORM with PostgreSQL dialect
- **@tanstack/react-query**: Server state management and caching
- **ws**: WebSocket implementation for Node.js
- **wouter**: Lightweight React router

### UI Dependencies
- **@radix-ui/***: Comprehensive set of accessible UI primitives
- **tailwindcss**: Utility-first CSS framework
- **lucide-react**: Icon library with consistent design
- **class-variance-authority**: Utility for conditional CSS classes

### Development Dependencies
- **vite**: Fast build tool with HMR support
- **tsx**: TypeScript execution for Node.js
- **@hookform/resolvers**: Form validation with Zod integration

## Deployment Strategy

### Development Environment
- **Local Development**: Vite dev server with Express backend
- **Hot Module Replacement**: Instant updates during development
- **Database**: Neon serverless PostgreSQL with connection pooling

### Production Build
- **Frontend**: Vite builds optimized React bundle
- **Backend**: ESBuild compiles TypeScript to ESM
- **Asset Serving**: Express serves static files in production
- **Environment Variables**: DATABASE_URL required for database connection

### Database Management
- **Schema Migrations**: Drizzle Kit handles schema changes
- **Connection Pooling**: Neon serverless handles connection management
- **Session Storage**: PostgreSQL sessions with connect-pg-simple

### Monitoring and Logging
- **Request Logging**: Express middleware logs API requests with timing
- **Error Handling**: Centralized error handling with proper status codes
- **WebSocket Monitoring**: Connection state tracking and reconnection logic

The architecture prioritizes real-time user experience, type safety, and scalable agent orchestration while maintaining clean separation of concerns between frontend, backend, and data layers.