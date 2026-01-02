"""
Vercel serverless entrypoint - Minimal standalone API
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import hashlib
import secrets

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

# In-memory storage for demo (resets on cold start)
users_db = {}
tokens_db = {}


# Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None


# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    return secrets.token_urlsafe(32)


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
            "interviews": "demo mode",
            "resume_parsing": "requires full deployment",
            "ai_evaluation": "requires full deployment"
        },
        "message": "This is a lightweight deployment. For full AI features, deploy on Railway or Render."
    }


@app.post("/api/auth/register")
async def register(user: UserRegister):
    """Register a new user"""
    # Check if username exists
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    for u in users_db.values():
        if u["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create user
    user_id = len(users_db) + 1
    users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password_hash": hash_password(user.password)
    }
    
    # Generate token
    token = generate_token()
    tokens_db[token] = user.username
    
    return {
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }


@app.post("/api/auth/login")
async def login(credentials: UserLogin):
    """Login user"""
    user = users_db.get(credentials.username)
    
    if not user or user["password_hash"] != hash_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate token
    token = generate_token()
    tokens_db[token] = credentials.username
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"]
        }
    }


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics (demo data)"""
    return {
        "total_interviews": 0,
        "average_score": 0,
        "improvement_rate": 0,
        "interviews_this_week": 0
    }


@app.get("/api/interview/")
async def list_interviews():
    """List interviews (demo - empty)"""
    return []


@app.get("/api/test")
async def test_endpoint():
    return {"test": "success", "message": "API is working!"}

