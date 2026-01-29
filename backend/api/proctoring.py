"""
Proctoring API Endpoints

Provides REST API for anti-cheat monitoring during interviews.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
import cv2
import base64
from datetime import datetime

from backend.core.security import get_current_user
from backend.models import User

# Import anti-cheat module
try:
    from ai_modules.proctoring import (
        AntiCheatMonitor,
        ProctorSession,
        MEDIAPIPE_AVAILABLE,
        DEEPFACE_AVAILABLE
    )
    PROCTORING_AVAILABLE = True
except ImportError as e:
    print(f"Proctoring module not available: {e}")
    PROCTORING_AVAILABLE = False

router = APIRouter(prefix="/proctoring", tags=["proctoring"])

# Global monitor instance
proctor_monitor: Optional[AntiCheatMonitor] = None


def get_monitor() -> AntiCheatMonitor:
    """Get or create the proctor monitor"""
    global proctor_monitor
    if proctor_monitor is None and PROCTORING_AVAILABLE:
        proctor_monitor = AntiCheatMonitor(sensitivity="medium")
    return proctor_monitor


# Request/Response Models
class StartSessionRequest(BaseModel):
    interview_id: int
    sensitivity: Optional[str] = "medium"  # low, medium, high


class StartSessionResponse(BaseModel):
    session_id: str
    status: str
    features_available: dict


class FrameAnalysisRequest(BaseModel):
    session_id: str
    frame_base64: str  # Base64 encoded image
    verify_person: Optional[bool] = False


class TabSwitchRequest(BaseModel):
    session_id: str
    event_type: str  # 'switch' or 'blur'


class ProctorStatusResponse(BaseModel):
    available: bool
    features: dict
    sensitivity_levels: List[str]


@router.get("/status")
async def get_proctoring_status() -> ProctorStatusResponse:
    """
    Get proctoring system status and available features.
    """
    return {
        "available": PROCTORING_AVAILABLE,
        "features": {
            "face_detection": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False,
            "gaze_tracking": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False,
            "head_pose": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False,
            "person_verification": DEEPFACE_AVAILABLE if PROCTORING_AVAILABLE else False,
            "tab_switch_detection": True,
            "multiple_face_detection": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False
        },
        "accuracy": {
            "face_detection": "99%",
            "multiple_faces": "95%",
            "gaze_tracking": "85-90%",
            "person_verification": "97%",
            "head_pose": "90%"
        },
        "sensitivity_levels": ["low", "medium", "high"]
    }


@router.post("/session/start")
async def start_proctoring_session(
    request: StartSessionRequest,
    current_user: User = Depends(get_current_user)
) -> StartSessionResponse:
    """
    Start a new proctoring session for an interview.
    
    This should be called when the interview begins.
    Returns a session_id to use for subsequent frame analysis.
    """
    if not PROCTORING_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Proctoring system not available. Install mediapipe and deepface."
        )
    
    monitor = get_monitor()
    
    # Generate unique session ID
    session_id = f"proctor_{current_user.id}_{request.interview_id}_{datetime.utcnow().timestamp()}"
    
    # Start session
    monitor.start_session(
        session_id=session_id,
        user_id=current_user.id,
        interview_id=request.interview_id
    )
    
    return {
        "session_id": session_id,
        "status": "active",
        "features_available": {
            "face_detection": MEDIAPIPE_AVAILABLE,
            "gaze_tracking": MEDIAPIPE_AVAILABLE,
            "person_verification": DEEPFACE_AVAILABLE,
            "tab_switch_detection": True
        }
    }


@router.post("/session/reference-photo")
async def set_reference_photo(
    session_id: str,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Set reference photo for person verification.
    
    Upload a photo of the user to compare against during the interview.
    This helps detect if a different person takes over.
    """
    if not PROCTORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Proctoring not available")
    
    if not DEEPFACE_AVAILABLE:
        return {"status": "skipped", "reason": "DeepFace not available"}
    
    monitor = get_monitor()
    
    # Read and decode image
    contents = await photo.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    
    # Update session with reference
    session = monitor.sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session.reference_face_encoding = monitor._extract_face_encoding(image)
        return {"status": "success", "message": "Reference photo set"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract face: {str(e)}")


@router.post("/analyze-frame")
async def analyze_frame(
    request: FrameAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a video frame for anti-cheat violations.
    
    Send frames periodically (e.g., every 1-2 seconds) for analysis.
    Returns detected violations and alerts.
    """
    if not PROCTORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Proctoring not available")
    
    monitor = get_monitor()
    
    # Decode base64 image
    try:
        image_data = base64.b64decode(request.frame_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise ValueError("Could not decode image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
    
    # Analyze frame
    try:
        results = monitor.analyze_frame(
            session_id=request.session_id,
            frame=frame,
            check_person=request.verify_person
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tab-switch")
async def record_tab_switch(
    request: TabSwitchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Record a tab switch or window blur event.
    
    Called from frontend when:
    - User switches to another tab
    - Browser window loses focus
    """
    if not PROCTORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Proctoring not available")
    
    monitor = get_monitor()
    
    try:
        violation = monitor.process_tab_switch(
            session_id=request.session_id,
            event_type=request.event_type
        )
        return {
            "status": "recorded",
            "violation": {
                "type": violation.type.value,
                "severity": violation.severity.value,
                "timestamp": violation.timestamp.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/session/{session_id}/report")
async def get_session_report(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the proctoring report for a session.
    
    Returns:
    - Face visibility ratio
    - Attention ratio
    - Integrity score
    - Violation summary
    - Recommendation
    """
    if not PROCTORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Proctoring not available")
    
    monitor = get_monitor()
    
    try:
        report = monitor.get_session_report(session_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/session/{session_id}/end")
async def end_proctoring_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    End a proctoring session and get final report.
    
    This should be called when the interview ends.
    Returns the complete proctoring report with integrity assessment.
    """
    if not PROCTORING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Proctoring not available")
    
    monitor = get_monitor()
    
    try:
        report = monitor.end_session(session_id)
        return {
            "status": "completed",
            "report": report
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/capabilities")
async def get_capabilities():
    """
    Get detailed information about proctoring capabilities and accuracy.
    """
    return {
        "overview": "AI-powered proctoring system for interview integrity monitoring",
        "capabilities": [
            {
                "name": "Face Presence Detection",
                "description": "Detects if user's face is visible in frame",
                "technology": "MediaPipe Face Detection",
                "accuracy": "99%",
                "available": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False
            },
            {
                "name": "Multiple Face Detection",
                "description": "Detects if multiple people are visible (potential help)",
                "technology": "MediaPipe Face Detection",
                "accuracy": "95%",
                "available": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False
            },
            {
                "name": "Gaze/Eye Tracking",
                "description": "Tracks where user is looking (screen vs away)",
                "technology": "MediaPipe Face Mesh + Iris Tracking",
                "accuracy": "85-90%",
                "available": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False
            },
            {
                "name": "Head Pose Estimation",
                "description": "Estimates head orientation (looking at notes, etc.)",
                "technology": "MediaPipe Face Mesh + PnP Solver",
                "accuracy": "90%",
                "available": MEDIAPIPE_AVAILABLE if PROCTORING_AVAILABLE else False
            },
            {
                "name": "Person Verification",
                "description": "Verifies same person throughout interview",
                "technology": "DeepFace with Facenet",
                "accuracy": "97%",
                "available": DEEPFACE_AVAILABLE if PROCTORING_AVAILABLE else False
            },
            {
                "name": "Tab Switch Detection",
                "description": "Detects when user switches browser tabs",
                "technology": "Browser Visibility API",
                "accuracy": "100%",
                "available": True
            }
        ],
        "violation_types": [
            {"type": "no_face", "description": "Face not visible", "severity": "medium"},
            {"type": "multiple_faces", "description": "More than one face detected", "severity": "high"},
            {"type": "looking_away", "description": "User looking away from screen", "severity": "low"},
            {"type": "different_person", "description": "Different person detected", "severity": "critical"},
            {"type": "tab_switch", "description": "User switched tabs", "severity": "medium"},
            {"type": "window_blur", "description": "Browser window lost focus", "severity": "medium"}
        ],
        "requirements": {
            "mediapipe": "Face detection, gaze tracking, head pose",
            "deepface": "Person verification (optional)",
            "opencv-python": "Image processing"
        }
    }
