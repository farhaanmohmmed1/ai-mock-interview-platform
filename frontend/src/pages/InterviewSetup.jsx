import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  CardActions,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Divider,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  AppBar,
  Toolbar,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
  ArrowForward,
  ArrowBack,
  Home,
  School,
  Work,
  Psychology,
  Star,
  Delete,
  Visibility,
} from '@mui/icons-material';
import { useAuth } from '../App';
import API_URL from '../config';

const InterviewSetup = () => {
  const { type } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuth();

  // For UPSC type, automatically set mode and skip resume
  const isUPSC = type === 'upsc';

  // Steps - UPSC doesn't need resume selection
  const [activeStep, setActiveStep] = useState(0);
  const steps = isUPSC 
    ? ['Choose Difficulty', 'Start Interview'] 
    : ['Select Resume', 'Choose Difficulty', 'Start Interview'];

  // Resume state
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [resumeError, setResumeError] = useState('');

  // Difficulty state
  const [difficulty, setDifficulty] = useState('medium');
  const [interviewMode, setInterviewMode] = useState(isUPSC ? 'upsc' : 'standard'); // standard or upsc

  // Loading states
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState('');

  // Resume preview dialog
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewResume, setPreviewResume] = useState(null);

  useEffect(() => {
    // Only fetch resumes for non-UPSC interviews
    if (!isUPSC) {
      fetchResumes();
    } else {
      setLoading(false);
    }
  }, [isUPSC]);

  const fetchResumes = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/resume/list`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setResumes(data);
        // Auto-select active resume
        const activeResume = data.find((r) => r.is_active);
        if (activeResume) {
          setSelectedResume(activeResume);
        }
      } else if (response.status === 401) {
        // Only redirect if truly unauthorized, not just API error
        console.error('Unauthorized - token may be invalid');
      }
    } catch (err) {
      console.error('Error fetching resumes:', err);
      // Don't set error for UPSC mode since it doesn't need resumes
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      setResumeError('Please upload a PDF, DOCX, or TXT file');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setResumeError('File size must be less than 10MB');
      return;
    }

    setUploadingResume(true);
    setResumeError('');

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/resume/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        await fetchResumes();
        setSelectedResume(data.resume);
      } else {
        setResumeError(data.detail || 'Failed to upload resume');
      }
    } catch (err) {
      console.error('Error uploading resume:', err);
      setResumeError('Failed to upload resume. Please try again.');
    } finally {
      setUploadingResume(false);
    }
  };

  const handleDeleteResume = async (resumeId) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`${API_URL}/api/resume/${resumeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      await fetchResumes();
      if (selectedResume?.id === resumeId) {
        setSelectedResume(null);
      }
    } catch (err) {
      console.error('Error deleting resume:', err);
    }
  };

  const startInterview = async () => {
    setStarting(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/interview/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          interview_type: type,
          resume_id: selectedResume?.id,
          difficulty_level: difficulty,
          interview_mode: interviewMode,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Navigate to interview with interview data
        navigate(`/interview/${type}`, {
          state: {
            interviewId: data.interview_id,
            questions: data.questions,
            difficulty: difficulty,
            mode: interviewMode,
            resumeSkills: selectedResume?.skills || [],
          },
        });
      } else {
        setError(data.detail || 'Failed to start interview');
      }
    } catch (err) {
      console.error('Error starting interview:', err);
      setError('Failed to connect to server');
    } finally {
      setStarting(false);
    }
  };

  const handleNext = () => {
    if (activeStep === 0 && type === 'technical' && !selectedResume) {
      setError('Please select or upload a resume for technical interview');
      return;
    }
    setError('');
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const canProceed = () => {
    if (activeStep === 0) {
      // For technical interview, resume is required
      if (type === 'technical') {
        return selectedResume !== null;
      }
      return true; // For other types, resume is optional
    }
    return true;
  };

  const getDifficultyDescription = (diff) => {
    const descriptions = {
      easy: {
        title: 'Easy',
        description: 'Basic questions to build confidence. Great for beginners.',
        icon: null,
        color: '#10B981',
      },
      medium: {
        title: 'Moderate',
        description: 'Balanced mix of questions. Recommended for most candidates.',
        icon: null,
        color: '#F59E0B',
      },
      hard: {
        title: 'Hard',
        description: 'Challenging questions for experienced candidates.',
        icon: null,
        color: '#EF4444',
      },
    };
    return descriptions[diff];
  };

  const getModeDescription = (mode) => {
    const descriptions = {
      standard: {
        title: 'Standard Mode',
        description: 'Regular interview format with behavioral and technical questions based on your resume and selected difficulty.',
        features: ['Personalized questions', 'Adaptive difficulty', 'Detailed feedback'],
        icon: <Work />,
      },
      upsc: {
        title: 'UPSC Interview Mode',
        description: 'Civil Services style interview focusing on current affairs, ethics, personality assessment, and administrative aptitude.',
        features: ['Current affairs', 'Ethics & integrity', 'Decision making', 'Administrative scenarios', 'Opinion-based questions'],
        icon: <School />,
      },
    };
    return descriptions[mode];
  };

  if (loading) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: '#000000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box textAlign="center">
          <CircularProgress sx={{ color: '#0EA5E9' }} />
          <Typography sx={{ mt: 2, color: '#FFFFFF' }}>Loading...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000' }}>
      <Container maxWidth="md" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="overline" sx={{ color: '#0EA5E9', fontWeight: 600, letterSpacing: '0.1em' }}>
            INTERVIEW SETUP
          </Typography>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#FFFFFF', mt: 0.5 }}>
            {type.charAt(0).toUpperCase() + type.slice(1)} Interview
          </Typography>
        </Box>

        {/* Stepper */}
        <Stepper 
          activeStep={activeStep} 
          sx={{ 
            mb: 4,
            '& .MuiStepLabel-label': { color: '#888888' },
            '& .MuiStepLabel-label.Mui-active': { color: '#FFFFFF' },
            '& .MuiStepLabel-label.Mui-completed': { color: '#10B981' },
            '& .MuiStepIcon-root': { color: '#333333' },
            '& .MuiStepIcon-root.Mui-active': { color: '#0EA5E9' },
            '& .MuiStepIcon-root.Mui-completed': { color: '#10B981' },
          }}
        >
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3, 
              bgcolor: 'rgba(239, 68, 68, 0.1)', 
              border: '1px solid rgba(239, 68, 68, 0.3)',
              '& .MuiAlert-icon': { color: '#EF4444' },
            }} 
            onClose={() => setError('')}
          >
            {error}
          </Alert>
        )}

        {/* Step Content */}
        <Paper sx={{ p: 4, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
          {/* Step 1: Resume Selection (skipped for UPSC) */}
          {!isUPSC && activeStep === 0 && (
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Description sx={{ color: '#0EA5E9' }} />
                Select Your Resume
              </Typography>
              <Typography sx={{ color: '#888888', mb: 3 }}>
                {type === 'technical'
                  ? 'Your resume will be used to generate personalized technical questions based on your skills.'
                  : 'Upload a resume to get personalized questions (optional for this interview type).'}
              </Typography>

              {resumeError && (
                <Alert 
                  severity="error" 
                  sx={{ 
                    mb: 3, 
                    bgcolor: 'rgba(239, 68, 68, 0.1)', 
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    '& .MuiAlert-icon': { color: '#EF4444' },
                  }} 
                  onClose={() => setResumeError('')}
                >
                  {resumeError}
                </Alert>
              )}

              {/* Upload Button */}
              <Box sx={{ mb: 3 }}>
                <input
                  type="file"
                  id="resume-upload"
                  accept=".pdf,.docx,.txt"
                  style={{ display: 'none' }}
                  onChange={handleFileUpload}
                />
                <label htmlFor="resume-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={uploadingResume ? <CircularProgress size={20} sx={{ color: '#0EA5E9' }} /> : <CloudUpload />}
                    disabled={uploadingResume}
                    sx={{ 
                      borderColor: '#333333', 
                      color: '#E0E0E0',
                      '&:hover': { borderColor: '#0EA5E9', bgcolor: 'rgba(14, 165, 233, 0.08)' },
                    }}
                  >
                    {uploadingResume ? 'Uploading...' : 'Upload New Resume'}
                  </Button>
                </label>
                <Typography variant="caption" display="block" sx={{ mt: 1, color: '#555555' }}>
                  Supported formats: PDF, DOCX, TXT (Max 10MB)
                </Typography>
              </Box>

              <Divider sx={{ my: 3, borderColor: '#262626' }} />

              {/* Existing Resumes */}
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 2 }}>
                Your Resumes
              </Typography>

              {resumes.length === 0 ? (
                <Alert 
                  severity="info"
                  sx={{ 
                    bgcolor: 'rgba(14, 165, 233, 0.1)', 
                    border: '1px solid rgba(14, 165, 233, 0.3)',
                    '& .MuiAlert-icon': { color: '#0EA5E9' },
                  }}
                >
                  No resumes uploaded yet. Upload your resume to get personalized interview questions.
                </Alert>
              ) : (
                <Grid container spacing={2}>
                  {resumes.map((resume) => (
                    <Grid item xs={12} key={resume.id}>
                      <Card
                        sx={{
                          cursor: 'pointer',
                          bgcolor: selectedResume?.id === resume.id ? 'rgba(14, 165, 233, 0.1)' : '#0B0B0B',
                          border: selectedResume?.id === resume.id ? '1px solid rgba(14, 165, 233, 0.5)' : '1px solid #262626',
                          transition: 'all 0.15s ease',
                          '&:hover': { borderColor: '#333333' },
                        }}
                        onClick={() => setSelectedResume(resume)}
                      >
                        <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                          <Radio
                            checked={selectedResume?.id === resume.id}
                            onChange={() => setSelectedResume(resume)}
                            sx={{ color: '#555555', '&.Mui-checked': { color: '#0EA5E9' } }}
                          />
                          <Box sx={{ flexGrow: 1, ml: 2 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#FFFFFF' }}>
                              {resume.filename}
                              {resume.is_active && (
                                <Chip 
                                  label="Active" 
                                  size="small" 
                                  sx={{ 
                                    ml: 1, 
                                    bgcolor: 'rgba(14, 165, 233, 0.15)', 
                                    color: '#0EA5E9',
                                    border: '1px solid rgba(14, 165, 233, 0.3)',
                                  }} 
                                />
                              )}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#888888' }}>
                              Uploaded: {new Date(resume.uploaded_at).toLocaleDateString()}
                            </Typography>
                            {resume.skills && resume.skills.length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                {resume.skills.slice(0, 5).map((skill, idx) => (
                                  <Chip 
                                    key={idx} 
                                    label={skill} 
                                    size="small" 
                                    sx={{ 
                                      mr: 0.5, 
                                      mb: 0.5, 
                                      bgcolor: '#1A1A1A', 
                                      color: '#E0E0E0',
                                      border: '1px solid #333333',
                                    }} 
                                  />
                                ))}
                                {resume.skills.length > 5 && (
                                  <Chip 
                                    label={`+${resume.skills.length - 5} more`} 
                                    size="small" 
                                    sx={{ bgcolor: 'transparent', color: '#888888', border: '1px solid #333333' }} 
                                  />
                                )}
                              </Box>
                            )}
                          </Box>
                          <IconButton
                            onClick={(e) => {
                              e.stopPropagation();
                              setPreviewResume(resume);
                              setPreviewOpen(true);
                            }}
                            sx={{ color: '#888888', '&:hover': { color: '#0EA5E9' } }}
                          >
                            <Visibility />
                          </IconButton>
                          <IconButton
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteResume(resume.id);
                            }}
                            sx={{ color: '#888888', '&:hover': { color: '#EF4444' } }}
                          >
                            <Delete />
                          </IconButton>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}

              {type !== 'technical' && (
                <Box sx={{ mt: 3 }}>
                  <Button
                    variant="text"
                    onClick={() => {
                      setSelectedResume(null);
                      handleNext();
                    }}
                    sx={{ color: '#888888', '&:hover': { color: '#0EA5E9' } }}
                  >
                    Skip - Continue without resume
                  </Button>
                </Box>
              )}
            </Box>
          )}

          {/* Step 1: Difficulty Selection (Step 0 for UPSC, Step 1 for others) */}
          {((isUPSC && activeStep === 0) || (!isUPSC && activeStep === 1)) && (
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <Psychology sx={{ color: '#A855F7' }} />
                Choose Interview Settings
              </Typography>

              {/* Interview Mode - only show for non-UPSC */}
              {!isUPSC && (
                <>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 2 }}>
                    Interview Mode
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 4 }}>
                    {['standard', 'upsc'].map((mode) => {
                      const modeInfo = getModeDescription(mode);
                      return (
                        <Grid item xs={12} md={6} key={mode}>
                          <Card
                            sx={{
                              cursor: 'pointer',
                              height: '100%',
                              bgcolor: interviewMode === mode ? 'rgba(14, 165, 233, 0.1)' : '#0B0B0B',
                              border: interviewMode === mode ? '1px solid rgba(14, 165, 233, 0.5)' : '1px solid #262626',
                              transition: 'all 0.15s ease',
                              '&:hover': { borderColor: '#333333' },
                            }}
                            onClick={() => setInterviewMode(mode)}
                          >
                            <CardContent>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Radio 
                                  checked={interviewMode === mode} 
                                  sx={{ color: '#555555', '&.Mui-checked': { color: '#0EA5E9' } }}
                                />
                                <Box sx={{ color: '#0EA5E9' }}>{modeInfo.icon}</Box>
                                <Typography variant="h6" sx={{ ml: 1, fontWeight: 600, color: '#FFFFFF' }}>
                                  {modeInfo.title}
                                </Typography>
                              </Box>
                              <Typography variant="body2" sx={{ color: '#888888', mb: 2 }}>
                                {modeInfo.description}
                              </Typography>
                              <Box>
                                {modeInfo.features.map((feature, idx) => (
                                  <Chip
                                    key={idx}
                                    label={feature}
                                    size="small"
                                    sx={{ mr: 0.5, mb: 0.5, bgcolor: 'transparent', color: '#888888', border: '1px solid #333333' }}
                                  />
                                ))}
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      );
                    })}
                  </Grid>
                </>
              )}

              {/* For UPSC, show description */}
              {isUPSC && (
                <Box sx={{ mb: 4, p: 3, bgcolor: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '6px' }}>
                  <Typography variant="h6" sx={{ color: '#A855F7', mb: 1, fontWeight: 600 }}>
                    UPSC Civil Services Interview Mode
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888888' }}>
                    This interview focuses on current affairs, ethics & integrity, personality assessment, 
                    administrative scenarios, and opinion-based questions - similar to the actual UPSC 
                    Personality Test (Interview).
                  </Typography>
                </Box>
              )}

              {/* Difficulty Level */}
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 2 }}>
                Difficulty Level
              </Typography>
              <Grid container spacing={2}>
                {['easy', 'medium', 'hard'].map((diff) => {
                  const diffInfo = getDifficultyDescription(diff);
                  return (
                    <Grid item xs={12} md={4} key={diff}>
                      <Card
                        sx={{
                          cursor: 'pointer',
                          bgcolor: difficulty === diff ? `${diffInfo.color}15` : '#0B0B0B',
                          border: difficulty === diff ? `1px solid ${diffInfo.color}50` : '1px solid #262626',
                          transition: 'all 0.15s ease',
                          '&:hover': { borderColor: '#333333' },
                        }}
                        onClick={() => setDifficulty(diff)}
                      >
                        <CardContent sx={{ textAlign: 'center' }}>
                          <Radio 
                            checked={difficulty === diff} 
                            sx={{ color: '#555555', '&.Mui-checked': { color: diffInfo.color } }}
                          />
                          <Typography variant="h6" sx={{ mt: 1, fontWeight: 600, color: '#FFFFFF' }}>
                            {diffInfo.title}
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#888888' }}>
                            {diffInfo.description}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  );
                })}
              </Grid>
            </Box>
          )}

          {/* Final Step: Confirmation (Step 1 for UPSC, Step 2 for others) */}
          {((isUPSC && activeStep === 1) || (!isUPSC && activeStep === 2)) && (
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 2 }}>
                <CheckCircle sx={{ color: '#10B981' }} />
                Ready to Start!
              </Typography>

              <Paper sx={{ p: 3, my: 3, textAlign: 'left', bgcolor: '#0B0B0B', border: '1px solid #262626' }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 2 }}>
                  Interview Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography sx={{ color: '#888888', fontSize: '0.875rem' }}>Interview Type</Typography>
                    <Typography sx={{ fontWeight: 600, color: '#FFFFFF' }}>
                      {type === 'upsc' ? 'UPSC Civil Services' : type.charAt(0).toUpperCase() + type.slice(1)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography sx={{ color: '#888888', fontSize: '0.875rem' }}>Mode</Typography>
                    <Typography sx={{ fontWeight: 600, color: '#FFFFFF' }}>
                      {getModeDescription(interviewMode).title}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography sx={{ color: '#888888', fontSize: '0.875rem' }}>Difficulty</Typography>
                    <Typography sx={{ fontWeight: 600, color: '#FFFFFF' }}>
                      {getDifficultyDescription(difficulty).title}
                    </Typography>
                  </Grid>
                  {!isUPSC && (
                    <Grid item xs={6}>
                      <Typography sx={{ color: '#888888', fontSize: '0.875rem' }}>Resume</Typography>
                      <Typography sx={{ fontWeight: 600, color: '#FFFFFF' }}>
                        {selectedResume ? selectedResume.filename : 'Not selected'}
                      </Typography>
                    </Grid>
                  )}
                  {selectedResume?.skills && selectedResume.skills.length > 0 && (
                    <Grid item xs={12}>
                      <Typography sx={{ color: '#888888', fontSize: '0.875rem', mb: 1 }}>Skills Detected</Typography>
                      <Box>
                        {selectedResume.skills.map((skill, idx) => (
                          <Chip 
                            key={idx} 
                            label={skill} 
                            size="small" 
                            sx={{ mr: 0.5, mb: 0.5, bgcolor: '#1A1A1A', color: '#E0E0E0', border: '1px solid #333333' }} 
                          />
                        ))}
                      </Box>
                    </Grid>
                  )}
                </Grid>
              </Paper>

              <Alert 
                severity="info" 
                sx={{ 
                  mb: 3, 
                  textAlign: 'left',
                  bgcolor: 'rgba(14, 165, 233, 0.1)', 
                  border: '1px solid rgba(14, 165, 233, 0.3)',
                  '& .MuiAlert-icon': { color: '#0EA5E9' },
                }}
              >
                <Typography variant="body2" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 1 }}>
                  Tips for the interview:
                </Typography>
                <Box component="ul" sx={{ m: 0, pl: 2.5, color: '#E0E0E0' }}>
                  <li>Find a quiet place with good lighting</li>
                  <li>Enable your camera for better engagement</li>
                  <li>Answer each question thoughtfully before moving to the next</li>
                  <li>Take your time - quality matters more than speed</li>
                </Box>
              </Alert>

              <Button
                variant="contained"
                size="large"
                onClick={startInterview}
                disabled={starting}
                startIcon={starting ? <CircularProgress size={20} sx={{ color: '#FFFFFF' }} /> : <ArrowForward />}
                sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
              >
                {starting ? 'Preparing Interview...' : 'Start Interview'}
              </Button>
            </Box>
          )}

          {/* Navigation Buttons */}
          <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              startIcon={<ArrowBack />}
              sx={{ color: '#888888', '&:hover': { color: '#FFFFFF' }, '&.Mui-disabled': { color: '#333333' } }}
            >
              Back
            </Button>
            {activeStep < steps.length - 1 && (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!canProceed()}
                endIcon={<ArrowForward />}
                sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
              >
                Next
              </Button>
            )}
          </Box>
        </Paper>
      </Container>

      {/* Resume Preview Dialog */}
      <Dialog 
        open={previewOpen} 
        onClose={() => setPreviewOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: { bgcolor: '#1A1A1A', border: '1px solid #262626' }
        }}
      >
        <DialogTitle sx={{ color: '#FFFFFF' }}>Resume Details - {previewResume?.filename}</DialogTitle>
        <DialogContent>
          {previewResume && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#888888', mb: 1 }}>
                  Skills Extracted
                </Typography>
                <Box>
                  {previewResume.skills?.length > 0 ? (
                    previewResume.skills.map((skill, idx) => (
                      <Chip 
                        key={idx} 
                        label={skill} 
                        sx={{ mr: 0.5, mb: 0.5, bgcolor: '#0B0B0B', color: '#E0E0E0', border: '1px solid #333333' }} 
                      />
                    ))
                  ) : (
                    <Typography sx={{ color: '#555555' }}>No skills detected</Typography>
                  )}
                </Box>
              </Grid>
              {previewResume.experience_years && (
                <Grid item xs={6}>
                  <Typography variant="subtitle2" sx={{ color: '#888888' }}>
                    Experience
                  </Typography>
                  <Typography sx={{ color: '#FFFFFF' }}>{previewResume.experience_years} years</Typography>
                </Grid>
              )}
              {previewResume.education && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" sx={{ color: '#888888' }}>
                    Education
                  </Typography>
                  <Typography sx={{ color: '#FFFFFF' }}>
                    {typeof previewResume.education === 'object'
                      ? JSON.stringify(previewResume.education, null, 2)
                      : previewResume.education}
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid #262626' }}>
          <Button onClick={() => setPreviewOpen(false)} sx={{ color: '#888888' }}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InterviewSetup;
