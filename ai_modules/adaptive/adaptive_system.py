from sqlalchemy.orm import Session
from typing import Dict, List
from backend.models import Interview, Response, PerformanceMetric, AdaptiveProfile
import numpy as np


class AdaptiveSystem:
    """Adaptive learning system that personalizes interviews based on performance"""
    
    def __init__(self):
        self.difficulty_weights = {
            "easy": 0.7,
            "medium": 1.0,
            "hard": 1.3
        }
    
    def get_recommended_difficulty(
        self,
        user_id: int,
        interview_type: str,
        db: Session
    ) -> str:
        """Recommend difficulty level based on past performance"""
        
        # Get user's adaptive profile
        profile = db.query(AdaptiveProfile).filter(
            AdaptiveProfile.user_id == user_id
        ).first()
        
        # Get recent interviews of this type
        recent_interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.interview_type == interview_type,
            Interview.status == "completed"
        ).order_by(Interview.completed_at.desc()).limit(3).all()
        
        if not recent_interviews:
            # First interview - start with medium
            return "medium"
        
        # Calculate average score from recent interviews
        avg_score = sum(i.overall_score or 0 for i in recent_interviews) / len(recent_interviews)
        
        # Determine difficulty based on performance
        if avg_score >= 80:
            return "hard"
        elif avg_score >= 60:
            return "medium"
        else:
            return "easy"
    
    def update_user_profile(
        self,
        user_id: int,
        interview: Interview,
        db: Session
    ):
        """Update user's adaptive profile after interview"""
        
        # Get or create adaptive profile
        profile = db.query(AdaptiveProfile).filter(
            AdaptiveProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = AdaptiveProfile(user_id=user_id)
            db.add(profile)
        
        # Update performance metrics
        self._update_performance_metrics(user_id, interview, db)
        
        # Analyze weak and strong areas
        weak_topics = self._identify_weak_topics(user_id, db)
        strong_topics = self._identify_strong_topics(user_id, db)
        
        # Update profile
        profile.weak_topics = weak_topics
        profile.strong_topics = strong_topics
        profile.focus_areas = self._determine_focus_areas(weak_topics)
        profile.recommended_practice = self._generate_practice_recommendations(weak_topics)
        
        # Calculate learning characteristics
        profile.consistency_score = self._calculate_consistency(user_id, db)
        profile.avg_response_time = self._calculate_avg_response_time(user_id, db)
        
        db.commit()
    
    def _update_performance_metrics(
        self,
        user_id: int,
        interview: Interview,
        db: Session
    ):
        """Update overall performance metrics"""
        
        # Get or create performance metric
        metric = db.query(PerformanceMetric).filter(
            PerformanceMetric.user_id == user_id
        ).first()
        
        if not metric:
            metric = PerformanceMetric(user_id=user_id)
            db.add(metric)
        
        # Get all completed interviews
        all_interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == "completed"
        ).all()
        
        if not all_interviews:
            return
        
        # Update counts
        metric.total_interviews = len(all_interviews)
        
        # Calculate averages
        metric.average_score = sum(i.overall_score or 0 for i in all_interviews) / len(all_interviews)
        
        # Category averages
        general_interviews = [i for i in all_interviews if i.interview_type == "general"]
        technical_interviews = [i for i in all_interviews if i.interview_type == "technical"]
        hr_interviews = [i for i in all_interviews if i.interview_type == "hr"]
        
        if general_interviews:
            metric.general_avg_score = sum(i.overall_score or 0 for i in general_interviews) / len(general_interviews)
        
        if technical_interviews:
            metric.technical_avg_score = sum(i.overall_score or 0 for i in technical_interviews) / len(technical_interviews)
        
        if hr_interviews:
            metric.hr_avg_score = sum(i.overall_score or 0 for i in hr_interviews) / len(hr_interviews)
        
        # Calculate improvement rate
        if len(all_interviews) >= 2:
            first_half = all_interviews[:len(all_interviews)//2]
            second_half = all_interviews[len(all_interviews)//2:]
            
            first_avg = sum(i.overall_score or 0 for i in first_half) / len(first_half)
            second_avg = sum(i.overall_score or 0 for i in second_half) / len(second_half)
            
            if first_avg > 0:
                metric.improvement_rate = ((second_avg - first_avg) / first_avg) * 100
        
        # Skill scores (average from interview scores)
        metric.communication_score = sum(
            (i.clarity_score or 0) + (i.fluency_score or 0) for i in all_interviews
        ) / (len(all_interviews) * 2) if all_interviews else 0
        
        metric.technical_knowledge_score = metric.technical_avg_score or 0
        
        metric.problem_solving_score = sum(i.content_score or 0 for i in all_interviews) / len(all_interviews)
        
        metric.confidence_score = sum(i.confidence_score or 0 for i in all_interviews) / len(all_interviews)
        
        # Identify skill gaps
        metric.skill_gaps = self._identify_skill_gaps(user_id, db)
        
        # Generate learning path
        metric.learning_path = self._generate_learning_path(metric.skill_gaps)
        
        # Next focus areas
        metric.next_focus_areas = self._determine_next_focus(metric.skill_gaps)
        
        db.commit()
    
    def _identify_weak_topics(self, user_id: int, db: Session) -> List[Dict]:
        """Identify topics where user struggles"""
        
        interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == "completed"
        ).all()
        
        weak_areas_map = {}
        
        for interview in interviews:
            if interview.weak_areas:
                for area in interview.weak_areas:
                    area_name = area.get("area", "Unknown")
                    score = area.get("score", 0)
                    
                    if area_name not in weak_areas_map:
                        weak_areas_map[area_name] = []
                    weak_areas_map[area_name].append(score)
        
        # Calculate average scores
        weak_topics = []
        for area, scores in weak_areas_map.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 70:  # Threshold for weak area
                weak_topics.append({
                    "topic": area,
                    "average_score": round(avg_score, 2),
                    "attempts": len(scores)
                })
        
        # Sort by score (weakest first)
        weak_topics.sort(key=lambda x: x["average_score"])
        
        return weak_topics[:10]  # Top 10 weak topics
    
    def _identify_strong_topics(self, user_id: int, db: Session) -> List[Dict]:
        """Identify topics where user excels"""
        
        interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == "completed"
        ).all()
        
        strong_areas_map = {}
        
        for interview in interviews:
            if interview.strong_areas:
                for area in interview.strong_areas:
                    area_name = area.get("area", "Unknown")
                    score = area.get("score", 0)
                    
                    if area_name not in strong_areas_map:
                        strong_areas_map[area_name] = []
                    strong_areas_map[area_name].append(score)
        
        # Calculate average scores
        strong_topics = []
        for area, scores in strong_areas_map.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 80:  # Threshold for strong area
                strong_topics.append({
                    "topic": area,
                    "average_score": round(avg_score, 2),
                    "attempts": len(scores)
                })
        
        # Sort by score (strongest first)
        strong_topics.sort(key=lambda x: x["average_score"], reverse=True)
        
        return strong_topics[:10]
    
    def _determine_focus_areas(self, weak_topics: List[Dict]) -> List[str]:
        """Determine which areas to focus on next"""
        # Focus on top 3 weakest topics
        return [topic["topic"] for topic in weak_topics[:3]]
    
    def _generate_practice_recommendations(self, weak_topics: List[Dict]) -> List[Dict]:
        """Generate practice recommendations"""
        recommendations = []
        
        for topic_data in weak_topics[:5]:  # Top 5 weak topics
            topic = topic_data["topic"]
            score = topic_data["average_score"]
            
            # Determine intensity
            if score < 50:
                intensity = "High Priority"
                sessions = 5
            elif score < 70:
                intensity = "Medium Priority"
                sessions = 3
            else:
                intensity = "Low Priority"
                sessions = 2
            
            recommendations.append({
                "topic": topic,
                "current_score": score,
                "target_score": 80,
                "priority": intensity,
                "recommended_sessions": sessions,
                "estimated_time_hours": sessions * 0.5
            })
        
        return recommendations
    
    def _calculate_consistency(self, user_id: int, db: Session) -> float:
        """Calculate performance consistency"""
        
        interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.status == "completed"
        ).order_by(Interview.completed_at).all()
        
        if len(interviews) < 2:
            return 100.0
        
        scores = [i.overall_score or 0 for i in interviews]
        
        # Calculate standard deviation
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to consistency score (lower std dev = higher consistency)
        # Max std dev of 30 maps to 0 consistency, 0 std dev maps to 100
        consistency = max(0, 100 - (std_dev / 30 * 100))
        
        return round(consistency, 2)
    
    def _calculate_avg_response_time(self, user_id: int, db: Session) -> float:
        """Calculate average response time"""
        
        responses = db.query(Response).join(Interview).filter(
            Interview.user_id == user_id
        ).all()
        
        if not responses:
            return 0
        
        response_times = [r.response_time_seconds for r in responses if r.response_time_seconds]
        
        if not response_times:
            return 0
        
        return round(sum(response_times) / len(response_times), 2)
    
    def _identify_skill_gaps(self, user_id: int, db: Session) -> List[Dict]:
        """Identify specific skill gaps"""
        
        metric = db.query(PerformanceMetric).filter(
            PerformanceMetric.user_id == user_id
        ).first()
        
        if not metric:
            return []
        
        gaps = []
        
        # Check each skill area
        skills = {
            "Communication": metric.communication_score or 0,
            "Technical Knowledge": metric.technical_knowledge_score or 0,
            "Problem Solving": metric.problem_solving_score or 0,
            "Confidence": metric.confidence_score or 0
        }
        
        for skill, score in skills.items():
            if score < 70:
                gap_size = 80 - score  # Target is 80
                gaps.append({
                    "skill": skill,
                    "current_level": round(score, 2),
                    "target_level": 80,
                    "gap": round(gap_size, 2),
                    "priority": "high" if gap_size > 30 else "medium" if gap_size > 15 else "low"
                })
        
        gaps.sort(key=lambda x: x["gap"], reverse=True)
        
        return gaps
    
    def _generate_learning_path(self, skill_gaps: List[Dict]) -> List[Dict]:
        """Generate learning path to address skill gaps"""
        
        learning_path = []
        
        learning_resources = {
            "Communication": [
                {"resource": "Practice articulating thoughts clearly", "type": "exercise"},
                {"resource": "Record and review your responses", "type": "practice"},
                {"resource": "Public speaking course", "type": "course"}
            ],
            "Technical Knowledge": [
                {"resource": "LeetCode/HackerRank practice", "type": "practice"},
                {"resource": "System design courses", "type": "course"},
                {"resource": "Read technical documentation", "type": "reading"}
            ],
            "Problem Solving": [
                {"resource": "Daily coding challenges", "type": "exercise"},
                {"resource": "Case study analysis", "type": "practice"},
                {"resource": "Logic puzzles and brain teasers", "type": "exercise"}
            ],
            "Confidence": [
                {"resource": "Mock interview practice", "type": "practice"},
                {"resource": "Positive self-talk exercises", "type": "exercise"},
                {"resource": "Stress management techniques", "type": "wellness"}
            ]
        }
        
        for gap in skill_gaps:
            skill = gap["skill"]
            resources = learning_resources.get(skill, [])
            
            learning_path.append({
                "skill": skill,
                "current_level": gap["current_level"],
                "target_level": gap["target_level"],
                "estimated_weeks": max(2, int(gap["gap"] / 10)),
                "resources": resources
            })
        
        return learning_path
    
    def _determine_next_focus(self, skill_gaps: List[Dict]) -> List[str]:
        """Determine immediate next steps"""
        if not skill_gaps:
            return ["Continue practicing to maintain current skills"]
        
        # Focus on highest priority gaps
        high_priority = [gap["skill"] for gap in skill_gaps if gap.get("priority") == "high"]
        
        if high_priority:
            return high_priority[:2]  # Top 2 high priority
        
        # If no high priority, take medium priority
        medium_priority = [gap["skill"] for gap in skill_gaps if gap.get("priority") == "medium"]
        return medium_priority[:2] if medium_priority else ["General practice across all areas"]
