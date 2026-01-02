import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  TrendingUp,
  Lightbulb,
  Home,
  Refresh,
  Assessment,
  EmojiEmotions,
  RecordVoiceOver,
  Psychology,
} from '@mui/icons-material';
import API_URL from '../config';

const ScoreCircle = ({ score, label, color }) => (
  <Box sx={{ textAlign: 'center' }}>
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <CircularProgress
        variant="determinate"
        value={score || 0}
        size={100}
        thickness={4}
        sx={{ color: color || 'primary.main' }}
      />
      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="h5" component="div" fontWeight="bold">
          {score?.toFixed(0) || 0}%
        </Typography>
      </Box>
    </Box>
    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
      {label}
    </Typography>
  </Box>
);

const Results = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchResults();
  }, [id]);

  const fetchResults = async () => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      console.log('Fetching results for interview:', id);
      
      if (!token) {
        setError('Not authenticated. Please login again.');
        setLoading(false);
        return;
      }
      
      const response = await fetch(`${API_URL}/api/interview/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      console.log('Results response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Results error:', errorData);
        setError(errorData.detail || `Failed to load results (${response.status})`);
        setLoading(false);
        return;
      }
      
      const data = await response.json();
      console.log('Results data:', data);
      setResults(data);
    } catch (err) {
      console.error('Error fetching results:', err);
      setError('Unable to connect to server: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'warning.main';
    return 'error.main';
  };

  const getGrade = (score) => {
    if (score >= 90) return { grade: 'A+', label: 'Excellent' };
    if (score >= 80) return { grade: 'A', label: 'Great' };
    if (score >= 70) return { grade: 'B', label: 'Good' };
    if (score >= 60) return { grade: 'C', label: 'Fair' };
    return { grade: 'D', label: 'Needs Improvement' };
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading your results...
        </Typography>
      </Container>
    );
  }

  if (error) {
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

  if (!results) {
    return (
      <Container maxWidth="md" sx={{ mt: 8 }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          No results data available
        </Alert>
        <Button variant="contained" onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  const overallScore = results?.overall_score || 0;
  const { grade, label } = getGrade(overallScore);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Interview Results
          </Typography>
          <Button color="inherit" startIcon={<Home />} onClick={() => navigate('/dashboard')}>
            Dashboard
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Overall Score Card */}
        <Paper sx={{ p: 4, mb: 4, textAlign: 'center', bgcolor: 'primary.main', color: 'white' }}>
          <Typography variant="h4" gutterBottom>
            Interview Complete!
          </Typography>
          <Typography variant="h6" gutterBottom>
            {results?.interview_type?.charAt(0).toUpperCase() + results?.interview_type?.slice(1)} Interview
          </Typography>
          
          <Box sx={{ my: 4 }}>
            <Typography variant="h1" fontWeight="bold">
              {grade}
            </Typography>
            <Typography variant="h5">
              {label} - {overallScore?.toFixed(1)}%
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Chip
              label={`${results?.answered_questions || 0}/${results?.total_questions || 0} Questions`}
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
            <Chip
              label={`${results?.duration_minutes?.toFixed(0) || 0} minutes`}
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
          </Box>
        </Paper>

        {/* Detailed Scores */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                Performance Breakdown
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={4} justifyContent="center">
                <Grid item>
                  <ScoreCircle
                    score={results?.content_score}
                    label="Content"
                    color={getScoreColor(results?.content_score)}
                  />
                </Grid>
                <Grid item>
                  <ScoreCircle
                    score={results?.clarity_score}
                    label="Clarity"
                    color={getScoreColor(results?.clarity_score)}
                  />
                </Grid>
                <Grid item>
                  <ScoreCircle
                    score={results?.fluency_score}
                    label="Fluency"
                    color={getScoreColor(results?.fluency_score)}
                  />
                </Grid>
                <Grid item>
                  <ScoreCircle
                    score={results?.confidence_score}
                    label="Confidence"
                    color={getScoreColor(results?.confidence_score)}
                  />
                </Grid>
                <Grid item>
                  <ScoreCircle
                    score={results?.emotion_score}
                    label="Expression"
                    color={getScoreColor(results?.emotion_score)}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>

        {/* Feedback and Areas */}
        <Grid container spacing={3}>
          {/* Feedback */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI Feedback
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body1" paragraph>
                {results?.feedback || 'Great job completing the interview! Review the detailed scores above to understand your performance.'}
              </Typography>
            </Paper>
          </Grid>

          {/* Strong Areas */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'success.main' }}>
                <CheckCircle sx={{ mr: 1, verticalAlign: 'middle' }} />
                Strong Areas
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List dense>
                {results?.strong_areas?.length > 0 ? (
                  results.strong_areas.map((area, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <TrendingUp color="success" />
                      </ListItemIcon>
                      <ListItemText
                        primary={area.area || area}
                        secondary={area.description}
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem>
                    <ListItemText primary="Keep practicing to identify your strengths!" />
                  </ListItem>
                )}
              </List>
            </Paper>
          </Grid>

          {/* Weak Areas */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'warning.main' }}>
                <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
                Areas for Improvement
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List dense>
                {results?.weak_areas?.length > 0 ? (
                  results.weak_areas.map((area, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Lightbulb color="warning" />
                      </ListItemIcon>
                      <ListItemText
                        primary={area.area || area}
                        secondary={area.suggestion}
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem>
                    <ListItemText primary="No major areas identified for improvement!" />
                  </ListItem>
                )}
              </List>
            </Paper>
          </Grid>

          {/* Recommendations */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                <Lightbulb sx={{ mr: 1, verticalAlign: 'middle', color: 'info.main' }} />
                Recommendations
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List>
                {results?.recommendations?.length > 0 ? (
                  results.recommendations.map((rec, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircle color="info" />
                      </ListItemIcon>
                      <ListItemText
                        primary={rec.title || rec}
                        secondary={rec.description}
                      />
                    </ListItem>
                  ))
                ) : (
                  <>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="info" /></ListItemIcon>
                      <ListItemText primary="Practice more interviews to build confidence" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="info" /></ListItemIcon>
                      <ListItemText primary="Review common interview questions in your field" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="info" /></ListItemIcon>
                      <ListItemText primary="Work on structuring your answers using the STAR method" />
                    </ListItem>
                  </>
                )}
              </List>
            </Paper>
          </Grid>
        </Grid>

        {/* Action Buttons */}
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="outlined"
            size="large"
            startIcon={<Home />}
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </Button>
          <Button
            variant="contained"
            size="large"
            startIcon={<Refresh />}
            onClick={() => navigate(`/interview/${results?.interview_type || 'general'}`)}
          >
            Practice Again
          </Button>
        </Box>
      </Container>
    </>
  );
};

export default Results;
