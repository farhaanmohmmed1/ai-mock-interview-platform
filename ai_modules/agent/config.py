"""
Agent Configuration

Configuration settings for the Interview Agent.
These settings control the agent's behavior, thresholds, and capabilities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os


@dataclass
class AgentConfig:
    """
    Configuration for the Interview Agent.
    
    These settings can be customized to adjust how the agent
    conducts interviews and generates recommendations.
    """
    
    # ==================== INTERVIEW SETTINGS ====================
    
    # Number of questions per interview
    max_questions_per_interview: int = 10
    min_questions_per_interview: int = 5
    default_questions_count: int = 8
    
    # Default difficulty if not specified or detected
    default_difficulty: str = "medium"
    
    # ==================== SCORING THRESHOLDS ====================
    
    # Score thresholds for weak/strong area identification
    weak_area_threshold: float = 65.0  # Below this is considered weak
    strong_area_threshold: float = 80.0  # Above this is considered strong
    
    # Threshold for triggering difficulty adjustment
    difficulty_adjustment_high: float = 85.0  # Increase difficulty above this
    difficulty_adjustment_low: float = 45.0  # Decrease difficulty below this
    
    # Minimum answers required before making difficulty adjustments
    min_answers_for_adjustment: int = 3
    
    # ==================== SCORE WEIGHTS ====================
    
    # Weights for calculating overall score
    content_weight: float = 0.40
    speech_weight: float = 0.30
    confidence_weight: float = 0.30
    
    # Weights for content sub-scores
    content_quality_weight: float = 0.60
    relevance_weight: float = 0.40
    
    # ==================== FEATURE FLAGS ====================
    
    # Enable/disable adaptive difficulty adjustment
    enable_adaptive_difficulty: bool = True
    
    # Enable real-time feedback after each answer
    enable_real_time_feedback: bool = True
    
    # Enable emotion/confidence analysis (requires video)
    enable_emotion_analysis: bool = True
    
    # Enable speech analysis (requires audio)
    enable_speech_analysis: bool = True
    
    # Enable follow-up question generation
    enable_followup_questions: bool = True
    
    # Enable agent observation logging (for transparency)
    enable_agent_logging: bool = True
    
    # ==================== SUGGESTION SETTINGS ====================
    
    # Maximum number of weak areas to report
    max_weak_areas_reported: int = 5
    
    # Maximum number of strong areas to report  
    max_strong_areas_reported: int = 5
    
    # Maximum number of suggestions to generate
    max_suggestions: int = 10
    
    # Default learning path duration in weeks
    default_learning_path_weeks: int = 4
    
    # ==================== ANSWER EVALUATION SETTINGS ====================
    
    # Minimum word count for a valid answer
    min_answer_word_count: int = 10
    
    # Optimal word count range for answers
    optimal_answer_min_words: int = 50
    optimal_answer_max_words: int = 150
    
    # ==================== SPEECH SETTINGS ====================
    
    # Optimal speaking rate (words per minute)
    optimal_wpm_min: int = 120
    optimal_wpm_max: int = 150
    
    # Pause thresholds (in seconds)
    short_pause_threshold: float = 0.5
    long_pause_threshold: float = 2.0
    
    # ==================== FEEDBACK LEVELS ====================
    
    # Score ranges for feedback levels
    feedback_excellent_threshold: float = 80.0
    feedback_good_threshold: float = 65.0
    feedback_fair_threshold: float = 50.0
    # Below fair_threshold is "needs_improvement"
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create configuration from environment variables"""
        return cls(
            max_questions_per_interview=int(os.getenv("AGENT_MAX_QUESTIONS", "10")),
            min_questions_per_interview=int(os.getenv("AGENT_MIN_QUESTIONS", "5")),
            weak_area_threshold=float(os.getenv("AGENT_WEAK_THRESHOLD", "65.0")),
            strong_area_threshold=float(os.getenv("AGENT_STRONG_THRESHOLD", "80.0")),
            enable_adaptive_difficulty=os.getenv("AGENT_ADAPTIVE_DIFFICULTY", "true").lower() == "true",
            enable_real_time_feedback=os.getenv("AGENT_REALTIME_FEEDBACK", "true").lower() == "true",
            enable_emotion_analysis=os.getenv("AGENT_EMOTION_ANALYSIS", "true").lower() == "true",
            enable_speech_analysis=os.getenv("AGENT_SPEECH_ANALYSIS", "true").lower() == "true",
        )
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            "interview": {
                "max_questions": self.max_questions_per_interview,
                "min_questions": self.min_questions_per_interview,
                "default_questions": self.default_questions_count,
                "default_difficulty": self.default_difficulty
            },
            "thresholds": {
                "weak_area": self.weak_area_threshold,
                "strong_area": self.strong_area_threshold,
                "difficulty_high": self.difficulty_adjustment_high,
                "difficulty_low": self.difficulty_adjustment_low
            },
            "weights": {
                "content": self.content_weight,
                "speech": self.speech_weight,
                "confidence": self.confidence_weight
            },
            "features": {
                "adaptive_difficulty": self.enable_adaptive_difficulty,
                "real_time_feedback": self.enable_real_time_feedback,
                "emotion_analysis": self.enable_emotion_analysis,
                "speech_analysis": self.enable_speech_analysis,
                "followup_questions": self.enable_followup_questions,
                "agent_logging": self.enable_agent_logging
            },
            "suggestions": {
                "max_weak_areas": self.max_weak_areas_reported,
                "max_strong_areas": self.max_strong_areas_reported,
                "max_suggestions": self.max_suggestions
            },
            "feedback": {
                "excellent_threshold": self.feedback_excellent_threshold,
                "good_threshold": self.feedback_good_threshold,
                "fair_threshold": self.feedback_fair_threshold
            }
        }


# Default configuration instance
default_config = AgentConfig()


def get_config() -> AgentConfig:
    """Get the agent configuration (from environment or defaults)"""
    try:
        return AgentConfig.from_env()
    except Exception:
        return default_config
