import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Avatar,
  Divider,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  EmojiEvents as TrophyIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as TimeIcon,
  Star as StarIcon,
  WorkspacePremium as BadgeIcon,
} from '@mui/icons-material';
import { useAuth } from '../App';
import API_URL from '../config';

const Profile = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalInterviews: 0,
    averageScore: 0,
    totalPracticeTime: 0,
    bestCategory: '-',
    improvementRate: 0,
    currentStreak: 0,
    longestStreak: 0,
    rank: 'Beginner',
  });
  const [skills, setSkills] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/api/dashboard/stats`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          const s = data.stats || {};

          // Determine best category
          const categories = [
            { name: 'General', avg: s.general_avg || 0 },
            { name: 'Technical', avg: s.technical_avg || 0 },
            { name: 'HR', avg: s.hr_avg || 0 },
          ];
          const best = categories.reduce((a, b) => (b.avg > a.avg ? b : a), categories[0]);
          const bestCategory = best.avg > 0 ? best.name : '-';

          // Determine rank based on average score
          const avg = s.average_score || 0;
          let rank = 'Beginner';
          if (avg >= 90) rank = 'Master';
          else if (avg >= 80) rank = 'Expert';
          else if (avg >= 65) rank = 'Advanced';
          else if (avg >= 40) rank = 'Intermediate';

          setStats(prev => ({
            ...prev,
            totalInterviews: s.completed_interviews || 0,
            averageScore: s.average_score || 0,
            improvementRate: s.improvement_rate || 0,
            totalPracticeTime: Math.round(s.total_practice_time || 0),
            currentStreak: s.current_streak || 0,
            bestCategory,
            rank,
          }));

          // Populate skills from skill_analysis
          const skillColors = ['#0EA5E9', '#10B981', '#F59E0B', '#A855F7', '#EF4444', '#EC4899'];
          if (data.skill_analysis && data.skill_analysis.length > 0) {
            setSkills(data.skill_analysis.map((sk, idx) => ({
              name: sk.skill_name,
              score: Math.round(sk.current_level),
              color: skillColors[idx % skillColors.length],
            })));
          }
        }
      } catch (err) {
        console.error('Failed to fetch profile stats:', err);
      }
    };
    fetchStats();
  }, []);

  // Achievement badges - using Material Icons instead of emojis for consistency
  const achievements = [
    { name: 'First Interview', description: 'Completed your first mock interview', earned: true, icon: 'target' },
    { name: 'Consistent Learner', description: 'Practiced 3 days in a row', earned: true, icon: 'streak' },
    { name: 'High Scorer', description: 'Scored above 85% in an interview', earned: true, icon: 'star' },
    { name: 'Quick Learner', description: 'Improved score by 10% in a week', earned: true, icon: 'trending' },
    { name: 'Interview Master', description: 'Complete 10 interviews', earned: false, icon: 'crown' },
    { name: 'Perfect Score', description: 'Score 100% in any category', earned: false, icon: 'perfect' },
  ];



  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const getRankColor = (rank) => {
    switch (rank) {
      case 'Beginner': return '#888888';
      case 'Intermediate': return '#0EA5E9';
      case 'Advanced': return '#F59E0B';
      case 'Expert': return '#10B981';
      case 'Master': return '#A855F7';
      default: return '#0EA5E9';
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000', py: 4 }}>
      <Container maxWidth="lg">
        {/* Profile Header */}
        <Paper sx={{ p: 4, mb: 4, bgcolor: '#0B0B0B', border: '1px solid #262626' }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item>
              <Avatar
                sx={{
                  width: 100,
                  height: 100,
                  bgcolor: '#0EA5E9',
                  color: '#FFFFFF',
                  fontSize: '2rem',
                  fontWeight: 700,
                }}
              >
                {getInitials(user?.full_name || user?.username)}
              </Avatar>
            </Grid>
            <Grid item xs>
              <Typography variant="h4" sx={{ color: '#FFFFFF', fontWeight: 700 }}>
                {user?.full_name || user?.username || 'Demo User'}
              </Typography>
              <Typography variant="body1" sx={{ color: '#888888', mt: 0.5 }}>
                {user?.email || 'demo@example.com'}
              </Typography>
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Chip
                  label={stats.rank}
                  sx={{
                    bgcolor: `${getRankColor(stats.rank)}20`,
                    color: getRankColor(stats.rank),
                    border: `1px solid ${getRankColor(stats.rank)}40`,
                    fontWeight: 600,
                  }}
                />
                <Chip
                  icon={<TrophyIcon sx={{ color: '#F59E0B !important', fontSize: 18 }} />}
                  label={`${achievements.filter(a => a.earned).length} Achievements`}
                  sx={{ 
                    bgcolor: 'rgba(245, 158, 11, 0.15)', 
                    color: '#F59E0B',
                    border: '1px solid rgba(245, 158, 11, 0.3)',
                  }}
                />
              </Box>
            </Grid>
            <Grid item>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h3" sx={{ fontWeight: 700, color: '#0EA5E9' }}>
                  {stats.averageScore}%
                </Typography>
                <Typography variant="body2" sx={{ color: '#888888' }}>Average Score</Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        <Grid container spacing={3}>
          {/* Stats Cards */}
          <Grid item xs={12} md={8}>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#0EA5E9', fontWeight: 700 }}>{stats.totalInterviews}</Typography>
                    <Typography variant="body2" sx={{ color: '#888888' }}>Total Interviews</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#10B981', fontWeight: 700 }}>{stats.totalPracticeTime}m</Typography>
                    <Typography variant="body2" sx={{ color: '#888888' }}>Practice Time</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#F59E0B', fontWeight: 700 }}>{stats.currentStreak}</Typography>
                    <Typography variant="body2" sx={{ color: '#888888' }}>Day Streak</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card sx={{ bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ color: '#A855F7', fontWeight: 700 }}>+{stats.improvementRate}%</Typography>
                    <Typography variant="body2" sx={{ color: '#888888' }}>Improvement</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Skills Breakdown */}
            <Paper sx={{ p: 3, mt: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TrendingUpIcon sx={{ color: '#0EA5E9' }} /> Skills Breakdown
              </Typography>
              <Divider sx={{ mb: 3, borderColor: '#262626' }} />
              {skills.length === 0 ? (
                <Typography variant="body2" sx={{ color: '#888888', textAlign: 'center', py: 2 }}>
                  Complete interviews to see your skills breakdown
                </Typography>
              ) : skills.map((skill) => (
                <Box key={skill.name} sx={{ mb: 2.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ color: '#E0E0E0' }}>{skill.name}</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#FFFFFF' }}>{skill.score}%</Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={skill.score}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      bgcolor: '#262626',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: skill.color,
                        borderRadius: 3,
                      },
                    }}
                  />
                </Box>
              ))}
            </Paper>
          </Grid>

          {/* Right Sidebar */}
          <Grid item xs={12} md={4}>
            {/* Account Info */}
            <Paper sx={{ p: 3, mb: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PersonIcon sx={{ color: '#0EA5E9' }} /> Account Info
              </Typography>
              <Divider sx={{ mb: 2, borderColor: '#262626' }} />
              <List dense>
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}><PersonIcon sx={{ color: '#555555' }} /></ListItemIcon>
                  <ListItemText 
                    primary="Username" 
                    secondary={user?.username || 'demo_user'} 
                    primaryTypographyProps={{ sx: { color: '#888888', fontSize: '0.8rem' } }}
                    secondaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                  />
                </ListItem>
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}><EmailIcon sx={{ color: '#555555' }} /></ListItemIcon>
                  <ListItemText 
                    primary="Email" 
                    secondary={user?.email || 'demo@example.com'} 
                    primaryTypographyProps={{ sx: { color: '#888888', fontSize: '0.8rem' } }}
                    secondaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                  />
                </ListItem>
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}><CalendarIcon sx={{ color: '#555555' }} /></ListItemIcon>
                  <ListItemText 
                    primary="Member Since" 
                    secondary="January 2025" 
                    primaryTypographyProps={{ sx: { color: '#888888', fontSize: '0.8rem' } }}
                    secondaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                  />
                </ListItem>
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon sx={{ minWidth: 36 }}><StarIcon sx={{ color: '#555555' }} /></ListItemIcon>
                  <ListItemText 
                    primary="Best Category" 
                    secondary={stats.bestCategory} 
                    primaryTypographyProps={{ sx: { color: '#888888', fontSize: '0.8rem' } }}
                    secondaryTypographyProps={{ sx: { color: '#FFFFFF' } }}
                  />
                </ListItem>
              </List>
            </Paper>

            {/* Achievements */}
            <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
              <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BadgeIcon sx={{ color: '#0EA5E9' }} /> Achievements
              </Typography>
              <Divider sx={{ mb: 2, borderColor: '#262626' }} />
              <Grid container spacing={1}>
                {achievements.map((achievement) => (
                  <Grid item xs={6} key={achievement.name}>
                    <Box
                      sx={{
                        p: 1.5,
                        textAlign: 'center',
                        borderRadius: '6px',
                        bgcolor: achievement.earned ? 'rgba(14, 165, 233, 0.1)' : '#0B0B0B',
                        opacity: achievement.earned ? 1 : 0.4,
                        border: achievement.earned ? '1px solid rgba(14, 165, 233, 0.3)' : '1px dashed #333333',
                      }}
                    >
                      <Box sx={{ 
                        width: 32, 
                        height: 32, 
                        bgcolor: achievement.earned ? 'rgba(14, 165, 233, 0.2)' : '#1A1A1A',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mx: 'auto',
                        mb: 1,
                      }}>
                        <StarIcon sx={{ color: achievement.earned ? '#0EA5E9' : '#555555', fontSize: 18 }} />
                      </Box>
                      <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', color: achievement.earned ? '#FFFFFF' : '#555555' }}>
                        {achievement.name}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Profile;
