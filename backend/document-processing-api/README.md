# Document Processing API

This is an advanced, microservice-based application for processing and searching documents, built with FastAPI and Celery.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Async Processing:** Celery
- **Relational Database:** PostgreSQL 15+ (with SQLAlchemy)
- **Vector Database:** Weaviate
- **Message Queue / Cache:** Redis
- **Containerization:** Docker, Docker Compose
- **Reverse Proxy / Load Balancer:** Nginx
- **AI Models:** Sentence-Transformers (for embeddings), Google Gemini (for summarization), OpenAI Whisper (for transcription)

## Project Structure

The project follows the principles of Clean Architecture with a clear separation of concerns:

- `app/api`: FastAPI routers and endpoints.
- `app/services`: Business logic layer.
- `app/models`: SQLAlchemy database models.
- `app/schemas`: Pydantic data validation schemas.
- `app/workers`: Asynchronous Celery tasks.
- `app/core`: Core components like security, config, and middleware.
- `app/database.py`: Database session management.
- `app/celery_app.py`: Celery application setup.

## Getting Started (Development)

1.  **Create Environment File:**
    Copy `.env.example` to `.env` and fill in the required values, especially `SECRET_KEY` and `GOOGLE_API_KEY`.
    \`\`\`bash
    cp .env.example .env
    \`\`\`

2.  **Build and Run with Docker Compose:**
    \`\`\`bash
    make build
    make up
    \`\`\`

3.  **Apply Database Migrations:**
    You will need to set up Alembic first. Once configured, you can run:
    \`\`\`bash
    # To create a new migration
    make makemigrations m="Your migration message"
    # To apply migrations
    make migrate
    \`\`\`

4.  **Access the API:**
    - API Docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
    - Health Check: [http://localhost:8000/health](http://localhost:8000/health)

## Running in Production

The `docker-compose.prod.yml` file is configured for a production-like deployment with multiple replicas and services.

\`\`\`bash
make build-prod
make up-prod
\`\`\`

Remember to configure Nginx with your domain and SSL certificates.
