import speech_recognition as sr
import librosa
import numpy as np
from typing import Dict
import os
import soundfile as sf


class SpeechAnalyzer:
    """Analyze speech for clarity, fluency, and transcription"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def analyze_audio(self, audio_path: str) -> Dict:
        """Comprehensive audio analysis"""
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Transcribe audio
        transcription = self._transcribe_audio(audio_path)
        
        # Analyze audio properties
        audio_properties = self._analyze_audio_properties(audio_path)
        
        # Calculate clarity score
        clarity_score = self._calculate_clarity_score(audio_properties)
        
        # Calculate fluency score
        fluency_score = self._calculate_fluency_score(transcription, audio_properties)
        
        # Detect filler words
        filler_words = self._detect_filler_words(transcription)
        
        # Calculate speaking rate
        speaking_rate = self._calculate_speaking_rate(transcription, audio_properties["duration"])
        
        return {
            "transcription": transcription,
            "duration": audio_properties["duration"],
            "clarity_score": round(clarity_score, 2),
            "fluency_score": round(fluency_score, 2),
            "speaking_rate_wpm": round(speaking_rate, 2),
            "filler_words": filler_words,
            "audio_quality": audio_properties["quality"],
            "volume_consistency": audio_properties["volume_consistency"],
            "pauses": audio_properties["pauses"],
            "feedback": self._generate_speech_feedback(
                clarity_score, fluency_score, speaking_rate, filler_words
            )
        }
    
    def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio to text"""
        try:
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "[Unable to transcribe audio]"
            except sr.RequestError:
                # Fallback to basic transcription
                return "[Speech recognition service unavailable]"
                
        except Exception as e:
            print(f"Transcription error: {e}")
            return "[Error transcribing audio]"
    
    def _analyze_audio_properties(self, audio_path: str) -> Dict:
        """Analyze audio signal properties"""
        try:
            # Load audio file
            y, sr_rate = librosa.load(audio_path, sr=None)
            
            # Duration
            duration = len(y) / sr_rate
            
            # Volume/amplitude analysis
            rms = librosa.feature.rms(y=y)[0]
            avg_volume = np.mean(rms)
            volume_std = np.std(rms)
            volume_consistency = 100 - min((volume_std / avg_volume * 100), 100) if avg_volume > 0 else 0
            
            # Detect pauses (silence detection)
            threshold = np.mean(rms) * 0.3  # 30% of average
            is_silent = rms < threshold
            
            # Count pauses (consecutive silent frames)
            pause_count = 0
            in_pause = False
            pause_durations = []
            current_pause_len = 0
            
            hop_length = 512
            frame_duration = hop_length / sr_rate
            
            for silent in is_silent:
                if silent:
                    if not in_pause:
                        in_pause = True
                        current_pause_len = 1
                    else:
                        current_pause_len += 1
                else:
                    if in_pause:
                        pause_duration = current_pause_len * frame_duration
                        if pause_duration > 0.5:  # Only count pauses > 0.5 seconds
                            pause_count += 1
                            pause_durations.append(pause_duration)
                        in_pause = False
                        current_pause_len = 0
            
            # Audio quality based on signal-to-noise ratio (simplified)
            # Calculate zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            avg_zcr = np.mean(zcr)
            
            # Quality score (0-100)
            quality_score = min(100, (1 - min(avg_zcr, 0.5)) * 100)
            
            return {
                "duration": duration,
                "avg_volume": float(avg_volume),
                "volume_consistency": float(volume_consistency),
                "quality": float(quality_score),
                "pauses": {
                    "count": pause_count,
                    "avg_duration": float(np.mean(pause_durations)) if pause_durations else 0,
                    "total_pause_time": float(sum(pause_durations))
                }
            }
            
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return {
                "duration": 0,
                "avg_volume": 0,
                "volume_consistency": 50,
                "quality": 50,
                "pauses": {"count": 0, "avg_duration": 0, "total_pause_time": 0}
            }
    
    def _calculate_clarity_score(self, audio_properties: Dict) -> float:
        """Calculate speech clarity score"""
        score = 0
        
        # Audio quality (0-40 points)
        score += (audio_properties["quality"] / 100) * 40
        
        # Volume consistency (0-30 points)
        score += (audio_properties["volume_consistency"] / 100) * 30
        
        # Pause analysis (0-30 points)
        pause_score = 30
        pause_count = audio_properties["pauses"]["count"]
        duration = audio_properties["duration"]
        
        if duration > 0:
            pause_rate = pause_count / (duration / 60)  # Pauses per minute
            
            # Optimal: 2-4 pauses per minute
            if 2 <= pause_rate <= 4:
                pause_score = 30
            elif pause_rate < 2:
                pause_score = 20 + (pause_rate / 2) * 10
            else:
                pause_score = max(0, 30 - (pause_rate - 4) * 5)
        
        score += pause_score
        
        return min(score, 100)
    
    def _calculate_fluency_score(self, transcription: str, audio_properties: Dict) -> float:
        """Calculate speech fluency score"""
        if not transcription or transcription.startswith("["):
            return 0
        
        score = 0
        words = transcription.split()
        word_count = len(words)
        duration = audio_properties["duration"]
        
        if duration == 0:
            return 0
        
        # Speaking rate (0-40 points)
        wpm = (word_count / duration) * 60
        if 120 <= wpm <= 160:  # Optimal speaking rate
            score += 40
        elif 100 <= wpm < 120 or 160 < wpm <= 180:
            score += 30
        elif wpm < 100:
            score += (wpm / 100) * 20
        else:  # Too fast
            score += max(0, 40 - (wpm - 180) * 0.5)
        
        # Pause appropriateness (0-30 points)
        pause_time = audio_properties["pauses"]["total_pause_time"]
        pause_ratio = pause_time / duration if duration > 0 else 0
        
        # Optimal pause ratio: 15-25%
        if 0.15 <= pause_ratio <= 0.25:
            score += 30
        elif 0.10 <= pause_ratio < 0.15 or 0.25 < pause_ratio <= 0.30:
            score += 20
        else:
            score += 10
        
        # Word variety (0-30 points)
        if word_count > 0:
            unique_words = len(set(words))
            variety_ratio = unique_words / word_count
            score += min(30, variety_ratio * 60)
        
        return min(score, 100)
    
    def _detect_filler_words(self, transcription: str) -> Dict:
        """Detect filler words in transcription"""
        filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 
                       'literally', 'sort of', 'kind of', 'i mean']
        
        transcription_lower = transcription.lower()
        detected = {}
        total_count = 0
        
        for filler in filler_words:
            count = transcription_lower.count(filler)
            if count > 0:
                detected[filler] = count
                total_count += count
        
        words = transcription.split()
        filler_percentage = (total_count / len(words) * 100) if words else 0
        
        return {
            "detected": detected,
            "total_count": total_count,
            "percentage": round(filler_percentage, 2)
        }
    
    def _calculate_speaking_rate(self, transcription: str, duration: float) -> float:
        """Calculate words per minute"""
        if duration == 0:
            return 0
        
        word_count = len(transcription.split())
        wpm = (word_count / duration) * 60
        
        return wpm
    
    def _generate_speech_feedback(
        self,
        clarity_score: float,
        fluency_score: float,
        speaking_rate: float,
        filler_words: Dict
    ) -> str:
        """Generate feedback on speech quality"""
        feedback_parts = []
        
        # Overall assessment
        avg_score = (clarity_score + fluency_score) / 2
        
        if avg_score >= 80:
            feedback_parts.append("Excellent speech clarity and fluency!")
        elif avg_score >= 60:
            feedback_parts.append("Good speech quality with some areas for improvement.")
        else:
            feedback_parts.append("Your speech quality needs significant improvement.")
        
        # Specific feedback
        if clarity_score < 70:
            feedback_parts.append("Try to speak more clearly and maintain consistent volume.")
        
        if fluency_score < 70:
            if speaking_rate < 100:
                feedback_parts.append("Try to speak a bit faster for better fluency.")
            elif speaking_rate > 180:
                feedback_parts.append("Slow down slightly to improve clarity.")
        
        if filler_words["percentage"] > 5:
            feedback_parts.append(f"Reduce filler words (detected {filler_words['total_count']} times).")
        
        return " ".join(feedback_parts)
