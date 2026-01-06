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

const Profile = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalInterviews: 4,
    averageScore: 79,
    totalPracticeTime: 79,
    bestCategory: 'HR',
    improvementRate: 12.5,
    currentStreak: 3,
    longestStreak: 7,
    rank: 'Intermediate',
  });

  // Achievement badges
  const achievements = [
    { name: 'First Interview', description: 'Completed your first mock interview', earned: true, icon: '🎯' },
    { name: 'Consistent Learner', description: 'Practiced 3 days in a row', earned: true, icon: '🔥' },
    { name: 'High Scorer', description: 'Scored above 85% in an interview', earned: true, icon: '⭐' },
    { name: 'Quick Learner', description: 'Improved score by 10% in a week', earned: true, icon: '📈' },
    { name: 'Interview Master', description: 'Complete 10 interviews', earned: false, icon: '👑' },
    { name: 'Perfect Score', description: 'Score 100% in any category', earned: false, icon: '💯' },
  ];

  // Skill breakdown
  const skills = [
    { name: 'Technical Knowledge', score: 82, color: '#2196f3' },
    { name: 'Communication', score: 78, color: '#4caf50' },
    { name: 'Problem Solving', score: 85, color: '#ff9800' },
    { name: 'Confidence', score: 75, color: '#9c27b0' },
    { name: 'Body Language', score: 70, color: '#f44336' },
  ];

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const getRankColor = (rank) => {
    switch (rank) {
      case 'Beginner': return '#9e9e9e';
      case 'Intermediate': return '#2196f3';
      case 'Advanced': return '#ff9800';
      case 'Expert': return '#4caf50';
      case 'Master': return '#9c27b0';
      default: return '#2196f3';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Profile Header */}
      <Paper sx={{ p: 4, mb: 3, background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)' }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item>
            <Avatar
              sx={{
                width: 100,
                height: 100,
                bgcolor: '#fff',
                color: '#1976d2',
                fontSize: '2rem',
                fontWeight: 'bold',
              }}
            >
              {getInitials(user?.full_name || user?.username)}
            </Avatar>
          </Grid>
          <Grid item xs>
            <Typography variant="h4" sx={{ color: '#fff', fontWeight: 'bold' }}>
              {user?.full_name || user?.username || 'Demo User'}
            </Typography>
            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)', mt: 0.5 }}>
              {user?.email || 'demo@example.com'}
            </Typography>
            <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
              <Chip
                label={stats.rank}
                sx={{
                  bgcolor: getRankColor(stats.rank),
                  color: '#fff',
                  fontWeight: 'bold',
                }}
              />
              <Chip
                icon={<TrophyIcon sx={{ color: '#fff !important' }} />}
                label={`${achievements.filter(a => a.earned).length} Achievements`}
                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: '#fff' }}
              />
            </Box>
          </Grid>
          <Grid item>
            <Box sx={{ textAlign: 'center', color: '#fff' }}>
              <Typography variant="h3" sx={{ fontWeight: 'bold' }}>
                {stats.averageScore}%
              </Typography>
              <Typography variant="body2">Average Score</Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">{stats.totalInterviews}</Typography>
                  <Typography variant="body2" color="text.secondary">Total Interviews</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">{stats.totalPracticeTime}m</Typography>
                  <Typography variant="body2" color="text.secondary">Practice Time</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">{stats.currentStreak}</Typography>
                  <Typography variant="body2" color="text.secondary">Day Streak 🔥</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">+{stats.improvementRate}%</Typography>
                  <Typography variant="body2" color="text.secondary">Improvement</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Skills Breakdown */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUpIcon color="primary" /> Skills Breakdown
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {skills.map((skill) => (
              <Box key={skill.name} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">{skill.name}</Typography>
                  <Typography variant="body2" fontWeight="bold">{skill.score}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={skill.score}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'grey.200',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: skill.color,
                      borderRadius: 4,
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
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <PersonIcon color="primary" /> Account Info
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <List dense>
              <ListItem>
                <ListItemIcon><PersonIcon /></ListItemIcon>
                <ListItemText primary="Username" secondary={user?.username || 'demo_user'} />
              </ListItem>
              <ListItem>
                <ListItemIcon><EmailIcon /></ListItemIcon>
                <ListItemText primary="Email" secondary={user?.email || 'demo@example.com'} />
              </ListItem>
              <ListItem>
                <ListItemIcon><CalendarIcon /></ListItemIcon>
                <ListItemText primary="Member Since" secondary="January 2026" />
              </ListItem>
              <ListItem>
                <ListItemIcon><StarIcon /></ListItemIcon>
                <ListItemText primary="Best Category" secondary={stats.bestCategory} />
              </ListItem>
            </List>
          </Paper>

          {/* Achievements */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <BadgeIcon color="primary" /> Achievements
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={1}>
              {achievements.map((achievement) => (
                <Grid item xs={6} key={achievement.name}>
                  <Box
                    sx={{
                      p: 1.5,
                      textAlign: 'center',
                      borderRadius: 2,
                      bgcolor: achievement.earned ? 'primary.50' : 'grey.100',
                      opacity: achievement.earned ? 1 : 0.5,
                      border: achievement.earned ? '2px solid' : '2px dashed',
                      borderColor: achievement.earned ? 'primary.main' : 'grey.300',
                    }}
                  >
                    <Typography variant="h5">{achievement.icon}</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block' }}>
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
  );
};

export default Profile;
