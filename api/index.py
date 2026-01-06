"""
Vercel serverless entrypoint - Minimal standalone API
"""

from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import random

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

# ============== DEMO DATA ==============

# Sample interview history for demo users
DEMO_INTERVIEW_HISTORY = [
    {
        "id": 101,
        "interview_type": "technical",
        "status": "completed",
        "difficulty_level": "medium",
        "total_questions": 5,
        "answered_questions": 5,
        "overall_score": 82,
        "content_score": 85,
        "clarity_score": 78,
        "fluency_score": 84,
        "confidence_score": 80,
        "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=7)).isoformat(),
        "duration_minutes": 18.5
    },
    {
        "id": 102,
        "interview_type": "general",
        "status": "completed",
        "difficulty_level": "easy",
        "total_questions": 5,
        "answered_questions": 5,
        "overall_score": 75,
        "content_score": 72,
        "clarity_score": 80,
        "fluency_score": 76,
        "confidence_score": 72,
        "created_at": (datetime.now() - timedelta(days=5)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=5)).isoformat(),
        "duration_minutes": 15.2
    },
    {
        "id": 103,
        "interview_type": "hr",
        "status": "completed",
        "difficulty_level": "medium",
        "total_questions": 5,
        "answered_questions": 5,
        "overall_score": 88,
        "content_score": 90,
        "clarity_score": 85,
        "fluency_score": 88,
        "confidence_score": 89,
        "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=3)).isoformat(),
        "duration_minutes": 20.1
    },
    {
        "id": 104,
        "interview_type": "upsc",
        "status": "completed",
        "difficulty_level": "hard",
        "total_questions": 5,
        "answered_questions": 5,
        "overall_score": 71,
        "content_score": 74,
        "clarity_score": 68,
        "fluency_score": 72,
        "confidence_score": 70,
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "completed_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "duration_minutes": 25.3
    }
]

# Sample resumes for demo
DEMO_RESUMES = [
    {
        "id": 1,
        "filename": "john_doe_resume.pdf",
        "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Machine Learning", "AWS"],
        "experience_years": 3.5,
        "education": {
            "degree": "B.Tech in Computer Science",
            "institution": "IIT Delhi",
            "year": 2021
        },
        "projects": [
            {"name": "E-commerce Platform", "description": "Built a full-stack e-commerce site"},
            {"name": "ML Chatbot", "description": "Developed an NLP-based customer service bot"}
        ],
        "uploaded_at": (datetime.now() - timedelta(days=10)).isoformat(),
        "is_active": True
    }
]

# Sample detailed results for completed interviews
DEMO_RESULTS = {
    101: {
        "id": 101,
        "interview_type": "technical",
        "status": "completed",
        "overall_score": 82,
        "content_score": 85,
        "clarity_score": 78,
        "fluency_score": 84,
        "confidence_score": 80,
        "emotion_score": 76,
        "duration_minutes": 18.5,
        "total_questions": 5,
        "answered_questions": 5,
        "feedback": "Excellent technical knowledge demonstrated. Your explanations of data structures were clear and accurate. Consider providing more real-world examples to strengthen your answers.",
        "weak_areas": ["System design depth", "Time complexity analysis"],
        "strong_areas": ["Core programming concepts", "Problem-solving approach", "Code explanation"],
        "recommendations": [
            {"text": "Practice more system design questions to improve architectural thinking"},
            {"text": "Review Big-O notation and practice analyzing algorithm complexity"},
            {"text": "Great job on explaining your thought process - keep it up!"}
        ],
        "questions_summary": [
            {
                "question": "Explain the difference between a stack and a queue.",
                "score": 90,
                "feedback": "Excellent explanation with good examples",
                "user_answer": "A stack follows LIFO (Last In First Out) principle where the last element added is the first one to be removed, like a stack of plates. A queue follows FIFO (First In First Out) where the first element added is the first to be removed, like a line at a ticket counter.",
                "ideal_answer": "Stack: LIFO structure with push/pop operations, O(1) time. Used in function calls, undo operations. Queue: FIFO structure with enqueue/dequeue, O(1) time. Used in BFS, task scheduling, buffering.",
                "voice_clarity": 88,
                "concept_clarity": 92
            },
            {
                "question": "What is the time complexity of binary search?",
                "score": 75,
                "feedback": "Correct answer but could explain the derivation better",
                "user_answer": "Binary search has O(log n) time complexity because we divide the array in half each time.",
                "ideal_answer": "O(log n) because each comparison eliminates half the remaining elements. For n elements, we need log₂(n) comparisons. Space complexity is O(1) for iterative, O(log n) for recursive due to call stack.",
                "voice_clarity": 82,
                "concept_clarity": 70
            },
            {
                "question": "Explain the concept of object-oriented programming.",
                "score": 88,
                "feedback": "Comprehensive coverage of OOP principles",
                "user_answer": "OOP is a programming paradigm based on objects containing data and methods. The four pillars are encapsulation, inheritance, polymorphism, and abstraction. It helps in code reusability and organization.",
                "ideal_answer": "OOP organizes code into objects. Four pillars: 1) Encapsulation - bundling data with methods, 2) Inheritance - creating new classes from existing ones, 3) Polymorphism - same interface different implementations, 4) Abstraction - hiding complex implementation details.",
                "voice_clarity": 85,
                "concept_clarity": 90
            },
            {
                "question": "How would you design a URL shortening service?",
                "score": 72,
                "feedback": "Good start but missing scalability considerations",
                "user_answer": "I would create a database to store original URLs with short codes. Generate unique codes using base62 encoding. When someone accesses the short URL, look up and redirect to the original.",
                "ideal_answer": "Key components: 1) Hash/encode long URLs to short codes (base62), 2) Database for mapping (NoSQL for scale), 3) Cache layer (Redis) for popular URLs, 4) Load balancer, 5) Analytics tracking. Consider: collision handling, expiration, rate limiting, 301 vs 302 redirects.",
                "voice_clarity": 78,
                "concept_clarity": 68
            },
            {
                "question": "What is the difference between SQL and NoSQL databases?",
                "score": 85,
                "feedback": "Clear comparison with practical use cases",
                "user_answer": "SQL databases are relational with fixed schemas and use structured query language. They're good for complex queries and transactions. NoSQL databases are non-relational, flexible schema, and better for large-scale distributed data.",
                "ideal_answer": "SQL: Relational, ACID compliant, fixed schema, vertical scaling, good for complex joins. Examples: PostgreSQL, MySQL. NoSQL: Non-relational, BASE, flexible schema, horizontal scaling, types include document (MongoDB), key-value (Redis), column (Cassandra), graph (Neo4j).",
                "voice_clarity": 86,
                "concept_clarity": 84
            }
        ]
    },
    102: {
        "id": 102,
        "interview_type": "general",
        "status": "completed",
        "overall_score": 75,
        "content_score": 72,
        "clarity_score": 80,
        "fluency_score": 76,
        "confidence_score": 72,
        "emotion_score": 78,
        "duration_minutes": 15.2,
        "total_questions": 5,
        "answered_questions": 5,
        "feedback": "Good communication skills and confident delivery. Your self-introduction was well-structured. Work on providing more specific examples from your experience.",
        "weak_areas": ["Specific examples", "Quantifiable achievements"],
        "strong_areas": ["Communication clarity", "Professional demeanor", "Positive attitude"],
        "recommendations": [
            {"text": "Prepare 3-4 specific stories using the STAR method"},
            {"text": "Include numbers and metrics when discussing achievements"},
            {"text": "Research the company more to tailor your answers"}
        ],
        "questions_summary": [
            {
                "question": "Tell me about yourself.",
                "score": 78,
                "feedback": "Good structure but could be more concise",
                "user_answer": "I'm a software developer with 3 years of experience. I graduated from XYZ University and have worked on various web development projects. I enjoy problem-solving and learning new technologies.",
                "ideal_answer": "Present-Past-Future format: Current role and key achievement, relevant background and skills, why you're excited about this opportunity. Keep it under 2 minutes with specific accomplishments.",
                "voice_clarity": 82,
                "concept_clarity": 75
            },
            {
                "question": "What are your greatest strengths and weaknesses?",
                "score": 70,
                "feedback": "Be more specific with examples",
                "user_answer": "My strength is problem-solving and I work well under pressure. My weakness is sometimes I focus too much on details.",
                "ideal_answer": "Strengths: Give specific example with impact (e.g., 'My analytical skills helped reduce bugs by 30%'). Weakness: Show self-awareness and improvement steps (e.g., 'I used to struggle with delegation, now I use task management tools and regular check-ins').",
                "voice_clarity": 78,
                "concept_clarity": 65
            },
            {
                "question": "Where do you see yourself in 5 years?",
                "score": 75,
                "feedback": "Show more alignment with company goals",
                "user_answer": "In 5 years, I see myself in a senior technical role, leading projects and mentoring junior developers. I want to continue growing my skills.",
                "ideal_answer": "Show ambition aligned with company growth. Mention skills you want to develop, leadership aspirations, and how you'd contribute to the organization's goals. Research company's career paths.",
                "voice_clarity": 80,
                "concept_clarity": 72
            },
            {
                "question": "Why should we hire you?",
                "score": 72,
                "feedback": "Highlight unique value proposition",
                "user_answer": "I have the skills and experience you're looking for. I'm a hard worker and quick learner. I'm passionate about technology.",
                "ideal_answer": "Connect your unique skills to their specific needs. Use format: 'Based on the job description, you need X. I have proven experience in X, demonstrated by [specific achievement]. I'd bring [unique value].'",
                "voice_clarity": 75,
                "concept_clarity": 68
            },
            {
                "question": "Do you have any questions for us?",
                "score": 80,
                "feedback": "Good thoughtful questions asked",
                "user_answer": "What does a typical day look like? What are the growth opportunities? How would you describe the team culture?",
                "ideal_answer": "Ask insightful questions about: team structure, success metrics, challenges the team faces, company culture, growth opportunities. Avoid salary/benefits questions in first round.",
                "voice_clarity": 84,
                "concept_clarity": 78
            }
        ]
    },
    103: {
        "id": 103,
        "interview_type": "hr",
        "status": "completed",
        "overall_score": 88,
        "content_score": 90,
        "clarity_score": 85,
        "fluency_score": 88,
        "confidence_score": 89,
        "emotion_score": 92,
        "duration_minutes": 20.1,
        "total_questions": 5,
        "answered_questions": 5,
        "feedback": "Outstanding performance! Your behavioral answers were well-structured using the STAR method. Excellent emotional intelligence and self-awareness demonstrated.",
        "weak_areas": ["Could elaborate more on lessons learned"],
        "strong_areas": ["STAR method usage", "Self-awareness", "Conflict resolution", "Leadership examples"],
        "recommendations": [
            {"text": "Continue using the STAR method - it's working great!"},
            {"text": "Add more reflection on what you learned from each experience"},
            {"text": "Excellent job showing growth mindset"}
        ],
        "questions_summary": [
            {
                "question": "Tell me about a time you faced a conflict at work.",
                "score": 92,
                "feedback": "Excellent example with clear resolution",
                "user_answer": "In my previous role, a colleague and I disagreed on the project approach. I initiated a one-on-one discussion, listened to their concerns, and we found a compromise that incorporated both ideas. The project was delivered successfully.",
                "ideal_answer": "Use STAR method: Situation (brief context), Task (your responsibility), Action (specific steps you took), Result (positive outcome with metrics if possible). Show emotional intelligence and collaboration.",
                "voice_clarity": 90,
                "concept_clarity": 94
            },
            {
                "question": "How do you handle stress and pressure?",
                "score": 85,
                "feedback": "Good strategies mentioned",
                "user_answer": "I prioritize tasks, break large projects into smaller milestones, and maintain open communication with stakeholders. I also practice regular exercise and mindfulness to stay balanced.",
                "ideal_answer": "Mention specific techniques: prioritization methods (Eisenhower matrix), breaking tasks down, time management, communication strategies. Include both professional and personal stress management approaches.",
                "voice_clarity": 88,
                "concept_clarity": 82
            },
            {
                "question": "Describe a situation where you showed leadership.",
                "score": 90,
                "feedback": "Strong leadership example",
                "user_answer": "When our team lead was on leave, I stepped up to coordinate a critical release. I organized daily standups, delegated tasks based on team strengths, and ensured we delivered on time. The team appreciated the clear communication.",
                "ideal_answer": "Show initiative, delegation, communication, and results. Leadership isn't just about titles - show how you influenced others, made decisions, and achieved team goals.",
                "voice_clarity": 92,
                "concept_clarity": 88
            },
            {
                "question": "What motivates you in your work?",
                "score": 88,
                "feedback": "Authentic and aligned with role",
                "user_answer": "I'm motivated by solving complex problems and seeing the impact of my work. I enjoy learning new technologies and collaborating with talented people. Making users' lives easier through good software gives me satisfaction.",
                "ideal_answer": "Be authentic but align with the role. Mention intrinsic motivators (learning, impact, growth) over extrinsic (money, titles). Show passion for the field and company's mission.",
                "voice_clarity": 86,
                "concept_clarity": 90
            },
            {
                "question": "How do you prioritize your tasks?",
                "score": 85,
                "feedback": "Practical and organized approach",
                "user_answer": "I use a combination of urgency and importance to prioritize. I start each day reviewing my task list, identify the top 3 priorities, and block focused time for deep work. I also keep stakeholders updated on progress.",
                "ideal_answer": "Mention specific frameworks (Eisenhower matrix, MoSCoW), tools you use, how you handle competing priorities, and communication with stakeholders. Show flexibility and adaptability.",
                "voice_clarity": 84,
                "concept_clarity": 86
            }
        ]
    },
    104: {
        "id": 104,
        "interview_type": "upsc",
        "status": "completed",
        "overall_score": 71,
        "content_score": 74,
        "clarity_score": 68,
        "fluency_score": 72,
        "confidence_score": 70,
        "emotion_score": 65,
        "duration_minutes": 25.3,
        "total_questions": 5,
        "answered_questions": 5,
        "feedback": "Good foundational knowledge of governance and ethics. Your analytical skills are developing well. Focus on presenting balanced perspectives and supporting arguments with current examples.",
        "weak_areas": ["Current affairs integration", "Multiple perspectives", "Time management"],
        "strong_areas": ["Constitutional knowledge", "Ethical reasoning", "Structured thinking"],
        "recommendations": [
            {"text": "Read newspaper editorials daily for current affairs"},
            {"text": "Practice presenting multiple viewpoints on issues"},
            {"text": "Work on time management - some answers were too long"},
            {"text": "Include more recent examples and case studies"}
        ],
        "questions_summary": [
            {
                "question": "What are the key challenges facing India's agricultural sector?",
                "score": 75,
                "feedback": "Good points but missing recent policy changes",
                "user_answer": "Key challenges include fragmented land holdings, dependence on monsoons, lack of modern technology, poor storage infrastructure, and middlemen exploitation. Government schemes like PM-KISAN are trying to address income issues.",
                "ideal_answer": "Cover: 1) Structural issues (land fragmentation, small holdings), 2) Infrastructure (irrigation, storage, cold chains), 3) Market access (MSP issues, APMC reforms), 4) Climate change impact, 5) Technology adoption. Mention recent reforms like farm laws, e-NAM, PM-KISAN with critical analysis.",
                "voice_clarity": 72,
                "concept_clarity": 78
            },
            {
                "question": "Discuss the importance of ethics in public administration.",
                "score": 78,
                "feedback": "Strong ethical framework presented",
                "user_answer": "Ethics in public administration ensures accountability, transparency, and public trust. Civil servants must uphold integrity, impartiality, and dedication to public service. The Code of Conduct for civil servants outlines these principles.",
                "ideal_answer": "Discuss: 1) Foundational values (integrity, objectivity, impartiality), 2) Constitutional morality, 3) Nolan Committee principles, 4) Recent examples of ethical dilemmas, 5) Role of RTI and Lokpal, 6) Work culture and organizational ethics. Use case studies.",
                "voice_clarity": 75,
                "concept_clarity": 80
            },
            {
                "question": "What is your understanding of cooperative federalism?",
                "score": 72,
                "feedback": "Correct concept but needs more examples",
                "user_answer": "Cooperative federalism is where the Centre and States work together for national development rather than in conflict. GST Council and NITI Aayog are examples. It balances federal structure with unified governance.",
                "ideal_answer": "Define cooperative vs competitive federalism. Examples: GST Council (consensus-based), NITI Aayog replacing Planning Commission, Inter-State Council, Finance Commission. Discuss Article 263, recent tensions (GST compensation, farm laws), and need for cooperative federalism in diverse India.",
                "voice_clarity": 70,
                "concept_clarity": 74
            },
            {
                "question": "How can India balance economic development with environmental sustainability?",
                "score": 65,
                "feedback": "Need more balanced perspective",
                "user_answer": "India needs both development and environment protection. We can promote renewable energy, implement stricter pollution norms, and encourage sustainable industries. The Paris Agreement commits India to clean energy targets.",
                "ideal_answer": "Discuss: 1) Green growth model, 2) NDCs under Paris Agreement, 3) National Action Plan on Climate Change, 4) Circular economy, 5) Environmental impact assessment reforms, 6) Case studies (renewable energy success, forest rights). Present multiple perspectives - development needs vs environmental limits.",
                "voice_clarity": 65,
                "concept_clarity": 66
            },
            {
                "question": "What role does civil society play in strengthening democracy?",
                "score": 68,
                "feedback": "Good but could include international comparisons",
                "user_answer": "Civil society acts as a watchdog, raises awareness on issues, and holds government accountable. NGOs, media, and citizen groups contribute to participatory democracy. RTI movement is an example of civil society impact.",
                "ideal_answer": "Roles: 1) Advocacy and awareness, 2) Service delivery gap filling, 3) Policy input and monitoring, 4) Promoting participation, 5) Protecting rights. Examples: RTI movement, environmental activism, women's rights. Discuss challenges: foreign funding regulations, FCRA, space for dissent. International comparisons helpful.",
                "voice_clarity": 68,
                "concept_clarity": 70
            }
        ]
    }
}
            {"question": "What motivates you in your work?", "score": 88, "feedback": "Authentic and aligned with role"},
            {"question": "How do you prioritize your tasks?", "score": 85, "feedback": "Practical and organized approach"}
        ]
    },
    104: {
        "id": 104,
        "interview_type": "upsc",
        "status": "completed",
        "overall_score": 71,
        "content_score": 74,
        "clarity_score": 68,
        "fluency_score": 72,
        "confidence_score": 70,
        "emotion_score": 65,
        "duration_minutes": 25.3,
        "feedback": "Good foundational knowledge of governance and ethics. Your analytical skills are developing well. Focus on presenting balanced perspectives and supporting arguments with current examples.",
        "weak_areas": ["Current affairs integration", "Multiple perspectives", "Time management"],
        "strong_areas": ["Constitutional knowledge", "Ethical reasoning", "Structured thinking"],
        "recommendations": [
            {"text": "Read editorials daily to improve current affairs knowledge"},
            {"text": "Practice presenting multiple viewpoints on issues"},
            {"text": "Work on time management - some answers were too long"},
            {"text": "Include more recent examples and case studies"}
        ],
        "questions_summary": [
            {"question": "What are the key challenges facing India's agricultural sector?", "score": 75, "feedback": "Good points but missing recent policy changes"},
            {"question": "Discuss the importance of ethics in public administration.", "score": 78, "feedback": "Strong ethical framework presented"},
            {"question": "What is your understanding of cooperative federalism?", "score": 72, "feedback": "Correct concept but needs more examples"},
            {"question": "How can India balance economic development with environmental sustainability?", "score": 65, "feedback": "Need more balanced perspective"},
            {"question": "What role does civil society play in strengthening democracy?", "score": 68, "feedback": "Good but could include international comparisons"}
        ]
    }
}

# In-memory storage for demo (resets on cold start)
users_db = {}
tokens_db = {}

# Initialize with a demo user
users_db["demo_user"] = {
    "id": 1,
    "username": "demo_user",
    "email": "demo@example.com",
    "full_name": "Demo User",
    "password_hash": hashlib.sha256("demo123".encode()).hexdigest()
}


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
        "total_interviews": 4,
        "average_score": 79,
        "improvement_rate": 12.5,
        "interviews_this_week": 2,
        "total_practice_time": 79,  # minutes
        "best_category": "HR",
        "needs_improvement": "UPSC"
    }


@app.get("/api/interview/")
async def list_interviews():
    """List interviews (returns demo history)"""
    return DEMO_INTERVIEW_HISTORY


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
    # Check demo results first
    if interview_id in DEMO_RESULTS:
        return DEMO_RESULTS[interview_id]
    
    # Check active interviews
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
    
    # Generate varied demo results based on interview type
    interview_type = interview.get("interview_type", "general")
    base_score = random.randint(70, 90)
    
    # Store completed interview with results
    result = {
        "id": interview_id,
        "interview_type": interview_type,
        "status": "completed",
        "overall_score": base_score,
        "content_score": base_score + random.randint(-5, 5),
        "clarity_score": base_score + random.randint(-8, 8),
        "fluency_score": base_score + random.randint(-5, 5),
        "confidence_score": base_score + random.randint(-10, 5),
        "emotion_score": base_score + random.randint(-5, 10),
        "duration_minutes": round(random.uniform(12, 25), 1),
        "feedback": get_demo_feedback(interview_type, base_score),
        "weak_areas": get_demo_weak_areas(interview_type),
        "strong_areas": get_demo_strong_areas(interview_type),
        "recommendations": get_demo_recommendations(interview_type),
        "questions_summary": get_demo_questions_summary(interview.get("questions", []), base_score)
    }
    
    # Store for later retrieval
    DEMO_RESULTS[interview_id] = result
    
    return result


def get_demo_feedback(interview_type: str, score: int) -> str:
    feedbacks = {
        "technical": f"Good technical foundation demonstrated (Score: {score}%). Your problem-solving approach shows promise. Continue practicing system design and algorithm optimization.",
        "general": f"Solid interview performance (Score: {score}%). Your communication was clear and professional. Work on adding more specific examples to strengthen your answers.",
        "hr": f"Strong behavioral responses (Score: {score}%). You showed good self-awareness and emotional intelligence. Keep using the STAR method for structured answers.",
        "upsc": f"Decent analytical thinking (Score: {score}%). Your knowledge of governance is developing well. Focus on integrating current affairs and presenting balanced perspectives."
    }
    return feedbacks.get(interview_type, feedbacks["general"])


def get_demo_weak_areas(interview_type: str) -> List[str]:
    areas = {
        "technical": ["System design scalability", "Time complexity analysis", "Edge case handling"],
        "general": ["Specific examples", "Quantifiable achievements", "Company research"],
        "hr": ["Lessons learned reflection", "Failure examples", "Long-term vision"],
        "upsc": ["Current affairs integration", "Multiple perspectives", "Time management"]
    }
    return random.sample(areas.get(interview_type, areas["general"]), 2)


def get_demo_strong_areas(interview_type: str) -> List[str]:
    areas = {
        "technical": ["Core concepts", "Problem-solving", "Code explanation", "Logical thinking"],
        "general": ["Communication", "Professional demeanor", "Enthusiasm", "Preparation"],
        "hr": ["STAR method", "Self-awareness", "Positive attitude", "Team examples"],
        "upsc": ["Constitutional knowledge", "Ethical reasoning", "Structured answers", "Articulation"]
    }
    return random.sample(areas.get(interview_type, areas["general"]), 3)


def get_demo_recommendations(interview_type: str) -> List[dict]:
    recs = {
        "technical": [
            {"text": "Practice system design questions on platforms like LeetCode"},
            {"text": "Review data structures and algorithms fundamentals"},
            {"text": "Work on explaining your thought process while coding"}
        ],
        "general": [
            {"text": "Prepare 5 strong stories using the STAR method"},
            {"text": "Research the company's recent news and projects"},
            {"text": "Practice your elevator pitch until it feels natural"}
        ],
        "hr": [
            {"text": "Prepare examples of failures and what you learned"},
            {"text": "Practice active listening during conversations"},
            {"text": "Develop questions that show genuine interest"}
        ],
        "upsc": [
            {"text": "Read newspaper editorials daily for current affairs"},
            {"text": "Practice answer writing with time constraints"},
            {"text": "Study multiple perspectives on key issues"}
        ]
    }
    return recs.get(interview_type, recs["general"])


def get_demo_questions_summary(questions: List[dict], base_score: int) -> List[dict]:
    summaries = []
    feedbacks = [
        "Good explanation with clear examples",
        "Correct approach but could be more detailed",
        "Strong answer showing deep understanding",
        "Adequate response, consider adding more context",
        "Well-structured answer with practical insights"
    ]
    for i, q in enumerate(questions):
        summaries.append({
            "question": q.get("question_text", f"Question {i+1}"),
            "score": min(100, max(50, base_score + random.randint(-15, 15))),
            "feedback": feedbacks[i % len(feedbacks)]
        })
    return summaries


@app.delete("/api/interview/{interview_id}")
async def delete_interview(interview_id: int):
    """Delete/cancel an interview"""
    if interview_id in interviews_db:
        del interviews_db[interview_id]
    return {"message": "Interview cancelled"}


# ============== RESUME ENDPOINTS ==============

@app.get("/api/resume/list")
async def list_resumes():
    """List uploaded resumes (demo data)"""
    return DEMO_RESUMES


@app.post("/api/resume/upload")
async def upload_resume():
    """Upload resume (demo mode - returns sample parsed data)"""
    return {
        "message": "Resume uploaded successfully (Demo Mode)",
        "resume": {
            "id": 2,
            "filename": "uploaded_resume.pdf",
            "skills": ["Python", "JavaScript", "React", "SQL", "Git", "Docker"],
            "experience_years": 2.5,
            "education": {
                "degree": "B.Sc in Computer Science",
                "institution": "Sample University",
                "year": 2022
            },
            "projects": [
                {"name": "Web Application", "description": "Full-stack web application project"}
            ],
            "uploaded_at": datetime.now().isoformat(),
            "is_active": True
        }
    }


@app.get("/api/resume/{resume_id}")
async def get_resume(resume_id: int):
    """Get resume details"""
    for resume in DEMO_RESUMES:
        if resume["id"] == resume_id:
            return resume
    raise HTTPException(status_code=404, detail="Resume not found")


@app.delete("/api/resume/{resume_id}")
async def delete_resume(resume_id: int):
    """Delete resume"""
    return {"message": "Resume deleted successfully"}


# ============== PROFILE ENDPOINTS ==============

@app.get("/api/profile")
async def get_profile():
    """Get user profile with stats"""
    return {
        "user": {
            "id": 1,
            "username": "demo_user",
            "email": "demo@example.com",
            "full_name": "Demo User",
            "joined_date": (datetime.now() - timedelta(days=30)).isoformat()
        },
        "stats": {
            "total_interviews": 4,
            "average_score": 79,
            "best_score": 88,
            "total_practice_hours": 1.3,
            "interviews_by_type": {
                "technical": 1,
                "general": 1,
                "hr": 1,
                "upsc": 1
            },
            "score_trend": [65, 72, 75, 82, 88, 79],  # Last 6 interviews
            "skills_assessed": ["Communication", "Technical Knowledge", "Problem Solving", "Leadership", "Ethics"]
        },
        "achievements": [
            {"name": "First Interview", "description": "Completed your first mock interview", "earned": True},
            {"name": "Quick Learner", "description": "Improved score by 10% in a week", "earned": True},
            {"name": "Consistent", "description": "Practiced 3 days in a row", "earned": True},
            {"name": "High Scorer", "description": "Score above 85% in any interview", "earned": True},
            {"name": "All Rounder", "description": "Complete all 4 interview types", "earned": True}
        ]
    }


# ============== ANALYTICS ENDPOINTS ==============

@app.get("/api/analytics/progress")
async def get_progress_analytics():
    """Get progress analytics over time"""
    return {
        "weekly_scores": [
            {"week": "Week 1", "score": 65},
            {"week": "Week 2", "score": 72},
            {"week": "Week 3", "score": 78},
            {"week": "Week 4", "score": 82}
        ],
        "category_scores": {
            "technical": 82,
            "general": 75,
            "hr": 88,
            "upsc": 71
        },
        "skill_breakdown": {
            "content": 80,
            "clarity": 78,
            "fluency": 82,
            "confidence": 76,
            "emotion": 79
        },
        "improvement_areas": [
            {"area": "Time Management", "current": 70, "target": 85},
            {"area": "Specific Examples", "current": 72, "target": 85},
            {"area": "Current Affairs", "current": 65, "target": 80}
        ],
        "practice_streak": 3,
        "total_questions_answered": 20
    }


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

