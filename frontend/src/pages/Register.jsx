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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
} from '@mui/material';
import { Check, Close, ArrowBack } from '@mui/icons-material';
import API_URL from '../config';

// Password validation rules
const passwordRules = [
  { id: 'length', label: 'At least 8 characters', test: (pwd) => pwd.length >= 8 },
  { id: 'uppercase', label: 'One uppercase letter (A-Z)', test: (pwd) => /[A-Z]/.test(pwd) },
  { id: 'lowercase', label: 'One lowercase letter (a-z)', test: (pwd) => /[a-z]/.test(pwd) },
  { id: 'number', label: 'One number (0-9)', test: (pwd) => /[0-9]/.test(pwd) },
  { id: 'special', label: 'One special character (!@#$%^&*)', test: (pwd) => /[!@#$%^&*(),.?":{}|<>]/.test(pwd) },
];

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validatePassword = (password) => {
    return passwordRules.every((rule) => rule.test(password));
  };

  const validateUsername = (username) => {
    // Username: 3-20 characters, alphanumeric and underscores only
    return /^[a-zA-Z0-9_]{3,20}$/.test(username);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate username
    if (!validateUsername(formData.username)) {
      setError('Username must be 3-20 characters and contain only letters, numbers, and underscores');
      return;
    }

    // Validate password
    if (!validatePassword(formData.password)) {
      setError('Password does not meet all requirements');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          full_name: formData.full_name,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        navigate('/login', { state: { message: 'Registration successful! Please login.' } });
      } else {
        setError(data.detail || 'Registration failed. Please try again.');
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError('Unable to connect to server. Please make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#000000', py: 6, display: 'flex', alignItems: 'center', position: 'relative' }}>
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
            Create your account
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
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                '& .MuiInputLabel-root': { color: '#888888' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#0EA5E9' },
              }}
            />
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
              helperText="3-20 characters, letters, numbers, and underscores only"
              sx={{
                '& .MuiInputLabel-root': { color: '#888888' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#0EA5E9' },
                '& .MuiFormHelperText-root': { color: '#555555' },
              }}
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              required
              autoComplete="email"
              sx={{
                '& .MuiInputLabel-root': { color: '#888888' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#0EA5E9' },
              }}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
              autoComplete="new-password"
              sx={{
                '& .MuiInputLabel-root': { color: '#888888' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#0EA5E9' },
              }}
            />
            
            {/* Password Requirements */}
            {formData.password && (
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 2, 
                  mt: 2, 
                  mb: 2, 
                  bgcolor: '#0B0B0B', 
                  border: '1px solid #333333' 
                }}
              >
                <Typography variant="subtitle2" sx={{ color: '#888888', mb: 1 }}>
                  Password Requirements:
                </Typography>
                <List dense>
                  {passwordRules.map((rule) => {
                    const passed = rule.test(formData.password);
                    return (
                      <ListItem key={rule.id} sx={{ py: 0 }}>
                        <ListItemIcon sx={{ minWidth: 28 }}>
                          {passed ? (
                            <Check fontSize="small" sx={{ color: '#10B981' }} />
                          ) : (
                            <Close fontSize="small" sx={{ color: '#555555' }} />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={rule.label}
                          primaryTypographyProps={{
                            variant: 'body2',
                            sx: { color: passed ? '#10B981' : '#555555' },
                          }}
                        />
                      </ListItem>
                    );
                  })}
                </List>
              </Paper>
            )}

            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              margin="normal"
              required
              autoComplete="new-password"
              error={formData.confirmPassword && formData.password !== formData.confirmPassword}
              helperText={
                formData.confirmPassword && formData.password !== formData.confirmPassword
                  ? 'Passwords do not match'
                  : ''
              }
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
              {loading ? <CircularProgress size={24} sx={{ color: '#FFFFFF' }} /> : 'Register'}
            </Button>
          </Box>

          <Typography align="center" sx={{ mt: 3, color: '#888888' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: '#0EA5E9', textDecoration: 'none' }}>
              Login here
            </Link>
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default Register;
