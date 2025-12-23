from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.core.database import get_db
from backend.models import User, Interview, Question, Response, Resume
from backend.api.auth import get_current_user
from ai_modules.nlp.question_generator import QuestionGenerator
from ai_modules.adaptive.adaptive_system import AdaptiveSystem

router = APIRouter()
question_generator = QuestionGenerator()
adaptive_system = AdaptiveSystem()


class InterviewCreate(BaseModel):
    interview_type: str  # general, technical, hr
    resume_id: Optional[int] = None
    difficulty_level: Optional[str] = "medium"
    interview_mode: Optional[str] = "standard"  # standard or upsc


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: str
    category: Optional[str]
    difficulty: str
    order_number: int
    
    class Config:
        from_attributes = True


class InterviewResponse(BaseModel):
    id: int
    interview_type: str
    status: str
    difficulty_level: str
    total_questions: int
    answered_questions: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    overall_score: Optional[float]
    duration_minutes: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class InterviewDetailResponse(InterviewResponse):
    questions: List[QuestionResponse] = []
    content_score: Optional[float] = None
    clarity_score: Optional[float] = None
    fluency_score: Optional[float] = None
    confidence_score: Optional[float] = None
    emotion_score: Optional[float] = None
    feedback: Optional[str] = None
    weak_areas: Optional[List[dict]] = None
    strong_areas: Optional[List[dict]] = None
    recommendations: Optional[List[dict]] = None


class StartInterviewResponse(BaseModel):
    interview_id: int
    questions: List[QuestionResponse]
    message: str


@router.post("/create", response_model=StartInterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and start a new interview"""
    # Validate interview type
    valid_types = ["general", "technical", "hr", "upsc"]
    if interview_data.interview_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interview type. Must be one of: {', '.join(valid_types)}"
        )
    
    # For UPSC type, automatically set mode to upsc
    if interview_data.interview_type == "upsc":
        interview_data.interview_mode = "upsc"
    
    # Get resume if technical interview
    resume = None
    if interview_data.interview_type == "technical":
        if not interview_data.resume_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume ID required for technical interview"
            )
        
        resume = db.query(Resume).filter(
            Resume.id == interview_data.resume_id,
            Resume.user_id == current_user.id
        ).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
    
    # Use provided difficulty level or get adaptive one
    difficulty = interview_data.difficulty_level or adaptive_system.get_recommended_difficulty(
        user_id=current_user.id,
        interview_type=interview_data.interview_type,
        db=db
    )
    
    # Get interview mode
    interview_mode = interview_data.interview_mode or "standard"
    
    # Create interview
    new_interview = Interview(
        user_id=current_user.id,
        resume_id=interview_data.resume_id,
        interview_type=interview_data.interview_type,
        status="in_progress",
        difficulty_level=difficulty,
        started_at=datetime.utcnow()
    )
    
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    
    # Generate questions
    questions_data = question_generator.generate_questions(
        interview_type=interview_data.interview_type,
        difficulty=difficulty,
        interview_mode=interview_mode,
        resume_data=resume.parsed_data if resume else None,
        skills=resume.skills if resume else None,
        user_id=current_user.id,
        db=db
    )
    
    # Save questions
    questions = []
    for idx, q_data in enumerate(questions_data):
        question = Question(
            interview_id=new_interview.id,
            question_text=q_data["text"],
            question_type=q_data["type"],
            category=q_data.get("category"),
            difficulty=q_data["difficulty"],
            expected_keywords=q_data.get("keywords", []),
            order_number=idx + 1
        )
        db.add(question)
        questions.append(question)
    
    new_interview.total_questions = len(questions)
    db.commit()
    
    # Refresh all questions to get IDs
    for q in questions:
        db.refresh(q)
    
    return {
        "interview_id": new_interview.id,
        "questions": questions,
        "message": f"{interview_data.interview_type.title()} interview started successfully"
    }


@router.get("/", response_model=List[InterviewResponse])
@router.get("/list", response_model=List[InterviewResponse])
async def list_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Get user's interviews"""
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.created_at.desc()).offset(skip).limit(limit).all()
    
    return interviews


@router.get("/{interview_id}", response_model=InterviewDetailResponse)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview details"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    return interview


@router.post("/{interview_id}/complete", response_model=InterviewResponse)
async def complete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete an interview and generate final scores"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview already completed"
        )
    
    # Calculate final scores and generate report
    from ai_modules.adaptive.report_generator import ReportGenerator
    report_gen = ReportGenerator()
    
    try:
        report = report_gen.generate_final_report(interview_id, db)
    except Exception as e:
        # Generate default report if error
        report = {
            "overall_score": 50,
            "content_score": 50,
            "clarity_score": 50,
            "fluency_score": 50,
            "confidence_score": 50,
            "emotion_score": 50,
            "weak_areas": [],
            "strong_areas": [],
            "feedback": "Interview completed. Thank you for practicing!",
            "recommendations": [{"text": "Keep practicing to improve your interview skills!"}]
        }
    
    # Update interview with scores
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    interview.duration_minutes = (
        interview.completed_at - interview.started_at
    ).total_seconds() / 60 if interview.started_at else 0
    interview.overall_score = report.get("overall_score", 50)
    interview.content_score = report.get("content_score", 50)
    interview.clarity_score = report.get("clarity_score", 50)
    interview.fluency_score = report.get("fluency_score", 50)
    interview.confidence_score = report.get("confidence_score", 50)
    interview.emotion_score = report.get("emotion_score", 50)
    interview.weak_areas = report.get("weak_areas", [])
    interview.strong_areas = report.get("strong_areas", [])
    interview.feedback = report.get("feedback", "Thank you for completing the interview!")
    interview.recommendations = report.get("recommendations", [])
    
    db.commit()
    db.refresh(interview)
    
    # Update adaptive profile
    try:
        adaptive_system.update_user_profile(current_user.id, interview, db)
    except Exception:
        pass  # Ignore adaptive system errors
    
    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an interview"""
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed interview"
        )
    
    interview.status = "cancelled"
    db.commit()
    
    return None
