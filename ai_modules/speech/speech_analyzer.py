import librosa
import numpy as np
from typing import Dict, Optional
import os
import soundfile as sf

# Try to import Whisper (preferred) or fallback to speech_recognition
WHISPER_AVAILABLE = False
SPEECH_RECOGNITION_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    pass

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    pass


class SpeechAnalyzer:
    """
    Analyze speech for clarity, fluency, and transcription.
    
    Uses OpenAI Whisper for high-accuracy transcription (97%+).
    Falls back to Google Speech Recognition if Whisper unavailable.
    
    Whisper Models:
    - tiny: Fastest, ~32x realtime, ~72% accuracy
    - base: Fast, ~16x realtime, ~82% accuracy  
    - small: Balanced, ~6x realtime, ~90% accuracy (RECOMMENDED)
    - medium: Accurate, ~2x realtime, ~95% accuracy
    - large: Most accurate, ~1x realtime, ~97% accuracy
    """
    
    def __init__(self, whisper_model: str = "small"):
        """
        Initialize speech analyzer.
        
        Args:
            whisper_model: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
                          Larger models are more accurate but slower.
        """
        self.whisper_model_name = whisper_model
        self.whisper_model = None
        self.recognizer = None
        
        # Initialize Whisper if available (preferred)
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model(whisper_model)
                print(f"Whisper model '{whisper_model}' loaded successfully")
            except Exception as e:
                print(f"Failed to load Whisper model: {e}")
        
        # Fallback to speech_recognition
        if self.whisper_model is None and SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            print("Using Google Speech Recognition (fallback)")
        
        if self.whisper_model is None and self.recognizer is None:
            print("WARNING: No speech recognition backend available!")
    
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
            "transcription_backend": self.get_transcription_backend(),
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
        """
        Transcribe audio to text using Whisper (preferred) or Google Speech API.
        
        Whisper provides ~97% accuracy vs ~85% for Google Speech Recognition.
        """
        # Try Whisper first (more accurate)
        if self.whisper_model is not None:
            return self._transcribe_with_whisper(audio_path)
        
        # Fallback to Google Speech Recognition
        if self.recognizer is not None:
            return self._transcribe_with_google(audio_path)
        
        return "[No speech recognition backend available]"
    
    def _transcribe_with_whisper(self, audio_path: str) -> str:
        """
        Transcribe using OpenAI Whisper.
        
        Whisper is a state-of-the-art speech recognition model with:
        - 97%+ accuracy for English
        - Robust to background noise
        - Handles accents well
        - Works offline
        """
        try:
            # Whisper can directly process audio files
            result = self.whisper_model.transcribe(
                audio_path,
                language="en",  # Can be None for auto-detect
                fp16=False,  # Use FP32 for CPU compatibility
                verbose=False
            )
            
            transcription = result.get("text", "").strip()
            
            if not transcription:
                return "[No speech detected in audio]"
            
            return transcription
            
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            # Try fallback to Google if available
            if self.recognizer is not None:
                return self._transcribe_with_google(audio_path)
            return f"[Transcription error: {str(e)}]"
    
    def _transcribe_with_google(self, audio_path: str) -> str:
        """
        Transcribe using Google Speech Recognition (fallback).
        
        Less accurate (~85%) but doesn't require model download.
        Requires internet connection.
        """
        try:
            import speech_recognition as sr
            
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "[Unable to transcribe audio - speech not clear]"
            except sr.RequestError:
                return "[Speech recognition service unavailable - check internet]"
                
        except Exception as e:
            print(f"Google transcription error: {e}")
            return "[Error transcribing audio]"
    
    def get_transcription_backend(self) -> str:
        """Return which transcription backend is being used"""
        if self.whisper_model is not None:
            return f"whisper-{self.whisper_model_name}"
        elif self.recognizer is not None:
            return "google-speech-recognition"
        return "none"
    
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
            # Natural speech has ~30-50% volume variation, be more lenient
            # Coefficient of variation (CV) = std/mean
            cv = volume_std / avg_volume if avg_volume > 0 else 1.0
            # CV of 0.3-0.6 is normal for speech, only penalize extremes
            if cv < 0.3:
                volume_consistency = 90  # Very consistent (possibly monotone)
            elif cv < 0.7:
                volume_consistency = 85 - (cv - 0.3) * 25  # Normal range: 75-85
            elif cv < 1.0:
                volume_consistency = 75 - (cv - 0.7) * 50  # Slightly variable: 60-75  
            else:
                volume_consistency = max(40, 60 - (cv - 1.0) * 30)  # Very variable
            
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
            
            # Audio quality based on multiple factors
            # 1. Zero crossing rate (normalized - speech typically 0.05-0.15)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            avg_zcr = np.mean(zcr)
            # ZCR contribution: Speech ZCR ~0.05-0.15 is good, penalize extremes
            if avg_zcr < 0.05:
                zcr_score = 60 + avg_zcr * 200  # Low ZCR (possible silence/noise)
            elif avg_zcr < 0.20:
                zcr_score = 80 + (0.15 - abs(avg_zcr - 0.10)) * 100  # Optimal range
            else:
                zcr_score = max(50, 90 - (avg_zcr - 0.15) * 100)  # High ZCR
            
            # 2. RMS energy - ensure there's actual audio content
            energy_score = min(100, avg_volume * 5000)  # Scale for typical mic input
            
            # 3. Spectral centroid - higher values indicate clearer speech
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr_rate)[0]
            avg_centroid = np.mean(spectral_centroid)
            # Human speech typically 200-4000 Hz centroid
            if 500 < avg_centroid < 3000:
                centroid_score = 85 + min(15, (avg_centroid - 500) / 100)
            else:
                centroid_score = 60
            
            # Combined quality score (weighted average)
            quality_score = min(100, (zcr_score * 0.3 + energy_score * 0.3 + centroid_score * 0.4))
            
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
        """
        Calculate speech clarity score using structured scoring bands:
        
        SCORING BANDS:
        - 80-100: Excellent - Crystal clear audio, consistent volume, natural pauses
        - 60-80: Good - Clear audio with minor volume variations
        - 40-60: Average - Acceptable clarity with noticeable issues
        - 20-40: Poor - Muffled/unclear audio, inconsistent volume
        - 0-20: Very Poor - Barely audible or no audio
        """
        audio_quality = audio_properties.get("quality", 0)
        volume_consistency = audio_properties.get("volume_consistency", 0)
        duration = audio_properties.get("duration", 0)
        pause_count = audio_properties.get("pauses", {}).get("count", 0)
        
        # No audio or very short
        if duration < 1:
            return 5.0
        
        # Calculate pause effectiveness
        pause_rate = pause_count / (duration / 60) if duration > 0 else 0
        
        # BAND 5: Excellent Clarity (80-100)
        # High quality audio + consistent volume + natural pauses
        if audio_quality >= 70 and volume_consistency >= 70:
            if 2 <= pause_rate <= 5:
                return 85 + min(15, (audio_quality - 70) * 0.5 + (volume_consistency - 70) * 0.3)
            else:
                return 80 + min(10, (audio_quality - 70) * 0.3)
        
        # BAND 4: Good Clarity (60-80)
        # Decent quality with minor issues
        if audio_quality >= 50 and volume_consistency >= 50:
            base = 60
            base += (audio_quality - 50) * 0.4  # Up to +8 from quality
            base += (volume_consistency - 50) * 0.3  # Up to +6 from volume
            if 1 <= pause_rate <= 6:
                base += 5  # Reasonable pause pattern
            return min(79, base)
        
        # BAND 3: Average Clarity (40-60)
        # Noticeable issues but acceptable
        if audio_quality >= 30 and volume_consistency >= 30:
            base = 40
            base += (audio_quality - 30) * 0.5  # Up to +10
            base += (volume_consistency - 30) * 0.4  # Up to +8
            return min(59, base)
        
        # BAND 2: Poor Clarity (20-40)
        # Significant issues - hard to understand
        if audio_quality >= 15 or volume_consistency >= 15:
            base = 20
            base += max(audio_quality, volume_consistency) * 0.5
            return min(39, base)
        
        # BAND 1: Very Poor (0-20)
        # Barely audible or major distortion
        return max(5, audio_quality * 0.5 + volume_consistency * 0.3)
    
    def _calculate_fluency_score(self, transcription: str, audio_properties: Dict) -> float:
        """
        Calculate speech fluency score using structured scoring bands:
        
        SCORING BANDS:
        - 80-100: Excellent - Natural pace (120-160 wpm), varied vocabulary, good rhythm
        - 60-80: Good - Slightly fast/slow but maintains flow
        - 40-60: Average - Noticeable hesitation or rushed sections
        - 20-40: Poor - Frequent stops, very slow/fast, monotonous
        - 0-20: Very Poor - No fluency, single words, major speech issues
        """
        if not transcription or transcription.startswith("["):
            return 5.0  # No speech detected
        
        words = transcription.split()
        word_count = len(words)
        duration = audio_properties.get("duration", 0)
        
        if duration < 1:
            return 5.0
        
        if word_count < 3:
            return 10.0  # Almost no speech
        
        # Calculate metrics
        wpm = (word_count / duration) * 60
        pause_time = audio_properties.get("pauses", {}).get("total_pause_time", 0)
        pause_ratio = pause_time / duration if duration > 0 else 0
        unique_words = len(set(word.lower() for word in words))
        variety_ratio = unique_words / word_count if word_count > 0 else 0
        
        # Detect filler words in transcription
        filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually']
        filler_count = sum(transcription.lower().count(filler) for filler in filler_words)
        filler_ratio = filler_count / word_count if word_count > 0 else 0
        
        # BAND 5: Excellent Fluency (80-100)
        # Optimal pace + good variety + natural pauses + few fillers
        if 110 <= wpm <= 170 and variety_ratio >= 0.5 and filler_ratio < 0.05:
            base = 80
            # Bonus for optimal range (120-160 is ideal)
            if 120 <= wpm <= 160:
                base += 8
            # Bonus for high variety
            if variety_ratio >= 0.6:
                base += 5
            # Bonus for good pause ratio
            if 0.12 <= pause_ratio <= 0.28:
                base += 5
            return min(100, base)
        
        # BAND 4: Good Fluency (60-80)
        # Slightly off pace but maintains flow
        if 90 <= wpm <= 190 and variety_ratio >= 0.35 and filler_ratio < 0.10:
            base = 60
            # Adjust for pace
            if 100 <= wpm <= 180:
                base += 8
            # Adjust for variety
            base += min(7, (variety_ratio - 0.35) * 30)
            # Pause penalty/bonus
            if 0.10 <= pause_ratio <= 0.35:
                base += 4
            return min(79, base)
        
        # BAND 3: Average Fluency (40-60)
        # Noticeable issues but acceptable
        if 60 <= wpm <= 220 and variety_ratio >= 0.25:
            base = 40
            # Adjust for pace (penalize extremes)
            if wpm < 80:
                base += (wpm - 60) * 0.3
            elif wpm > 200:
                base += max(0, 10 - (wpm - 200) * 0.2)
            else:
                base += 10
            # Adjust for variety
            base += min(8, (variety_ratio - 0.25) * 25)
            return min(59, base)
        
        # BAND 2: Poor Fluency (20-40)
        # Too slow/fast, low variety, many fillers
        if word_count >= 5 and (40 <= wpm <= 250 or variety_ratio >= 0.15):
            base = 20
            if 50 <= wpm <= 230:
                base += 8
            if variety_ratio >= 0.2:
                base += 6
            if filler_ratio < 0.20:
                base += 4
            return min(39, base)
        
        # BAND 1: Very Poor (0-20)
        # Major fluency issues
        base = 10
        if word_count >= 10:
            base += 5
        if variety_ratio >= 0.15:
            base += 3
        return min(19, base)
    
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
        """
        Generate feedback on speech quality using scoring bands:
        
        FEEDBACK BANDS (based on average of clarity and fluency):
        - 80-100: Excellent - Professional quality speech
        - 60-80: Good - Minor improvements suggested
        - 40-60: Average - Clear areas to work on
        - 20-40: Poor - Significant practice needed
        - 0-20: Very Poor - Fundamental issues to address
        """
        feedback_parts = []
        avg_score = (clarity_score + fluency_score) / 2
        filler_percentage = filler_words.get("percentage", 0) if isinstance(filler_words, dict) else 0
        filler_count = filler_words.get("total_count", 0) if isinstance(filler_words, dict) else 0
        
        # BAND 5: Excellent (80-100)
        if avg_score >= 80:
            feedback_parts.append("Excellent speech quality! Your clarity and fluency are professional-level.")
            if 120 <= speaking_rate <= 160:
                feedback_parts.append("Your speaking pace is ideal for interviews.")
            if filler_percentage < 2:
                feedback_parts.append("You use minimal filler words - very polished delivery.")
        
        # BAND 4: Good (60-80)
        elif avg_score >= 60:
            feedback_parts.append("Good speech quality with minor areas for improvement.")
            if clarity_score < 70:
                feedback_parts.append("Work on speaking more clearly with consistent volume.")
            if fluency_score < 70:
                if speaking_rate < 100:
                    feedback_parts.append("Try speaking slightly faster to improve flow.")
                elif speaking_rate > 180:
                    feedback_parts.append("Slow down a bit to enhance clarity.")
            if filler_percentage > 3:
                feedback_parts.append(f"Reduce filler words (used {filler_count} times). Practice pausing instead.")
        
        # BAND 3: Average (40-60)
        elif avg_score >= 40:
            feedback_parts.append("Your speech quality is average. Practice will help significantly.")
            if clarity_score < 50:
                feedback_parts.append("Focus on speaking more clearly - project your voice and enunciate.")
            if fluency_score < 50:
                if speaking_rate < 80:
                    feedback_parts.append("You speak too slowly. Practice speaking at 120-150 words per minute.")
                elif speaking_rate > 200:
                    feedback_parts.append("You speak too fast. Slow down to let your words be understood.")
                else:
                    feedback_parts.append("Work on speaking more smoothly with fewer hesitations.")
            if filler_percentage > 5:
                feedback_parts.append(f"Too many filler words ({filler_count} detected). Record yourself and practice eliminating them.")
        
        # BAND 2: Poor (20-40)
        elif avg_score >= 20:
            feedback_parts.append("Your speech needs significant work. Consider practicing with a speech coach or recording yourself.")
            if clarity_score < 40:
                feedback_parts.append("Your voice is hard to understand. Practice speaking clearly in a quiet environment.")
            if fluency_score < 40:
                feedback_parts.append("Your speech lacks fluency. Practice reading aloud daily to improve flow.")
            if filler_percentage > 8:
                feedback_parts.append(f"Excessive filler words ({filler_count} detected). This severely impacts your communication.")
        
        # BAND 1: Very Poor (0-20)
        else:
            feedback_parts.append("Your speech quality needs fundamental improvement.")
            feedback_parts.append("Recommendations: 1) Practice speaking clearly in short sentences.")
            feedback_parts.append("2) Record yourself and listen back to identify issues.")
            feedback_parts.append("3) Consider working with a speech coach or joining speaking groups.")
        
        return " ".join(feedback_parts)
