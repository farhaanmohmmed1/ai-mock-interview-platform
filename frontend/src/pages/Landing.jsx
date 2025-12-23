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
      icon: <VideoCall sx={{ fontSize: 40, color: '#1976d2' }} />,
      title: 'Live Video Interviews',
      description: 'Practice with realistic mock interviews using WebRTC-powered audio/video capture. Experience real interview pressure in a safe environment.',
    },
    {
      icon: <Psychology sx={{ fontSize: 40, color: '#9c27b0' }} />,
      title: 'AI-Powered Questions',
      description: 'Our AI generates personalized questions based on your resume, skills, and experience level. Questions adapt to your performance in real-time.',
    },
    {
      icon: <RecordVoiceOver sx={{ fontSize: 40, color: '#2196f3' }} />,
      title: 'Speech Analysis',
      description: 'Get detailed feedback on your communication - speech clarity, pace, filler words, and fluency scores to improve your verbal delivery.',
    },
    {
      icon: <EmojiEmotions sx={{ fontSize: 40, color: '#ff9800' }} />,
      title: 'Emotion & Confidence Analysis',
      description: 'Advanced AI analyzes your facial expressions and voice tone to measure confidence levels and emotional readiness throughout the interview.',
    },
    {
      icon: <Assessment sx={{ fontSize: 40, color: '#4caf50' }} />,
      title: 'Comprehensive Scoring',
      description: 'Receive detailed scores on content accuracy, technical knowledge, communication skills, and overall interview performance.',
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40, color: '#f44336' }} />,
      title: 'Progress Tracking',
      description: 'Track your improvement over time with detailed analytics. Identify weak areas and watch your interview skills grow.',
    },
  ];

  const interviewTypes = [
    {
      title: 'General Interview',
      description: 'Practice behavioral questions, self-introduction, situational scenarios, and common interview questions asked across all industries.',
      duration: '~20 minutes',
      questions: '5-8 questions',
      color: '#4caf50',
      icon: <Groups />,
    },
    {
      title: 'Technical Interview',
      description: 'Resume-based technical questions covering programming, algorithms, system design, databases, and technology-specific concepts.',
      duration: '~30 minutes',
      questions: '8-10 questions',
      color: '#2196f3',
      icon: <Description />,
    },
    {
      title: 'HR Interview',
      description: 'Culture fit assessment, career goals discussion, salary negotiations, work-life balance, and soft skills evaluation.',
      duration: '~15 minutes',
      questions: '5-6 questions',
      color: '#ff9800',
      icon: <Psychology />,
    },
    {
      title: 'UPSC Interview',
      description: 'Civil Services style personality test with current affairs, ethics & integrity, administrative scenarios, and opinion-based questions.',
      duration: '~25 minutes',
      questions: '8-12 questions',
      color: '#9c27b0',
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
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa' }}>
      {/* Navigation Bar */}
      <AppBar position="fixed" color="inherit" elevation={1}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
            🎯 AI Mock Interview Platform
          </Typography>
          <Box>
            {isAuthenticated ? (
              <Button color="primary" variant="contained" onClick={() => navigate('/dashboard')}>
                Go to Dashboard
              </Button>
            ) : (
              <>
                <Button color="inherit" onClick={handleLogin} sx={{ mr: 1 }}>
                  Login
                </Button>
                <Button color="primary" variant="contained" onClick={handleGetStarted}>
                  Get Started Free
                </Button>
              </>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 50%, #0d47a1 100%)',
          color: 'white',
          pt: 15,
          pb: 10,
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold" sx={{ fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
            Master Your Interview Skills with AI
          </Typography>
          <Typography variant="h5" sx={{ mb: 4, opacity: 0.9, fontWeight: 300 }}>
            Practice realistic mock interviews powered by artificial intelligence. 
            Get instant feedback on your communication, technical accuracy, and confidence.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
              startIcon={<VideoCall />}
              sx={{
                py: 2,
                px: 5,
                fontSize: '1.1rem',
                borderRadius: 3,
                bgcolor: 'white',
                color: '#1976d2',
                '&:hover': { bgcolor: '#f5f5f5' },
                boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
              }}
            >
              Start Free Interview
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={handleLogin}
              sx={{
                py: 2,
                px: 5,
                fontSize: '1.1rem',
                borderRadius: 3,
                borderColor: 'white',
                color: 'white',
                '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' },
              }}
            >
              Sign In
            </Button>
          </Box>
          <Typography variant="body2" sx={{ mt: 3, opacity: 0.8 }}>
            ✓ No credit card required &nbsp; ✓ Free demo available &nbsp; ✓ Instant feedback
          </Typography>
        </Container>
      </Box>

      {/* About Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={6} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography variant="h3" gutterBottom fontWeight="bold" color="primary">
              What is AI Mock Interview Platform?
            </Typography>
            <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
              Our platform is a comprehensive interview preparation tool that uses cutting-edge 
              artificial intelligence to simulate real interview experiences. Whether you're preparing 
              for a software engineering role, civil services exam, or any professional interview, 
              we've got you covered.
            </Typography>
            <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
              Unlike traditional mock interviews, our AI-powered system provides:
            </Typography>
            <List>
              {[
                'Personalized questions based on your resume and skills',
                'Real-time speech and emotion analysis',
                'Instant, unbiased feedback on your performance',
                'Adaptive difficulty that grows with you',
                'Detailed analytics to track your progress',
              ].map((item, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <CheckCircle color="success" />
                  </ListItemIcon>
                  <ListItemText primary={item} />
                </ListItem>
              ))}
            </List>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 4, borderRadius: 3, bgcolor: '#f8f9fa' }}>
              <Typography variant="h5" gutterBottom fontWeight="bold" align="center">
                Why Practice Matters
              </Typography>
              <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="primary" fontWeight="bold">85%</Typography>
                    <Typography variant="body2" color="text.secondary">
                      of candidates feel more confident after practice
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="success.main" fontWeight="bold">3x</Typography>
                    <Typography variant="body2" color="text.secondary">
                      higher success rate with mock interviews
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="secondary.main" fontWeight="bold">40%</Typography>
                    <Typography variant="body2" color="text.secondary">
                      improvement in communication clarity
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h3" color="warning.main" fontWeight="bold">24/7</Typography>
                    <Typography variant="body2" color="text.secondary">
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
      <Box sx={{ bgcolor: 'white', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" align="center" gutterBottom fontWeight="bold">
            Powerful Features
          </Typography>
          <Typography variant="h6" align="center" color="text.secondary" sx={{ mb: 6, maxWidth: 700, mx: 'auto' }}>
            Our AI-powered platform offers comprehensive tools to help you ace your next interview
          </Typography>

          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    transition: 'all 0.3s',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                    <Typography variant="h6" gutterBottom fontWeight="bold">
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
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
      <Box sx={{ py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" align="center" gutterBottom fontWeight="bold">
            Interview Types
          </Typography>
          <Typography variant="h6" align="center" color="text.secondary" sx={{ mb: 6 }}>
            Choose the interview format that matches your preparation needs
          </Typography>

          <Grid container spacing={3}>
            {interviewTypes.map((type, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    borderTop: `4px solid ${type.color}`,
                    transition: 'all 0.3s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ bgcolor: type.color, mr: 1 }}>{type.icon}</Avatar>
                      <Typography variant="h6" fontWeight="bold">
                        {type.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 80 }}>
                      {type.description}
                    </Typography>
                    <Divider sx={{ my: 2 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Chip label={type.duration} size="small" variant="outlined" />
                      <Chip label={type.questions} size="small" variant="outlined" />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Box sx={{ bgcolor: '#1976d2', color: 'white', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" align="center" gutterBottom fontWeight="bold">
            How It Works
          </Typography>
          <Typography variant="h6" align="center" sx={{ mb: 6, opacity: 0.9 }}>
            Get started in just 4 simple steps
          </Typography>

          <Grid container spacing={4}>
            {howItWorks.map((item, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Box textAlign="center">
                  <Avatar
                    sx={{
                      width: 60,
                      height: 60,
                      bgcolor: 'white',
                      color: '#1976d2',
                      fontSize: '1.5rem',
                      fontWeight: 'bold',
                      mx: 'auto',
                      mb: 2,
                    }}
                  >
                    {item.step}
                  </Avatar>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    {item.title}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    {item.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ py: 10, textAlign: 'center', bgcolor: 'white' }}>
        <Container maxWidth="md">
          <Typography variant="h3" gutterBottom fontWeight="bold">
            Ready to Ace Your Next Interview?
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
            Join thousands of candidates who have improved their interview skills with our AI-powered platform. 
            Start practicing today and land your dream job!
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
              startIcon={<LoginIcon />}
              sx={{ py: 2, px: 5, fontSize: '1.1rem', borderRadius: 3 }}
            >
              Create Free Account
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={handleLogin}
              sx={{ py: 2, px: 5, fontSize: '1.1rem', borderRadius: 3 }}
            >
              Already have an account? Sign In
            </Button>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
            🔒 Your data is secure and private. We never share your information.
          </Typography>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: '#1a1a2e', color: 'white', py: 6 }}>
        <Container>
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                🎯 AI Mock Interview Platform
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                Empowering candidates with AI-driven interview preparation. 
                Practice smarter, interview better, succeed faster.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Features
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• AI-Powered Questions</Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• Speech Analysis</Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• Emotion Detection</Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• Progress Tracking</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Interview Types
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• General Interview</Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• Technical Interview</Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• HR Interview</Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>• UPSC Interview</Typography>
            </Grid>
          </Grid>
          <Divider sx={{ my: 4, borderColor: 'rgba(255,255,255,0.1)' }} />
          <Typography variant="body2" align="center" sx={{ opacity: 0.7 }}>
            © 2025 AI Mock Interview Platform. All rights reserved. | Prepare smarter, interview better.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default Landing;
