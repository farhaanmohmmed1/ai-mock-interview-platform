import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Chip,
  Avatar,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  VideoCall,
  School,
  Assessment,
  TrendingUp,
  Login as LoginIcon,
  CheckCircle,
  Psychology,
  RecordVoiceOver,
  EmojiEmotions,
  Description,
  Speed,
  Security,
  CloudUpload,
  Timeline,
  Lightbulb,
  Groups,
  ArrowForward,
} from '@mui/icons-material';
import { useAuth } from '../App';

const Landing = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/register');
    }
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const features = [
    {
      icon: <VideoCall sx={{ fontSize: 32, color: '#0EA5E9' }} />,
      title: 'Live Video Interviews',
      description: 'Practice with realistic mock interviews using WebRTC-powered audio/video capture. Experience real interview pressure in a safe environment.',
    },
    {
      icon: <Psychology sx={{ fontSize: 32, color: '#A855F7' }} />,
      title: 'AI-Powered Questions',
      description: 'Our AI generates personalized questions based on your resume, skills, and experience level. Questions adapt to your performance in real-time.',
    },
    {
      icon: <RecordVoiceOver sx={{ fontSize: 32, color: '#3B82F6' }} />,
      title: 'Speech Analysis',
      description: 'Get detailed feedback on your communication - speech clarity, pace, filler words, and fluency scores to improve your verbal delivery.',
    },
    {
      icon: <EmojiEmotions sx={{ fontSize: 32, color: '#F59E0B' }} />,
      title: 'Emotion & Confidence Analysis',
      description: 'Advanced AI analyzes your facial expressions and voice tone to measure confidence levels and emotional readiness throughout the interview.',
    },
    {
      icon: <Assessment sx={{ fontSize: 32, color: '#10B981' }} />,
      title: 'Comprehensive Scoring',
      description: 'Receive detailed scores on content accuracy, technical knowledge, communication skills, and overall interview performance.',
    },
    {
      icon: <TrendingUp sx={{ fontSize: 32, color: '#EF4444' }} />,
      title: 'Progress Tracking',
      description: 'Track your improvement over time with detailed analytics. Identify weak areas and watch your interview skills grow.',
    },
  ];

  const interviewTypes = [
    {
      title: 'General Interview',
      description: 'Practice behavioral questions, self-introduction, situational scenarios, and common interview questions asked across all industries.',
      duration: '~20 min',
      questions: '5-8 questions',
      color: '#10B981',
      icon: <Groups />,
    },
    {
      title: 'Technical Interview',
      description: 'Resume-based technical questions covering programming, algorithms, system design, databases, and technology-specific concepts.',
      duration: '~30 min',
      questions: '8-10 questions',
      color: '#3B82F6',
      icon: <Description />,
    },
    {
      title: 'HR Interview',
      description: 'Culture fit assessment, career goals discussion, salary negotiations, work-life balance, and soft skills evaluation.',
      duration: '~15 min',
      questions: '5-6 questions',
      color: '#F59E0B',
      icon: <Psychology />,
    },
    {
      title: 'UPSC Interview',
      description: 'Civil Services style personality test with current affairs, ethics & integrity, administrative scenarios, and opinion-based questions.',
      duration: '~25 min',
      questions: '8-12 questions',
      color: '#A855F7',
      icon: <School />,
    },
  ];

  const howItWorks = [
    {
      step: 1,
      title: 'Create Account & Upload Resume',
      description: 'Sign up for free and upload your resume. Our AI extracts your skills, experience, and education to personalize your interview.',
    },
    {
      step: 2,
      title: 'Choose Interview Type',
      description: 'Select from General, Technical, HR, or UPSC interview modes. Pick your difficulty level based on your preparation.',
    },
    {
      step: 3,
      title: 'Start Mock Interview',
      description: 'Answer AI-generated questions via video. Our system records and analyzes your responses in real-time.',
    },
    {
      step: 4,
      title: 'Get Detailed Feedback',
      description: 'Receive comprehensive analysis of your performance with specific improvement suggestions and resource recommendations.',
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000' }}>
      {/* Navigation Bar */}
      <AppBar 
        position="fixed" 
        elevation={0}
        sx={{ 
          bgcolor: 'rgba(0, 0, 0, 0.8)', 
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid #262626',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 700, color: '#FFFFFF' }}>
            AI Mock Interview
          </Typography>
          <Box>
            {isAuthenticated ? (
              <Button 
                variant="contained" 
                onClick={() => navigate('/dashboard')}
                sx={{ 
                  bgcolor: '#0EA5E9', 
                  '&:hover': { bgcolor: '#0284C7' },
                }}
              >
                Go to Dashboard
              </Button>
            ) : (
              <>
                <Button 
                  onClick={handleLogin} 
                  sx={{ mr: 1, color: '#E0E0E0', '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' } }}
                >
                  Login
                </Button>
                <Button 
                  variant="contained" 
                  onClick={handleGetStarted}
                  sx={{ 
                    bgcolor: '#0EA5E9', 
                    '&:hover': { bgcolor: '#0284C7' },
                  }}
                >
                  Get Started
                </Button>
              </>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: '#000000',
          color: 'white',
          pt: 18,
          pb: 12,
          textAlign: 'center',
          position: 'relative',
          borderBottom: '1px solid #262626',
        }}
      >
        <Container maxWidth="md">
          <Chip 
            label="AI-Powered Interview Preparation" 
            sx={{ 
              mb: 3, 
              bgcolor: 'rgba(14, 165, 233, 0.15)', 
              color: '#0EA5E9',
              border: '1px solid rgba(14, 165, 233, 0.3)',
              fontWeight: 500,
            }} 
          />
          <Typography 
            variant="h2" 
            component="h1" 
            gutterBottom 
            sx={{ 
              fontWeight: 700, 
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
            }}
          >
            Master Your Interview Skills
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 5, 
              color: '#888888',
              fontWeight: 400,
              maxWidth: 600,
              mx: 'auto',
              lineHeight: 1.6,
            }}
          >
            Practice realistic mock interviews powered by artificial intelligence. 
            Get instant feedback on your communication, technical accuracy, and confidence.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
              endIcon={<ArrowForward />}
              sx={{
                py: 1.5,
                px: 4,
                fontSize: '1rem',
                bgcolor: '#0EA5E9',
                color: '#FFFFFF',
                '&:hover': { bgcolor: '#0284C7' },
              }}
            >
              Start Free Interview
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={handleLogin}
              sx={{
                py: 1.5,
                px: 4,
                fontSize: '1rem',
                borderColor: '#333333',
                color: '#E0E0E0',
                '&:hover': { borderColor: '#0EA5E9', bgcolor: 'rgba(14, 165, 233, 0.08)' },
              }}
            >
              Sign In
            </Button>
          </Box>
          <Box sx={{ mt: 4, display: 'flex', gap: 4, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Typography variant="body2" sx={{ color: '#555555', display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle sx={{ fontSize: 16, color: '#10B981' }} /> No credit card required
            </Typography>
            <Typography variant="body2" sx={{ color: '#555555', display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle sx={{ fontSize: 16, color: '#10B981' }} /> Free demo available
            </Typography>
            <Typography variant="body2" sx={{ color: '#555555', display: 'flex', alignItems: 'center', gap: 1 }}>
              <CheckCircle sx={{ fontSize: 16, color: '#10B981' }} /> Instant feedback
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* About Section */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <Grid container spacing={6} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="overline" sx={{ color: '#0EA5E9', fontWeight: 600, letterSpacing: '0.1em' }}>
              ABOUT THE PLATFORM
            </Typography>
            <Typography variant="h3" gutterBottom sx={{ fontWeight: 700, color: '#FFFFFF', mt: 1 }}>
              What is AI Mock Interview Platform?
            </Typography>
            <Typography variant="body1" paragraph sx={{ fontSize: '1rem', lineHeight: 1.8, color: '#888888' }}>
              Our platform is a comprehensive interview preparation tool that uses cutting-edge 
              artificial intelligence to simulate real interview experiences. Whether you're preparing 
              for a software engineering role, civil services exam, or any professional interview, 
              we've got you covered.
            </Typography>
            <List sx={{ mt: 3 }}>
              {[
                'Personalized questions based on your resume and skills',
                'Real-time speech and emotion analysis',
                'Instant, unbiased feedback on your performance',
                'Adaptive difficulty that grows with you',
                'Detailed analytics to track your progress',
              ].map((item, index) => (
                <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <CheckCircle sx={{ color: '#10B981', fontSize: 20 }} />
                  </ListItemIcon>
                  <ListItemText primary={item} sx={{ '& .MuiTypography-root': { color: '#E0E0E0' } }} />
                </ListItem>
              ))}
            </List>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper 
              elevation={0} 
              sx={{ 
                p: 4, 
                bgcolor: '#0B0B0B', 
                border: '1px solid #262626',
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: '#FFFFFF', textAlign: 'center', mb: 4 }}>
                Why Practice Matters
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" sx={{ color: '#0EA5E9', fontWeight: 700 }}>85%</Typography>
                    <Typography variant="body2" sx={{ color: '#888888', mt: 1 }}>
                      of candidates feel more confident after practice
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" sx={{ color: '#10B981', fontWeight: 700 }}>3x</Typography>
                    <Typography variant="body2" sx={{ color: '#888888', mt: 1 }}>
                      higher success rate with mock interviews
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" sx={{ color: '#A855F7', fontWeight: 700 }}>40%</Typography>
                    <Typography variant="body2" sx={{ color: '#888888', mt: 1 }}>
                      improvement in communication clarity
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" sx={{ color: '#F59E0B', fontWeight: 700 }}>24/7</Typography>
                    <Typography variant="body2" sx={{ color: '#888888', mt: 1 }}>
                      practice anytime, anywhere
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Features Section */}
      <Box sx={{ bgcolor: '#0B0B0B', py: 10, borderTop: '1px solid #262626', borderBottom: '1px solid #262626' }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={6}>
            <Typography variant="overline" sx={{ color: '#0EA5E9', fontWeight: 600, letterSpacing: '0.1em' }}>
              FEATURES
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, color: '#FFFFFF', mt: 1 }}>
              Powerful Features
            </Typography>
            <Typography variant="body1" sx={{ color: '#888888', mt: 2, maxWidth: 600, mx: 'auto' }}>
              Our AI-powered platform offers comprehensive tools to help you ace your next interview
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    bgcolor: '#1A1A1A',
                    border: '1px solid #262626',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#333333',
                      bgcolor: '#1F1F1F',
                    },
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 1 }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#888888', lineHeight: 1.7 }}>
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Interview Types Section */}
      <Box sx={{ py: 10 }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={6}>
            <Typography variant="overline" sx={{ color: '#0EA5E9', fontWeight: 600, letterSpacing: '0.1em' }}>
              INTERVIEW MODES
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, color: '#FFFFFF', mt: 1 }}>
              Interview Types
            </Typography>
            <Typography variant="body1" sx={{ color: '#888888', mt: 2 }}>
              Choose the interview format that matches your preparation needs
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {interviewTypes.map((type, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    bgcolor: '#1A1A1A',
                    border: '1px solid #262626',
                    borderTop: `2px solid ${type.color}`,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#333333',
                      bgcolor: '#1F1F1F',
                    },
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: `${type.color}20`, color: type.color, mr: 1.5, width: 36, height: 36 }}>
                        {type.icon}
                      </Avatar>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#FFFFFF' }}>
                        {type.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ color: '#888888', mb: 3, minHeight: 80, lineHeight: 1.7 }}>
                      {type.description}
                    </Typography>
                    <Divider sx={{ borderColor: '#262626', my: 2 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Chip 
                        label={type.duration} 
                        size="small" 
                        sx={{ 
                          bgcolor: 'transparent', 
                          border: '1px solid #333333',
                          color: '#888888',
                          fontSize: '0.75rem',
                        }} 
                      />
                      <Chip 
                        label={type.questions} 
                        size="small" 
                        sx={{ 
                          bgcolor: 'transparent', 
                          border: '1px solid #333333',
                          color: '#888888',
                          fontSize: '0.75rem',
                        }} 
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Box sx={{ bgcolor: '#0B0B0B', py: 10, borderTop: '1px solid #262626', borderBottom: '1px solid #262626' }}>
        <Container maxWidth="lg">
          <Box textAlign="center" mb={6}>
            <Typography variant="overline" sx={{ color: '#0EA5E9', fontWeight: 600, letterSpacing: '0.1em' }}>
              GETTING STARTED
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 700, color: '#FFFFFF', mt: 1 }}>
              How It Works
            </Typography>
            <Typography variant="body1" sx={{ color: '#888888', mt: 2 }}>
              Get started in just 4 simple steps
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {howItWorks.map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Box textAlign="center">
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      bgcolor: 'rgba(14, 165, 233, 0.15)',
                      border: '1px solid rgba(14, 165, 233, 0.3)',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    <Typography sx={{ color: '#0EA5E9', fontWeight: 700, fontSize: '1.25rem' }}>
                      {item.step}
                    </Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 1 }}>
                    {item.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#888888', lineHeight: 1.7 }}>
                    {item.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ py: 12, textAlign: 'center' }}>
        <Container maxWidth="md">
          <Typography variant="h3" sx={{ fontWeight: 700, color: '#FFFFFF', mb: 2 }}>
            Ready to Ace Your Next Interview?
          </Typography>
          <Typography variant="body1" sx={{ color: '#888888', mb: 5, maxWidth: 600, mx: 'auto', lineHeight: 1.8 }}>
            Join thousands of candidates who have improved their interview skills with our AI-powered platform. 
            Start practicing today and land your dream job.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
              endIcon={<ArrowForward />}
              sx={{
                py: 1.5,
                px: 4,
                bgcolor: '#0EA5E9',
                '&:hover': { bgcolor: '#0284C7' },
              }}
            >
              Create Free Account
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={handleLogin}
              sx={{
                py: 1.5,
                px: 4,
                borderColor: '#333333',
                color: '#E0E0E0',
                '&:hover': { borderColor: '#0EA5E9', bgcolor: 'rgba(14, 165, 233, 0.08)' },
              }}
            >
              Sign In
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: '#0B0B0B', borderTop: '1px solid #262626', py: 6 }}>
        <Container>
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ fontWeight: 700, color: '#FFFFFF', mb: 2 }}>
                AI Mock Interview
              </Typography>
              <Typography variant="body2" sx={{ color: '#555555', lineHeight: 1.8 }}>
                Empowering candidates with AI-driven interview preparation. 
                Practice smarter, interview better, succeed faster.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#888888', mb: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Features
              </Typography>
              <Typography variant="body2" sx={{ color: '#555555', mb: 1 }}>AI-Powered Questions</Typography>
              <Typography variant="body2" sx={{ color: '#555555', mb: 1 }}>Speech Analysis</Typography>
              <Typography variant="body2" sx={{ color: '#555555', mb: 1 }}>Emotion Detection</Typography>
              <Typography variant="body2" sx={{ color: '#555555' }}>Progress Tracking</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#888888', mb: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Interview Types
              </Typography>
              <Typography variant="body2" sx={{ color: '#555555', mb: 1 }}>General Interview</Typography>
              <Typography variant="body2" sx={{ color: '#555555', mb: 1 }}>Technical Interview</Typography>
              <Typography variant="body2" sx={{ color: '#555555', mb: 1 }}>HR Interview</Typography>
              <Typography variant="body2" sx={{ color: '#555555' }}>UPSC Interview</Typography>
            </Grid>
          </Grid>
          <Divider sx={{ my: 4, borderColor: '#262626' }} />
          <Typography variant="body2" align="center" sx={{ color: '#555555' }}>
            2025 AI Mock Interview Platform. All rights reserved.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing;
