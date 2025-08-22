# LegalTech Pro - Secure Document Management Platform

## Overview

LegalTech Pro is a comprehensive legal document management platform built with a modern TypeScript stack. The application provides secure document handling with envelope encryption, AI-powered document analysis, and real-time collaboration features for legal professionals. It combines a React frontend with Supabase backend services to deliver enterprise-grade security and functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The client-side application is built with **React 18** using **TypeScript** and **Vite** as the build tool. The UI framework leverages **Tailwind CSS** with **shadcn/ui** components for a professional legal interface. Key architectural decisions include:

- **State Management**: Uses **TanStack Query** for server state management and caching, eliminating the need for complex client-side state
- **Routing**: Implements **Wouter** for lightweight client-side routing with minimal bundle impact
- **Form Handling**: **React Hook Form** with **Zod** validation provides type-safe form management
- **Component Architecture**: Follows atomic design principles with reusable UI components in the `/components/ui` directory

### Backend Architecture
The backend follows a **serverless-first approach** using **Supabase** as the primary backend service:

- **Database**: **PostgreSQL** with **Drizzle ORM** for type-safe database operations and migrations
- **Authentication**: Supabase Auth handles user management with row-level security policies
- **API Layer**: Minimal Express.js server primarily for development, with core functionality handled by Supabase Edge Functions
- **Edge Functions**: Custom serverless functions for document processing and AI operations written in **Deno/TypeScript**

### Data Storage Solutions
Multi-tier storage strategy designed for legal document security:

- **Primary Database**: PostgreSQL with comprehensive schema including profiles, cases, documents, and processing queues
- **File Storage**: Supabase Storage with separate buckets for temporary uploads and encrypted document storage
- **Caching Layer**: TanStack Query provides intelligent client-side caching with automatic invalidation

### Authentication and Authorization
Enterprise-grade security implementation:

- **User Authentication**: Supabase Auth with email/password and potential OAuth providers
- **Role-Based Access Control**: Four user roles (admin, lawyer, paralegal, client) with granular permissions
- **Database Security**: Row-level security policies enforce data isolation between organizations
- **Session Management**: Automatic session handling with secure token refresh

### Document Security Architecture
Advanced security features for legal document protection:

- **Envelope Encryption**: Document processor Edge Function implements KMS-based envelope encryption
- **Processing Queue**: Asynchronous document processing with status tracking and progress updates
- **Storage Isolation**: Separate storage buckets for unencrypted uploads and encrypted final storage
- **Real-time Notifications**: Supabase Realtime subscriptions for processing status updates

## External Dependencies

### Core Backend Services
- **Supabase**: Primary backend-as-a-service providing database, authentication, storage, and Edge Functions
- **Neon Database**: PostgreSQL database provider (configured in Drizzle config)

### AI and ML Services
- **OpenAI API**: Primary AI provider for document analysis and RAG operations
- **Google Gemini API**: Alternative AI provider with automatic failover capability
- **Vector Search**: Supabase's built-in vector search for document similarity and RAG queries

### Development and Build Tools
- **Vite**: Frontend build tool and development server
- **Drizzle Kit**: Database migration and schema management
- **ESBuild**: Server-side TypeScript compilation for production builds

### UI and Styling Dependencies
- **Radix UI**: Headless component primitives for complex UI interactions
- **Tailwind CSS**: Utility-first CSS framework with custom legal industry color scheme
- **Lucide React**: Icon library optimized for professional interfaces

### File Handling and Processing
- **React Dropzone**: Drag-and-drop file upload functionality
- **Date-fns**: Date manipulation and formatting for legal document timestamps

### Real-time Features
- **Supabase Realtime**: WebSocket-based real-time subscriptions for live updates
- **Connect-PG-Simple**: Session store for server-side session management (legacy compatibility)