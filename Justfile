set dotenv-load := true

default: run

PORT := env("PORT")

# Run FastAPI using uv, respecting the PORT from .env
run:
    @echo "🚀 Starting FastAPI on port {{PORT}}"
    uv run uvicorn phinder_api.main:app --host 0.0.0.0 --port {{PORT}}

# Build Docker image, injecting the PORT into build args
docker-build:
    @echo "🐳 Building Docker image..."
    docker build --build-arg PORT={{PORT}} -t phinder-api .

# Run Docker container with env file and port binding
docker-run:
    @echo "🐳 Running Docker container on port {{PORT}}"
    docker run --env-file .env -p {{PORT}}:{{PORT}} phinder-api

# Rebuild & restart container (clean dev loop)
docker-restart: docker-build docker-run

# Kill process using the API port (default 8080 from .env)
kill-port:
    @echo "🔪 Killing process on port {{PORT}}..."
    @PID=$(sudo netstat -tulpn 2>/dev/null | grep ":{{PORT}}" | awk '{ print $7 }' | cut -d/ -f1); \
    if [ -n "$PID" ]; then \
      sudo kill -9 $PID && echo "✅ Port {{PORT}} freed (PID $PID)."; \
    else \
        echo "ℹ️ No process is using port $PORT."; \
    fi

# Format and Lint
format:
  @echo "🎨 Formatting and linting..."
  @uv run ruff check . --fix

