# 🐳 Professional Docker Deployment Guide

This guide describes how to containerize the **IntelliInteraction Clinical Platform** for production-grade institutional environments.

## 🚀 Recommended: Docker Compose
The easiest way to build and run the entire platform (Frontend + Backend) is using Docker Compose.

### 1. Build and Start
Run the following in the project root:
```powershell
docker compose up --build -d
```

### 2. Verify Deployment
Access the unified platform at:
- **Dashboard**: [http://localhost:8080](http://localhost:8080)
- **API Docs**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **Health Check**: [http://localhost:8080/health](http://localhost:8080/health)

---

## 🏗️ Standalone Image Build
If you need to "excrete" (build) a standalone image for a container registry (e.g., Docker Hub, AWS ECR):

### 1. Build the Standalone Image
```powershell
docker build -t intelliinteraction:v2.0.0 .
```

### 2. Run the Standalone Container
```powershell
docker run -d -p 8000:8000 \
  -v ${PWD}/data:/app/data \
  --name clinical-app \
  intelliinteraction:v2.0.0
```

---

## 🛡️ Production-Grade Security Features
The IntelliInteraction Docker image is optimized for HIPAA-compliant environments:
- **Non-Root Execution**: The service runs as `appuser`, preventing container breakout attacks.
- **Monolithic Efficiency**: A 100% static frontend is served directly by the FastAPI high-performance event loop.
- **Persistence Layer**: The clinical database is isolated in a persistent volume at `/app/data`.
- **Health Monitoring**: Built-in Docker health diagnostics monitor the clinical logic every 30 seconds.

## 🛑 Management Commands
- **Stop Services**: `docker compose stop`
- **Down & Clean**: `docker compose down`
- **View Logs**: `docker compose logs -f`
