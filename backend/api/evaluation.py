from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from backend.core.database import get_db
from backend.models import User, Interview, Question, Response
from backend.api.auth import get_current_user

# Conditional imports for AI modules (may not be available on Vercel)
try:
    from ai_modules.nlp.answer_evaluator import AnswerEvaluator
    from ai_modules.speech.speech_analyzer import SpeechAnalyzer
    from ai_modules.emotion.emotion_analyzer import EmotionAnalyzer
    AI_MODULES_AVAILABLE = True
except ImportError:
    AI_MODULES_AVAILABLE = False
    AnswerEvaluator = None
    SpeechAnalyzer = None
    EmotionAnalyzer = None

router = APIRouter()

# Initialize AI modules only if available
if AI_MODULES_AVAILABLE:
    answer_evaluator = AnswerEvaluator()
    speech_analyzer = SpeechAnalyzer()
    emotion_analyzer = EmotionAnalyzer()
else:
    answer_evaluator = None
    speech_analyzer = None
    emotion_analyzer = None


class ResponseCreate(BaseModel):
    question_id: int
    text_response: str
    thinking_time_seconds: Optional[float] = 0


class ResponseSubmit(BaseModel):
    response_id: int
    message: str
    scores: dict
    transcription: Optional[str] = None


class ResponseDetail(BaseModel):
    id: int
    question_id: int
    text_response: Optional[str]
    content_score: Optional[float]
    relevance_score: Optional[float]
    clarity_score: Optional[float]
    fluency_score: Optional[float]
    confidence_score: Optional[float]
    feedback: Optional[str]
    improvement_suggestions: Optional[list]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TranscriptionResponse(BaseModel):
    transcription: str
    duration: Optional[float] = None


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    question_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transcribe audio file to text"""
    # Verify question exists and belongs to user's interview
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    interview = db.query(Interview).filter(
        Interview.id == question.interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found or access denied"
        )
    
    # Save uploaded audio to temp file
    temp_dir = Path(tempfile.mkdtemp())
    temp_audio_path = temp_dir / "audio.webm"
    wav_path = temp_dir / "audio.wav"
    
    try:
        # Save the uploaded file
        with open(temp_audio_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Convert webm to wav using ffmpeg
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", str(temp_audio_path),
                "-ar", "16000", "-ac", "1",
                str(wav_path)
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to convert audio format. Please ensure ffmpeg is installed."
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ffmpeg not found. Please install ffmpeg for audio processing."
            )
        
        # Transcribe using speech analyzer
        if not AI_MODULES_AVAILABLE or speech_analyzer is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI modules not available. Speech analysis requires full deployment."
            )
        
        result = speech_analyzer.analyze_audio(str(wav_path))
        
        return {
            "transcription": result.get("transcription", ""),
            "duration": result.get("duration", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
    finally:
        # Cleanup temp files
        shutil.rmtree(str(temp_dir), ignore_errors=True)


@router.post("/submit-text", response_model=ResponseSubmit, status_code=status.HTTP_201_CREATED)
async def submit_text_response(
    response_data: ResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit text response to a question"""
    # Get question
    question = db.query(Question).filter(Question.id == response_data.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Verify interview belongs to user
    interview = db.query(Interview).filter(
        Interview.id == question.interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found or access denied"
        )
    
    if interview.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is not in progress"
        )
    
    # Check AI module availability
    if not AI_MODULES_AVAILABLE or answer_evaluator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI modules not available. Answer evaluation requires full deployment."
        )
    
    # Evaluate answer
    evaluation = answer_evaluator.evaluate_answer(
        question=question.question_text,
        answer=response_data.text_response,
        expected_keywords=question.expected_keywords,
        question_type=question.question_type
    )
    
    # Create response
    new_response = Response(
        interview_id=interview.id,
        question_id=question.id,
        text_response=response_data.text_response,
        content_score=evaluation["content_score"],
        relevance_score=evaluation["relevance_score"],
        thinking_time_seconds=response_data.thinking_time_seconds,
        nlp_analysis=evaluation["nlp_analysis"],
        feedback=evaluation["feedback"],
        improvement_suggestions=evaluation["suggestions"]
    )
    
    db.add(new_response)
    
    # Update interview progress
    interview.answered_questions += 1
    
    db.commit()
    db.refresh(new_response)
    
    return {
        "response_id": new_response.id,
        "message": "Response submitted successfully",
        "scores": {
            "content_score": new_response.content_score,
            "relevance_score": new_response.relevance_score
        }
    }


@router.post("/submit-audio/{question_id}", response_model=ResponseSubmit)
async def submit_audio_response(
    question_id: int,
    audio_file: UploadFile = File(...),
    thinking_time: float = Form(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit audio response to a question"""
    # Get question
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Verify interview belongs to user
    interview = db.query(Interview).filter(
        Interview.id == question.interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found or access denied"
        )
    
    # Save audio file (OS-agnostic paths)
    audio_dir = Path("data") / "recordings" / f"interview_{interview.id}"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get original file extension
    original_ext = Path(audio_file.filename or "recording.webm").suffix or ".webm"
    temp_audio_path = audio_dir / f"q{question_id}_{timestamp}_temp{original_ext}"
    audio_path = audio_dir / f"q{question_id}_{timestamp}.wav"
    
    # Save the uploaded file
    with open(temp_audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    # Convert to WAV format using ffmpeg if needed
    if original_ext.lower() != ".wav":
        try:
            subprocess.run([
                "ffmpeg", "-i", str(temp_audio_path),
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                "-y", str(audio_path)
            ], check=True, capture_output=True)
            # Remove temp file
            temp_audio_path.unlink(missing_ok=True)
        except subprocess.CalledProcessError as e:
            # If ffmpeg fails, try to use the original file
            temp_audio_path.rename(audio_path)
        except FileNotFoundError:
            # ffmpeg not installed, try to use original file
            temp_audio_path.rename(audio_path)
    else:
        temp_audio_path.rename(audio_path)
    
    # Check AI module availability
    if not AI_MODULES_AVAILABLE or speech_analyzer is None or answer_evaluator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI modules not available. Speech/answer analysis requires full deployment."
        )
    
    # Analyze speech
    try:
        speech_analysis = speech_analyzer.analyze_audio(str(audio_path))
        text_response = speech_analysis["transcription"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze audio: {str(e)}"
        )
    
    # Evaluate answer
    evaluation = answer_evaluator.evaluate_answer(
        question=question.question_text,
        answer=text_response,
        expected_keywords=question.expected_keywords,
        question_type=question.question_type
    )
    
    # Calculate response time
    response_time = speech_analysis.get("duration", 0)
    
    # Create response
    new_response = Response(
        interview_id=interview.id,
        question_id=question.id,
        text_response=text_response,
        audio_path=audio_path,
        content_score=evaluation["content_score"],
        relevance_score=evaluation["relevance_score"],
        clarity_score=speech_analysis["clarity_score"],
        fluency_score=speech_analysis["fluency_score"],
        response_time_seconds=response_time,
        thinking_time_seconds=thinking_time,
        speech_analysis=speech_analysis,
        nlp_analysis=evaluation["nlp_analysis"],
        feedback=evaluation["feedback"],
        improvement_suggestions=evaluation["suggestions"]
    )
    
    db.add(new_response)
    
    # Update interview progress
    interview.answered_questions += 1
    
    db.commit()
    db.refresh(new_response)
    
    return {
        "response_id": new_response.id,
        "message": "Audio response submitted and analyzed successfully",
        "scores": {
            "content_score": new_response.content_score,
            "relevance_score": new_response.relevance_score,
            "clarity_score": new_response.clarity_score,
            "fluency_score": new_response.fluency_score
        },
        "transcription": text_response
    }


@router.post("/submit-video/{question_id}", response_model=ResponseSubmit)
async def submit_video_response(
    question_id: int,
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    thinking_time: float = Form(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit video response with emotion analysis"""
    # Get question
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Verify interview belongs to user
    interview = db.query(Interview).filter(
        Interview.id == question.interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found or access denied"
        )
    
    # Save files (OS-agnostic paths)
    media_dir = Path("data") / "videos" / f"interview_{interview.id}"
    media_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save video
    video_filename = f"q{question_id}_{timestamp}.webm"
    video_path = media_dir / video_filename
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
    
    # Save audio
    audio_filename = f"q{question_id}_{timestamp}.wav"
    audio_path = media_dir / audio_filename
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    # Analyze speech
    try:
        speech_analysis = speech_analyzer.analyze_audio(str(audio_path))
        text_response = speech_analysis["transcription"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze audio: {str(e)}"
        )
    
    # Analyze emotions
    try:
        emotion_analysis = emotion_analyzer.analyze_video(str(video_path))
    except Exception as e:
        emotion_analysis = {"error": str(e), "confidence_score": 0}
    
    # Evaluate answer
    evaluation = answer_evaluator.evaluate_answer(
        question=question.question_text,
        answer=text_response,
        expected_keywords=question.expected_keywords,
        question_type=question.question_type
    )
    
    # Calculate response time
    response_time = speech_analysis.get("duration", 0)
    
    # Create response
    new_response = Response(
        interview_id=interview.id,
        question_id=question.id,
        text_response=text_response,
        audio_path=str(audio_path),
        video_path=str(video_path),
        content_score=evaluation["content_score"],
        relevance_score=evaluation["relevance_score"],
        clarity_score=speech_analysis["clarity_score"],
        fluency_score=speech_analysis["fluency_score"],
        confidence_score=emotion_analysis.get("confidence_score", 0),
        response_time_seconds=response_time,
        thinking_time_seconds=thinking_time,
        speech_analysis=speech_analysis,
        emotion_analysis=emotion_analysis,
        nlp_analysis=evaluation["nlp_analysis"],
        feedback=evaluation["feedback"],
        improvement_suggestions=evaluation["suggestions"]
    )
    
    db.add(new_response)
    
    # Update interview progress
    interview.answered_questions += 1
    
    db.commit()
    db.refresh(new_response)
    
    return {
        "response_id": new_response.id,
        "message": "Video response submitted and analyzed successfully",
        "scores": {
            "content_score": new_response.content_score,
            "relevance_score": new_response.relevance_score,
            "clarity_score": new_response.clarity_score,
            "fluency_score": new_response.fluency_score,
            "confidence_score": new_response.confidence_score
        }
    }


@router.get("/response/{response_id}", response_model=ResponseDetail)
async def get_response_detail(
    response_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed response information"""
    response = db.query(Response).filter(Response.id == response_id).first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    # Verify access
    interview = db.query(Interview).filter(
        Interview.id == response.interview_id,
        Interview.user_id == current_user.id
    ).first()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return response
