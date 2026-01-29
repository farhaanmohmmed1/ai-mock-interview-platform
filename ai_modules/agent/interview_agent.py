"""
Interview Agent

The main AI agent that orchestrates the entire interview process.
This agent coordinates question generation, answer evaluation,
weak area identification, and personalized suggestion generation.

The agent follows an observe-think-act loop to make intelligent
decisions throughout the interview session.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from .agent_state import AgentState, InterviewContext, AgentPhase, QuestionContext
from .tools import AgentTools, ToolResult
from .config import AgentConfig, get_config
from backend.models import Interview, Question, Response


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterviewAgent:
    """
    AI Agent for conducting intelligent mock interviews.
    
    The agent operates through several phases:
    1. Initialization: Gather context about user and interview
    2. Question Generation: Create personalized questions
    3. Answer Collection & Evaluation: Real-time assessment
    4. Analysis: Identify patterns, weak areas, strengths
    5. Suggestion Generation: Create actionable recommendations
    6. Report Generation: Comprehensive final report
    
    The agent maintains state across the interview and makes
    adaptive decisions based on user performance.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or get_config()
        self.state = AgentState(
            max_questions_per_interview=self.config.max_questions_per_interview,
            min_questions_per_interview=self.config.min_questions_per_interview,
            weak_area_threshold=self.config.weak_area_threshold,
            strong_area_threshold=self.config.strong_area_threshold,
            enable_adaptive_difficulty=self.config.enable_adaptive_difficulty,
            enable_real_time_feedback=self.config.enable_real_time_feedback,
            enable_emotion_analysis=self.config.enable_emotion_analysis,
            enable_speech_analysis=self.config.enable_speech_analysis
        )
        self.tools = AgentTools()
        self._initialized = True
        logger.info("Interview Agent initialized with config: %s", self.config.to_dict())
    
    # ==================== MAIN ORCHESTRATION METHODS ====================
    
    def start_interview(
        self,
        interview_id: int,
        user_id: int,
        interview_type: str,
        interview_mode: str = "standard",
        difficulty_level: Optional[str] = None,
        resume_data: Optional[Dict] = None,
        user_skills: Optional[List[str]] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Start a new interview session.
        
        The agent will:
        1. Create interview context
        2. Get adaptive recommendations (if available)
        3. Generate personalized questions
        4. Return the interview setup
        """
        logger.info(f"Starting interview {interview_id} for user {user_id}")
        
        # Get past performance for adaptive recommendations
        past_performance = None
        if db:
            past_performance = self._get_user_history(user_id, interview_type, db)
        
        # Determine difficulty if not specified
        if not difficulty_level and db:
            rec_result = self.tools.get_adaptive_recommendation(user_id, interview_type, db)
            difficulty_level = rec_result.data.get("recommended_difficulty", "medium")
        elif not difficulty_level:
            difficulty_level = "medium"
        
        # Create interview context
        context = self.state.create_context(
            interview_id=interview_id,
            user_id=user_id,
            interview_type=interview_type,
            interview_mode=interview_mode,
            difficulty_level=difficulty_level,
            resume_data=resume_data,
            user_skills=user_skills,
            past_performance=past_performance
        )
        
        # Record agent observation
        context.record_observation(
            "Interview session initialized",
            {
                "interview_type": interview_type,
                "difficulty": difficulty_level,
                "has_resume": resume_data is not None,
                "skills_count": len(user_skills) if user_skills else 0
            }
        )
        
        # Transition to question generation phase
        context.current_phase = AgentPhase.QUESTION_GENERATION
        
        # Generate questions
        questions_result = self._generate_interview_questions(context, db)
        
        if not questions_result.success:
            logger.error(f"Failed to generate questions: {questions_result.message}")
            raise Exception(questions_result.message)
        
        # Store questions in context
        questions_data = questions_result.data
        for idx, q_data in enumerate(questions_data):
            q_context = QuestionContext(
                question_id=idx,  # Will be updated with actual IDs
                question_text=q_data["text"],
                question_type=q_data["type"],
                category=q_data.get("category", "General"),
                difficulty=q_data.get("difficulty", difficulty_level),
                expected_keywords=q_data.get("keywords", []),
                order_number=idx + 1
            )
            context.questions.append(q_context)
        
        # Record decision
        context.record_decision(
            decision="Generated question set",
            reasoning=f"Created {len(questions_data)} questions based on user profile and interview type",
            action="question_generation_complete"
        )
        
        # Update analytics
        self.state.update_analytics(questions=len(questions_data), interviews=1)
        
        # Transition to answer collection phase
        context.current_phase = AgentPhase.ANSWER_COLLECTION
        
        return {
            "interview_id": interview_id,
            "difficulty_level": difficulty_level,
            "questions": questions_data,
            "total_questions": len(questions_data),
            "context_summary": {
                "has_resume_context": resume_data is not None,
                "focus_areas": context.known_weak_areas,
                "adaptive_enabled": self.state.enable_adaptive_difficulty
            }
        }
    
    def process_answer(
        self,
        interview_id: int,
        question_id: int,
        answer_text: str,
        audio_path: Optional[str] = None,
        video_path: Optional[str] = None
    ) -> Dict:
        """
        Process a user's answer to a question.
        
        The agent will:
        1. Evaluate the answer content
        2. Analyze speech (if audio provided)
        3. Analyze emotion (if video provided)
        4. Update running metrics
        5. Identify emerging weak/strong areas
        6. Return feedback
        """
        context = self.state.get_context(interview_id)
        if not context:
            raise ValueError(f"No active interview found with ID {interview_id}")
        
        logger.info(f"Processing answer for question {question_id} in interview {interview_id}")
        
        # Find the question in context
        question_context = None
        for q in context.questions:
            if q.order_number == question_id or q.question_id == question_id:
                question_context = q
                break
        
        if not question_context:
            raise ValueError(f"Question {question_id} not found in interview")
        
        # Evaluate the answer
        eval_result = self.tools.evaluate_answer(
            question=question_context.question_text,
            answer=answer_text,
            expected_keywords=question_context.expected_keywords,
            question_type=question_context.question_type
        )
        
        if not eval_result.success:
            logger.error(f"Evaluation failed: {eval_result.message}")
            return {"error": eval_result.message}
        
        evaluation = eval_result.data
        
        # Update question context
        question_context.answer_received = True
        question_context.answer_text = answer_text
        question_context.evaluation_result = evaluation
        
        # Update running scores
        context.cumulative_content_scores.append(evaluation.get("content_score", 0))
        context.cumulative_relevance_scores.append(evaluation.get("relevance_score", 0))
        
        # Track area performance
        self._update_area_tracking(context, question_context, evaluation)
        
        # Record observation
        context.record_observation(
            f"Answer received for question {question_id}",
            {
                "content_score": evaluation.get("content_score"),
                "relevance_score": evaluation.get("relevance_score"),
                "word_count": evaluation.get("nlp_analysis", {}).get("word_count")
            }
        )
        
        # Update analytics
        self.state.update_analytics(answers=1)
        
        # Move to next question
        context.current_question_index += 1
        
        # Generate real-time feedback
        feedback = self._generate_realtime_feedback(context, evaluation)
        
        return {
            "evaluation": evaluation,
            "feedback": feedback,
            "running_performance": context.get_overall_performance(),
            "questions_remaining": len(context.get_unanswered_questions())
        }
    
    def complete_interview(
        self,
        interview_id: int,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Complete the interview and generate final analysis.
        
        The agent will:
        1. Compile all evaluations
        2. Identify weak areas
        3. Identify strong areas
        4. Generate personalized suggestions
        5. Create learning path
        6. Generate comprehensive report
        """
        context = self.state.get_context(interview_id)
        if not context:
            raise ValueError(f"No active interview found with ID {interview_id}")
        
        logger.info(f"Completing interview {interview_id}")
        
        # Transition to analysis phase
        context.current_phase = AgentPhase.ANALYSIS
        
        # Collect all evaluations
        evaluations = []
        questions_context = []
        for q in context.questions:
            if q.answer_received and q.evaluation_result:
                evaluations.append(q.evaluation_result)
                questions_context.append({
                    "text": q.question_text,
                    "category": q.category,
                    "type": q.question_type
                })
        
        # Identify weak areas
        context.record_observation("Analyzing weak areas", {"evaluations_count": len(evaluations)})
        weak_areas_result = self.tools.identify_weak_areas(
            evaluations=evaluations,
            questions_context=questions_context,
            threshold=self.state.weak_area_threshold
        )
        weak_areas = weak_areas_result.data if weak_areas_result.success else []
        
        # Identify strong areas
        strong_areas_result = self.tools.identify_strong_areas(
            evaluations=evaluations,
            questions_context=questions_context,
            threshold=self.state.strong_area_threshold
        )
        strong_areas = strong_areas_result.data if strong_areas_result.success else []
        
        # Analyze skill gaps
        skill_gaps_result = self.tools.analyze_skill_gaps(
            weak_areas=weak_areas,
            user_skills=context.user_skills,
            interview_type=context.interview_type
        )
        skill_gaps = skill_gaps_result.data if skill_gaps_result.success else []
        
        # Transition to suggestion generation
        context.current_phase = AgentPhase.SUGGESTION_GENERATION
        
        # Generate personalized suggestions
        suggestions_result = self.tools.generate_suggestions(
            weak_areas=weak_areas,
            strong_areas=strong_areas,
            interview_type=context.interview_type,
            evaluations=evaluations
        )
        suggestions = suggestions_result.data if suggestions_result.success else []
        
        # Generate learning path
        learning_path_result = self.tools.generate_learning_path(
            weak_areas=weak_areas,
            skill_gaps=skill_gaps,
            interview_type=context.interview_type
        )
        learning_path = learning_path_result.data if learning_path_result.success else {}
        
        # Transition to report generation
        context.current_phase = AgentPhase.REPORT_GENERATION
        
        # Calculate final scores
        final_scores = self._calculate_final_scores(context, evaluations)
        
        # Generate comprehensive feedback
        comprehensive_feedback = self._generate_comprehensive_feedback(
            context, final_scores, weak_areas, strong_areas
        )
        
        # Record final decision
        context.record_decision(
            decision="Interview analysis completed",
            reasoning=f"Identified {len(weak_areas)} weak areas, {len(strong_areas)} strong areas, generated {len(suggestions)} suggestions",
            action="generate_final_report"
        )
        
        # Mark as completed
        context.current_phase = AgentPhase.COMPLETED
        
        # Compile final report
        report = {
            "interview_id": interview_id,
            "completed_at": datetime.utcnow().isoformat(),
            "scores": final_scores,
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "skill_gaps": skill_gaps,
            "suggestions": suggestions,
            "learning_path": learning_path,
            "feedback": comprehensive_feedback,
            "agent_insights": {
                "observations": context.agent_observations[-10:],  # Last 10 observations
                "key_decisions": context.agent_decisions[-5:]  # Last 5 decisions
            },
            "statistics": {
                "total_questions": len(context.questions),
                "questions_answered": len(evaluations),
                "average_content_score": context.get_average_score("content"),
                "average_relevance_score": context.get_average_score("relevance")
            }
        }
        
        # Clean up context
        self.state.remove_context(context.user_id)
        
        return report
    
    # ==================== HELPER METHODS ====================
    
    def _generate_interview_questions(
        self,
        context: InterviewContext,
        db: Optional[Session] = None
    ) -> ToolResult:
        """Generate questions based on interview context"""
        
        # Determine focus areas (from known weak areas)
        focus_areas = context.known_weak_areas if context.known_weak_areas else None
        
        # Determine topics to potentially reduce (strong areas)
        avoid_topics = None
        if context.known_strong_areas and len(context.known_strong_areas) > 3:
            # Only avoid if user has many strong areas
            avoid_topics = context.known_strong_areas[:2]
        
        return self.tools.generate_questions(
            interview_type=context.interview_type,
            difficulty=context.difficulty_level,
            interview_mode=context.interview_mode,
            resume_data=context.resume_data,
            user_skills=context.user_skills,
            focus_areas=focus_areas,
            avoid_topics=avoid_topics,
            user_id=context.user_id,
            db=db,
            num_questions=self.state.max_questions_per_interview
        )
    
    def _get_user_history(
        self,
        user_id: int,
        interview_type: str,
        db: Session
    ) -> Optional[Dict]:
        """Get user's historical performance"""
        try:
            # Get recent interviews
            from backend.models import AdaptiveProfile, PerformanceMetric
            
            profile = db.query(AdaptiveProfile).filter(
                AdaptiveProfile.user_id == user_id
            ).first()
            
            metrics = db.query(PerformanceMetric).filter(
                PerformanceMetric.user_id == user_id
            ).first()
            
            if not profile and not metrics:
                return None
            
            return {
                "weak_areas": profile.weak_topics if profile and profile.weak_topics else [],
                "strong_areas": profile.strong_topics if profile and profile.strong_topics else [],
                "focus_areas": profile.focus_areas if profile and profile.focus_areas else [],
                "average_score": metrics.average_score if metrics else None,
                "total_interviews": metrics.total_interviews if metrics else 0,
                "improvement_rate": metrics.improvement_rate if metrics else None
            }
        except Exception as e:
            logger.warning(f"Could not fetch user history: {e}")
            return None
    
    def _update_area_tracking(
        self,
        context: InterviewContext,
        question: QuestionContext,
        evaluation: Dict
    ):
        """Update weak/strong area tracking based on evaluation"""
        category = question.category
        score = (evaluation.get("content_score", 0) + evaluation.get("relevance_score", 0)) / 2
        
        # Add to appropriate tracking
        if score < self.state.weak_area_threshold:
            if category not in context.session_weak_areas:
                context.session_weak_areas[category] = []
            context.session_weak_areas[category].append(score)
        elif score >= self.state.strong_area_threshold:
            if category not in context.session_strong_areas:
                context.session_strong_areas[category] = []
            context.session_strong_areas[category].append(score)
    
    def _generate_realtime_feedback(
        self,
        context: InterviewContext,
        evaluation: Dict
    ) -> Dict:
        """Generate immediate feedback after an answer"""
        content_score = evaluation.get("content_score", 0)
        relevance_score = evaluation.get("relevance_score", 0)
        
        # Determine feedback level
        avg_score = (content_score + relevance_score) / 2
        
        if avg_score >= 80:
            feedback_level = "excellent"
            message = "Excellent response! You addressed the question thoroughly."
        elif avg_score >= 65:
            feedback_level = "good"
            message = "Good answer with room for minor improvements."
        elif avg_score >= 50:
            feedback_level = "fair"
            message = "Decent answer, but consider adding more specific details."
        else:
            feedback_level = "needs_improvement"
            message = "This area needs more focus. Try to be more specific and relevant."
        
        # Add specific tips
        tips = []
        if evaluation.get("nlp_analysis", {}).get("word_count", 0) < 30:
            tips.append("Try to elaborate more on your answers")
        
        keywords_missing = evaluation.get("nlp_analysis", {}).get("keywords_missing", [])
        if keywords_missing:
            tips.append(f"Consider addressing: {', '.join(keywords_missing[:3])}")
        
        return {
            "level": feedback_level,
            "message": message,
            "tips": tips,
            "score_summary": {
                "content": content_score,
                "relevance": relevance_score
            }
        }
    
    def _calculate_final_scores(
        self,
        context: InterviewContext,
        evaluations: List[Dict]
    ) -> Dict:
        """Calculate final aggregate scores"""
        if not evaluations:
            return {
                "overall_score": 0,
                "content_score": 0,
                "relevance_score": 0,
                "clarity_score": 0,
                "fluency_score": 0,
                "confidence_score": 0
            }
        
        # Average scores
        content_scores = [e.get("content_score", 0) for e in evaluations]
        relevance_scores = [e.get("relevance_score", 0) for e in evaluations]
        
        avg_content = sum(content_scores) / len(content_scores)
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Combined content score
        combined_content = (avg_content * 0.6 + avg_relevance * 0.4)
        
        # Use defaults for speech/emotion if not available
        avg_clarity = context.get_average_score("clarity") or 70
        avg_fluency = context.get_average_score("fluency") or 70
        avg_confidence = context.get_average_score("confidence") or 70
        
        # Overall score (weighted)
        overall = (
            combined_content * 0.40 +
            ((avg_clarity + avg_fluency) / 2) * 0.30 +
            avg_confidence * 0.30
        )
        
        return {
            "overall_score": round(overall, 2),
            "content_score": round(combined_content, 2),
            "relevance_score": round(avg_relevance, 2),
            "clarity_score": round(avg_clarity, 2),
            "fluency_score": round(avg_fluency, 2),
            "confidence_score": round(avg_confidence, 2)
        }
    
    def _generate_comprehensive_feedback(
        self,
        context: InterviewContext,
        scores: Dict,
        weak_areas: List[Dict],
        strong_areas: List[Dict]
    ) -> str:
        """Generate comprehensive textual feedback"""
        overall = scores.get("overall_score", 0)
        
        # Opening assessment
        if overall >= 80:
            opening = "Outstanding performance! You demonstrated strong interview skills."
        elif overall >= 65:
            opening = "Good performance overall. You showed competence in most areas."
        elif overall >= 50:
            opening = "Satisfactory performance with clear areas for improvement."
        else:
            opening = "This interview highlighted several areas that need focused practice."
        
        # Strengths section
        strengths_text = ""
        if strong_areas:
            areas = [s["area"] for s in strong_areas[:3]]
            strengths_text = f" Your strengths include: {', '.join(areas)}."
        
        # Improvement section
        improvement_text = ""
        if weak_areas:
            areas = [w["area"] for w in weak_areas[:3]]
            improvement_text = f" Focus on improving: {', '.join(areas)}."
        
        # Closing encouragement
        closing = " Continue practicing regularly, and review the detailed suggestions below for targeted improvement."
        
        return opening + strengths_text + improvement_text + closing
    
    # ==================== UTILITY METHODS ====================
    
    def get_interview_status(self, interview_id: int) -> Optional[Dict]:
        """Get current status of an interview"""
        context = self.state.get_context(interview_id)
        if not context:
            return None
        
        return {
            "interview_id": interview_id,
            "phase": context.current_phase.value,
            "questions_total": len(context.questions),
            "questions_answered": len([q for q in context.questions if q.answer_received]),
            "current_performance": context.get_overall_performance(),
            "started_at": context.started_at.isoformat()
        }
    
    def get_next_question(self, interview_id: int) -> Optional[Dict]:
        """Get the next question to ask"""
        context = self.state.get_context(interview_id)
        if not context:
            return None
        
        question = context.get_current_question()
        if not question:
            return None
        
        return {
            "question_id": question.order_number,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "category": question.category,
            "difficulty": question.difficulty,
            "order": question.order_number,
            "total_questions": len(context.questions)
        }
    
    def should_adjust_difficulty(self, interview_id: int) -> Tuple[bool, str]:
        """
        Determine if difficulty should be adjusted mid-interview.
        Returns (should_adjust, new_difficulty)
        """
        if not self.state.enable_adaptive_difficulty:
            return False, ""
        
        context = self.state.get_context(interview_id)
        if not context:
            return False, ""
        
        # Need at least 3 answers to make adjustment
        answered = len([q for q in context.questions if q.answer_received])
        if answered < 3:
            return False, ""
        
        avg_score = context.get_average_score("content")
        current_diff = context.difficulty_level
        
        # Adjust based on performance
        if avg_score >= 85 and current_diff != "hard":
            return True, "hard"
        elif avg_score <= 45 and current_diff != "easy":
            return True, "easy"
        
        return False, ""
    
    def get_agent_insights(self, interview_id: int) -> Dict:
        """Get agent's observations and decisions for transparency"""
        context = self.state.get_context(interview_id)
        if not context:
            return {}
        
        return {
            "observations": context.agent_observations,
            "decisions": context.agent_decisions,
            "current_phase": context.current_phase.value
        }
