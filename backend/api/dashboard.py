from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.models import User, Interview, Response, PerformanceMetric
from backend.api.auth import get_current_user

router = APIRouter()


class DashboardStats(BaseModel):
    total_interviews: int
    completed_interviews: int
    average_score: float
    improvement_rate: float
    general_avg: float
    technical_avg: float
    hr_avg: float


class PerformanceHistory(BaseModel):
    date: str
    score: float
    interview_type: str
    interview_id: int


class SkillAnalysis(BaseModel):
    skill_name: str
    current_level: float
    target_level: float
    progress: float


class RecentInterview(BaseModel):
    id: int
    interview_type: str
    overall_score: Optional[float]
    completed_at: Optional[datetime]
    status: str
    
    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    stats: DashboardStats
    performance_history: List[PerformanceHistory]
    skill_analysis: List[SkillAnalysis]
    recent_interviews: List[RecentInterview]
    weak_areas: List[dict]
    recommendations: List[dict]


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard statistics"""
    
    # Get all completed interviews
    completed_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "completed"
    ).all()
    
    total_interviews = len(db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).all())
    
    # Calculate averages
    if completed_interviews:
        avg_score = sum(i.overall_score or 0 for i in completed_interviews) / len(completed_interviews)
        
        # Calculate by type
        general_interviews = [i for i in completed_interviews if i.interview_type == "general"]
        technical_interviews = [i for i in completed_interviews if i.interview_type == "technical"]
        hr_interviews = [i for i in completed_interviews if i.interview_type == "hr"]
        
        general_avg = sum(i.overall_score or 0 for i in general_interviews) / len(general_interviews) if general_interviews else 0
        technical_avg = sum(i.overall_score or 0 for i in technical_interviews) / len(technical_interviews) if technical_interviews else 0
        hr_avg = sum(i.overall_score or 0 for i in hr_interviews) / len(hr_interviews) if hr_interviews else 0
        
        # Calculate improvement rate
        if len(completed_interviews) >= 2:
            recent_avg = sum(i.overall_score or 0 for i in completed_interviews[-3:]) / min(3, len(completed_interviews))
            older_avg = sum(i.overall_score or 0 for i in completed_interviews[:3]) / min(3, len(completed_interviews))
            improvement_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            improvement_rate = 0
    else:
        avg_score = 0
        general_avg = 0
        technical_avg = 0
        hr_avg = 0
        improvement_rate = 0
    
    # Stats
    stats = DashboardStats(
        total_interviews=total_interviews,
        completed_interviews=len(completed_interviews),
        average_score=round(avg_score, 2),
        improvement_rate=round(improvement_rate, 2),
        general_avg=round(general_avg, 2),
        technical_avg=round(technical_avg, 2),
        hr_avg=round(hr_avg, 2)
    )
    
    # Performance history
    performance_history = [
        PerformanceHistory(
            date=i.completed_at.strftime("%Y-%m-%d") if i.completed_at else "",
            score=i.overall_score or 0,
            interview_type=i.interview_type,
            interview_id=i.id
        )
        for i in completed_interviews[-10:]  # Last 10 interviews
    ]
    
    # Skill analysis (aggregate from weak/strong areas)
    skill_scores = {}
    for interview in completed_interviews:
        if interview.weak_areas:
            for area in interview.weak_areas:
                skill = area.get("area", "Unknown")
                score = area.get("score", 0)
                if skill not in skill_scores:
                    skill_scores[skill] = []
                skill_scores[skill].append(score)
        
        if interview.strong_areas:
            for area in interview.strong_areas:
                skill = area.get("area", "Unknown")
                score = area.get("score", 0)
                if skill not in skill_scores:
                    skill_scores[skill] = []
                skill_scores[skill].append(score)
    
    skill_analysis = [
        SkillAnalysis(
            skill_name=skill,
            current_level=round(sum(scores) / len(scores), 2),
            target_level=85.0,
            progress=round((sum(scores) / len(scores)) / 85.0 * 100, 2)
        )
        for skill, scores in list(skill_scores.items())[:5]
    ]
    
    # Recent interviews
    recent_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(desc(Interview.created_at)).limit(5).all()
    
    # Aggregate weak areas from recent interviews
    weak_areas_agg = {}
    for interview in completed_interviews[-5:]:
        if interview.weak_areas:
            for area in interview.weak_areas:
                area_name = area.get("area", "Unknown")
                if area_name not in weak_areas_agg:
                    weak_areas_agg[area_name] = {
                        "area": area_name,
                        "frequency": 0,
                        "avg_score": 0,
                        "scores": []
                    }
                weak_areas_agg[area_name]["frequency"] += 1
                weak_areas_agg[area_name]["scores"].append(area.get("score", 0))
    
    weak_areas = []
    for area_name, data in weak_areas_agg.items():
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
        weak_areas.append({
            "area": area_name,
            "frequency": data["frequency"],
            "average_score": round(avg, 2),
            "priority": "high" if avg < 50 else "medium" if avg < 70 else "low"
        })
    
    # Sort by frequency and low score
    weak_areas.sort(key=lambda x: (x["frequency"], -x["average_score"]), reverse=True)
    weak_areas = weak_areas[:5]
    
    # Aggregate recommendations
    recommendations_set = []
    for interview in completed_interviews[-3:]:
        if interview.recommendations:
            for rec in interview.recommendations:
                if rec not in recommendations_set:
                    recommendations_set.append(rec)
    
    recommendations = recommendations_set[:5]
    
    return DashboardResponse(
        stats=stats,
        performance_history=performance_history,
        skill_analysis=skill_analysis,
        recent_interviews=recent_interviews,
        weak_areas=weak_areas,
        recommendations=recommendations
    )


@router.get("/performance-metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed performance metrics"""
    
    # Get or create performance metric
    metric = db.query(PerformanceMetric).filter(
        PerformanceMetric.user_id == current_user.id
    ).first()
    
    if not metric:
        metric = PerformanceMetric(user_id=current_user.id)
        db.add(metric)
        db.commit()
        db.refresh(metric)
    
    return {
        "total_interviews": metric.total_interviews or 0,
        "average_score": metric.average_score or 0,
        "improvement_rate": metric.improvement_rate or 0,
        "general_avg_score": metric.general_avg_score or 0,
        "technical_avg_score": metric.technical_avg_score or 0,
        "hr_avg_score": metric.hr_avg_score or 0,
        "communication_score": metric.communication_score or 0,
        "technical_knowledge_score": metric.technical_knowledge_score or 0,
        "problem_solving_score": metric.problem_solving_score or 0,
        "confidence_score": metric.confidence_score or 0,
        "skill_gaps": metric.skill_gaps or [],
        "learning_path": metric.learning_path or [],
        "next_focus_areas": metric.next_focus_areas or []
    }


@router.get("/progress/{interview_type}")
async def get_progress_by_type(
    interview_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress for specific interview type"""
    
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.interview_type == interview_type,
        Interview.status == "completed"
    ).order_by(Interview.completed_at).all()
    
    if not interviews:
        return {
            "interview_type": interview_type,
            "total_count": 0,
            "progress_data": []
        }
    
    progress_data = []
    for idx, interview in enumerate(interviews):
        progress_data.append({
            "attempt": idx + 1,
            "date": interview.completed_at.strftime("%Y-%m-%d") if interview.completed_at else "",
            "overall_score": interview.overall_score or 0,
            "content_score": interview.content_score or 0,
            "clarity_score": interview.clarity_score or 0,
            "fluency_score": interview.fluency_score or 0,
            "confidence_score": interview.confidence_score or 0
        })
    
    return {
        "interview_type": interview_type,
        "total_count": len(interviews),
        "progress_data": progress_data,
        "average_score": sum(i.overall_score or 0 for i in interviews) / len(interviews),
        "best_score": max(i.overall_score or 0 for i in interviews),
        "latest_score": interviews[-1].overall_score or 0
    }
