import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  TextField,
  LinearProgress,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  AppBar,
  Toolbar,
  Snackbar,
} from '@mui/material';
import ProctoringClient from '../proctoring';
import {
  Videocam,
  VideocamOff,
  Send,
  NavigateNext,
  NavigateBefore,
  ExitToApp,
  Timer,
  QuestionAnswer,
  CheckCircle,
  Mic,
  MicOff,
  Stop,
  FiberManualRecord,
  SkipNext,
  VolumeUp,
  VolumeOff,
} from '@mui/icons-material';
import { useAuth } from '../App';
import API_URL from '../config';

const Interview = () => {
  const { type } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const isRecordingRef = useRef(false);
  const accumulatedTranscriptRef = useRef('');

  // Get data from setup page
  const setupData = location.state || {};

  // Interview state
  const [loading, setLoading] = useState(!setupData.interviewId);
  const [error, setError] = useState('');
  const [interviewId, setInterviewId] = useState(setupData.interviewId || null);
  const [questions, setQuestions] = useState(setupData.questions || []);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [currentAnswer, setCurrentAnswer] = useState('');
  const currentAnswerRef = useRef('');
  const [submitting, setSubmitting] = useState(false);
  const [questionStartTime, setQuestionStartTime] = useState(null);
  const [interviewMode, setInterviewMode] = useState(setupData.mode || 'standard');
  const [difficulty, setDifficulty] = useState(setupData.difficulty || 'medium');
  
  // Webcam state
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [cameraError, setCameraError] = useState('');
  
  // Audio recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcribing, setTranscribing] = useState(false);
  const [liveTranscriptSupported, setLiveTranscriptSupported] = useState(true);
  
  // Dialog state
  const [exitDialogOpen, setExitDialogOpen] = useState(false);
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false);

  // Text-to-speech state
  const [isSpeaking, setIsSpeaking] = useState(false);
  const speechSynthRef = useRef(window.speechSynthesis);

  // Round-based interview state (for full interview mode)
  const [currentRound, setCurrentRound] = useState(0); // 0: General, 1: Technical, 2: HR
  const [roundTransitionOpen, setRoundTransitionOpen] = useState(false);
  const [roundTimeLeft, setRoundTimeLeft] = useState(null);
  const roundTimerRef = useRef(null);
  
  // Round configuration
  const rounds = [
    { name: 'General Round', key: 'general', duration: 10 * 60, color: '#10B981' }, // 10 minutes
    { name: 'Technical Round', key: 'technical', duration: 15 * 60, color: '#3B82F6' }, // 15 minutes
    { name: 'HR Round', key: 'hr', duration: 10 * 60, color: '#F59E0B' }, // 10 minutes
  ];
  
  const isFullInterview = type === 'full';

  // Proctoring state
  const proctoringClientRef = useRef(null);
  const [proctoringActive, setProctoringActive] = useState(false);
  const [proctoringAlert, setProctoringAlert] = useState('');
  const [tabSwitchCount, setTabSwitchCount] = useState(0);
  const [proctoringViolations, setProctoringViolations] = useState([]);

  // Keep currentAnswerRef in sync with currentAnswer
  useEffect(() => {
    currentAnswerRef.current = currentAnswer;
  }, [currentAnswer]);

  // Timer state
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    // If no setup data, redirect to setup page
    if (!setupData.interviewId) {
      navigate(`/interview/setup/${type}`);
      return;
    }
    
    setQuestionStartTime(Date.now());
    startCamera();
    initProctoring();
    
    return () => {
      stopCamera();
      stopProctoring();
      // Stop any ongoing speech
      if (speechSynthRef.current) {
        speechSynthRef.current.cancel();
      }
    };
  }, [type, setupData.interviewId]);

  // Initialize proctoring system
  const initProctoring = async () => {
    try {
      proctoringClientRef.current = new ProctoringClient({
        apiBase: `${API_URL}/api/proctoring`,
        enableTabSwitchDetection: true,
        enableCopyPasteDetection: true,
        showAlerts: true,
        onViolation: handleProctoringViolation,
        onAlert: handleProctoringAlert,
      });

      // Check if proctoring is available
      const status = await proctoringClientRef.current.checkStatus();
      if (status.available) {
        // Start proctoring session
        await proctoringClientRef.current.startSession(interviewId, 'medium');
        setProctoringActive(true);
        console.log('Proctoring initialized successfully');
        
        // Wait for camera to be ready, then start frame capture
        setTimeout(() => {
          if (videoRef.current && proctoringClientRef.current) {
            // Use the existing video element for proctoring
            proctoringClientRef.current.videoElement = videoRef.current;
            
            // Create a hidden canvas for frame capture
            const canvas = document.createElement('canvas');
            canvas.width = 640;
            canvas.height = 480;
            proctoringClientRef.current.canvasElement = canvas;
            
            // Start frame capture for face detection
            proctoringClientRef.current.startFrameCapture();
            console.log('Frame capture started for proctoring');
          }
        }, 2000); // Wait 2 seconds for camera to initialize
      } else {
        console.log('Proctoring not available, using basic monitoring');
        // Fall back to basic tab switch detection
        setupBasicTabSwitchDetection();
      }
    } catch (error) {
      console.error('Failed to initialize proctoring:', error);
      // Fall back to basic tab switch detection
      setupBasicTabSwitchDetection();
    }
  };

  // Basic tab switch detection fallback
  const setupBasicTabSwitchDetection = () => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        setTabSwitchCount(prev => prev + 1);
        setProctoringAlert('⚠️ Tab switch detected! Please stay on this page during the interview.');
        setProctoringViolations(prev => [...prev, {
          type: 'tab_switch',
          timestamp: new Date().toISOString(),
          message: 'User switched to another tab'
        }]);
      }
    };

    const handleWindowBlur = () => {
      setProctoringAlert('⚠️ Window lost focus. Please keep this window active.');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);

    // Store cleanup function
    window._proctoringCleanup = () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
    };
  };

  const stopProctoring = async () => {
    if (proctoringClientRef.current && proctoringActive) {
      try {
        await proctoringClientRef.current.endSession();
      } catch (error) {
        console.error('Error stopping proctoring:', error);
      }
    }
    // Clean up basic detection if used
    if (window._proctoringCleanup) {
      window._proctoringCleanup();
      delete window._proctoringCleanup;
    }
  };

  const handleProctoringViolation = (violation) => {
    // Handle single violation object (not array)
    console.log('Proctoring violation detected:', violation);
    setProctoringViolations(prev => [...prev, violation]);
    
    if (violation.type === 'tab_switch') {
      setTabSwitchCount(prev => prev + 1);
      setProctoringAlert('⚠️ Tab switch detected! Please stay on this page.');
    } else if (violation.type === 'multiple_faces') {
      setProctoringAlert('🚨 Multiple faces detected! Only the candidate should be visible.');
    } else if (violation.type === 'no_face') {
      setProctoringAlert('⚠️ Face not visible. Please stay in front of the camera.');
    } else if (violation.type === 'looking_away') {
      setProctoringAlert('👀 Please look at the screen during the interview.');
    } else if (violation.type === 'different_person') {
      setProctoringAlert('🚨 ALERT: Face does not match registered user!');
    } else if (violation.type === 'copy_attempt' || violation.type === 'paste_attempt') {
      setProctoringAlert('⚠️ Copy/paste detected during interview.');
    } else if (violation.type === 'devtools_attempt') {
      setProctoringAlert('⚠️ DevTools access detected.');
    }
  };

  const handleProctoringAlert = (message) => {
    setProctoringAlert(message);
  };

  useEffect(() => {
    // Timer
    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Handle visibility change to resume video when returning to tab
  useEffect(() => {
    const resumeVideoStream = async () => {
      if (!cameraEnabled) return;
      
      // Check if stream is still active
      if (streamRef.current) {
        const tracks = streamRef.current.getVideoTracks();
        const isStreamActive = tracks.length > 0 && tracks[0].readyState === 'live';
        
        if (isStreamActive && videoRef.current) {
          // Stream is active, just resume playback
          try {
            await videoRef.current.play();
          } catch (err) {
            console.log('Video resume failed, restarting camera:', err);
            await startCamera();
          }
        } else {
          // Stream is dead, restart camera
          console.log('Stream inactive, restarting camera');
          await startCamera();
        }
      } else if (cameraEnabled) {
        // No stream but camera should be enabled, restart it
        await startCamera();
      }
    };

    const handleVisibilityChange = () => {
      if (!document.hidden) {
        // Small delay to let browser settle after becoming visible
        setTimeout(() => {
          resumeVideoStream();
        }, 100);
      }
    };

    const handleWindowFocus = () => {
      // Delay to avoid race conditions with visibility change
      setTimeout(() => {
        resumeVideoStream();
      }, 100);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleWindowFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleWindowFocus);
    };
  }, [cameraEnabled]);

  // Round timer for full interview mode
  useEffect(() => {
    if (!isFullInterview || roundTransitionOpen) return;
    
    // Initialize round time on round change
    if (roundTimeLeft === null) {
      setRoundTimeLeft(rounds[currentRound]?.duration || 600);
    }
    
    const roundInterval = setInterval(() => {
      setRoundTimeLeft((prev) => {
        if (prev <= 1) {
          // Time's up for this round, auto-advance
          handleRoundComplete();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    roundTimerRef.current = roundInterval;
    return () => clearInterval(roundInterval);
  }, [isFullInterview, currentRound, roundTransitionOpen]);

  // Get questions for current round
  const getRoundQuestions = () => {
    if (!isFullInterview) return questions;
    
    const roundKey = rounds[currentRound]?.key;
    const roundName = rounds[currentRound]?.name?.toLowerCase();
    
    return questions.filter(q => {
      // Check the round property first (from backend)
      const qRound = (q.round || '').toLowerCase();
      if (qRound && (qRound.includes(roundKey) || qRound.includes(roundName?.split(' ')[0]))) {
        return true;
      }
      
      // Fallback: infer round from question_type
      const qType = (q.question_type || '').toLowerCase();
      if (roundKey === 'general') {
        return qType === 'behavioral' || qType === 'general' || qType === 'situational';
      } else if (roundKey === 'technical') {
        return qType === 'technical';
      } else if (roundKey === 'hr') {
        return qType === 'hr';
      }
      return false;
    });
  };

  // Get current question index within the round
  const getCurrentRoundQuestionIndex = () => {
    if (!isFullInterview) return currentQuestionIndex;
    
    const roundQuestions = getRoundQuestions();
    const globalQuestion = questions[currentQuestionIndex];
    return roundQuestions.findIndex(q => q.id === globalQuestion?.id);
  };

  // Handle round completion
  const handleRoundComplete = () => {
    if (currentRound < rounds.length - 1) {
      // Show transition screen
      setRoundTransitionOpen(true);
    } else {
      // All rounds complete - show completion dialog
      setCompleteDialogOpen(true);
    }
  };

  // Move to next round
  const startNextRound = () => {
    const nextRound = currentRound + 1;
    setCurrentRound(nextRound);
    setRoundTimeLeft(rounds[nextRound]?.duration || 600);
    setRoundTransitionOpen(false);
    
    // Find the first question of the next round
    const nextRoundKey = rounds[nextRound]?.key;
    const nextRoundName = rounds[nextRound]?.name?.toLowerCase();
    
    const nextRoundFirstQuestionIndex = questions.findIndex(q => {
      // Check the round property first
      const qRound = (q.round || '').toLowerCase();
      if (qRound && (qRound.includes(nextRoundKey) || qRound.includes(nextRoundName?.split(' ')[0]))) {
        return true;
      }
      // Fallback: infer from question_type
      const qType = (q.question_type || '').toLowerCase();
      if (nextRoundKey === 'general') {
        return qType === 'behavioral' || qType === 'general' || qType === 'situational';
      } else if (nextRoundKey === 'technical') {
        return qType === 'technical';
      } else if (nextRoundKey === 'hr') {
        return qType === 'hr';
      }
      return false;
    });
    
    if (nextRoundFirstQuestionIndex !== -1) {
      setCurrentQuestionIndex(nextRoundFirstQuestionIndex);
    } else {
      // If no questions found for this round, advance sequentially
      setCurrentQuestionIndex((prev) => Math.min(prev + 1, questions.length - 1));
    }
  };

  // Check if current question is the last in the round
  const isLastQuestionInRound = () => {
    if (!isFullInterview) return currentQuestionIndex === questions.length - 1;
    
    const roundQuestions = getRoundQuestions();
    const currentRoundIdx = getCurrentRoundQuestionIndex();
    return currentRoundIdx === roundQuestions.length - 1;
  };

  useEffect(() => {
    // Reset timer when question changes
    setQuestionStartTime(Date.now());
  }, [currentQuestionIndex]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Text-to-speech function to read question aloud
  const speakQuestion = (text) => {
    if (isSpeaking) {
      // Stop speaking
      speechSynthRef.current.cancel();
      setIsSpeaking(false);
      return;
    }

    // Start speaking
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1;
    utterance.volume = 1;
    
    // Try to use a good English voice
    const voices = speechSynthRef.current.getVoices();
    const englishVoice = voices.find(voice => 
      voice.lang.startsWith('en') && voice.name.includes('Google')
    ) || voices.find(voice => voice.lang.startsWith('en'));
    
    if (englishVoice) {
      utterance.voice = englishVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    speechSynthRef.current.speak(utterance);
  };

  // Stop speaking when question changes
  useEffect(() => {
    if (speechSynthRef.current) {
      speechSynthRef.current.cancel();
      setIsSpeaking(false);
    }
  }, [currentQuestionIndex]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
        audio: false,
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      streamRef.current = stream;
      setCameraEnabled(true);
      setCameraError('');
    } catch (err) {
      console.error('Camera error:', err);
      setCameraError('Unable to access camera. Please grant permission.');
      setCameraEnabled(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setCameraEnabled(false);
  };

  const toggleCamera = () => {
    if (cameraEnabled) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  // Speech Recognition for live transcription
  const recognitionRef = useRef(null);
  const [liveTranscript, setLiveTranscript] = useState('');

  // Audio Recording Functions with live transcription
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
        
        // Always use backend Whisper transcription for better accuracy
        // Web Speech API live transcript is just for preview
        const liveTranscriptText = accumulatedTranscriptRef.current.trim();
        
        // Use backend transcription if we have audio and recording was > 1 second
        if (audioBlob && audioBlob.size > 1000) {
          console.log('Transcribing with Whisper backend...');
          await transcribeAudio(audioBlob);
        } else if (liveTranscriptText) {
          // Use live transcript if no audio blob but we have text
          setCurrentAnswer(liveTranscriptText);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      isRecordingRef.current = true;
      setRecordingTime(0);
      setAudioBlob(null);
      setLiveTranscript('');
      accumulatedTranscriptRef.current = ''; // Reset accumulated transcript

      // Start Speech Recognition for live transcription
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';
        recognitionRef.current.maxAlternatives = 1;

        recognitionRef.current.onresult = (event) => {
          // Build transcript from current recognition session
          let interimTranscript = '';
          let finalTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript + ' ';
            } else {
              interimTranscript += transcript;
            }
          }
          
          // Add final transcript to accumulated
          if (finalTranscript) {
            accumulatedTranscriptRef.current += finalTranscript;
          }
          
          // Display accumulated + interim
          const fullTranscript = accumulatedTranscriptRef.current + interimTranscript;
          setLiveTranscript(fullTranscript);
          setCurrentAnswer(fullTranscript.trim()); // Auto-fill the text area
        };

        recognitionRef.current.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          if (event.error === 'not-allowed') {
            setError('Microphone access denied. Please allow microphone access for speech recognition.');
          } else if (event.error === 'no-speech') {
            // No speech detected is not really an error, just continue recording
            console.log('No speech detected, continuing...');
          } else if (event.error === 'network') {
            // Network error - speech recognition might not work, but recording continues
            console.log('Network error for speech recognition. Your answer is still being recorded.');
          } else if (event.error === 'aborted') {
            // User aborted - ignore
            console.log('Speech recognition aborted');
          }
        };

        recognitionRef.current.onend = () => {
          console.log('Speech recognition ended');
          // Restart if still recording (use ref to avoid stale closure)
          if (isRecordingRef.current && recognitionRef.current) {
            try {
              recognitionRef.current.start();
            } catch (e) {
              // Ignore "already started" errors
            }
          }
        };

        try {
          recognitionRef.current.start();
        } catch (e) {
          console.error('Failed to start speech recognition:', e);
        }
      } else {
        // Live transcription not available, but recording still works
        // Audio will be transcribed by Whisper when recording stops
        setLiveTranscriptSupported(false);
        console.log('Live speech recognition not available. Audio will be transcribed after recording.');
      }
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Unable to access microphone. Please grant permission.');
    }
  };

  const stopRecording = () => {
    isRecordingRef.current = false;
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
  };

  // Transcribe audio using backend API (Whisper)
  const transcribeAudio = async (blob) => {
    if (!blob) return;
    
    console.log('Starting Whisper transcription, audio size:', blob.size, 'bytes');
    
    setTranscribing(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const currentQuestion = questions[currentQuestionIndex];
      
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');
      formData.append('question_id', currentQuestion.id);

      const response = await fetch(`${API_URL}/api/evaluation/transcribe`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Transcription response:', data);
        if (data.transcription && !data.transcription.startsWith('[')) {
          setCurrentAnswer(data.transcription);
          setLiveTranscript(data.transcription);
        } else {
          // Whisper returned empty or error message
          console.log('Transcription result:', data.transcription);
          if (accumulatedTranscriptRef.current.trim()) {
            // Fall back to live transcript
            setCurrentAnswer(accumulatedTranscriptRef.current.trim());
          } else {
            setError('No speech detected. Please try speaking louder or type your answer.');
          }
        }
      } else {
        const errData = await response.json();
        console.error('Transcription error:', errData);
        // Check if it's ffmpeg error
        if (errData.detail && errData.detail.includes('ffmpeg')) {
          setError('Audio processing error. Please type your answer below instead.');
        } else {
          setError(`Transcription error: ${errData.detail || 'Unknown error'}. Please type your answer.`);
        }
      }
    } catch (err) {
      console.error('Transcription error:', err);
      setError('Could not transcribe audio. Please type your answer below.');
    } finally {
      setTranscribing(false);
    }
  };

  // Skip question function
  const skipQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      // For full interview, check if this is the last question in the round
      if (isFullInterview && isLastQuestionInRound()) {
        handleRoundComplete();
      } else {
        setCurrentQuestionIndex((prev) => prev + 1);
      }
      setCurrentAnswer('');
      setAudioBlob(null);
      setRecordingTime(0);
      setLiveTranscript('');
    } else {
      setCompleteDialogOpen(true);
    }
  };

  // Recording timer
  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const submitAnswer = async () => {
    // Allow submission if there's text OR audio recorded
    if (!currentAnswer.trim() && !audioBlob) {
      setError('Please record an answer or type your response.');
      return;
    }

    setSubmitting(true);
    const thinkingTime = (Date.now() - questionStartTime) / 1000;

    try {
      const token = localStorage.getItem('token');
      const currentQuestion = questions[currentQuestionIndex];
      let answerText = currentAnswer.trim();
      let data;

      // If user has edited text in the textarea, always use text submission
      // This ensures any edits to the transcription are preserved
      if (answerText) {
        // Text submission (including edited transcriptions)
        const response = await fetch(`${API_URL}/api/evaluation/submit-text`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            question_id: currentQuestion.id,
            text_response: answerText,
            thinking_time_seconds: thinkingTime,
          }),
        });

        data = await response.json();

        if (!response.ok) {
          setError(data.detail || 'Failed to submit answer');
          setSubmitting(false);
          return;
        }
      } else if (audioBlob) {
        // Audio-only submission (no text available)
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.webm');
        formData.append('thinking_time', thinkingTime.toString());

        const response = await fetch(`${API_URL}/api/evaluation/submit-audio/${currentQuestion.id}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        });

        data = await response.json();

        if (!response.ok) {
          setError(data.detail || 'Failed to submit audio answer');
          setSubmitting(false);
          return;
        }
        
        // Update answer text from transcription
        if (data.transcription) {
          answerText = data.transcription;
          setCurrentAnswer(answerText);
        }
      }

      // Success - save answer locally
      setAnswers((prev) => ({
        ...prev,
        [currentQuestion.id]: {
          answer: answerText,
          scores: data.scores,
          responseId: data.response_id,
        },
      }));

      // Move to next question or complete
      if (currentQuestionIndex < questions.length - 1) {
        // For full interview, check if this is the last question in the round
        if (isFullInterview && isLastQuestionInRound()) {
          handleRoundComplete();
        } else {
          setCurrentQuestionIndex((prev) => prev + 1);
        }
        setCurrentAnswer('');
        setAudioBlob(null);
        setRecordingTime(0);
        setLiveTranscript('');
      } else {
        setCompleteDialogOpen(true);
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
      setError('Failed to submit answer. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const completeInterview = async () => {
    setSubmitting(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      console.log('Completing interview:', interviewId);
      
      const response = await fetch(`${API_URL}/api/interview/${interviewId}/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      console.log('Complete response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Interview completed successfully:', data);
        stopProctoring();
        stopCamera();
        setCompleteDialogOpen(false);
        // Small delay to ensure state is updated before navigation
        setTimeout(() => {
          navigate(`/results/${interviewId}`);
        }, 100);
      } else {
        const data = await response.json();
        console.error('Complete failed:', data);
        setError(data.detail || 'Failed to complete interview');
      }
    } catch (err) {
      console.error('Error completing interview:', err);
      setError('Failed to complete interview. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const exitInterview = async () => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_URL}/api/interview/${interviewId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (err) {
      console.error('Error cancelling interview:', err);
    } finally {
      stopProctoring();
      stopCamera();
      navigate('/dashboard');
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;
  const answeredCount = Object.keys(answers).length;

  if (loading) {
    return (
      <Box sx={{ bgcolor: '#000000', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} sx={{ color: '#0EA5E9' }} />
          <Typography variant="h6" sx={{ mt: 2, color: '#FFFFFF' }}>
            Preparing your {type} interview...
          </Typography>
          <Typography sx={{ color: '#888888' }}>
            Generating personalized questions
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error && !interviewId) {
    return (
      <Box sx={{ bgcolor: '#000000', minHeight: '100vh', pt: 8 }}>
        <Container maxWidth="md">
          <Alert severity="error" sx={{ mb: 2, bgcolor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
            {error}
          </Alert>
          <Button variant="contained" onClick={() => navigate('/dashboard')} sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}>
            Back to Dashboard
          </Button>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: '#000000', minHeight: '100vh' }}>
      <AppBar position="static" sx={{ bgcolor: '#0A0A0A', borderBottom: '1px solid #1E1E1E' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, color: '#FFFFFF' }}>
            {type.charAt(0).toUpperCase() + type.slice(1)} Interview
            {isFullInterview && (
              <Chip 
                label={rounds[currentRound]?.name}
                size="small"
                sx={{ 
                  ml: 2, 
                  bgcolor: `${rounds[currentRound]?.color}20`,
                  color: rounds[currentRound]?.color,
                  border: `1px solid ${rounds[currentRound]?.color}50`,
                  fontWeight: 600,
                }}
              />
            )}
          </Typography>
          {/* Round Timer for Full Interview */}
          {isFullInterview && roundTimeLeft !== null && (
            <Chip
              icon={<Timer sx={{ color: roundTimeLeft < 60 ? '#EF4444' : '#FFFFFF' }} />}
              label={`Round: ${formatTime(roundTimeLeft)}`}
              sx={{ 
                mr: 2, 
                bgcolor: roundTimeLeft < 60 ? 'rgba(239, 68, 68, 0.2)' : '#1A1A1A', 
                color: roundTimeLeft < 60 ? '#EF4444' : '#FFFFFF', 
                border: `1px solid ${roundTimeLeft < 60 ? '#EF4444' : '#333333'}`,
                animation: roundTimeLeft < 60 ? 'pulse 1s infinite' : 'none',
              }}
            />
          )}
          <Chip
            icon={<Timer sx={{ color: '#FFFFFF' }} />}
            label={formatTime(elapsedTime)}
            sx={{ mr: 2, bgcolor: '#1A1A1A', color: '#FFFFFF', border: '1px solid #333333' }}
          />
          <Chip
            icon={<QuestionAnswer sx={{ color: '#FFFFFF' }} />}
            label={`${answeredCount}/${questions.length}`}
            sx={{ mr: 2, bgcolor: '#1A1A1A', color: '#FFFFFF', border: '1px solid #333333' }}
          />
          <Button
            sx={{ color: '#888888', '&:hover': { color: '#FFFFFF' } }}
            startIcon={<ExitToApp />}
            onClick={() => setExitDialogOpen(true)}
          >
            Exit
          </Button>
        </Toolbar>
      </AppBar>

      {/* Progress Bar */}
      <LinearProgress 
        variant="determinate" 
        value={progress} 
        sx={{ 
          height: 4, 
          bgcolor: '#1A1A1A',
          '& .MuiLinearProgress-bar': { bgcolor: '#0EA5E9' }
        }} 
      />

      <Container maxWidth="lg" sx={{ mt: 3, mb: 4 }}>
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2, bgcolor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }} 
            onClose={() => setError('')}
          >
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 3 }}>
          {/* Left Panel - Webcam */}
          <Box sx={{ width: 350, flexShrink: 0 }}>
            <Paper sx={{ p: 2, bgcolor: '#0A0A0A', border: '1px solid #1E1E1E' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#FFFFFF' }}>Camera Preview</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {tabSwitchCount > 0 && (
                    <Chip 
                      label={`${tabSwitchCount} tab switch${tabSwitchCount > 1 ? 'es' : ''}`}
                      size="small"
                      sx={{ bgcolor: 'rgba(234, 179, 8, 0.2)', color: '#EAB308', border: '1px solid rgba(234, 179, 8, 0.3)' }}
                    />
                  )}
                  <IconButton onClick={toggleCamera} sx={{ color: cameraEnabled ? '#0EA5E9' : '#666666' }}>
                    {cameraEnabled ? <Videocam /> : <VideocamOff />}
                  </IconButton>
                </Box>
              </Box>
              
              <Box
                sx={{
                  width: '100%',
                  aspectRatio: '4/3',
                  bgcolor: '#111111',
                  borderRadius: 1,
                  overflow: 'hidden',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid #262626',
                }}
              >
                {cameraEnabled ? (
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }}
                  />
                ) : (
                  <Typography sx={{ color: '#555555' }}>
                    {cameraError || 'Camera disabled'}
                  </Typography>
                )}
              </Box>

              {/* Question Progress */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" sx={{ color: '#888888', mb: 1 }}>
                  Progress
                </Typography>
                <Stepper activeStep={currentQuestionIndex} orientation="vertical" sx={{ 
                  '& .MuiStepLabel-label': { color: '#888888' },
                  '& .MuiStepLabel-label.Mui-active': { color: '#FFFFFF' },
                  '& .MuiStepLabel-label.Mui-completed': { color: '#888888' },
                  '& .MuiStepIcon-root': { color: '#333333' },
                  '& .MuiStepIcon-root.Mui-active': { color: '#0EA5E9' },
                  '& .MuiStepIcon-root.Mui-completed': { color: '#10B981' },
                }}>
                  {questions.map((q, index) => (
                    <Step key={q.id} completed={answers[q.id] !== undefined}>
                      <StepLabel>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 250, color: 'inherit' }}>
                          Q{index + 1}: {q.question_text.substring(0, 30)}...
                        </Typography>
                      </StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Box>
            </Paper>
          </Box>

          {/* Right Panel - Question and Answer */}
          <Box sx={{ flexGrow: 1 }}>
            {currentQuestion && (
              <Card sx={{ mb: 3, bgcolor: '#0A0A0A', border: '1px solid #1E1E1E' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="overline" sx={{ color: '#888888' }}>
                      Question {currentQuestionIndex + 1} of {questions.length}
                    </Typography>
                    <Box>
                      <Chip
                        label={currentQuestion.question_type}
                        size="small"
                        sx={{ mr: 1, bgcolor: 'rgba(14, 165, 233, 0.15)', color: '#0EA5E9', border: '1px solid rgba(14, 165, 233, 0.3)' }}
                      />
                      <Chip
                        label={currentQuestion.difficulty}
                        size="small"
                        sx={{
                          bgcolor: currentQuestion.difficulty === 'easy' ? 'rgba(16, 185, 129, 0.15)' :
                                   currentQuestion.difficulty === 'medium' ? 'rgba(234, 179, 8, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                          color: currentQuestion.difficulty === 'easy' ? '#10B981' :
                                 currentQuestion.difficulty === 'medium' ? '#EAB308' : '#EF4444',
                          border: `1px solid ${currentQuestion.difficulty === 'easy' ? 'rgba(16, 185, 129, 0.3)' :
                                   currentQuestion.difficulty === 'medium' ? 'rgba(234, 179, 8, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                        }}
                      />
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                    <Typography variant="h5" sx={{ color: '#FFFFFF', flex: 1 }}>
                      {currentQuestion.question_text}
                    </Typography>
                    <IconButton
                      onClick={() => speakQuestion(currentQuestion.question_text)}
                      sx={{ 
                        color: isSpeaking ? '#0EA5E9' : '#888888',
                        '&:hover': { color: '#0EA5E9', bgcolor: 'rgba(14, 165, 233, 0.1)' },
                        mt: -0.5,
                      }}
                      title={isSpeaking ? 'Stop reading' : 'Read question aloud'}
                    >
                      {isSpeaking ? <VolumeOff /> : <VolumeUp />}
                    </IconButton>
                  </Box>

                  {currentQuestion.category && (
                    <Typography variant="body2" sx={{ color: '#888888', mb: 1 }}>
                      Category: {currentQuestion.category}
                    </Typography>
                  )}

                  {/* Tags Display Section */}
                  {currentQuestion.tags && currentQuestion.tags.length > 0 && (
                    <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {currentQuestion.tags.map((tag, index) => {
                        // Define colors for different tag types
                        const getTagStyle = (tagName) => {
                          const tagLower = tagName.toLowerCase();
                          // Company colors
                          const companyColors = {
                            'google': { bg: 'rgba(66, 133, 244, 0.15)', color: '#4285F4', border: 'rgba(66, 133, 244, 0.3)' },
                            'amazon': { bg: 'rgba(255, 153, 0, 0.15)', color: '#FF9900', border: 'rgba(255, 153, 0, 0.3)' },
                            'meta': { bg: 'rgba(6, 104, 225, 0.15)', color: '#0668E1', border: 'rgba(6, 104, 225, 0.3)' },
                            'microsoft': { bg: 'rgba(0, 164, 239, 0.15)', color: '#00A4EF', border: 'rgba(0, 164, 239, 0.3)' },
                            'apple': { bg: 'rgba(85, 85, 85, 0.15)', color: '#A2AAAD', border: 'rgba(85, 85, 85, 0.3)' },
                            'netflix': { bg: 'rgba(229, 9, 20, 0.15)', color: '#E50914', border: 'rgba(229, 9, 20, 0.3)' },
                            'uber': { bg: 'rgba(0, 0, 0, 0.15)', color: '#EEEEEE', border: 'rgba(255, 255, 255, 0.3)' },
                            'linkedin': { bg: 'rgba(10, 102, 194, 0.15)', color: '#0A66C2', border: 'rgba(10, 102, 194, 0.3)' },
                            'twitter': { bg: 'rgba(29, 161, 242, 0.15)', color: '#1DA1F2', border: 'rgba(29, 161, 242, 0.3)' },
                            'airbnb': { bg: 'rgba(255, 90, 95, 0.15)', color: '#FF5A5F', border: 'rgba(255, 90, 95, 0.3)' },
                          };
                          
                          if (companyColors[tagLower]) {
                            return companyColors[tagLower];
                          }
                          
                          // Category-based colors
                          if (tagLower === 'system-design') return { bg: 'rgba(168, 85, 247, 0.15)', color: '#A855F7', border: 'rgba(168, 85, 247, 0.3)' };
                          if (tagLower === 'leetcode') return { bg: 'rgba(255, 161, 22, 0.15)', color: '#FFA116', border: 'rgba(255, 161, 22, 0.3)' };
                          if (tagLower === 'ai-generated') return { bg: 'rgba(16, 185, 129, 0.15)', color: '#10B981', border: 'rgba(16, 185, 129, 0.3)' };
                          if (tagLower === 'adaptive' || tagLower === 'personalized') return { bg: 'rgba(236, 72, 153, 0.15)', color: '#EC4899', border: 'rgba(236, 72, 153, 0.3)' };
                          
                          // Default style
                          return { bg: 'rgba(107, 114, 128, 0.15)', color: '#6B7280', border: 'rgba(107, 114, 128, 0.3)' };
                        };
                        
                        const tagStyle = getTagStyle(tag);
                        
                        return (
                          <Chip
                            key={index}
                            label={tag.charAt(0).toUpperCase() + tag.slice(1).replace('-', ' ')}
                            size="small"
                            sx={{
                              bgcolor: tagStyle.bg,
                              color: tagStyle.color,
                              border: `1px solid ${tagStyle.border}`,
                              fontSize: '0.7rem',
                              height: '22px'
                            }}
                          />
                        );
                      })}
                    </Box>
                  )}

                  {/* Source Display */}
                  {currentQuestion.source && (
                    <Typography variant="caption" sx={{ color: '#666666', display: 'block', mt: 1 }}>
                      Source: {currentQuestion.source}
                      {currentQuestion.company_name && ` • Asked at ${currentQuestion.company_name}`}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Answer Input */}
            <Paper sx={{ p: 3, bgcolor: '#0A0A0A', border: '1px solid #1E1E1E' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#FFFFFF' }}>
                  Your Answer
                </Typography>
                <Chip
                  label="Voice Recording"
                  sx={{ bgcolor: 'rgba(14, 165, 233, 0.15)', color: '#0EA5E9', border: '1px solid rgba(14, 165, 233, 0.3)' }}
                />
              </Box>

              {/* Audio Recording Section */}
              <Box 
                sx={{ 
                  p: 3, 
                  mb: 3, 
                  border: '2px dashed',
                  borderColor: isRecording ? '#EF4444' : '#333333',
                  borderRadius: 2,
                  bgcolor: isRecording ? 'rgba(239, 68, 68, 0.1)' : '#111111',
                  textAlign: 'center',
                  transition: 'all 0.3s ease'
                }}
              >
                {isRecording ? (
                  <>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                      <FiberManualRecord sx={{ color: '#EF4444', animation: 'pulse 1s infinite', mr: 1 }} />
                      <Typography variant="h4" sx={{ color: '#EF4444' }}>
                        {formatTime(recordingTime)}
                      </Typography>
                    </Box>
                    <Typography variant="body1" sx={{ color: '#888888', mb: 1 }}>
                      Recording your answer... Speak clearly
                    </Typography>
                    {/* Live Transcription Display */}
                    {liveTranscript && (
                      <Paper sx={{ p: 2, mb: 2, bgcolor: '#1A1A1A', border: '1px solid #262626', textAlign: 'left', maxHeight: 100, overflow: 'auto' }}>
                        <Typography variant="body2" sx={{ color: '#E0E0E0' }}>
                          <strong style={{ color: '#888888' }}>Live transcript:</strong> {liveTranscript}
                        </Typography>
                      </Paper>
                    )}
                    {/* Info for browsers without live transcription */}
                    {!liveTranscriptSupported && !liveTranscript && (
                      <Typography variant="caption" sx={{ color: '#0EA5E9', mb: 2, display: 'block' }}>
                        Your speech will be transcribed after you stop recording
                      </Typography>
                    )}
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<Stop />}
                      onClick={stopRecording}
                      sx={{ px: 4, bgcolor: '#EF4444', '&:hover': { bgcolor: '#DC2626' } }}
                    >
                      Stop Recording
                    </Button>
                  </>
                ) : audioBlob ? (
                  <>
                    {transcribing ? (
                      <>
                        <CircularProgress size={48} sx={{ mb: 1, color: '#0EA5E9' }} />
                        <Typography variant="h6" sx={{ color: '#0EA5E9', mb: 1 }}>
                          Transcribing your answer...
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#888888' }}>
                          Please wait while we convert your speech to text
                        </Typography>
                      </>
                    ) : (
                      <>
                        <CheckCircle sx={{ fontSize: 48, color: '#10B981', mb: 1 }} />
                        <Typography variant="h6" sx={{ color: '#10B981', mb: 1 }}>
                          Recording Complete!
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#888888', mb: 2 }}>
                          Duration: {formatTime(recordingTime)}
                        </Typography>
                        {currentAnswer && (
                          <Paper sx={{ p: 2, mb: 2, bgcolor: '#1A1A1A', border: '1px solid #262626', textAlign: 'left' }}>
                            <Typography variant="body2" sx={{ color: '#E0E0E0' }}>
                              <strong style={{ color: '#888888' }}>Transcription:</strong> {currentAnswer}
                            </Typography>
                          </Paper>
                        )}
                        {!currentAnswer && (
                          <Alert severity="warning" sx={{ mb: 2, bgcolor: 'rgba(234, 179, 8, 0.1)', border: '1px solid rgba(234, 179, 8, 0.3)' }}>
                            Could not transcribe audio. Please type your answer below or try recording again.
                          </Alert>
                        )}
                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                          <Button
                            variant="outlined"
                            startIcon={<Mic />}
                            onClick={() => {
                              setAudioBlob(null);
                              setRecordingTime(0);
                              setCurrentAnswer('');
                              setLiveTranscript('');
                            }}
                            sx={{ color: '#0EA5E9', borderColor: '#0EA5E9', '&:hover': { borderColor: '#0EA5E9', bgcolor: 'rgba(14, 165, 233, 0.1)' } }}
                          >
                            Record Again
                          </Button>
                        </Box>
                      </>
                    )}
                  </>
                ) : (
                  <>
                    <Mic sx={{ fontSize: 48, color: '#0EA5E9', mb: 1 }} />
                    <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 1 }}>
                      Click to Start Recording
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#888888', mb: 2 }}>
                      Answer the question by speaking. Your response will be transcribed automatically.
                    </Typography>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<Mic />}
                      onClick={startRecording}
                      disabled={submitting}
                      sx={{ px: 4, bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
                    >
                      Start Recording
                    </Button>
                  </>
                )}
              </Box>

              {/* Transcription status */}
              {transcribing && (
                <Alert severity="info" sx={{ mb: 2, bgcolor: 'rgba(14, 165, 233, 0.1)', border: '1px solid rgba(14, 165, 233, 0.3)' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={20} sx={{ color: '#0EA5E9' }} />
                    <Typography sx={{ color: '#E0E0E0' }}>Transcribing your audio response...</Typography>
                  </Box>
                </Alert>
              )}

              {/* Text input for answer */}
              <Typography variant="body2" sx={{ color: '#888888', mb: 1 }}>
                {audioBlob && !currentAnswer.trim() 
                  ? '⬇️ Type your answer below (transcription unavailable):' 
                  : 'Or type/edit your answer:'}
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                placeholder="Type your answer here..."
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                disabled={submitting}
                sx={{ 
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    bgcolor: audioBlob && !currentAnswer.trim() ? '#1a1a2e' : '#111111',
                    color: '#E0E0E0',
                    '& fieldset': { borderColor: audioBlob && !currentAnswer.trim() ? '#0EA5E9' : '#333333' },
                    '&:hover fieldset': { borderColor: '#444444' },
                    '&.Mui-focused fieldset': { borderColor: '#0EA5E9' },
                  },
                  '& .MuiInputBase-input::placeholder': { color: '#555555' },
                }}
              />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<NavigateBefore />}
                    disabled={currentQuestionIndex === 0 || submitting || isRecording}
                    onClick={() => {
                      setCurrentQuestionIndex((prev) => prev - 1);
                      const prevQuestion = questions[currentQuestionIndex - 1];
                      setCurrentAnswer(answers[prevQuestion?.id]?.answer || '');
                      setAudioBlob(null);
                      setRecordingTime(0);
                      setLiveTranscript('');
                    }}
                    sx={{ 
                      color: '#888888', 
                      borderColor: '#333333', 
                      '&:hover': { borderColor: '#555555', bgcolor: 'rgba(255,255,255,0.05)' },
                      '&.Mui-disabled': { color: '#444444', borderColor: '#222222' }
                    }}
                  >
                    Previous
                  </Button>
                  
                  {/* Skip Button */}
                  <Button
                    variant="outlined"
                    endIcon={<SkipNext />}
                    disabled={submitting || isRecording}
                    onClick={skipQuestion}
                    sx={{ 
                      color: '#EAB308', 
                      borderColor: 'rgba(234, 179, 8, 0.5)', 
                      '&:hover': { borderColor: '#EAB308', bgcolor: 'rgba(234, 179, 8, 0.1)' },
                      '&.Mui-disabled': { color: '#444444', borderColor: '#222222' }
                    }}
                  >
                    Skip Question
                  </Button>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {currentAnswer.length > 0 && (
                    <Typography variant="body2" sx={{ color: '#888888' }}>
                      {currentAnswer.length} characters
                    </Typography>
                  )}
                  
                  {currentQuestionIndex === questions.length - 1 ? (
                    <Button
                      variant="contained"
                      endIcon={submitting ? <CircularProgress size={20} sx={{ color: '#FFFFFF' }} /> : <CheckCircle />}
                      onClick={submitAnswer}
                      disabled={(!currentAnswer.trim() && !audioBlob) || submitting || isRecording}
                      sx={{ bgcolor: '#10B981', '&:hover': { bgcolor: '#059669' } }}
                    >
                      {submitting ? (transcribing ? 'Transcribing...' : 'Submitting...') : 'Submit & Complete'}
                    </Button>
                  ) : (
                    <Button
                      variant="contained"
                      endIcon={submitting ? <CircularProgress size={20} sx={{ color: '#FFFFFF' }} /> : <NavigateNext />}
                      onClick={submitAnswer}
                      disabled={(!currentAnswer.trim() && !audioBlob) || submitting || isRecording}
                      sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
                    >
                      {submitting ? (transcribing ? 'Transcribing...' : 'Submitting...') : 'Submit & Next'}
                    </Button>
                  )}
                </Box>
              </Box>
            </Paper>

            {/* Tips */}
            <Paper sx={{ p: 2, mt: 2, bgcolor: '#0B0B0B', border: '1px solid #1E1E1E' }}>
              <Typography variant="subtitle2" sx={{ color: '#FFFFFF', mb: 1 }}>
                Interview Tips
              </Typography>
              <Typography variant="body2" sx={{ color: '#888888' }}>
                - Speak clearly and maintain eye contact with the camera<br />
                - Structure your answer with a clear beginning, middle, and end<br />
                - Use specific examples to support your points<br />
                - Take a moment to think before answering
              </Typography>
            </Paper>
          </Box>
        </Box>
      </Container>

      {/* Exit Confirmation Dialog */}
      <Dialog 
        open={exitDialogOpen} 
        onClose={() => setExitDialogOpen(false)}
        PaperProps={{ sx: { bgcolor: '#1A1A1A', border: '1px solid #262626' } }}
      >
        <DialogTitle sx={{ color: '#FFFFFF' }}>Exit Interview?</DialogTitle>
        <DialogContent>
          <Typography sx={{ color: '#E0E0E0' }}>
            Are you sure you want to exit? Your progress will be lost and the interview will be cancelled.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid #262626' }}>
          <Button onClick={() => setExitDialogOpen(false)} sx={{ color: '#888888' }}>Continue Interview</Button>
          <Button onClick={exitInterview} sx={{ color: '#EF4444', '&:hover': { bgcolor: 'rgba(239, 68, 68, 0.1)' } }}>
            Exit & Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Complete Interview Dialog */}
      <Dialog 
        open={completeDialogOpen} 
        onClose={() => setCompleteDialogOpen(false)}
        PaperProps={{ sx: { bgcolor: '#1A1A1A', border: '1px solid #262626' } }}
      >
        <DialogTitle sx={{ color: '#FFFFFF' }}>Complete Interview?</DialogTitle>
        <DialogContent>
          <Typography sx={{ color: '#E0E0E0' }}>
            You have answered all {questions.length} questions. 
            Click "Complete" to submit your interview and see your results.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid #262626' }}>
          <Button onClick={() => setCompleteDialogOpen(false)} sx={{ color: '#888888' }}>Review Answers</Button>
          <Button
            onClick={completeInterview}
            variant="contained"
            disabled={submitting}
            sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
          >
            {submitting ? <CircularProgress size={20} sx={{ color: '#FFFFFF' }} /> : 'Complete Interview'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Round Transition Dialog (for Full Interview mode) */}
      <Dialog 
        open={roundTransitionOpen} 
        onClose={() => {}}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { bgcolor: '#0A0A0A', border: '1px solid #262626', textAlign: 'center' } }}
      >
        <DialogTitle sx={{ color: '#FFFFFF', pt: 4 }}>
          <CheckCircle sx={{ fontSize: 64, color: '#10B981', mb: 2 }} />
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            {rounds[currentRound]?.name} Complete!
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Typography sx={{ color: '#888888', mb: 3 }}>
            Great job! You've completed the {rounds[currentRound]?.name}.
          </Typography>
          
          {currentRound < rounds.length - 1 && (
            <Box sx={{ 
              p: 3, 
              bgcolor: 'rgba(14, 165, 233, 0.1)', 
              border: '1px solid rgba(14, 165, 233, 0.3)', 
              borderRadius: 2,
              mb: 2 
            }}>
              <Typography variant="h6" sx={{ color: '#FFFFFF', mb: 1 }}>
                Next: {rounds[currentRound + 1]?.name}
              </Typography>
              <Typography sx={{ color: '#888888' }}>
                Time Limit: {Math.floor(rounds[currentRound + 1]?.duration / 60)} minutes
              </Typography>
              <Typography sx={{ color: '#888888', mt: 1 }}>
                {currentRound + 1 === 1 && 'Get ready for technical questions based on your resume and skills.'}
                {currentRound + 1 === 2 && 'Final round - questions about culture fit and soft skills.'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ justifyContent: 'center', pb: 4 }}>
          <Button
            onClick={startNextRound}
            variant="contained"
            size="large"
            sx={{ 
              bgcolor: rounds[currentRound + 1]?.color || '#0EA5E9', 
              '&:hover': { filter: 'brightness(0.9)' },
              px: 4,
              py: 1.5,
            }}
          >
            Start {rounds[currentRound + 1]?.name || 'Next Round'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Proctoring Alert Snackbar */}
      <Snackbar
        open={!!proctoringAlert}
        autoHideDuration={5000}
        onClose={() => setProctoringAlert('')}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setProctoringAlert('')} 
          severity="warning" 
          sx={{ 
            width: '100%',
            bgcolor: 'rgba(234, 179, 8, 0.15)',
            border: '1px solid rgba(234, 179, 8, 0.3)',
            color: '#E0E0E0',
          }}
        >
          {proctoringAlert}
          {tabSwitchCount > 0 && (
            <Typography variant="caption" display="block" sx={{ color: '#888888' }}>
              Tab switches detected: {tabSwitchCount}
            </Typography>
          )}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Interview;
