FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies (YARA requires C compiler)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install .

FROM python:3.11-slim

WORKDIR /app

# Copy python packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run migrations and start app
CMD ["bash", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
