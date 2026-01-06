import React, { useState, useEffect, useRef } from 'react';
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
} from '@mui/material';
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
  
  // Dialog state
  const [exitDialogOpen, setExitDialogOpen] = useState(false);
  const [completeDialogOpen, setCompleteDialogOpen] = useState(false);

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
    
    return () => {
      stopCamera();
    };
  }, [type, setupData.interviewId]);

  useEffect(() => {
    // Timer
    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Reset timer when question changes
    setQuestionStartTime(Date.now());
  }, [currentQuestionIndex]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

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
        
        // Auto-transcribe if no live transcript (e.g., Firefox without Speech API)
        if (!currentAnswerRef.current.trim()) {
          await transcribeAudio(audioBlob);
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
        setError('Speech recognition not supported. Please use Chrome or Edge browser.');
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

  // Transcribe audio using backend API
  const transcribeAudio = async (blob) => {
    if (!blob) return;
    
    setTranscribing(true);
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
        if (data.transcription) {
          setCurrentAnswer(data.transcription);
          setLiveTranscript(data.transcription);
        } else {
          setError('Could not transcribe audio. Please type your answer or try recording again.');
        }
      } else {
        const errData = await response.json();
        setError(errData.detail || 'Transcription failed. Please type your answer.');
      }
    } catch (err) {
      console.error('Transcription error:', err);
      setError('Transcription failed. Please type your answer manually.');
    } finally {
      setTranscribing(false);
    }
  };

  // Skip question function
  const skipQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
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

      // If we have audio but no text, transcribe audio first
      if (!answerText && audioBlob) {
        setTranscribing(true);
        try {
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');
          formData.append('question_id', currentQuestion.id);

          const transcribeResponse = await fetch(`${API_URL}/api/evaluation/transcribe`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
            body: formData,
          });

          if (transcribeResponse.ok) {
            const transcribeData = await transcribeResponse.json();
            answerText = transcribeData.transcription || '';
            setCurrentAnswer(answerText);
          } else {
            // If transcription fails, use a placeholder
            answerText = '[Audio response - transcription unavailable]';
          }
        } catch (transcribeErr) {
          console.error('Transcription error:', transcribeErr);
          answerText = '[Audio response - transcription unavailable]';
        } finally {
          setTranscribing(false);
        }
      }

      // Now submit the answer
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

      const data = await response.json();

      if (response.ok) {
        // Save answer locally
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
          setCurrentQuestionIndex((prev) => prev + 1);
          setCurrentAnswer('');
          setAudioBlob(null);
          setRecordingTime(0);
          setLiveTranscript('');
        } else {
          setCompleteDialogOpen(true);
        }
      } else {
        setError(data.detail || 'Failed to submit answer');
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
      stopCamera();
      navigate('/dashboard');
    }
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;
  const answeredCount = Object.keys(answers).length;

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Preparing your {type} interview...
        </Typography>
        <Typography color="text.secondary">
          Generating personalized questions
        </Typography>
      </Container>
    );
  }

  if (error && !interviewId) {
    return (
      <Container maxWidth="md" sx={{ mt: 8 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {type.charAt(0).toUpperCase() + type.slice(1)} Interview
          </Typography>
          <Chip
            icon={<Timer />}
            label={formatTime(elapsedTime)}
            color="default"
            sx={{ mr: 2, bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
          />
          <Chip
            icon={<QuestionAnswer />}
            label={`${answeredCount}/${questions.length}`}
            color="default"
            sx={{ mr: 2, bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
          />
          <Button
            color="inherit"
            startIcon={<ExitToApp />}
            onClick={() => setExitDialogOpen(true)}
          >
            Exit
          </Button>
        </Toolbar>
      </AppBar>

      {/* Progress Bar */}
      <LinearProgress variant="determinate" value={progress} sx={{ height: 8 }} />

      <Container maxWidth="lg" sx={{ mt: 3, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 3 }}>
          {/* Left Panel - Webcam */}
          <Box sx={{ width: 350, flexShrink: 0 }}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Camera Preview</Typography>
                <IconButton onClick={toggleCamera} color={cameraEnabled ? 'primary' : 'default'}>
                  {cameraEnabled ? <Videocam /> : <VideocamOff />}
                </IconButton>
              </Box>
              
              <Box
                sx={{
                  width: '100%',
                  aspectRatio: '4/3',
                  bgcolor: 'black',
                  borderRadius: 1,
                  overflow: 'hidden',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
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
                  <Typography color="grey.500">
                    {cameraError || 'Camera disabled'}
                  </Typography>
                )}
              </Box>

              {/* Question Progress */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Progress
                </Typography>
                <Stepper activeStep={currentQuestionIndex} orientation="vertical">
                  {questions.map((q, index) => (
                    <Step key={q.id} completed={answers[q.id] !== undefined}>
                      <StepLabel
                        StepIconProps={{
                          sx: {
                            '&.Mui-completed': { color: 'success.main' },
                            '&.Mui-active': { color: 'primary.main' },
                          },
                        }}
                      >
                        <Typography variant="body2" noWrap sx={{ maxWidth: 250 }}>
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
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="overline" color="text.secondary">
                      Question {currentQuestionIndex + 1} of {questions.length}
                    </Typography>
                    <Box>
                      <Chip
                        label={currentQuestion.question_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                        sx={{ mr: 1 }}
                      />
                      <Chip
                        label={currentQuestion.difficulty}
                        size="small"
                        color={
                          currentQuestion.difficulty === 'easy' ? 'success' :
                          currentQuestion.difficulty === 'medium' ? 'warning' : 'error'
                        }
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="h5" gutterBottom>
                    {currentQuestion.question_text}
                  </Typography>

                  {currentQuestion.category && (
                    <Typography variant="body2" color="text.secondary">
                      Category: {currentQuestion.category}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Answer Input */}
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Your Answer
                </Typography>
                <Chip
                  label="🎤 Voice Recording"
                  color="primary"
                  variant="outlined"
                />
              </Box>

              {/* Audio Recording Section */}
              <Box 
                sx={{ 
                  p: 3, 
                  mb: 3, 
                  border: '2px dashed',
                  borderColor: isRecording ? 'error.main' : 'grey.300',
                  borderRadius: 2,
                  bgcolor: isRecording ? 'error.light' : 'grey.50',
                  textAlign: 'center',
                  transition: 'all 0.3s ease'
                }}
              >
                {isRecording ? (
                  <>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                      <FiberManualRecord sx={{ color: 'error.main', animation: 'pulse 1s infinite', mr: 1 }} />
                      <Typography variant="h4" color="error.main">
                        {formatTime(recordingTime)}
                      </Typography>
                    </Box>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
                      Recording your answer... Speak clearly
                    </Typography>
                    {/* Live Transcription Display */}
                    {liveTranscript && (
                      <Paper sx={{ p: 2, mb: 2, bgcolor: 'white', textAlign: 'left', maxHeight: 100, overflow: 'auto' }}>
                        <Typography variant="body2" color="text.secondary">
                          <strong>Live transcript:</strong> {liveTranscript}
                        </Typography>
                      </Paper>
                    )}
                    <Button
                      variant="contained"
                      color="error"
                      size="large"
                      startIcon={<Stop />}
                      onClick={stopRecording}
                      sx={{ px: 4 }}
                    >
                      Stop Recording
                    </Button>
                  </>
                ) : audioBlob ? (
                  <>
                    {transcribing ? (
                      <>
                        <CircularProgress size={48} sx={{ mb: 1 }} />
                        <Typography variant="h6" color="primary.main" sx={{ mb: 1 }}>
                          Transcribing your answer...
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Please wait while we convert your speech to text
                        </Typography>
                      </>
                    ) : (
                      <>
                        <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
                        <Typography variant="h6" color="success.main" sx={{ mb: 1 }}>
                          Recording Complete!
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Duration: {formatTime(recordingTime)}
                        </Typography>
                        {currentAnswer && (
                          <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.100', textAlign: 'left' }}>
                            <Typography variant="body2">
                              <strong>Transcription:</strong> {currentAnswer}
                            </Typography>
                          </Paper>
                        )}
                        {!currentAnswer && (
                          <Alert severity="warning" sx={{ mb: 2 }}>
                            Could not transcribe audio. Please type your answer below or try recording again.
                          </Alert>
                        )}
                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                          <Button
                            variant="outlined"
                            color="primary"
                            startIcon={<Mic />}
                            onClick={() => {
                              setAudioBlob(null);
                              setRecordingTime(0);
                              setCurrentAnswer('');
                              setLiveTranscript('');
                            }}
                          >
                            Record Again
                          </Button>
                        </Box>
                      </>
                    )}
                  </>
                ) : (
                  <>
                    <Mic sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      Click to Start Recording
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Answer the question by speaking. Your response will be transcribed automatically.
                    </Typography>
                    <Button
                      variant="contained"
                      color="primary"
                      size="large"
                      startIcon={<Mic />}
                      onClick={startRecording}
                      disabled={submitting}
                      sx={{ px: 4 }}
                    >
                      Start Recording
                    </Button>
                  </>
                )}
              </Box>

              {/* Transcription status */}
              {transcribing && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={20} />
                    <Typography>Transcribing your audio response...</Typography>
                  </Box>
                </Alert>
              )}

              {/* Optional text input for corrections */}
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Or type your answer (optional):
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                placeholder="You can also type your answer here if you prefer..."
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                disabled={submitting}
                sx={{ mb: 2 }}
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
                  >
                    Previous
                  </Button>
                  
                  {/* Skip Button */}
                  <Button
                    variant="outlined"
                    color="warning"
                    endIcon={<SkipNext />}
                    disabled={submitting || isRecording}
                    onClick={skipQuestion}
                  >
                    Skip Question
                  </Button>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  {currentAnswer.length > 0 && (
                    <Typography variant="body2" color="text.secondary">
                      {currentAnswer.length} characters
                    </Typography>
                  )}
                  
                  {currentQuestionIndex === questions.length - 1 ? (
                    <Button
                      variant="contained"
                      color="success"
                      endIcon={submitting ? <CircularProgress size={20} color="inherit" /> : <CheckCircle />}
                      onClick={submitAnswer}
                      disabled={(!currentAnswer.trim() && !audioBlob) || submitting || isRecording}
                    >
                      {submitting ? (transcribing ? 'Transcribing...' : 'Submitting...') : 'Submit & Complete'}
                    </Button>
                  ) : (
                    <Button
                      variant="contained"
                      endIcon={submitting ? <CircularProgress size={20} color="inherit" /> : <NavigateNext />}
                      onClick={submitAnswer}
                      disabled={(!currentAnswer.trim() && !audioBlob) || submitting || isRecording}
                    >
                      {submitting ? (transcribing ? 'Transcribing...' : 'Submitting...') : 'Submit & Next'}
                    </Button>
                  )}
                </Box>
              </Box>
            </Paper>

            {/* Tips */}
            <Paper sx={{ p: 2, mt: 2, bgcolor: 'info.light' }}>
              <Typography variant="subtitle2" gutterBottom>
                💡 Interview Tips
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Speak clearly and maintain eye contact with the camera<br />
                • Structure your answer with a clear beginning, middle, and end<br />
                • Use specific examples to support your points<br />
                • Take a moment to think before answering
              </Typography>
            </Paper>
          </Box>
        </Box>
      </Container>

      {/* Exit Confirmation Dialog */}
      <Dialog open={exitDialogOpen} onClose={() => setExitDialogOpen(false)}>
        <DialogTitle>Exit Interview?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to exit? Your progress will be lost and the interview will be cancelled.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExitDialogOpen(false)}>Continue Interview</Button>
          <Button onClick={exitInterview} color="error">
            Exit & Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Complete Interview Dialog */}
      <Dialog open={completeDialogOpen} onClose={() => setCompleteDialogOpen(false)}>
        <DialogTitle>Complete Interview?</DialogTitle>
        <DialogContent>
          <Typography>
            You have answered all {questions.length} questions. 
            Click "Complete" to submit your interview and see your results.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompleteDialogOpen(false)}>Review Answers</Button>
          <Button
            onClick={completeInterview}
            color="primary"
            variant="contained"
            disabled={submitting}
          >
            {submitting ? <CircularProgress size={20} /> : 'Complete Interview'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Interview;
