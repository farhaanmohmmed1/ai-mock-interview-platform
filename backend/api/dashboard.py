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
    total_practice_time: float
    current_streak: int


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
    
    # Get all completed interviews ordered by completion time
    completed_interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "completed"
    ).order_by(Interview.completed_at.asc()).all()
    
    total_interviews = len(db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).all())
    
    # Calculate averages
    total_practice_time = sum(i.duration_minutes or 0 for i in completed_interviews)
    
    # Calculate day streak from completed_at dates
    current_streak = 0
    if completed_interviews:
        interview_dates = sorted(set(
            i.completed_at.date() for i in completed_interviews if i.completed_at
        ), reverse=True)
        if interview_dates:
            from datetime import date
            today = date.today()
            # Allow streak if latest interview is today or yesterday
            if interview_dates[0] >= today - timedelta(days=1):
                current_streak = 1
                for j in range(1, len(interview_dates)):
                    if (interview_dates[j - 1] - interview_dates[j]).days <= 1:
                        current_streak += 1
                    else:
                        break
    
    if completed_interviews:
        # Only include interviews that have actual scores (exclude broken ones with 0 or null)
        scored_interviews = [i for i in completed_interviews if i.overall_score and i.overall_score > 0]
        
        avg_score = sum(i.overall_score for i in scored_interviews) / len(scored_interviews) if scored_interviews else 0
        
        # Calculate by type (include 'full' interviews in all categories)
        general_interviews = [i for i in scored_interviews if i.interview_type in ("general", "full")]
        technical_interviews = [i for i in scored_interviews if i.interview_type in ("technical", "full")]
        hr_interviews = [i for i in scored_interviews if i.interview_type in ("hr", "full")]
        
        general_avg = sum(i.overall_score or 0 for i in general_interviews) / len(general_interviews) if general_interviews else 0
        technical_avg = sum(i.overall_score or 0 for i in technical_interviews) / len(technical_interviews) if technical_interviews else 0
        hr_avg = sum(i.overall_score or 0 for i in hr_interviews) / len(hr_interviews) if hr_interviews else 0
        
        # Calculate improvement rate by comparing recent half vs older half
        if len(scored_interviews) >= 2:
            mid = len(scored_interviews) // 2
            older_half = scored_interviews[:mid]
            recent_half = scored_interviews[mid:]
            older_avg = sum(i.overall_score or 0 for i in older_half) / len(older_half)
            recent_avg = sum(i.overall_score or 0 for i in recent_half) / len(recent_half)
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
        hr_avg=round(hr_avg, 2),
        total_practice_time=round(total_practice_time, 1),
        current_streak=current_streak
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
    
    # Skill analysis - always include core interview metrics
    core_skills = {}
    if completed_interviews:
        content_scores = [i.content_score for i in completed_interviews if i.content_score is not None]
        clarity_scores = [i.clarity_score for i in completed_interviews if i.clarity_score is not None]
        fluency_scores = [i.fluency_score for i in completed_interviews if i.fluency_score is not None]
        confidence_scores = [i.confidence_score for i in completed_interviews if i.confidence_score is not None]
        emotion_scores = [i.emotion_score for i in completed_interviews if i.emotion_score is not None]
        
        if content_scores:
            core_skills["Content Quality"] = sum(content_scores) / len(content_scores)
        if clarity_scores:
            core_skills["Clarity"] = sum(clarity_scores) / len(clarity_scores)
        if fluency_scores:
            core_skills["Fluency"] = sum(fluency_scores) / len(fluency_scores)
        if confidence_scores:
            core_skills["Confidence"] = sum(confidence_scores) / len(confidence_scores)
        if emotion_scores:
            core_skills["Expression"] = sum(emotion_scores) / len(emotion_scores)
    
    # Also aggregate from weak/strong areas for additional skills
    skill_scores = {}
    for interview in completed_interviews:
        if interview.weak_areas:
            for area in interview.weak_areas:
                skill = area.get("area", "Unknown")
                score = area.get("score", 0)
                if skill not in skill_scores and skill not in core_skills:
                    skill_scores[skill] = []
                if skill not in core_skills:
                    skill_scores[skill].append(score)
        
        if interview.strong_areas:
            for area in interview.strong_areas:
                skill = area.get("area", "Unknown")
                score = area.get("score", 0)
                if skill not in skill_scores and skill not in core_skills:
                    skill_scores[skill] = []
                if skill not in core_skills:
                    skill_scores[skill].append(score)
    
    # Build skill_analysis: core skills first, then additional
    skill_analysis = [
        SkillAnalysis(
            skill_name=skill,
            current_level=round(avg, 2),
            target_level=85.0,
            progress=round(avg / 85.0 * 100, 2)
        )
        for skill, avg in core_skills.items()
    ]
    
    for skill, scores in list(skill_scores.items())[:3]:
        if scores:
            avg = sum(scores) / len(scores)
            skill_analysis.append(SkillAnalysis(
                skill_name=skill,
                current_level=round(avg, 2),
                target_level=85.0,
                progress=round(avg / 85.0 * 100, 2)
            ))
    
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
