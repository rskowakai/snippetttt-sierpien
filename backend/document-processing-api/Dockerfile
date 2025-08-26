# --- Build Stage ---
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies for whisper
RUN apt-get update && apt-get install -y --no-install-recommends gcc ffmpeg

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Final Stage ---
FROM python:3.11-slim

WORKDIR /usr/src/app

# Install runtime dependencies for whisper and python-magic
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libmagic1 && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

COPY --from=builder /usr/src/app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/*

COPY ./backend/app /usr/src/app/app

# Change ownership
RUN chown -R app:app /usr/src/app
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
