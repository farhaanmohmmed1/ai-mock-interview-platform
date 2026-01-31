import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
  IconButton,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useAuth } from '../App';
import API_URL from '../config';

const Login = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        login(data.access_token, data.user);
        navigate('/dashboard');
      } else {
        setError(data.detail || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Unable to connect to server. Please make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000', display: 'flex', alignItems: 'center', position: 'relative' }}>
      {/* Back to Home Button */}
      <IconButton
        component={Link}
        to="/"
        sx={{
          position: 'absolute',
          top: 24,
          left: 24,
          color: '#888888',
          '&:hover': { color: '#FFFFFF', bgcolor: 'rgba(255,255,255,0.1)' },
        }}
      >
        <ArrowBack />
      </IconButton>
      
      <Container maxWidth="sm">
        <Paper 
          sx={{ 
            p: 5, 
            bgcolor: '#1A1A1A', 
            border: '1px solid #262626',
          }}
        >
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#FFFFFF', textAlign: 'center' }}>
            AI Mock Interview
          </Typography>
          <Typography variant="body1" sx={{ color: '#888888', textAlign: 'center', mt: 1, mb: 4 }}>
            Login to your account
          </Typography>

          {error && (
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
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
              autoComplete="username"
              sx={{
                '& .MuiInputLabel-root': { color: '#888888' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#0EA5E9' },
              }}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
              autoComplete="current-password"
              sx={{
                '& .MuiInputLabel-root': { color: '#888888' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#0EA5E9' },
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ 
                mt: 3, 
                mb: 2, 
                py: 1.5,
                bgcolor: '#0EA5E9',
                '&:hover': { bgcolor: '#0284C7' },
              }}
            >
              {loading ? <CircularProgress size={24} sx={{ color: '#FFFFFF' }} /> : 'Login'}
            </Button>
          </Box>

          <Typography align="center" sx={{ mt: 3, color: '#888888' }}>
            Don't have an account?{' '}
            <Link to="/register" style={{ color: '#0EA5E9', textDecoration: 'none' }}>
              Register here
            </Link>
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default Login;
