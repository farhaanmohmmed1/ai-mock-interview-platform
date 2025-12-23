from sqlalchemy.orm import Session
from typing import Dict, List
from backend.models import Interview, Response, Question
import numpy as np


class ReportGenerator:
    """Generate comprehensive interview performance reports"""
    
    def __init__(self):
        pass
    
    def generate_final_report(self, interview_id: int, db: Session) -> Dict:
        """Generate final interview report"""
        
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise ValueError("Interview not found")
        
        # Get all responses
        responses = db.query(Response).filter(
            Response.interview_id == interview_id
        ).all()
        
        if not responses:
            return self._generate_empty_report()
        
        # Calculate scores
        scores = self._calculate_all_scores(responses)
        
        # Identify weak and strong areas
        weak_areas = self._identify_weak_areas(responses, db)
        strong_areas = self._identify_strong_areas(responses, db)
        
        # Generate feedback
        feedback = self._generate_comprehensive_feedback(scores, weak_areas, strong_areas)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, weak_areas, interview.interview_type)
        
        return {
            "overall_score": scores["overall"],
            "content_score": scores["content"],
            "clarity_score": scores["clarity"],
            "fluency_score": scores["fluency"],
            "confidence_score": scores["confidence"],
            "emotion_score": scores["emotion"],
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "feedback": feedback,
            "recommendations": recommendations,
            "detailed_scores": scores["detailed"]
        }
    
    def _generate_empty_report(self) -> Dict:
        """Generate report when no responses available"""
        return {
            "overall_score": 0,
            "content_score": 0,
            "clarity_score": 0,
            "fluency_score": 0,
            "confidence_score": 0,
            "emotion_score": 0,
            "weak_areas": [],
            "strong_areas": [],
            "feedback": "No responses recorded for this interview.",
            "recommendations": [
                {"type": "general", "text": "Complete the interview to receive personalized feedback"}
            ]
        }
    
    def _calculate_all_scores(self, responses: List[Response]) -> Dict:
        """Calculate all performance scores"""
        
        # Content scores
        content_scores = [r.content_score for r in responses if r.content_score is not None]
        relevance_scores = [r.relevance_score for r in responses if r.relevance_score is not None]
        
        # Speech scores
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        
        # Emotion scores
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        
        # Calculate averages
        avg_content = sum(content_scores) / len(content_scores) if content_scores else 0
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Combined scores
        content_combined = (avg_content * 0.6 + avg_relevance * 0.4) if (content_scores or relevance_scores) else 0
        speech_combined = (avg_clarity + avg_fluency) / 2 if (clarity_scores or fluency_scores) else 0
        
        # Overall score (weighted average)
        overall = (
            content_combined * 0.40 +  # 40% content
            speech_combined * 0.30 +   # 30% speech quality
            avg_confidence * 0.30      # 30% confidence/emotion
        )
        
        return {
            "overall": round(overall, 2),
            "content": round(content_combined, 2),
            "clarity": round(avg_clarity, 2),
            "fluency": round(avg_fluency, 2),
            "confidence": round(avg_confidence, 2),
            "emotion": round(avg_confidence, 2),  # Using confidence as emotion score
            "detailed": {
                "average_content": round(avg_content, 2),
                "average_relevance": round(avg_relevance, 2),
                "average_clarity": round(avg_clarity, 2),
                "average_fluency": round(avg_fluency, 2),
                "average_confidence": round(avg_confidence, 2)
            }
        }
    
    def _identify_weak_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify weak performance areas"""
        
        weak_areas = []
        
        # Analyze by question type/category
        category_scores = {}
        
        for response in responses:
            question = db.query(Question).filter(Question.id == response.question_id).first()
            
            if not question:
                continue
            
            category = question.category or question.question_type or "General"
            score = response.content_score or 0
            
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        
        # Identify categories with low scores
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 65:  # Threshold for weak area
                weak_areas.append({
                    "area": category,
                    "score": round(avg_score, 2),
                    "responses_count": len(scores),
                    "severity": "high" if avg_score < 50 else "medium"
                })
        
        # Check specific skills
        # Speech clarity
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        if clarity_scores:
            avg_clarity = sum(clarity_scores) / len(clarity_scores)
            if avg_clarity < 65:
                weak_areas.append({
                    "area": "Speech Clarity",
                    "score": round(avg_clarity, 2),
                    "responses_count": len(clarity_scores),
                    "severity": "high" if avg_clarity < 50 else "medium"
                })
        
        # Speech fluency
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        if fluency_scores:
            avg_fluency = sum(fluency_scores) / len(fluency_scores)
            if avg_fluency < 65:
                weak_areas.append({
                    "area": "Speech Fluency",
                    "score": round(avg_fluency, 2),
                    "responses_count": len(fluency_scores),
                    "severity": "high" if avg_fluency < 50 else "medium"
                })
        
        # Confidence
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence < 65:
                weak_areas.append({
                    "area": "Confidence",
                    "score": round(avg_confidence, 2),
                    "responses_count": len(confidence_scores),
                    "severity": "high" if avg_confidence < 50 else "medium"
                })
        
        # Sort by severity and score
        weak_areas.sort(key=lambda x: (x["severity"] == "high", -x["score"]), reverse=True)
        
        return weak_areas[:5]  # Top 5 weak areas
    
    def _identify_strong_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify strong performance areas"""
        
        strong_areas = []
        
        # Analyze by question type/category
        category_scores = {}
        
        for response in responses:
            question = db.query(Question).filter(Question.id == response.question_id).first()
            
            if not question:
                continue
            
            category = question.category or question.question_type or "General"
            score = response.content_score or 0
            
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        
        # Identify categories with high scores
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 75:  # Threshold for strong area
                strong_areas.append({
                    "area": category,
                    "score": round(avg_score, 2),
                    "responses_count": len(scores)
                })
        
        # Check specific skills
        # Speech clarity
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        if clarity_scores:
            avg_clarity = sum(clarity_scores) / len(clarity_scores)
            if avg_clarity >= 75:
                strong_areas.append({
                    "area": "Speech Clarity",
                    "score": round(avg_clarity, 2),
                    "responses_count": len(clarity_scores)
                })
        
        # Speech fluency
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        if fluency_scores:
            avg_fluency = sum(fluency_scores) / len(fluency_scores)
            if avg_fluency >= 75:
                strong_areas.append({
                    "area": "Speech Fluency",
                    "score": round(avg_fluency, 2),
                    "responses_count": len(fluency_scores)
                })
        
        # Confidence
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence >= 75:
                strong_areas.append({
                    "area": "Confidence",
                    "score": round(avg_confidence, 2),
                    "responses_count": len(confidence_scores)
                })
        
        # Sort by score (highest first)
        strong_areas.sort(key=lambda x: x["score"], reverse=True)
        
        return strong_areas[:5]  # Top 5 strong areas
    
    def _generate_comprehensive_feedback(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        strong_areas: List[Dict]
    ) -> str:
        """Generate comprehensive feedback"""
        
        feedback_parts = []
        
        # Overall performance
        overall = scores["overall"]
        if overall >= 80:
            feedback_parts.append("Excellent overall performance! You demonstrated strong skills across multiple areas.")
        elif overall >= 60:
            feedback_parts.append("Good performance with room for improvement in several areas.")
        elif overall >= 40:
            feedback_parts.append("Fair performance. Focus on improving key skills to enhance your interview readiness.")
        else:
            feedback_parts.append("Your performance needs significant improvement. Practice and preparation will help you succeed.")
        
        # Strong areas
        if strong_areas:
            areas_text = ", ".join([area["area"] for area in strong_areas[:3]])
            feedback_parts.append(f"Your strengths include: {areas_text}.")
        
        # Weak areas
        if weak_areas:
            areas_text = ", ".join([area["area"] for area in weak_areas[:3]])
            feedback_parts.append(f"Areas needing improvement: {areas_text}.")
        
        # Specific skill feedback
        if scores["content"] < 60:
            feedback_parts.append("Work on providing more detailed and relevant answers with concrete examples.")
        
        if scores["clarity"] < 60:
            feedback_parts.append("Practice speaking more clearly and at a moderate pace.")
        
        if scores["confidence"] < 60:
            feedback_parts.append("Build confidence through regular practice and preparation.")
        
        return " ".join(feedback_parts)
    
    def _generate_recommendations(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        interview_type: str
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Based on overall score
        if scores["overall"] < 60:
            recommendations.append({
                "type": "general",
                "priority": "high",
                "text": "Schedule more practice interviews to build fundamental skills",
                "action": "practice_interview"
            })
        
        # Based on weak areas
        for weak_area in weak_areas[:3]:
            area = weak_area["area"]
            score = weak_area["score"]
            
            if area == "Speech Clarity":
                recommendations.append({
                    "type": "speech",
                    "priority": "high" if score < 50 else "medium",
                    "text": "Practice vocal exercises and record yourself speaking",
                    "action": "speech_practice"
                })
            elif area == "Speech Fluency":
                recommendations.append({
                    "type": "speech",
                    "priority": "high" if score < 50 else "medium",
                    "text": "Work on reducing filler words and improving flow",
                    "action": "fluency_practice"
                })
            elif area == "Confidence":
                recommendations.append({
                    "type": "confidence",
                    "priority": "high" if score < 50 else "medium",
                    "text": "Practice stress management and positive visualization",
                    "action": "confidence_building"
                })
            else:
                recommendations.append({
                    "type": "content",
                    "priority": "high" if score < 50 else "medium",
                    "text": f"Study and practice {area} questions",
                    "action": "topic_study",
                    "topic": area
                })
        
        # Interview type specific recommendations
        if interview_type == "technical":
            if scores["content"] < 70:
                recommendations.append({
                    "type": "technical",
                    "priority": "high",
                    "text": "Practice coding problems on platforms like LeetCode or HackerRank",
                    "action": "coding_practice"
                })
        elif interview_type == "hr":
            recommendations.append({
                "type": "behavioral",
                "priority": "medium",
                "text": "Prepare STAR method responses for common HR questions",
                "action": "behavioral_prep"
            })
        
        # General best practices
        recommendations.append({
            "type": "general",
            "priority": "low",
            "text": "Review your recorded responses to identify improvement areas",
            "action": "self_review"
        })
        
        return recommendations
