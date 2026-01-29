"""
Agent State Management

Manages the state of the interview agent throughout the interview session,
tracking context, performance metrics, and conversation history.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class AgentPhase(Enum):
    """Phases of the interview agent's workflow"""
    INITIALIZATION = "initialization"
    QUESTION_GENERATION = "question_generation"
    ANSWER_COLLECTION = "answer_collection"
    EVALUATION = "evaluation"
    ANALYSIS = "analysis"
    SUGGESTION_GENERATION = "suggestion_generation"
    REPORT_GENERATION = "report_generation"
    COMPLETED = "completed"


class DifficultyLevel(Enum):
    """Difficulty levels for questions"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class QuestionContext:
    """Context for a single question in the interview"""
    question_id: int
    question_text: str
    question_type: str
    category: str
    difficulty: str
    expected_keywords: List[str]
    order_number: int
    asked_at: Optional[datetime] = None
    answer_received: bool = False
    answer_text: Optional[str] = None
    evaluation_result: Optional[Dict] = None


@dataclass
class PerformanceSnapshot:
    """Snapshot of user's performance at a point in time"""
    timestamp: datetime
    questions_answered: int
    total_questions: int
    average_content_score: float
    average_relevance_score: float
    average_confidence_score: float
    identified_weak_areas: List[str]
    identified_strong_areas: List[str]


@dataclass
class InterviewContext:
    """
    Complete context for an interview session.
    Maintains all state needed for the agent to make decisions.
    """
    # Interview metadata
    interview_id: int
    user_id: int
    interview_type: str  # general, technical, hr, upsc
    interview_mode: str  # standard, upsc
    difficulty_level: str
    started_at: datetime
    
    # Resume context (if available)
    resume_data: Optional[Dict] = None
    user_skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    
    # User history context
    past_performance: Optional[Dict] = None
    known_weak_areas: Optional[List[str]] = None
    known_strong_areas: Optional[List[str]] = None
    
    # Current session state
    current_phase: AgentPhase = AgentPhase.INITIALIZATION
    questions: List[QuestionContext] = field(default_factory=list)
    current_question_index: int = 0
    
    # Performance tracking
    performance_history: List[PerformanceSnapshot] = field(default_factory=list)
    
    # Running scores
    cumulative_content_scores: List[float] = field(default_factory=list)
    cumulative_relevance_scores: List[float] = field(default_factory=list)
    cumulative_clarity_scores: List[float] = field(default_factory=list)
    cumulative_fluency_scores: List[float] = field(default_factory=list)
    cumulative_confidence_scores: List[float] = field(default_factory=list)
    
    # Identified areas (updated in real-time)
    session_weak_areas: Dict[str, List[float]] = field(default_factory=dict)
    session_strong_areas: Dict[str, List[float]] = field(default_factory=dict)
    
    # Agent reasoning/memory
    agent_observations: List[Dict] = field(default_factory=list)
    agent_decisions: List[Dict] = field(default_factory=list)
    
    def get_current_question(self) -> Optional[QuestionContext]:
        """Get the current question being asked"""
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
    
    def get_unanswered_questions(self) -> List[QuestionContext]:
        """Get list of questions not yet answered"""
        return [q for q in self.questions if not q.answer_received]
    
    def get_average_score(self, score_type: str) -> float:
        """Get average of a specific score type"""
        score_map = {
            "content": self.cumulative_content_scores,
            "relevance": self.cumulative_relevance_scores,
            "clarity": self.cumulative_clarity_scores,
            "fluency": self.cumulative_fluency_scores,
            "confidence": self.cumulative_confidence_scores
        }
        scores = score_map.get(score_type, [])
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_overall_performance(self) -> Dict:
        """Get current overall performance metrics"""
        return {
            "questions_answered": len([q for q in self.questions if q.answer_received]),
            "total_questions": len(self.questions),
            "avg_content_score": self.get_average_score("content"),
            "avg_relevance_score": self.get_average_score("relevance"),
            "avg_clarity_score": self.get_average_score("clarity"),
            "avg_fluency_score": self.get_average_score("fluency"),
            "avg_confidence_score": self.get_average_score("confidence"),
            "weak_areas": list(self.session_weak_areas.keys()),
            "strong_areas": list(self.session_strong_areas.keys())
        }
    
    def record_observation(self, observation: str, data: Optional[Dict] = None):
        """Record an agent observation during the interview"""
        self.agent_observations.append({
            "timestamp": datetime.utcnow().isoformat(),
            "phase": self.current_phase.value,
            "observation": observation,
            "data": data or {}
        })
    
    def record_decision(self, decision: str, reasoning: str, action: Optional[str] = None):
        """Record an agent decision and its reasoning"""
        self.agent_decisions.append({
            "timestamp": datetime.utcnow().isoformat(),
            "phase": self.current_phase.value,
            "decision": decision,
            "reasoning": reasoning,
            "action": action
        })


@dataclass
class AgentState:
    """
    Global state of the Interview Agent.
    Manages multiple interview contexts and agent configuration.
    """
    # Configuration
    max_questions_per_interview: int = 10
    min_questions_per_interview: int = 5
    difficulty_adjustment_threshold: float = 0.7
    weak_area_threshold: float = 65.0
    strong_area_threshold: float = 80.0
    
    # Active interviews (user_id -> context)
    active_interviews: Dict[int, InterviewContext] = field(default_factory=dict)
    
    # Agent capabilities flags
    enable_adaptive_difficulty: bool = True
    enable_real_time_feedback: bool = True
    enable_emotion_analysis: bool = True
    enable_speech_analysis: bool = True
    
    # Analytics
    total_interviews_conducted: int = 0
    total_questions_generated: int = 0
    total_answers_evaluated: int = 0
    
    def get_context(self, interview_id: int) -> Optional[InterviewContext]:
        """Get context for a specific interview"""
        for context in self.active_interviews.values():
            if context.interview_id == interview_id:
                return context
        return None
    
    def create_context(
        self,
        interview_id: int,
        user_id: int,
        interview_type: str,
        interview_mode: str = "standard",
        difficulty_level: str = "medium",
        resume_data: Optional[Dict] = None,
        user_skills: Optional[List[str]] = None,
        past_performance: Optional[Dict] = None
    ) -> InterviewContext:
        """Create a new interview context"""
        context = InterviewContext(
            interview_id=interview_id,
            user_id=user_id,
            interview_type=interview_type,
            interview_mode=interview_mode,
            difficulty_level=difficulty_level,
            started_at=datetime.utcnow(),
            resume_data=resume_data,
            user_skills=user_skills,
            past_performance=past_performance,
            known_weak_areas=past_performance.get("weak_areas", []) if past_performance else None,
            known_strong_areas=past_performance.get("strong_areas", []) if past_performance else None
        )
        self.active_interviews[user_id] = context
        return context
    
    def remove_context(self, user_id: int):
        """Remove an interview context (after completion)"""
        if user_id in self.active_interviews:
            del self.active_interviews[user_id]
    
    def update_analytics(self, questions: int = 0, answers: int = 0, interviews: int = 0):
        """Update global analytics"""
        self.total_questions_generated += questions
        self.total_answers_evaluated += answers
        self.total_interviews_conducted += interviews
