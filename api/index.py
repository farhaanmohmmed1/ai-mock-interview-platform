"""
Vercel serverless entrypoint - Minimal standalone API
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import os

# Create minimal FastAPI app for Vercel
app = FastAPI(
    title="AI Mock Interview Platform API",
    description="API for AI-powered mock interviews",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "AI Mock Interview Platform API",
        "version": "1.0.0",
        "status": "operational",
        "mode": "lightweight",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "deployment": "vercel",
        "mode": "lightweight"
    }


@app.get("/api/status")
async def api_status():
    return {
        "api": "online",
        "features": {
            "auth": "available",
            "interviews": "requires full deployment",
            "resume_parsing": "requires full deployment",
            "ai_evaluation": "requires full deployment"
        },
        "message": "This is a lightweight deployment. For full AI features, deploy on Railway or Render."
    }


# Simple test endpoint
@app.get("/api/test")
async def test_endpoint():
    return {"test": "success", "message": "API is working!"}
