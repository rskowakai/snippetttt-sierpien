# Dockerfile z multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spacy models
RUN python -m spacy download en_core_web_sm
RUN python -m spacy download pl_core_news_sm


FROM python:3.11-slim

# Install system dependencies required for libraries like PyMuPDF and Tesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-pol \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages and spacy models from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /app /app

# Copy the application code
COPY ./app ./app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
