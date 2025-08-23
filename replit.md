# LegalTech Pro - Secure Document Management Platform

## Overview

LegalTech Pro is a comprehensive legal document management platform built with a modern TypeScript stack. The application provides secure document handling with envelope encryption, AI-powered document analysis, and real-time collaboration tools.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The client-side application is built with **React 18** using **TypeScript** and **Vite** as the build tool. The UI framework leverages **Tailwind CSS** with **shadcn/ui** components for a professional look and feel.

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

### Instructions for Running the Application

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rrsartgit/snippetttt-sierpien.git
   cd snippetttt-sierpien
   ```

2. **Install Dependencies**:
   Ensure you have Node.js installed. Then, run:
   ```bash
   npm install
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory with the following keys:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `DATABASE_URL`

4. **Run the Development Server**:
   To start the frontend and backend, use:
   ```bash
   npm run dev
   ```

5. **Access the Application**:
   Open your browser and navigate to `http://localhost:3000`.

6. **Run Migrations**:
   If database migrations are required (for Drizzle ORM), execute:
   ```bash
   npm run migrate
   ```
