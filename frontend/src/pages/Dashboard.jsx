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
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000' }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="overline" sx={{ color: '#0EA5E9', fontWeight: 600, letterSpacing: '0.1em' }}>
            DASHBOARD
          </Typography>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#FFFFFF', mt: 0.5 }}>
            Welcome back{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}
          </Typography>
        </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 5 }}>
        <Grid item xs={12} md={4}>
          <Paper 
            sx={{ 
              p: 3, 
              bgcolor: '#1A1A1A', 
              border: '1px solid #262626',
            }}
          >
            <Box display="flex" alignItems="center" mb={2}>
              <Box sx={{ 
                width: 40, 
                height: 40, 
                bgcolor: 'rgba(14, 165, 233, 0.15)', 
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2
              }}>
                <Assessment sx={{ color: '#0EA5E9', fontSize: 22 }} />
              </Box>
              <Typography variant="body2" sx={{ color: '#888888', fontWeight: 500 }}>Total Interviews</Typography>
            </Box>
            <Typography variant="h3" sx={{ color: '#FFFFFF', fontWeight: 700 }}>{stats.total_interviews}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper 
            sx={{ 
              p: 3, 
              bgcolor: '#1A1A1A', 
              border: '1px solid #262626',
            }}
          >
            <Box display="flex" alignItems="center" mb={2}>
              <Box sx={{ 
                width: 40, 
                height: 40, 
                bgcolor: 'rgba(168, 85, 247, 0.15)', 
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2
              }}>
                <School sx={{ color: '#A855F7', fontSize: 22 }} />
              </Box>
              <Typography variant="body2" sx={{ color: '#888888', fontWeight: 500 }}>Average Score</Typography>
            </Box>
            <Typography variant="h3" sx={{ color: '#FFFFFF', fontWeight: 700 }}>{stats.average_score}%</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper 
            sx={{ 
              p: 3, 
              bgcolor: '#1A1A1A', 
              border: '1px solid #262626',
            }}
          >
            <Box display="flex" alignItems="center" mb={2}>
              <Box sx={{ 
                width: 40, 
                height: 40, 
                bgcolor: 'rgba(16, 185, 129, 0.15)', 
                borderRadius: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2
              }}>
                <TrendingUp sx={{ color: '#10B981', fontSize: 22 }} />
              </Box>
              <Typography variant="body2" sx={{ color: '#888888', fontWeight: 500 }}>Improvement</Typography>
            </Box>
            <Typography variant="h3" sx={{ color: '#10B981', fontWeight: 700 }}>
              +{stats.improvement_rate}%
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Interview Types */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, color: '#FFFFFF' }}>
          Start New Interview
        </Typography>
      </Box>
      <Grid container spacing={3} sx={{ mb: 5 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            bgcolor: '#1A1A1A', 
            border: '1px solid #262626',
            borderTop: '2px solid #10B981',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 1 }}>
                General Interview
              </Typography>
              <Typography variant="body2" sx={{ color: '#888888', lineHeight: 1.6 }}>
                Practice common interview questions and behavioral scenarios.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: '#555555' }}>
                  Duration: ~20 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions sx={{ p: 2, pt: 0 }}>
              <Button
                size="small"
                variant="contained"
                startIcon={<VideoCall />}
                onClick={() => startNewInterview('general')}
                sx={{ 
                  bgcolor: '#10B981', 
                  '&:hover': { bgcolor: '#059669' },
                }}
              >
                Start Interview
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            bgcolor: '#1A1A1A', 
            border: '1px solid #262626',
            borderTop: '2px solid #3B82F6',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 1 }}>
                Technical Interview
              </Typography>
              <Typography variant="body2" sx={{ color: '#888888', lineHeight: 1.6 }}>
                Resume-based technical questions tailored to your skills.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: '#555555' }}>
                  Duration: ~30 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions sx={{ p: 2, pt: 0 }}>
              <Button
                size="small"
                variant="contained"
                startIcon={<VideoCall />}
                onClick={() => startNewInterview('technical')}
                sx={{ 
                  bgcolor: '#3B82F6', 
                  '&:hover': { bgcolor: '#2563EB' },
                }}
              >
                Start Interview
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            bgcolor: '#1A1A1A', 
            border: '1px solid #262626',
            borderTop: '2px solid #F59E0B',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 1 }}>
                HR Interview
              </Typography>
              <Typography variant="body2" sx={{ color: '#888888', lineHeight: 1.6 }}>
                Practice HR questions about culture fit and soft skills.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: '#555555' }}>
                  Duration: ~15 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions sx={{ p: 2, pt: 0 }}>
              <Button
                size="small"
                variant="contained"
                startIcon={<VideoCall />}
                onClick={() => startNewInterview('hr')}
                sx={{ 
                  bgcolor: '#F59E0B', 
                  '&:hover': { bgcolor: '#D97706' },
                }}
              >
                Start Interview
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            bgcolor: '#1A1A1A', 
            border: '1px solid #262626',
            borderTop: '2px solid #A855F7',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
          }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', mb: 1 }}>
                UPSC Interview
              </Typography>
              <Typography variant="body2" sx={{ color: '#888888', lineHeight: 1.6 }}>
                Civil Services style: current affairs, ethics, and personality assessment.
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: '#555555' }}>
                  Duration: ~25 minutes
                </Typography>
              </Box>
            </CardContent>
            <CardActions sx={{ p: 2, pt: 0 }}>
              <Button
                size="small"
                variant="contained"
                startIcon={<Gavel />}
                onClick={() => startNewInterview('upsc')}
                sx={{ 
                  bgcolor: '#A855F7', 
                  '&:hover': { bgcolor: '#9333EA' },
                }}
              >
                Start UPSC Mock
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Interviews */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600, color: '#FFFFFF' }}>
          Recent Interviews
        </Typography>
      </Box>
      <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
        {recentInterviews.length === 0 ? (
          <Typography sx={{ color: '#555555', textAlign: 'center', py: 4 }}>
            No interviews yet. Start your first interview above!
          </Typography>
        ) : (
          recentInterviews.map((interview, index) => (
            <Box
              key={interview.id}
              sx={{
                p: 2,
                mb: index < recentInterviews.length - 1 ? 2 : 0,
                bgcolor: '#0B0B0B',
                border: '1px solid #262626',
                borderRadius: '6px',
                cursor: interview.status === 'completed' ? 'pointer' : 'default',
                transition: 'all 0.15s ease',
                '&:hover': interview.status === 'completed' ? { 
                  borderColor: '#333333',
                  bgcolor: '#111111',
                } : {},
              }}
              onClick={() => interview.status === 'completed' && navigate(`/results/${interview.id}`)}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#FFFFFF', textTransform: 'capitalize' }}>
                  {interview.interview_type} Interview
                </Typography>
                <Chip 
                  label={interview.status} 
                  size="small"
                  sx={{
                    bgcolor: interview.status === 'completed' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                    color: interview.status === 'completed' ? '#10B981' : '#F59E0B',
                    border: `1px solid ${interview.status === 'completed' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                    fontWeight: 500,
                    fontSize: '0.75rem',
                  }}
                />
              </Box>
              <Typography variant="body2" sx={{ color: '#888888', mt: 1 }}>
                {interview.status === 'completed' 
                  ? `Score: ${interview.overall_score?.toFixed(0) || 0}%`
                  : 'In Progress'
                }
              </Typography>
              {interview.status === 'completed' && (
                <Box sx={{ mt: 1.5, mb: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={interview.overall_score || 0}
                    sx={{ 
                      height: 4,
                      borderRadius: 2,
                      bgcolor: '#262626',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: interview.overall_score >= 70 ? '#10B981' : interview.overall_score >= 50 ? '#F59E0B' : '#EF4444',
                      },
                    }}
                  />
                </Box>
              )}
              <Typography variant="caption" sx={{ color: '#555555' }}>
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
    </Box>
  );
};

export default Dashboard;
