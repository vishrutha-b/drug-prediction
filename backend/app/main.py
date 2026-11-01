import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api import auth, prediction, dashboard
from .db.database import engine, Base
from .db import models

# Professional Initialization: Auto-migrate schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IntelliInteraction API",
    description="Professional DDI Severity Prediction using Hybrid SemanticFusionNet",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Robust CORS Configuration for HIPAA/Clinical compliance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ROUTES (Prioritized) ---
app.include_router(auth.router, prefix="/api/v1")
app.include_router(prediction.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "IntelliInteraction Backend"}

# --- UNIFIED FRONTEND SERVING (NEXT.JS + TS) ---
# Mount the _next directory containing the frontend build chunks
app.mount("/_next", StaticFiles(directory="static/_next"), name="next_assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # 1. Attempt to serve the path directly from static/ (e.g., /favicon.ico)
    static_file_path = os.path.join("static", full_path)
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)

    # 2. Support Next.js static routes (e.g., /dashboard -> static/dashboard.html)
    html_path = f"static/{full_path.strip('/')}.html"
    if os.path.isfile(html_path):
        return FileResponse(html_path)

    # 3. Fallback to index.html for React Router / Client-side routing
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
