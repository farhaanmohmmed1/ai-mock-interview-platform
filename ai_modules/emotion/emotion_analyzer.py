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
            from fer.fer import FER
            # Use mtcnn=False for faster initialization and fewer dependencies
            self.emotion_detector = FER(mtcnn=False)
            print("[EmotionAnalyzer] FER initialized successfully")
        except ImportError as e:
            print(f"Warning: FER not installed ({e}). Emotion detection will be limited.")
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
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Prevent division by zero for sample interval
            frame_interval = max(1, int(fps * sample_rate)) if fps > 0 else 1
            
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
            
            # Aggregate results
            result = self._aggregate_emotions(emotions_timeline, duration)
            
            return result
        finally:
            # Ensure video capture is released even if an exception occurs
            cap.release()
    
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
        """
        Aggregate emotion data from timeline using structured scoring bands:
        
        EXPRESSION/CONFIDENCE SCORING BANDS:
        - 80-100: Excellent - Confident, happy/neutral, stable emotions, high visibility
        - 60-80: Good - Mostly positive, some variations, good visibility
        - 40-60: Average - Mixed emotions, moderate stability
        - 20-40: Poor - Stressed/nervous, unstable emotions
        - 0-20: Very Poor - Face rarely visible, fear/anger dominant
        """
        
        if not emotions_timeline:
            return {
                "confidence_score": 10,
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
            # BAND 1: Very Poor - No face data
            return {
                "confidence_score": 15,
                "dominant_emotion": "neutral",
                "emotion_distribution": {},
                "emotional_stability": 30,
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
            stability = 75
        
        # Calculate positive and negative emotion scores
        confidence_emotions = ["happy", "neutral"]
        stress_emotions = ["fear", "sad", "angry"]
        
        positive_score = sum(emotion_distribution.get(e, 0) for e in confidence_emotions)
        stress_score = sum(emotion_distribution.get(e, 0) for e in stress_emotions)
        
        # Apply scoring bands
        # BAND 5: Excellent Expression (80-100)
        # High positive emotions + stable + visible face
        if positive_score >= 0.6 and stress_score < 0.15 and stability >= 70 and face_visibility >= 80:
            confidence_score = 80
            if positive_score >= 0.75:
                confidence_score += 6
            if stability >= 85:
                confidence_score += 5
            if face_visibility >= 95:
                confidence_score += 4
            if dominant_emotion in ["happy", "neutral"]:
                confidence_score += 3
            confidence_score = min(100, confidence_score)
        
        # BAND 4: Good Expression (60-80)
        elif positive_score >= 0.45 and stress_score < 0.25 and stability >= 50 and face_visibility >= 60:
            confidence_score = 60
            confidence_score += min(8, (positive_score - 0.45) * 40)
            confidence_score += min(5, (stability - 50) * 0.15)
            confidence_score += min(4, (face_visibility - 60) * 0.1)
            confidence_score = min(79, confidence_score)
        
        # BAND 3: Average Expression (40-60)
        elif positive_score >= 0.3 and stress_score < 0.4 and stability >= 30 and face_visibility >= 40:
            confidence_score = 40
            confidence_score += min(8, (positive_score - 0.3) * 35)
            confidence_score += min(6, (stability - 30) * 0.15)
            confidence_score += min(4, (face_visibility - 40) * 0.1)
            confidence_score = min(59, confidence_score)
        
        # BAND 2: Poor Expression (20-40)
        elif face_visibility >= 20 and stress_score < 0.6:
            confidence_score = 20
            if positive_score >= 0.15:
                confidence_score += 6
            if stability >= 20:
                confidence_score += 5
            confidence_score += min(6, (face_visibility - 20) * 0.1)
            confidence_score = min(39, confidence_score)
        
        # BAND 1: Very Poor (0-20)
        else:
            confidence_score = 10
            if face_visibility >= 10:
                confidence_score += 3
            if positive_score >= 0.1:
                confidence_score += 3
            confidence_score = min(19, confidence_score)
        
        # Generate feedback
        feedback = self._generate_emotion_feedback(
            confidence_score, dominant_emotion, stability, face_visibility
        )
        
        return {
            "confidence_score": round(confidence_score, 2),
            "expression_score": round(confidence_score, 2),
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
        """
        Generate feedback based on emotion analysis using scoring bands:
        
        FEEDBACK BANDS:
        - 80-100: Excellent performance feedback
        - 60-80: Good with minor suggestions
        - 40-60: Average with improvement areas
        - 20-40: Needs significant work
        - 0-20: Critical issues to address
        """
        feedback_parts = []
        
        # BAND 5: Excellent (80-100)
        if confidence_score >= 80:
            feedback_parts.append("Excellent! You appeared highly confident and composed throughout the interview.")
            if dominant_emotion == "happy":
                feedback_parts.append("Your positive demeanor was very professional.")
            elif dominant_emotion == "neutral":
                feedback_parts.append("You maintained a professional, composed expression.")
        
        # BAND 4: Good (60-80)
        elif confidence_score >= 60:
            feedback_parts.append("Good confidence level. You appeared reasonably composed during the interview.")
            if dominant_emotion in ["happy", "neutral"]:
                feedback_parts.append("Your emotional state was appropriate.")
            else:
                feedback_parts.append("Try to maintain a more neutral or positive expression.")
            if stability < 70:
                feedback_parts.append("Work on keeping your emotions more consistent.")
        
        # BAND 3: Average (40-60)
        elif confidence_score >= 40:
            feedback_parts.append("Your confidence level was moderate. Practice appearing more relaxed and assured.")
            if dominant_emotion in ["fear", "sad"]:
                feedback_parts.append("You appeared somewhat nervous. Deep breathing exercises before interviews can help.")
            elif dominant_emotion == "surprise":
                feedback_parts.append("You showed surprise reactions - try to maintain composure even for unexpected questions.")
            if stability < 50:
                feedback_parts.append("Your emotions fluctuated noticeably. Practice maintaining emotional stability.")
        
        # BAND 2: Poor (20-40)
        elif confidence_score >= 20:
            feedback_parts.append("Work on appearing more confident. Your nervousness was noticeable.")
            if dominant_emotion in ["fear", "sad", "angry"]:
                feedback_parts.append("Stress management techniques and mock interview practice are recommended.")
            feedback_parts.append("Consider practicing in front of a mirror to become aware of your expressions.")
        
        # BAND 1: Very Poor (0-20)
        else:
            feedback_parts.append("Your confidence needs significant improvement. Consider extensive mock interview practice.")
            feedback_parts.append("Relaxation techniques, preparation, and practice are essential before your next interview.")
        
        # Face visibility feedback (applicable to all bands)
        if face_visibility < 50:
            feedback_parts.append("IMPORTANT: Ensure your face is clearly visible to the camera throughout the interview.")
        elif face_visibility < 80:
            feedback_parts.append("Try to keep your face visible to the camera at all times.")
        
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
            # Apply scoring bands for single image
            emotions = result.get("emotions", {})
            positive_score = emotions.get("happy", 0) + emotions.get("neutral", 0)
            stress_score = emotions.get("fear", 0) + emotions.get("sad", 0) + emotions.get("angry", 0)
            
            # Simple band assignment for single image
            if positive_score >= 0.7 and stress_score < 0.1:
                confidence_score = 85
            elif positive_score >= 0.5 and stress_score < 0.2:
                confidence_score = 70
            elif positive_score >= 0.35 and stress_score < 0.35:
                confidence_score = 50
            elif positive_score >= 0.2:
                confidence_score = 35
            else:
                confidence_score = 15
            
            return {
                "confidence_score": round(confidence_score, 2),
                "dominant_emotion": result.get("dominant_emotion", "unknown"),
                "emotion_distribution": emotions,
                "face_detected": True
            }
        else:
            return {
                "confidence_score": 10,
                "face_detected": False,
                "feedback": "No face detected in the image"
            }
