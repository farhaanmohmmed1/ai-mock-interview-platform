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


# Interview creation model
class InterviewCreate(BaseModel):
    interview_type: str
    resume_id: Optional[int] = None
    difficulty_level: Optional[str] = "medium"
    interview_mode: Optional[str] = "standard"


# Demo questions for different interview types
DEMO_QUESTIONS = {
    "upsc": [
        {"id": 1, "question_text": "What are the key challenges facing India's agricultural sector, and how can technology help address them?", "question_type": "analytical", "category": "economy", "difficulty": "medium", "order_number": 1},
        {"id": 2, "question_text": "Discuss the importance of ethics in public administration. Give examples.", "question_type": "opinion", "category": "ethics", "difficulty": "medium", "order_number": 2},
        {"id": 3, "question_text": "What is your understanding of the concept of 'cooperative federalism'?", "question_type": "conceptual", "category": "polity", "difficulty": "medium", "order_number": 3},
        {"id": 4, "question_text": "How can India balance economic development with environmental sustainability?",  "question_type": "analytical", "category": "environment", "difficulty": "medium", "order_number": 4},
        {"id": 5, "question_text": "What role does civil society play in strengthening democracy?", "question_type": "opinion", "category": "governance", "difficulty": "medium", "order_number": 5},
    ],
    "general": [
        {"id": 1, "question_text": "Tell me about yourself and your background.", "question_type": "introduction", "category": "personal", "difficulty": "easy", "order_number": 1},
        {"id": 2, "question_text": "What are your greatest strengths and weaknesses?", "question_type": "behavioral", "category": "self-assessment", "difficulty": "medium", "order_number": 2},
        {"id": 3, "question_text": "Where do you see yourself in 5 years?", "question_type": "career", "category": "goals", "difficulty": "medium", "order_number": 3},
        {"id": 4, "question_text": "Why should we hire you?", "question_type": "motivation", "category": "fit", "difficulty": "medium", "order_number": 4},
        {"id": 5, "question_text": "Do you have any questions for us?", "question_type": "closing", "category": "engagement", "difficulty": "easy", "order_number": 5},
    ],
    "technical": [
        {"id": 1, "question_text": "Explain the difference between a stack and a queue.", "question_type": "conceptual", "category": "data-structures", "difficulty": "easy", "order_number": 1},
        {"id": 2, "question_text": "What is the time complexity of binary search?", "question_type": "technical", "category": "algorithms", "difficulty": "medium", "order_number": 2},
        {"id": 3, "question_text": "Explain the concept of object-oriented programming.", "question_type": "conceptual", "category": "programming", "difficulty": "medium", "order_number": 3},
        {"id": 4, "question_text": "How would you design a URL shortening service?", "question_type": "system-design", "category": "design", "difficulty": "hard", "order_number": 4},
        {"id": 5, "question_text": "What is the difference between SQL and NoSQL databases?", "question_type": "conceptual", "category": "databases", "difficulty": "medium", "order_number": 5},
    ],
    "hr": [
        {"id": 1, "question_text": "Tell me about a time you faced a conflict at work.", "question_type": "behavioral", "category": "conflict", "difficulty": "medium", "order_number": 1},
        {"id": 2, "question_text": "How do you handle stress and pressure?", "question_type": "behavioral", "category": "stress", "difficulty": "medium", "order_number": 2},
        {"id": 3, "question_text": "Describe a situation where you showed leadership.", "question_type": "behavioral", "category": "leadership", "difficulty": "medium", "order_number": 3},
        {"id": 4, "question_text": "What motivates you in your work?", "question_type": "motivation", "category": "values", "difficulty": "easy", "order_number": 4},
        {"id": 5, "question_text": "How do you prioritize your tasks?", "question_type": "behavioral", "category": "organization", "difficulty": "medium", "order_number": 5},
    ]
}

# In-memory interview storage
interviews_db = {}
interview_counter = 0


@app.post("/api/interview/create")
async def create_interview(interview: InterviewCreate):
    """Create a new interview (demo mode)"""
    global interview_counter
    interview_counter += 1
    
    interview_type = interview.interview_type.lower()
    questions = DEMO_QUESTIONS.get(interview_type, DEMO_QUESTIONS["general"])
    
    interview_data = {
        "id": interview_counter,
        "interview_type": interview_type,
        "status": "in_progress",
        "difficulty_level": interview.difficulty_level,
        "total_questions": len(questions),
        "answered_questions": 0,
        "questions": questions,
        "current_question_index": 0
    }
    
    interviews_db[interview_counter] = interview_data
    
    return {
        "id": interview_counter,
        "interview_type": interview_type,
        "status": "in_progress",
        "difficulty_level": interview.difficulty_level,
        "total_questions": len(questions),
        "answered_questions": 0,
        "questions": questions
    }


@app.get("/api/interview/{interview_id}")
async def get_interview(interview_id: int):
    """Get interview details"""
    interview = interviews_db.get(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@app.post("/api/interview/{interview_id}/complete")
async def complete_interview(interview_id: int):
    """Complete an interview (demo mode)"""
    interview = interviews_db.get(interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview["status"] = "completed"
    
    # Return demo results
    return {
        "id": interview_id,
        "status": "completed",
        "overall_score": 75,
        "content_score": 78,
        "clarity_score": 72,
        "fluency_score": 80,
        "confidence_score": 70,
        "feedback": "Great job! You demonstrated good knowledge and communication skills.",
        "weak_areas": ["Time management", "Specific examples"],
        "strong_areas": ["Clear communication", "Confident delivery"],
        "recommendations": [
            {"text": "Practice with more specific examples from your experience"},
            {"text": "Work on managing your response time"}
        ]
    }


@app.delete("/api/interview/{interview_id}")
async def delete_interview(interview_id: int):
    """Delete/cancel an interview"""
    if interview_id in interviews_db:
        del interviews_db[interview_id]
    return {"message": "Interview cancelled"}


class TextResponse(BaseModel):
    question_id: int
    text_response: str
    thinking_time_seconds: Optional[float] = 0


@app.post("/api/evaluation/submit-text")
async def submit_text_response(response: TextResponse):
    """Submit text response (demo mode - returns mock evaluation)"""
    return {
        "response_id": response.question_id,
        "message": "Response recorded",
        "scores": {
            "content_score": 75,
            "relevance_score": 80,
            "clarity_score": 78
        }
    }


@app.get("/api/test")
async def test_endpoint():
    return {"test": "success", "message": "API is working!"}

