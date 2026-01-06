import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Box,
  LinearProgress,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Assessment,
  School,
  TrendingUp,
  VideoCall,
  Logout,
  Person,
  Gavel,
} from '@mui/icons-material';
import { useAuth } from '../App';
import API_URL from '../config';

const Dashboard = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [stats, setStats] = useState({
    total_interviews: 0,
    average_score: 0,
    improvement_rate: 0,
  });
  const [recentInterviews, setRecentInterviews] = useState([]);

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
    fetchRecentInterviews();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/dashboard/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStats({
          total_interviews: data.total_interviews || 0,
          average_score: data.average_score || 0,
          improvement_rate: data.improvement_rate || 0,
        });
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      // Use default mock data if API fails
      setStats({
        total_interviews: 0,
        average_score: 0,
        improvement_rate: 0,
      });
    }
  };

  const fetchRecentInterviews = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/interview/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setRecentInterviews(data);
      }
    } catch (err) {
      console.error('Failed to fetch recent interviews:', err);
    }
  };

  const startNewInterview = (type) => {
    navigate(`/interview/setup/${type}`);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Mock Interview Platform
          </Typography>
          <IconButton color="inherit" onClick={() => navigate('/profile')}>
            <Person />
          </IconButton>
          <Button color="inherit" onClick={handleLogout} startIcon={<Logout />}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Interview Dashboard
        </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Box display="flex" alignItems="center" mb={1}>
              <Assessment color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Total Interviews</Typography>
            </Box>
            <Typography variant="h3">{stats.total_interviews}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Box display="flex" alignItems="center" mb={1}>
              <School color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Average Score</Typography>
            </Box>
            <Typography variant="h3">{stats.average_score}%</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Box display="flex" alignItems="center" mb={1}>
              <TrendingUp color="success" sx={{ mr: 1 }} />
              <Typography variant="h6">Improvement</Typography>
            </Box>
            <Typography variant="h3" color="success.main">
              +{stats.improvement_rate}%
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Interview Types */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Start New Interview
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                General Interview
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Practice common interview questions and behavioral scenarios.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Duration: ~20 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                variant="contained"
                startIcon={<VideoCall />}
                onClick={() => startNewInterview('general')}
              >
                Start Interview
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Technical Interview
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Resume-based technical questions tailored to your skills.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Duration: ~30 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                variant="contained"
                startIcon={<VideoCall />}
                onClick={() => startNewInterview('technical')}
              >
                Start Interview
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                HR Interview
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Practice HR questions about culture fit and soft skills.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Duration: ~15 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                variant="contained"
                startIcon={<VideoCall />}
                onClick={() => startNewInterview('hr')}
              >
                Start Interview
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderTop: '4px solid #9c27b0' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ color: '#9c27b0' }}>
                🏛️ UPSC Interview
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Civil Services style: current affairs, ethics, and personality assessment. No resume needed.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Duration: ~25 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions>
              <Button
                size="small"
                variant="contained"
                color="secondary"
                startIcon={<Gavel />}
                onClick={() => startNewInterview('upsc')}
              >
                Start UPSC Mock
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Interviews */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Recent Interviews
      </Typography>
      <Paper sx={{ p: 2 }}>
        {recentInterviews.length === 0 ? (
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            No interviews yet. Start your first interview above!
          </Typography>
        ) : (
          recentInterviews.map((interview) => (
            <Box
              key={interview.id}
              sx={{
                p: 2,
                mb: 2,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                cursor: interview.status === 'completed' ? 'pointer' : 'default',
                '&:hover': interview.status === 'completed' ? { bgcolor: 'action.hover' } : {},
              }}
              onClick={() => interview.status === 'completed' && navigate(`/results/${interview.id}`)}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                  {interview.interview_type} Interview
                </Typography>
                <Chip 
                  label={interview.status} 
                  color={interview.status === 'completed' ? 'success' : 'warning'}
                  size="small"
                />
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {interview.status === 'completed' 
                  ? `Score: ${interview.overall_score?.toFixed(0) || 0}%`
                  : 'In Progress'
                }
              </Typography>
              {interview.status === 'completed' && (
                <LinearProgress
                  variant="determinate"
                  value={interview.overall_score || 0}
                  sx={{ mt: 1 }}
                  color={interview.overall_score >= 70 ? 'success' : interview.overall_score >= 50 ? 'warning' : 'error'}
                />
              )}
              <Typography variant="caption" color="text.secondary">
                {interview.completed_at 
                  ? `Completed: ${new Date(interview.completed_at).toLocaleDateString()}`
                  : `Started: ${new Date(interview.created_at).toLocaleDateString()}`
                }
              </Typography>
            </Box>
          ))
        )}
      </Paper>
    </Container>
    </>
  );
};

export default Dashboard;
