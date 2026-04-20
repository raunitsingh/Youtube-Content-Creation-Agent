# Build:  docker build -t youtube-agent .
# Run:    docker run -p 8080:8080 --env-file .env youtube-agent

FROM python:3.11-slim

# Keeps Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install dependencies first (layer cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app.py        .
COPY flask_app.py  .

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8080

# Gunicorn: 2 workers, 120s timeout for long Groq responses
CMD ["gunicorn", "flask_app:app", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]