FROM python:3.13-slim AS base

WORKDIR /app

# Install uv (fast dependency resolver)
RUN pip install uv

# Copy dep files first to leverage cache
COPY pyproject.toml uv.lock* .python-version ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy your application code
COPY phinder_api ./phinder_api
COPY .env .env

# Expose port from .env at runtime (optional, useful for docs)
ARG PORT
ENV PORT=${PORT}

# Start FastAPI using uvicorn, binding to PORT env
CMD uv run uvicorn phinder_api.main:app --host 0.0.0.0 --port ${PORT}
