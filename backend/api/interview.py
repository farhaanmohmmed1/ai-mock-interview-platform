from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.core.database import get_db
from backend.models import User, Interview, Question, Response, Resume
from backend.api.auth import get_current_user

# Conditional imports for AI modules (may not be available on Vercel)
try:
    from ai_modules.nlp.question_generator import QuestionGenerator
    from ai_modules.adaptive.adaptive_system import AdaptiveSystem
    from ai_modules.agent import InterviewAgent
    AI_MODULES_AVAILABLE = True
    AGENT_AVAILABLE = True
except ImportError:
    AI_MODULES_AVAILABLE = False
    AGENT_AVAILABLE = False
    QuestionGenerator = None
    AdaptiveSystem = None
    InterviewAgent = None

router = APIRouter()

# Initialize AI modules and agent
if AI_MODULES_AVAILABLE:
    question_generator = QuestionGenerator()
    adaptive_system = AdaptiveSystem()
else:
    question_generator = None
    adaptive_system = None

# Initialize the Interview Agent (central orchestrator)
if AGENT_AVAILABLE:
    interview_agent = InterviewAgent()
else:
    interview_agent = None


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
    # New fields for company questions and tags
    tags: Optional[List[str]] = []
    company: Optional[str] = None
    company_name: Optional[str] = None
    source: Optional[str] = None
    from_dataset: Optional[bool] = False
    round: Optional[str] = None  # Round info for full interviews
    
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
    course_recommendations: Optional[List[dict]] = None


class StartInterviewResponse(BaseModel):
    interview_id: int
    questions: List[QuestionResponse]
    message: str
    difficulty_level: Optional[str] = None
    context_summary: Optional[dict] = None


class AgentInsightsResponse(BaseModel):
    observations: List[dict] = []
    decisions: List[dict] = []
    current_phase: Optional[str] = None


class InterviewStatusResponse(BaseModel):
    interview_id: int
    phase: str
    questions_total: int
    questions_answered: int
    current_performance: dict
    started_at: str


@router.post("/create", response_model=StartInterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and start a new interview using the Interview Agent"""
    # Validate interview type
    valid_types = ["general", "technical", "hr", "full", "upsc"]
    if interview_data.interview_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interview type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Get resume if technical or full interview
    resume = None
    resume_data = None
    user_skills = None
    if interview_data.interview_type in ["technical", "full"]:
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
        
        resume_data = resume.parsed_data
        user_skills = resume.skills
    
    # Check AI module availability
    if not AI_MODULES_AVAILABLE or question_generator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI modules not available. Interview creation requires full deployment."
        )
    
    # Get interview mode
    interview_mode = interview_data.interview_mode or "standard"
    
    # Create interview record first to get ID
    new_interview = Interview(
        user_id=current_user.id,
        resume_id=interview_data.resume_id,
        interview_type=interview_data.interview_type,
        status="in_progress",
        difficulty_level=interview_data.difficulty_level or "medium",
        started_at=datetime.utcnow()
    )
    
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    
    # Use Interview Agent if available for intelligent orchestration
    context_summary = None
    if AGENT_AVAILABLE and interview_agent is not None:
        try:
            # Start interview via agent - agent handles question generation, 
            # difficulty recommendation, and context management
            agent_session = interview_agent.start_interview(
                interview_id=new_interview.id,
                user_id=current_user.id,
                interview_type=interview_data.interview_type,
                interview_mode=interview_mode,
                difficulty_level=interview_data.difficulty_level,  # Agent will adapt if None
                resume_data=resume_data,
                user_skills=user_skills,
                db=db
            )
            
            questions_data = agent_session["questions"]
            difficulty = agent_session["difficulty_level"]
            context_summary = agent_session.get("context_summary")
            
            # Update interview with agent-recommended difficulty
            new_interview.difficulty_level = difficulty
            
        except Exception as e:
            # Fall back to direct question generation if agent fails
            difficulty = interview_data.difficulty_level or "medium"
            if not difficulty and adaptive_system:
                difficulty = adaptive_system.get_recommended_difficulty(
                    user_id=current_user.id,
                    interview_type=interview_data.interview_type,
                    db=db
                )
            
            questions_data = question_generator.generate_questions(
                interview_type=interview_data.interview_type,
                difficulty=difficulty,
                interview_mode=interview_mode,
                resume_data=resume_data,
                skills=user_skills,
                user_id=current_user.id,
                db=db
            )
    else:
        # Fallback: Use direct question generation without agent
        difficulty = interview_data.difficulty_level
        if not difficulty and adaptive_system:
            difficulty = adaptive_system.get_recommended_difficulty(
                user_id=current_user.id,
                interview_type=interview_data.interview_type,
                db=db
            )
        if not difficulty:
            difficulty = "medium"
        
        new_interview.difficulty_level = difficulty
        
        questions_data = question_generator.generate_questions(
            interview_type=interview_data.interview_type,
            difficulty=difficulty,
            interview_mode=interview_mode,
            resume_data=resume_data,
            skills=user_skills,
            user_id=current_user.id,
            db=db
        )
    
    # Save questions to database
    questions = []
    for idx, q_data in enumerate(questions_data):
        question = Question(
            interview_id=new_interview.id,
            question_text=q_data["text"],
            question_type=q_data["type"],
            category=q_data.get("category"),
            difficulty=q_data.get("difficulty", difficulty),
            expected_keywords=q_data.get("keywords", []),
            order_number=idx + 1,
            # New fields for company questions and tags
            tags=q_data.get("tags", []),
            company=q_data.get("company", ""),
            company_name=q_data.get("company_name", ""),
            source=q_data.get("source", "AI Generated"),
            from_dataset=q_data.get("from_dataset", False),
            round=q_data.get("round")  # Save round info for full interviews
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
        "message": f"{interview_data.interview_type.title()} interview started successfully",
        "difficulty_level": new_interview.difficulty_level,
        "context_summary": context_summary
    }


@router.get("/agent/status/{interview_id}", response_model=InterviewStatusResponse)
async def get_agent_interview_status(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview status from the Interview Agent"""
    # Verify interview belongs to user
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if not AGENT_AVAILABLE or interview_agent is None:
        # Return basic status if agent not available
        return {
            "interview_id": interview_id,
            "phase": interview.status,
            "questions_total": interview.total_questions,
            "questions_answered": interview.answered_questions or 0,
            "current_performance": {},
            "started_at": interview.started_at.isoformat() if interview.started_at else ""
        }
    
    status_data = interview_agent.get_interview_status(interview_id)
    
    if not status_data:
        return {
            "interview_id": interview_id,
            "phase": interview.status,
            "questions_total": interview.total_questions,
            "questions_answered": interview.answered_questions or 0,
            "current_performance": {},
            "started_at": interview.started_at.isoformat() if interview.started_at else ""
        }
    
    return status_data


@router.get("/agent/insights/{interview_id}", response_model=AgentInsightsResponse)
async def get_agent_insights(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Interview Agent's observations and decisions for transparency"""
    # Verify interview belongs to user
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if not AGENT_AVAILABLE or interview_agent is None:
        return {
            "observations": [],
            "decisions": [],
            "current_phase": interview.status
        }
    
    insights = interview_agent.get_agent_insights(interview_id)
    
    return insights if insights else {
        "observations": [],
        "decisions": [],
        "current_phase": interview.status
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
    
    # Check if any questions were actually answered
    answered_responses = db.query(Response).filter(
        Response.interview_id == interview_id
    ).all()
    answered_count = len(answered_responses)
    total_questions = interview.total_questions or 1
    
    # If no questions were answered (all skipped), return 0 scores
    if answered_count == 0:
        report = {
            "overall_score": 0,
            "content_score": 0,
            "clarity_score": 0,
            "fluency_score": 0,
            "confidence_score": 0,
            "emotion_score": 0,
            "weak_areas": [{"area": "All Areas", "score": 0, "suggestion": "You skipped all questions. Please attempt answering to get meaningful feedback."}],
            "strong_areas": [],
            "feedback": "No questions were answered. Please attempt the interview again and try answering the questions to receive a proper evaluation.",
            "recommendations": [{"text": "Practice answering interview questions out loud to build confidence."}],
            "course_recommendations": []
        }
    # If some but not all questions answered, penalize score proportionally
    elif answered_count < total_questions:
        answer_ratio = answered_count / total_questions
        report = None  # Will be generated below, then adjusted
    else:
        report = None  # Full evaluation
    
    # Use Interview Agent for comprehensive analysis if available
    if report is None and AGENT_AVAILABLE and interview_agent is not None:
        try:
            # Complete interview via agent - agent handles:
            # - Weak area identification
            # - Strong area identification  
            # - Skill gap analysis
            # - Personalized suggestions
            # - Learning path generation
            # - Comprehensive report
            agent_report = interview_agent.complete_interview(
                interview_id=interview_id,
                db=db
            )
            
            agent_overall = agent_report.get("scores", {}).get("overall_score", 0)
            
            # Only use agent report if it produced valid scores (not 0)
            # Agent may return 0 if its in-memory context was lost
            if agent_overall and agent_overall > 0:
                report = {
                    "overall_score": agent_overall,
                    "content_score": agent_report.get("scores", {}).get("content_score", 50),
                    "clarity_score": agent_report.get("scores", {}).get("clarity_score", 50),
                    "fluency_score": agent_report.get("scores", {}).get("fluency_score", 50),
                    "confidence_score": agent_report.get("scores", {}).get("confidence_score", 50),
                    "emotion_score": agent_report.get("scores", {}).get("confidence_score", 50),
                    "weak_areas": agent_report.get("weak_areas", []),
                    "strong_areas": agent_report.get("strong_areas", []),
                    "feedback": agent_report.get("feedback", "Interview completed."),
                    "recommendations": agent_report.get("suggestions", []),
                    "skill_gaps": agent_report.get("skill_gaps", []),
                    "learning_path": agent_report.get("learning_path", {}),
                    "agent_insights": agent_report.get("agent_insights", {})
                }
            else:
                print(f"Agent returned 0 scores for interview {interview_id}, falling back to ReportGenerator")
                report = None
        except Exception as e:
            # Fall back to direct report generation
            print(f"Agent complete_interview failed: {e}")
            report = None
    elif report is None:
        report = None
    
    # Fallback: Use direct report generator if agent failed or unavailable
    if report is None:
        report_gen = None
        try:
            from ai_modules.adaptive.report_generator import ReportGenerator
            report_gen = ReportGenerator()
        except ImportError:
            pass
        
        try:
            if report_gen:
                report = report_gen.generate_final_report(interview_id, db)
                print(f"ReportGenerator returned scores: overall={report.get('overall_score')}")
            else:
                raise Exception("Report generator not available")
        except Exception as e:
            # Generate default report if error - give 0 scores instead of inflated defaults
            print(f"ReportGenerator failed: {e}")
            report = {
                "overall_score": 0,
                "content_score": 0,
                "clarity_score": 0,
                "fluency_score": 0,
                "confidence_score": 0,
                "emotion_score": 0,
                "weak_areas": [],
                "strong_areas": [],
                "feedback": "Could not generate detailed evaluation. Please try the interview again.",
                "recommendations": [{"text": "Keep practicing to improve your interview skills!"}],
                "course_recommendations": [
                    {
                        "topic": "Interview Skills",
                        "severity": "medium",
                        "course": {
                            "title": "Interview Skills: How to Get the Job",
                            "platform": "Udemy",
                            "url": "https://www.udemy.com/course/interview-skills-that-win-the-job/",
                            "level": "All Levels"
                        }
                    }
                ]
            }
    
    # If partially answered, scale down scores proportionally
    if answered_count > 0 and answered_count < total_questions:
        answer_ratio = answered_count / total_questions
        for key in ["overall_score", "content_score", "clarity_score", "fluency_score", "confidence_score", "emotion_score"]:
            if key in report and report[key]:
                report[key] = round(report[key] * answer_ratio, 1)
    
    # Update interview with scores
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    interview.duration_minutes = (
        interview.completed_at - interview.started_at
    ).total_seconds() / 60 if interview.started_at else 0
    interview.overall_score = report.get("overall_score", 0)
    interview.content_score = report.get("content_score", 0)
    interview.clarity_score = report.get("clarity_score", 0)
    interview.fluency_score = report.get("fluency_score", 0)
    interview.confidence_score = report.get("confidence_score", 0)
    interview.emotion_score = report.get("emotion_score", 0)
    interview.weak_areas = report.get("weak_areas", [])
    interview.strong_areas = report.get("strong_areas", [])
    interview.feedback = report.get("feedback", "Thank you for completing the interview!")
    interview.recommendations = report.get("recommendations", [])
    interview.course_recommendations = report.get("course_recommendations", [])
    
    db.commit()
    db.refresh(interview)
    
    # Update adaptive profile
    if AI_MODULES_AVAILABLE and adaptive_system:
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
