from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
from datetime import datetime
from pathlib import Path

from backend.core.database import get_db
from backend.core.config import settings
from backend.models import User, Resume
from backend.api.auth import get_current_user

# Conditional imports for AI modules (may not be available on Vercel)
try:
    from ai_modules.nlp.resume_parser import ResumeParser
    AI_MODULES_AVAILABLE = True
except ImportError:
    AI_MODULES_AVAILABLE = False
    ResumeParser = None

router = APIRouter()

# Initialize AI modules only if available
if AI_MODULES_AVAILABLE:
    resume_parser = ResumeParser()
else:
    resume_parser = None


class ResumeResponse(BaseModel):
    id: int
    filename: str
    skills: Optional[List[str]]
    experience_years: Optional[float]
    education: Optional[dict]
    projects: Optional[List[dict]]
    uploaded_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ResumeUploadResponse(BaseModel):
    message: str
    resume: ResumeResponse


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse resume"""
    # Validate file extension
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / 1048576:.2f} MB"
        )
    
    # Create user-specific upload directory (OS-agnostic)
    user_upload_dir = Path("data") / "uploads" / f"user_{current_user.id}"
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = user_upload_dir / filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parse resume
    if not AI_MODULES_AVAILABLE or resume_parser is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI modules not available. Resume parsing requires full deployment."
        )
    
    try:
        parsed_data = resume_parser.parse_resume(str(file_path))
    except Exception as e:
        # Clean up file if parsing fails
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )
    
    # Deactivate previous resumes
    db.query(Resume).filter(Resume.user_id == current_user.id).update({"is_active": False})
    
    # Save to database
    new_resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=str(file_path),  # Store as string for DB compatibility
        parsed_data=parsed_data.get("raw_data"),
        skills=parsed_data.get("skills", []),
        experience_years=parsed_data.get("experience_years"),
        education=parsed_data.get("education"),
        projects=parsed_data.get("projects", [])
    )
    
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    return {
        "message": "Resume uploaded and parsed successfully",
        "resume": new_resume
    }


@router.get("/list", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's resumes"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return None


@router.get("/active/current", response_model=ResumeResponse)
async def get_active_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active resume"""
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active resume found. Please upload a resume first."
        )
    
    return resume


class SkillExtractionRequest(BaseModel):
    text: str
    
    
class SkillExtractionResponse(BaseModel):
    skills: dict
    experience_years: Optional[float]
    skill_categories: dict


@router.post("/extract-skills", response_model=SkillExtractionResponse)
async def extract_skills_from_text(
    request: SkillExtractionRequest,
    current_user: User = Depends(get_current_user)
):
    """Extract skills from raw text without saving"""
    if len(request.text) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text must be at least 50 characters long"
        )
    
    if not AI_MODULES_AVAILABLE or resume_parser is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI modules not available. Skill extraction requires full deployment."
        )
    
    try:
        # Use resume parser's skill extraction
        skills_raw = resume_parser._extract_skills(request.text)
        experience = resume_parser._extract_experience_years(request.text)
        
        # Categorize skills
        skill_categories = _categorize_skills(skills_raw)
        
        return {
            "skills": {
                "technical": skills_raw,
                "soft": [],
                "tools": skill_categories.get("devops", []),
                "frameworks": skill_categories.get("frontend", []) + skill_categories.get("backend_frameworks", []),
                "languages": skill_categories.get("languages", []),
                "cloud": skill_categories.get("cloud", [])
            },
            "experience_years": experience,
            "skill_categories": skill_categories
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract skills: {str(e)}"
        )


class ResumeAnalysisResponse(BaseModel):
    resume_id: int
    analysis: dict


@router.post("/analyze/{resume_id}", response_model=ResumeAnalysisResponse)
async def analyze_resume_for_interview(
    resume_id: int,
    interview_type: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deep analysis of resume for interview preparation"""
    # Validate interview type
    valid_types = ["general", "technical", "hr", "all"]
    if interview_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interview type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    skills = resume.skills or []
    experience = resume.experience_years or 0
    
    # Determine experience level
    if experience < 2:
        exp_level = "junior"
        difficulty = "easy-medium"
    elif experience < 5:
        exp_level = "mid"
        difficulty = "medium"
    elif experience < 8:
        exp_level = "mid-senior"
        difficulty = "medium-hard"
    else:
        exp_level = "senior"
        difficulty = "hard"
    
    # Categorize skills
    skill_categories = _categorize_skills(skills)
    
    # Determine skill proficiency (simplified heuristic)
    skill_proficiency = {}
    for skill in skills[:10]:
        if skill in str(resume.projects).lower():
            skill_proficiency[skill] = "expert"
        elif skill in str(resume.parsed_data).lower().count(skill) > 2:
            skill_proficiency[skill] = "advanced"
        else:
            skill_proficiency[skill] = "intermediate"
    
    # Generate focus areas based on interview type
    focus_areas = {
        "technical": _get_technical_focus(skills),
        "behavioral": [
            "leadership experience",
            "project management",
            "team collaboration",
            "problem-solving approach"
        ],
        "hr": [
            "career goals",
            "work-life balance",
            "salary expectations",
            "company culture fit"
        ]
    }
    
    # Generate sample questions
    sample_questions = _generate_sample_questions(skills, exp_level, interview_type)
    
    # Gap analysis
    common_skills = ["kubernetes", "graphql", "typescript", "terraform", "ci/cd"]
    missing_skills = [s for s in common_skills if s not in [sk.lower() for sk in skills]]
    
    analysis = {
        "primary_skills": skills[:5],
        "skill_proficiency": skill_proficiency,
        "experience_level": exp_level,
        "recommended_difficulty": difficulty,
        "focus_areas": focus_areas if interview_type == "all" else {interview_type: focus_areas.get(interview_type, [])},
        "potential_questions_preview": sample_questions,
        "gap_analysis": {
            "missing_common_skills": missing_skills[:5],
            "improvement_areas": _identify_improvement_areas(skill_categories)
        }
    }
    
    return {
        "resume_id": resume_id,
        "analysis": analysis
    }


def _categorize_skills(skills: List[str]) -> dict:
    """Categorize skills into different groups"""
    categories = {
        "languages": [],
        "frontend": [],
        "backend_frameworks": [],
        "databases": [],
        "devops": [],
        "cloud": [],
        "ai_ml": [],
        "other": []
    }
    
    language_keywords = ["python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go", "rust"]
    frontend_keywords = ["react", "angular", "vue", "html", "css", "tailwind", "bootstrap", "next.js"]
    backend_keywords = ["django", "flask", "fastapi", "spring", "express", "node.js", "rails"]
    database_keywords = ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "dynamodb"]
    devops_keywords = ["docker", "kubernetes", "jenkins", "terraform", "ansible", "ci/cd", "git"]
    cloud_keywords = ["aws", "azure", "gcp", "google cloud", "lambda", "s3"]
    ai_ml_keywords = ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "computer vision"]
    
    for skill in skills:
        skill_lower = skill.lower()
        if any(kw in skill_lower for kw in language_keywords):
            categories["languages"].append(skill)
        elif any(kw in skill_lower for kw in frontend_keywords):
            categories["frontend"].append(skill)
        elif any(kw in skill_lower for kw in backend_keywords):
            categories["backend_frameworks"].append(skill)
        elif any(kw in skill_lower for kw in database_keywords):
            categories["databases"].append(skill)
        elif any(kw in skill_lower for kw in devops_keywords):
            categories["devops"].append(skill)
        elif any(kw in skill_lower for kw in cloud_keywords):
            categories["cloud"].append(skill)
        elif any(kw in skill_lower for kw in ai_ml_keywords):
            categories["ai_ml"].append(skill)
        else:
            categories["other"].append(skill)
    
    return {k: v for k, v in categories.items() if v}


def _get_technical_focus(skills: List[str]) -> List[str]:
    """Generate technical focus areas based on skills"""
    focus = []
    skills_lower = [s.lower() for s in skills]
    
    if any(s in skills_lower for s in ["python", "java", "javascript"]):
        focus.append("core programming concepts")
    if any(s in skills_lower for s in ["react", "angular", "vue"]):
        focus.append("frontend architecture")
    if any(s in skills_lower for s in ["sql", "postgresql", "mysql", "mongodb"]):
        focus.append("database design and optimization")
    if any(s in skills_lower for s in ["aws", "azure", "gcp"]):
        focus.append("cloud architecture")
    if any(s in skills_lower for s in ["docker", "kubernetes"]):
        focus.append("containerization and orchestration")
    if any(s in skills_lower for s in ["machine learning", "deep learning", "tensorflow"]):
        focus.append("ML system design")
    
    focus.append("system design")
    focus.append("data structures and algorithms")
    
    return focus[:6]


def _generate_sample_questions(skills: List[str], exp_level: str, interview_type: str) -> dict:
    """Generate sample interview questions"""
    questions = {
        "technical": [],
        "behavioral": [],
        "hr": []
    }
    
    # Technical questions based on skills
    if "python" in [s.lower() for s in skills]:
        questions["technical"].append("Explain Python's GIL and its implications for multithreading")
    if "react" in [s.lower() for s in skills]:
        questions["technical"].append("Describe the React component lifecycle and hooks")
    if any(s.lower() in ["aws", "azure", "gcp"] for s in skills):
        questions["technical"].append("Design a scalable microservices architecture on cloud")
    if any(s.lower() in ["sql", "postgresql", "mysql"] for s in skills):
        questions["technical"].append("How would you optimize a slow database query?")
    
    questions["technical"].extend([
        "Walk me through your approach to debugging a complex issue",
        "How do you ensure code quality in your projects?"
    ])
    
    # Behavioral questions
    questions["behavioral"] = [
        "Tell me about a challenging project you led",
        "How do you handle disagreements with team members?",
        "Describe a time you had to learn a new technology quickly",
        "How do you prioritize tasks when facing multiple deadlines?"
    ]
    
    # HR questions
    questions["hr"] = [
        "Where do you see yourself in 5 years?",
        "What motivates you in your work?",
        "Why are you interested in this opportunity?",
        "What are your salary expectations?"
    ]
    
    if interview_type != "all":
        return {interview_type: questions.get(interview_type, [])}
    
    return questions


def _identify_improvement_areas(skill_categories: dict) -> List[str]:
    """Identify areas for improvement based on skill gaps"""
    improvements = []
    
    if not skill_categories.get("frontend"):
        improvements.append("frontend development")
    if not skill_categories.get("devops"):
        improvements.append("DevOps practices")
    if not skill_categories.get("cloud"):
        improvements.append("cloud technologies")
    if not skill_categories.get("databases"):
        improvements.append("database management")
    if not skill_categories.get("ai_ml"):
        improvements.append("AI/ML fundamentals")
    
    return improvements[:3]
