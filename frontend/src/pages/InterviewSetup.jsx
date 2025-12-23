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
      const response = await fetch('http://localhost:8000/api/resume/list', {
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

      const response = await fetch('http://localhost:8000/api/resume/upload', {
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
      await fetch(`http://localhost:8000/api/resume/${resumeId}`, {
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
      const response = await fetch('http://localhost:8000/api/interview/create', {
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
        icon: '🌱',
        color: 'success',
      },
      medium: {
        title: 'Moderate',
        description: 'Balanced mix of questions. Recommended for most candidates.',
        icon: '⚡',
        color: 'warning',
      },
      hard: {
        title: 'Hard',
        description: 'Challenging questions for experienced candidates.',
        icon: '🔥',
        color: 'error',
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
      <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading...</Typography>
      </Container>
    );
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {type.charAt(0).toUpperCase() + type.slice(1)} Interview Setup
          </Typography>
          <Button color="inherit" startIcon={<Home />} onClick={() => navigate('/dashboard')}>
            Dashboard
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Step Content */}
        <Paper sx={{ p: 4 }}>
          {/* Step 1: Resume Selection (skipped for UPSC) */}
          {!isUPSC && activeStep === 0 && (
            <Box>
              <Typography variant="h5" gutterBottom>
                <Description sx={{ mr: 1, verticalAlign: 'middle' }} />
                Select Your Resume
              </Typography>
              <Typography color="text.secondary" paragraph>
                {type === 'technical'
                  ? 'Your resume will be used to generate personalized technical questions based on your skills.'
                  : 'Upload a resume to get personalized questions (optional for this interview type).'}
              </Typography>

              {resumeError && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setResumeError('')}>
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
                    startIcon={uploadingResume ? <CircularProgress size={20} /> : <CloudUpload />}
                    disabled={uploadingResume}
                  >
                    {uploadingResume ? 'Uploading...' : 'Upload New Resume'}
                  </Button>
                </label>
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Supported formats: PDF, DOCX, TXT (Max 10MB)
                </Typography>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Existing Resumes */}
              <Typography variant="h6" gutterBottom>
                Your Resumes
              </Typography>

              {resumes.length === 0 ? (
                <Alert severity="info">
                  No resumes uploaded yet. Upload your resume to get personalized interview questions.
                </Alert>
              ) : (
                <Grid container spacing={2}>
                  {resumes.map((resume) => (
                    <Grid item xs={12} key={resume.id}>
                      <Card
                        variant="outlined"
                        sx={{
                          cursor: 'pointer',
                          border: selectedResume?.id === resume.id ? 2 : 1,
                          borderColor: selectedResume?.id === resume.id ? 'primary.main' : 'divider',
                          bgcolor: selectedResume?.id === resume.id ? 'action.selected' : 'background.paper',
                        }}
                        onClick={() => setSelectedResume(resume)}
                      >
                        <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                          <Radio
                            checked={selectedResume?.id === resume.id}
                            onChange={() => setSelectedResume(resume)}
                          />
                          <Box sx={{ flexGrow: 1, ml: 2 }}>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {resume.filename}
                              {resume.is_active && (
                                <Chip label="Active" size="small" color="primary" sx={{ ml: 1 }} />
                              )}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Uploaded: {new Date(resume.uploaded_at).toLocaleDateString()}
                            </Typography>
                            {resume.skills && resume.skills.length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                {resume.skills.slice(0, 5).map((skill, idx) => (
                                  <Chip key={idx} label={skill} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                                ))}
                                {resume.skills.length > 5 && (
                                  <Chip label={`+${resume.skills.length - 5} more`} size="small" variant="outlined" />
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
                          >
                            <Visibility />
                          </IconButton>
                          <IconButton
                            color="error"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteResume(resume.id);
                            }}
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
              <Typography variant="h5" gutterBottom>
                <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
                Choose Interview Settings
              </Typography>

              {/* Interview Mode - only show for non-UPSC */}
              {!isUPSC && (
                <>
                  <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
                    Interview Mode
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 4 }}>
                    {['standard', 'upsc'].map((mode) => {
                      const modeInfo = getModeDescription(mode);
                      return (
                        <Grid item xs={12} md={6} key={mode}>
                          <Card
                            variant="outlined"
                            sx={{
                              cursor: 'pointer',
                              height: '100%',
                              border: interviewMode === mode ? 2 : 1,
                              borderColor: interviewMode === mode ? 'primary.main' : 'divider',
                              bgcolor: interviewMode === mode ? 'action.selected' : 'background.paper',
                            }}
                            onClick={() => setInterviewMode(mode)}
                          >
                            <CardContent>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Radio checked={interviewMode === mode} />
                                {modeInfo.icon}
                                <Typography variant="h6" sx={{ ml: 1 }}>
                                  {modeInfo.title}
                                </Typography>
                              </Box>
                              <Typography variant="body2" color="text.secondary" paragraph>
                                {modeInfo.description}
                              </Typography>
                              <Box>
                                {modeInfo.features.map((feature, idx) => (
                                  <Chip
                                    key={idx}
                                    label={feature}
                                    size="small"
                                    variant="outlined"
                                    sx={{ mr: 0.5, mb: 0.5 }}
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
                <Box sx={{ mb: 4, p: 2, bgcolor: '#f3e5f5', borderRadius: 2 }}>
                  <Typography variant="h6" sx={{ color: '#9c27b0', mb: 1 }}>
                    🏛️ UPSC Civil Services Interview Mode
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    This interview focuses on current affairs, ethics & integrity, personality assessment, 
                    administrative scenarios, and opinion-based questions - similar to the actual UPSC 
                    Personality Test (Interview).
                  </Typography>
                </Box>
              )}

              {/* Difficulty Level */}
              <Typography variant="h6" sx={{ mb: 2 }}>
                Difficulty Level
              </Typography>
              <Grid container spacing={2}>
                {['easy', 'medium', 'hard'].map((diff) => {
                  const diffInfo = getDifficultyDescription(diff);
                  return (
                    <Grid item xs={12} md={4} key={diff}>
                      <Card
                        variant="outlined"
                        sx={{
                          cursor: 'pointer',
                          border: difficulty === diff ? 2 : 1,
                          borderColor: difficulty === diff ? `${diffInfo.color}.main` : 'divider',
                          bgcolor: difficulty === diff ? 'action.selected' : 'background.paper',
                        }}
                        onClick={() => setDifficulty(diff)}
                      >
                        <CardContent sx={{ textAlign: 'center' }}>
                          <Radio checked={difficulty === diff} />
                          <Typography variant="h4">{diffInfo.icon}</Typography>
                          <Typography variant="h6" sx={{ mt: 1 }}>
                            {diffInfo.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
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
              <Typography variant="h5" gutterBottom>
                <CheckCircle sx={{ mr: 1, verticalAlign: 'middle', color: 'success.main' }} />
                Ready to Start!
              </Typography>

              <Paper variant="outlined" sx={{ p: 3, my: 3, textAlign: 'left' }}>
                <Typography variant="h6" gutterBottom>
                  Interview Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography color="text.secondary">Interview Type</Typography>
                    <Typography fontWeight="bold">
                      {type === 'upsc' ? '🏛️ UPSC Civil Services' : type.charAt(0).toUpperCase() + type.slice(1)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography color="text.secondary">Mode</Typography>
                    <Typography fontWeight="bold">
                      {getModeDescription(interviewMode).title}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography color="text.secondary">Difficulty</Typography>
                    <Typography fontWeight="bold">
                      {getDifficultyDescription(difficulty).title}
                    </Typography>
                  </Grid>
                  {!isUPSC && (
                    <Grid item xs={6}>
                      <Typography color="text.secondary">Resume</Typography>
                      <Typography fontWeight="bold">
                        {selectedResume ? selectedResume.filename : 'Not selected'}
                      </Typography>
                    </Grid>
                  )}
                  {selectedResume?.skills && selectedResume.skills.length > 0 && (
                    <Grid item xs={12}>
                      <Typography color="text.secondary">Skills Detected</Typography>
                      <Box sx={{ mt: 1 }}>
                        {selectedResume.skills.map((skill, idx) => (
                          <Chip key={idx} label={skill} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                        ))}
                      </Box>
                    </Grid>
                  )}
                </Grid>
              </Paper>

              <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
                <Typography variant="body2">
                  <strong>Tips for the interview:</strong>
                </Typography>
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  <li>Find a quiet place with good lighting</li>
                  <li>Enable your camera for better engagement</li>
                  <li>Answer each question thoughtfully before moving to the next</li>
                  <li>Take your time - quality matters more than speed</li>
                </ul>
              </Alert>

              <Button
                variant="contained"
                size="large"
                onClick={startInterview}
                disabled={starting}
                startIcon={starting ? <CircularProgress size={20} /> : <ArrowForward />}
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
            >
              Back
            </Button>
            {activeStep < steps.length - 1 && (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!canProceed()}
                endIcon={<ArrowForward />}
              >
                Next
              </Button>
            )}
          </Box>
        </Paper>
      </Container>

      {/* Resume Preview Dialog */}
      <Dialog open={previewOpen} onClose={() => setPreviewOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Resume Details - {previewResume?.filename}</DialogTitle>
        <DialogContent>
          {previewResume && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">
                  Skills Extracted
                </Typography>
                <Box sx={{ mt: 1 }}>
                  {previewResume.skills?.length > 0 ? (
                    previewResume.skills.map((skill, idx) => (
                      <Chip key={idx} label={skill} sx={{ mr: 0.5, mb: 0.5 }} />
                    ))
                  ) : (
                    <Typography color="text.secondary">No skills detected</Typography>
                  )}
                </Box>
              </Grid>
              {previewResume.experience_years && (
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Experience
                  </Typography>
                  <Typography>{previewResume.experience_years} years</Typography>
                </Grid>
              )}
              {previewResume.education && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Education
                  </Typography>
                  <Typography>
                    {typeof previewResume.education === 'object'
                      ? JSON.stringify(previewResume.education, null, 2)
                      : previewResume.education}
                  </Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default InterviewSetup;
