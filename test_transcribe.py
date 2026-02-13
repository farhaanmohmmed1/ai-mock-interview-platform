import tempfile
import os

# Create a simple WAV file for testing
import numpy as np
from scipy.io import wavfile

# Generate 2 seconds of sine wave (440Hz tone)
sample_rate = 16000
duration = 2.0
t = np.linspace(0, duration, int(sample_rate * duration))
audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)

temp_dir = tempfile.mkdtemp()
wav_path = os.path.join(temp_dir, 'test.wav')
wavfile.write(wav_path, sample_rate, audio)
print(f'Created test WAV at: {wav_path}')

# Test transcription
from ai_modules.speech.speech_analyzer import SpeechAnalyzer
analyzer = SpeechAnalyzer()
print(f"Backend: {analyzer.get_transcription_backend()}")
result = analyzer.analyze_audio(wav_path)
print(f"Transcription: {result.get('transcription', '')}")
print(f"Duration: {result.get('duration', 0)}")
