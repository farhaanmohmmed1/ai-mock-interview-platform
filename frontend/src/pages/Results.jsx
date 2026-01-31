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
        value={100}
        size={100}
        thickness={4}
        sx={{ color: '#262626', position: 'absolute' }}
      />
      <CircularProgress
        variant="determinate"
        value={score || 0}
        size={100}
        thickness={4}
        sx={{ color: color || '#0EA5E9' }}
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
        <Typography variant="h5" component="div" sx={{ fontWeight: 700, color: '#FFFFFF' }}>
          {score?.toFixed(0) || 0}%
        </Typography>
      </Box>
    </Box>
    <Typography variant="body2" sx={{ color: '#888888', mt: 1 }}>
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
    if (score >= 80) return '#10B981';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
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
      <Box sx={{ minHeight: '100vh', bgcolor: '#000000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Box textAlign="center">
          <CircularProgress size={60} sx={{ color: '#0EA5E9' }} />
          <Typography variant="h6" sx={{ mt: 2, color: '#FFFFFF' }}>
            Loading your results...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: '#000000', py: 8 }}>
        <Container maxWidth="md">
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3, 
              bgcolor: 'rgba(239, 68, 68, 0.1)', 
              border: '1px solid rgba(239, 68, 68, 0.3)',
              '& .MuiAlert-icon': { color: '#EF4444' },
            }}
          >
            {error}
          </Alert>
          <Button 
            variant="contained" 
            onClick={() => navigate('/dashboard')}
            sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
          >
            Back to Dashboard
          </Button>
        </Container>
      </Box>
    );
  }

  if (!results) {
    return (
      <Box sx={{ minHeight: '100vh', bgcolor: '#000000', py: 8 }}>
        <Container maxWidth="md">
          <Alert 
            severity="warning" 
            sx={{ 
              mb: 3, 
              bgcolor: 'rgba(245, 158, 11, 0.1)', 
              border: '1px solid rgba(245, 158, 11, 0.3)',
              '& .MuiAlert-icon': { color: '#F59E0B' },
            }}
          >
            No results data available
          </Alert>
          <Button 
            variant="contained" 
            onClick={() => navigate('/dashboard')}
            sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
          >
            Back to Dashboard
          </Button>
        </Container>
      </Box>
    );
  }

  const overallScore = results?.overall_score || 0;
  const { grade, label } = getGrade(overallScore);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000' }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Overall Score Card */}
        <Paper sx={{ p: 4, mb: 4, textAlign: 'center', bgcolor: '#0B0B0B', border: '1px solid #262626' }}>
          <Typography variant="overline" sx={{ color: '#0EA5E9', fontWeight: 600, letterSpacing: '0.1em' }}>
            INTERVIEW COMPLETE
          </Typography>
          <Typography variant="h5" sx={{ color: '#888888', mt: 1 }}>
            {results?.interview_type?.charAt(0).toUpperCase() + results?.interview_type?.slice(1)} Interview
          </Typography>
          
          <Box sx={{ my: 4 }}>
            <Typography variant="h1" sx={{ fontWeight: 700, color: '#0EA5E9', fontSize: '5rem' }}>
              {grade}
            </Typography>
            <Typography variant="h5" sx={{ color: '#FFFFFF', fontWeight: 500 }}>
              {label} - {overallScore?.toFixed(1)}%
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Chip
              label={`${results?.answered_questions || 0}/${results?.total_questions || 0} Questions`}
              sx={{ 
                bgcolor: 'rgba(14, 165, 233, 0.15)', 
                color: '#0EA5E9',
                border: '1px solid rgba(14, 165, 233, 0.3)',
              }}
            />
            <Chip
              label={`${results?.duration_minutes?.toFixed(0) || 0} minutes`}
              sx={{ 
                bgcolor: 'rgba(14, 165, 233, 0.15)', 
                color: '#0EA5E9',
                border: '1px solid rgba(14, 165, 233, 0.3)',
              }}
            />
          </Box>
        </Paper>

        {/* Detailed Scores */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <Assessment sx={{ color: '#0EA5E9' }} />
                Performance Breakdown
              </Typography>
              <Divider sx={{ mb: 4, borderColor: '#262626' }} />
              
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
            <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Psychology sx={{ color: '#A855F7' }} />
                AI Feedback
              </Typography>
              <Divider sx={{ mb: 2, borderColor: '#262626' }} />
              <Typography variant="body1" sx={{ color: '#E0E0E0', lineHeight: 1.8 }}>
                {results?.feedback || 'Great job completing the interview! Review the detailed scores above to understand your performance.'}
              </Typography>
            </Paper>
          </Grid>

          {/* Strong Areas */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%', bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#10B981', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CheckCircle sx={{ color: '#10B981' }} />
                Strong Areas
              </Typography>
              <Divider sx={{ mb: 2, borderColor: '#262626' }} />
              <List dense>
                {results?.strong_areas?.length > 0 ? (
                  results.strong_areas.map((area, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <TrendingUp sx={{ color: '#10B981' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={area.area || area}
                        secondary={area.description}
                        primaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                        secondaryTypographyProps={{ sx: { color: '#888888' } }}
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem sx={{ px: 0 }}>
                    <ListItemText primary="Keep practicing to identify your strengths!" primaryTypographyProps={{ sx: { color: '#888888' } }} />
                  </ListItem>
                )}
              </List>
            </Paper>
          </Grid>

          {/* Weak Areas */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%', bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#F59E0B', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Warning sx={{ color: '#F59E0B' }} />
                Areas for Improvement
              </Typography>
              <Divider sx={{ mb: 2, borderColor: '#262626' }} />
              <List dense>
                {results?.weak_areas?.length > 0 ? (
                  results.weak_areas.map((area, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <Lightbulb sx={{ color: '#F59E0B' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={area.area || area}
                        secondary={area.suggestion}
                        primaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                        secondaryTypographyProps={{ sx: { color: '#888888' } }}
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem sx={{ px: 0 }}>
                    <ListItemText primary="No major areas identified for improvement!" primaryTypographyProps={{ sx: { color: '#888888' } }} />
                  </ListItem>
                )}
              </List>
            </Paper>
          </Grid>

          {/* Recommendations */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Lightbulb sx={{ color: '#0EA5E9' }} />
                Recommendations
              </Typography>
              <Divider sx={{ mb: 2, borderColor: '#262626' }} />
              <List>
                {results?.recommendations?.length > 0 ? (
                  results.recommendations.map((rec, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle sx={{ color: '#0EA5E9' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={rec.text || rec.title || rec}
                        secondary={rec.description}
                        primaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                        secondaryTypographyProps={{ sx: { color: '#888888' } }}
                      />
                    </ListItem>
                  ))
                ) : (
                  <>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}><CheckCircle sx={{ color: '#0EA5E9' }} /></ListItemIcon>
                      <ListItemText primary="Practice more interviews to build confidence" primaryTypographyProps={{ sx: { color: '#E0E0E0' } }} />
                    </ListItem>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}><CheckCircle sx={{ color: '#0EA5E9' }} /></ListItemIcon>
                      <ListItemText primary="Review common interview questions in your field" primaryTypographyProps={{ sx: { color: '#E0E0E0' } }} />
                    </ListItem>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}><CheckCircle sx={{ color: '#0EA5E9' }} /></ListItemIcon>
                      <ListItemText primary="Work on structuring your answers using the STAR method" primaryTypographyProps={{ sx: { color: '#E0E0E0' } }} />
                    </ListItem>
                  </>
                )}
              </List>
            </Paper>
          </Grid>

          {/* Questions Summary */}
          {results?.questions_summary && results.questions_summary.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <RecordVoiceOver sx={{ color: '#0EA5E9' }} />
                  Question-by-Question Analysis
                </Typography>
                <Divider sx={{ mb: 3, borderColor: '#262626' }} />
                {results.questions_summary.map((q, index) => (
                  <Card key={index} sx={{ mb: 2, bgcolor: '#0B0B0B', border: '1px solid #262626' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#FFFFFF', flex: 1 }}>
                          Q{index + 1}: {q.question}
                        </Typography>
                        <Chip 
                          label={`${q.score}%`} 
                          size="small"
                          sx={{
                            bgcolor: q.score >= 80 ? 'rgba(16, 185, 129, 0.15)' : q.score >= 60 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                            color: q.score >= 80 ? '#10B981' : q.score >= 60 ? '#F59E0B' : '#EF4444',
                            border: `1px solid ${q.score >= 80 ? 'rgba(16, 185, 129, 0.3)' : q.score >= 60 ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                          }}
                        />
                      </Box>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ color: '#888888', mb: 1 }}>
                          <strong style={{ color: '#E0E0E0' }}>Feedback:</strong> {q.feedback}
                        </Typography>
                        {q.user_answer && (
                          <Typography variant="body2" sx={{ mb: 1, p: 2, bgcolor: '#1A1A1A', borderRadius: '6px', border: '1px solid #262626', color: '#E0E0E0' }}>
                            <strong>Your Answer:</strong> {q.user_answer}
                          </Typography>
                        )}
                        {q.ideal_answer && (
                          <Typography variant="body2" sx={{ p: 2, bgcolor: 'rgba(16, 185, 129, 0.1)', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.2)', color: '#10B981' }}>
                            <strong>Ideal Answer Points:</strong> {q.ideal_answer}
                          </Typography>
                        )}
                      </Box>
                      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {q.voice_clarity && (
                          <Chip size="small" label={`Voice Clarity: ${q.voice_clarity}%`} sx={{ bgcolor: 'transparent', border: '1px solid #333333', color: '#888888' }} />
                        )}
                        {q.concept_clarity && (
                          <Chip size="small" label={`Concept Clarity: ${q.concept_clarity}%`} sx={{ bgcolor: 'transparent', border: '1px solid #333333', color: '#888888' }} />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Paper>
            </Grid>
          )}
        </Grid>

        {/* Action Buttons */}
        <Box sx={{ mt: 5, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="outlined"
            size="large"
            startIcon={<Home />}
            onClick={() => navigate('/dashboard')}
            sx={{ 
              borderColor: '#333333', 
              color: '#E0E0E0',
              '&:hover': { borderColor: '#0EA5E9', bgcolor: 'rgba(14, 165, 233, 0.08)' },
            }}
          >
            Back to Dashboard
          </Button>
          <Button
            variant="contained"
            size="large"
            startIcon={<Refresh />}
            onClick={() => navigate(`/interview/${results?.interview_type || 'general'}`)}
            sx={{ bgcolor: '#0EA5E9', '&:hover': { bgcolor: '#0284C7' } }}
          >
            Practice Again
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default Results;
