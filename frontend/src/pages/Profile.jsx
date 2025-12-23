import React from 'react';
import { Container, Typography, Paper } from '@mui/material';

const Profile = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          User Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Profile and settings page - To be implemented
        </Typography>
      </Paper>
    </Container>
  );
};

export default Profile;
