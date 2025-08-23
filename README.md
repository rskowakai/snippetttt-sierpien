# LegalTech Pro - Secure Document Management Platform

## Overview

LegalTech Pro is a sophisticated, secure document management and analysis platform designed for legal professionals. It provides a robust environment for handling sensitive legal documents, leveraging AI for intelligent insights, and facilitating real-time collaboration. The platform is built with a modern, full-stack TypeScript architecture, combining a sleek frontend with a powerful and secure backend.

## Features

-   **Secure Document Handling**: Implements end-to-end security with envelope encryption. Documents are encrypted at rest using AES-256-GCM, with keys managed by a Key Encryption Key (KEK), ensuring that sensitive information is always protected.
-   **AI-Powered Document Analysis**: Utilizes a Retrieval-Augmented Generation (RAG) pipeline to answer natural language questions about your documents. The system can leverage either OpenAI or Google Gemini models to provide context-aware answers.
-   **Vector Similarity Search**: Finds relevant document chunks using vector embeddings for more accurate AI-powered analysis. It includes a fallback to traditional text search.
-   **Real-time Processing Queue**: Tracks the status of document uploads and processing in real-time, providing users with instant feedback.
-   **Modern User Interface**: A responsive and intuitive user interface built with React, Shadcn/UI, and Tailwind CSS.
-   **Scalable Architecture**: The hybrid backend,
    combining a lightweight Node.js server with Supabase's managed services,
    offers both flexibility and scalability.

## Architecture

LegalTech Pro uses a hybrid backend architecture to deliver a secure and scalable service.

-   **Frontend**: A modern web application built with **React** (using Vite) and written in **TypeScript**. The UI is styled with **Tailwind CSS** and **Shadcn/UI**.
-   **Web Server**: A lightweight **Express.js** server that serves the frontend application and handles health checks. In a production environment, this server is responsible for serving the built static files.
-   **Backend-as-a-Service (BaaS)**: **Supabase** is used for the core backend functionality:
    -   **Authentication**: Manages user sign-up, sign-in, and session handling.
    -   **Database**: A **PostgreSQL** database for storing application data, managed with the **Drizzle ORM**.
    -   **Storage**: Manages file uploads, with separate buckets for temporary, and encrypted documents.
    -   **Edge Functions**: Serverless functions written in Deno/TypeScript for handling intensive tasks.

### Edge Functions

-   `document-processor`: This function is triggered after a document is uploaded. It performs envelope encryption on the file, stores the encrypted version in a secure bucket, and manages the encryption keys.
-   `ai-rag-handler`: This function handles AI-powered queries. It takes a user's question, generates a vector embedding, searches for relevant document chunks in the database, and then uses a large language model (OpenAI or Gemini) to generate an answer based on the retrieved context.

## Technology Stack

-   **Frontend**: React, TypeScript, Vite, Wouter, Tailwind CSS, Shadcn/UI
-   **Backend**: Node.js, Express.js, Deno
-   **Database**: PostgreSQL, Drizzle ORM
-   **BaaS**: Supabase (Auth, Storage, Edge Functions)
-   **AI**: OpenAI (GPT-3.5-turbo), Google Gemini
-   **Deployment**: Can be deployed to any platform that supports Node.js and Docker (for Supabase).

## Getting Started

### Prerequisites

-   Node.js (v18 or later)
-   npm
-   Git
-   A Supabase project.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rrsartgit/snippetttt-sierpien.git
    cd snippetttt-sierpien
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the root of the project and add the following variables. You can get the Supabase-related keys from your Supabase project dashboard.

    ```env
    # Supabase credentials (client-side)
    VITE_SUPABASE_URL="YOUR_SUPABASE_URL"
    VITE_SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"

    # Supabase credentials (server-side)
    SUPABASE_URL="YOUR_SUPABASE_URL"
    SUPABASE_SERVICE_ROLE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY"

    # Database connection string from Supabase
    DATABASE_URL="YOUR_SUPABASE_DATABASE_CONNECTION_STRING"

    # AI Provider API Keys (at least one is required)
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

    # Key for encrypting data encryption keys (DEKs)
    KEK_KEY="a-secure-random-string-of-at-least-32-characters"

    # Port for the local development server
    PORT=5000
    ```
    **Note:** You also need to set these environment variables in your Supabase project settings for the Edge Functions to use them.

4. **Set up the database:**
    This command will push the Drizzle schema to your Supabase database.
    ```bash
    npm run db:push
    ```

5.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5000`.

## Scripts

-   `npm run dev`: Starts the development server with hot-reloading.
-   `npm run build`: Builds the frontend and backend for production.
-   `npm run start`: Starts the application in production mode.
-   `npm run db:push`: Pushes schema changes to the database using Drizzle Kit.
-   `npm run check`: Runs the TypeScript compiler to check for type errors.

## Project Structure

```
.
├── client/         # Frontend React application
├── server/         # Express.js server
├── supabase/       # Supabase configuration and edge functions
│   ├── functions/
│   │   ├── ai-rag-handler/
│   │   └── document-processor/
│   └── ...
├── shared/         # Shared code, like Drizzle schema
├── public/         # Static assets
└── ...
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your proposed changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
