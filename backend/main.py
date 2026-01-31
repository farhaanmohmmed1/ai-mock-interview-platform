from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path

# Add parent directory to path (OS-agnostic)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.core.config import settings
from backend.core.database import engine, Base
from backend.api import auth, interview, resume, evaluation, dashboard

# Check if AI modules are available
try:
    import ai_modules
    AI_MODULES_AVAILABLE = True
except ImportError:
    AI_MODULES_AVAILABLE = False

# Check if proctoring is available
try:
    from backend.api import proctoring
    PROCTORING_AVAILABLE = True
except ImportError:
    PROCTORING_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("Starting AI Interview Platform...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created")
    
    # Create necessary directories (OS-agnostic paths)
    data_dirs = ["uploads", "recordings", "videos", "models"]
    for dir_name in data_dirs:
        (BASE_DIR / "data" / dir_name).mkdir(parents=True, exist_ok=True)
    print("[OK] Data directories created")
    
    yield
    
    # Shutdown
    print("Shutting down AI Interview Platform...")


# Initialize FastAPI app
app = FastAPI(
    title="AI Mock Interview Platform",
    description="Adaptive interview platform with NLP, speech, and emotion analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# Include proctoring router if available
if PROCTORING_AVAILABLE:
    app.include_router(proctoring.router, prefix="/api", tags=["Proctoring"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Mock Interview Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_modules": "loaded" if AI_MODULES_AVAILABLE else "unavailable (lightweight mode)",
        "proctoring": "available" if PROCTORING_AVAILABLE else "unavailable"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG_MODE
    )
