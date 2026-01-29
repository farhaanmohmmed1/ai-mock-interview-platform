"""
SQLAlchemy Database Models for AI Mock Interview Platform
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base


class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetric", back_populates="user", cascade="all, delete-orphan")
    adaptive_profile = relationship("AdaptiveProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Resume(Base):
    """Resume model for uploaded resumes"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    parsed_data = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    experience_years = Column(Float, nullable=True)
    education = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="resumes")
    interviews = relationship("Interview", back_populates="resume")


class Interview(Base):
    """Interview session model"""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    interview_type = Column(String(50), nullable=False)  # general, technical, hr
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    difficulty_level = Column(String(20), default="medium")  # easy, medium, hard
    total_questions = Column(Integer, default=0)
    answered_questions = Column(Integer, default=0)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    content_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    emotion_score = Column(Float, nullable=True)
    weak_areas = Column(JSON, nullable=True)
    strong_areas = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="interview", cascade="all, delete-orphan")


class Question(Base):
    """Interview question model"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=True)  # behavioral, technical, situational, hr
    category = Column(String(100), nullable=True)  # programming, database, algorithms, etc.
    difficulty = Column(String(20), nullable=True)
    expected_keywords = Column(JSON, nullable=True)
    order_number = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    responses = relationship("Response", back_populates="question", cascade="all, delete-orphan")


class Response(Base):
    """User response model with multimodal analysis"""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text_response = Column(Text, nullable=True)
    audio_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    content_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    speech_analysis = Column(JSON, nullable=True)
    emotion_analysis = Column(JSON, nullable=True)
    nlp_analysis = Column(JSON, nullable=True)
    response_time_seconds = Column(Float, nullable=True)
    thinking_time_seconds = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    improvement_suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="responses")
    question = relationship("Question", back_populates="responses")


class PerformanceMetric(Base):
    """Performance metrics model for tracking user progress"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    total_interviews = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    improvement_rate = Column(Float, nullable=True)
    general_avg_score = Column(Float, nullable=True)
    technical_avg_score = Column(Float, nullable=True)
    hr_avg_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    technical_knowledge_score = Column(Float, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    skill_gaps = Column(JSON, nullable=True)
    learning_path = Column(JSON, nullable=True)
    next_focus_areas = Column(JSON, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="performance_metrics")


class AdaptiveProfile(Base):
    """Adaptive learning profile for personalized questioning"""
    __tablename__ = "adaptive_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    learning_pace = Column(String(20), default="medium")  # slow, medium, fast
    preferred_difficulty = Column(String(20), default="medium")
    strong_topics = Column(JSON, nullable=True)
    weak_topics = Column(JSON, nullable=True)
    avg_response_time = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)
    stress_indicators = Column(JSON, nullable=True)
    question_difficulty_multiplier = Column(Float, default=1.0)
    focus_areas = Column(JSON, nullable=True)
    recommended_practice = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="adaptive_profile")
