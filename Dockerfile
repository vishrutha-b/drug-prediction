# --- STAGE 1: Frontend Build ---
FROM node:21-slim AS frontend-build
WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./
RUN npm install

# Copy source and build (Next.js export)
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Final Monolithic Image ---
FROM python:3.12-slim
WORKDIR /app

# Set production environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False
ENV DATABASE_URL=sqlite:///./data/drug_interaction.db
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for institutional security compliance
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Create data directory and fix permissions
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Copy built frontend assets from Stage 1 into the backend's static directory
# FastAPI serves these as configured in app/main.py
COPY --from=frontend-build /app/frontend/out /app/static
RUN chown -R appuser:appgroup /app/static

# Copy trained FAERS ML model artifacts
COPY ml/models/ /app/ml/models/
RUN chown -R appuser:appgroup /app/ml

# Switch to non-root user
USER appuser

# Expose the single port (8000) for both Backend and Frontend
EXPOSE 8000

# Health check to ensure service is up
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the unified FastAPI server
# We use uvicorn with workers for better production performance
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
