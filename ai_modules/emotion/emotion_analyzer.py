import cv2
import numpy as np
from typing import Dict, List
import os


class EmotionAnalyzer:
    """Analyze emotions and confidence from video"""
    
    def __init__(self):
        self.emotion_detector = None
        self._initialize_detector()
    
    def _initialize_detector(self):
        """Initialize emotion detection model"""
        try:
            from fer import FER
            self.emotion_detector = FER(mtcnn=True)
        except ImportError:
            print("Warning: FER not installed. Emotion detection will be limited.")
            self.emotion_detector = None
        except Exception as e:
            print(f"Warning: Could not initialize FER: {e}")
            self.emotion_detector = None
    
    def analyze_video(self, video_path: str, sample_rate: int = 2) -> Dict:
        """Analyze emotions throughout video"""
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        # Sample frames for analysis
        frame_interval = int(fps * sample_rate)  # Sample every N seconds
        
        emotions_timeline = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Analyze every Nth frame
            if frame_count % frame_interval == 0:
                emotion_data = self._analyze_frame(frame, frame_count / fps if fps > 0 else 0)
                if emotion_data:
                    emotions_timeline.append(emotion_data)
            
            frame_count += 1
        
        cap.release()
        
        # Aggregate results
        result = self._aggregate_emotions(emotions_timeline, duration)
        
        return result
    
    def _analyze_frame(self, frame, timestamp: float) -> Dict:
        """Analyze emotions in a single frame"""
        if self.emotion_detector is None:
            # Fallback to basic analysis
            return self._basic_frame_analysis(frame, timestamp)
        
        try:
            # Detect emotions
            result = self.emotion_detector.detect_emotions(frame)
            
            if result and len(result) > 0:
                # Take the first face detected
                face = result[0]
                emotions = face['emotions']
                
                # Get dominant emotion
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                
                return {
                    "timestamp": timestamp,
                    "emotions": emotions,
                    "dominant_emotion": dominant_emotion[0],
                    "dominant_score": dominant_emotion[1],
                    "face_detected": True
                }
            else:
                return {
                    "timestamp": timestamp,
                    "face_detected": False
                }
                
        except Exception as e:
            print(f"Frame analysis error: {e}")
            return self._basic_frame_analysis(frame, timestamp)
    
    def _basic_frame_analysis(self, frame, timestamp: float) -> Dict:
        """Basic frame analysis without emotion detection"""
        # Detect face using OpenCV's Haar Cascade
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return {
            "timestamp": timestamp,
            "face_detected": len(faces) > 0,
            "face_count": len(faces)
        }
    
    def _aggregate_emotions(self, emotions_timeline: List[Dict], duration: float) -> Dict:
        """Aggregate emotion data from timeline"""
        
        if not emotions_timeline:
            return {
                "confidence_score": 0,
                "dominant_emotion": "unknown",
                "emotion_distribution": {},
                "emotional_stability": 0,
                "face_visibility": 0,
                "feedback": "Could not analyze emotions. Ensure your face is visible in the camera."
            }
        
        # Count frames with face detected
        faces_detected = sum(1 for e in emotions_timeline if e.get("face_detected", False))
        face_visibility = (faces_detected / len(emotions_timeline)) * 100 if emotions_timeline else 0
        
        # Aggregate emotions from frames with detected faces
        valid_frames = [e for e in emotions_timeline if e.get("face_detected", False) and "emotions" in e]
        
        if not valid_frames:
            return {
                "confidence_score": 50,
                "dominant_emotion": "neutral",
                "emotion_distribution": {},
                "emotional_stability": 50,
                "face_visibility": face_visibility,
                "feedback": "Limited emotion data available. Try to keep your face visible to the camera."
            }
        
        # Aggregate emotion scores
        emotion_totals = {}
        for frame in valid_frames:
            for emotion, score in frame["emotions"].items():
                if emotion not in emotion_totals:
                    emotion_totals[emotion] = []
                emotion_totals[emotion].append(score)
        
        # Calculate average for each emotion
        emotion_distribution = {
            emotion: sum(scores) / len(scores)
            for emotion, scores in emotion_totals.items()
        }
        
        # Find dominant emotion
        dominant_emotion = max(emotion_distribution.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence score based on positive emotions
        confidence_emotions = ["happy", "neutral"]
        stress_emotions = ["fear", "sad", "angry"]
        
        confidence_score = sum(
            emotion_distribution.get(e, 0) for e in confidence_emotions
        )
        stress_score = sum(
            emotion_distribution.get(e, 0) for e in stress_emotions
        )
        
        # Normalize confidence score (0-100)
        total_score = confidence_score + stress_score
        if total_score > 0:
            confidence_score = (confidence_score / total_score) * 100
        else:
            confidence_score = 50
        
        # Calculate emotional stability (how much emotions fluctuate)
        emotion_changes = []
        for i in range(1, len(valid_frames)):
            prev_emotion = valid_frames[i-1]["dominant_emotion"]
            curr_emotion = valid_frames[i]["dominant_emotion"]
            if prev_emotion != curr_emotion:
                emotion_changes.append(1)
            else:
                emotion_changes.append(0)
        
        if emotion_changes:
            stability = (1 - (sum(emotion_changes) / len(emotion_changes))) * 100
        else:
            stability = 80
        
        # Generate feedback
        feedback = self._generate_emotion_feedback(
            confidence_score, dominant_emotion, stability, face_visibility
        )
        
        return {
            "confidence_score": round(confidence_score, 2),
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": {k: round(v, 2) for k, v in emotion_distribution.items()},
            "emotional_stability": round(stability, 2),
            "face_visibility": round(face_visibility, 2),
            "timeline": emotions_timeline,
            "feedback": feedback
        }
    
    def _generate_emotion_feedback(
        self,
        confidence_score: float,
        dominant_emotion: str,
        stability: float,
        face_visibility: float
    ) -> str:
        """Generate feedback based on emotion analysis"""
        feedback_parts = []
        
        # Confidence feedback
        if confidence_score >= 70:
            feedback_parts.append("You demonstrated good confidence throughout the interview.")
        elif confidence_score >= 50:
            feedback_parts.append("Your confidence level was moderate. Try to appear more relaxed and positive.")
        else:
            feedback_parts.append("Work on appearing more confident. Practice relaxation techniques before interviews.")
        
        # Emotion feedback
        if dominant_emotion in ["happy", "neutral"]:
            feedback_parts.append("Your emotional state was appropriate for an interview.")
        elif dominant_emotion == "surprise":
            feedback_parts.append("You showed surprise reactions. Try to maintain composure.")
        elif dominant_emotion in ["fear", "sad", "angry"]:
            feedback_parts.append("Try to manage stress better and maintain a positive demeanor.")
        
        # Stability feedback
        if stability < 60:
            feedback_parts.append("Your emotions fluctuated significantly. Practice maintaining emotional stability.")
        
        # Face visibility
        if face_visibility < 80:
            feedback_parts.append("Ensure your face is clearly visible to the camera throughout the interview.")
        
        return " ".join(feedback_parts)
    
    def analyze_image(self, image_path: str) -> Dict:
        """Analyze emotions in a single image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        frame = cv2.imread(image_path)
        
        if frame is None:
            raise ValueError("Could not read image file")
        
        result = self._analyze_frame(frame, 0)
        
        if result.get("face_detected", False):
            confidence_score = result.get("emotions", {}).get("happy", 0) * 50 + \
                             result.get("emotions", {}).get("neutral", 0) * 50
            
            return {
                "confidence_score": round(confidence_score, 2),
                "dominant_emotion": result.get("dominant_emotion", "unknown"),
                "emotion_distribution": result.get("emotions", {}),
                "face_detected": True
            }
        else:
            return {
                "confidence_score": 0,
                "face_detected": False,
                "feedback": "No face detected in the image"
            }
