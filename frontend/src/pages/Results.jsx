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
  School,
  OpenInNew,
  Download,
  PictureAsPdf,
  Mic,
  Videocam,
} from '@mui/icons-material';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import { useAuth } from '../App';
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
  const { logout } = useAuth();
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
      
      if (response.status === 401) {
        logout();
        navigate('/login');
        return;
      }
      
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
    if (score >= 40) return { grade: 'D', label: 'Needs Improvement' };
    if (score > 0) return { grade: 'E', label: 'Poor' };
    return { grade: 'F', label: 'No Answers Submitted' };
  };

  const [exporting, setExporting] = useState(false);

  const exportReport = async () => {
    setExporting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/interview/${id}/export`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        alert(errorData.detail || 'Failed to export report');
        return;
      }

      const data = await response.json();
      
      // Generate PDF
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 20;
      let yPos = margin;
      
      // Helper function to add new page if needed
      const checkPageBreak = (height = 10) => {
        if (yPos + height > pageHeight - margin) {
          doc.addPage();
          yPos = margin;
          return true;
        }
        return false;
      };
      
      // Helper to add section header
      const addSectionHeader = (text) => {
        checkPageBreak(15);
        doc.setFillColor(14, 165, 233); // #0EA5E9
        doc.rect(margin, yPos, pageWidth - 2 * margin, 8, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.text(text, margin + 3, yPos + 5.5);
        doc.setTextColor(0, 0, 0);
        yPos += 12;
      };
      
      // Title
      doc.setFillColor(11, 11, 11);
      doc.rect(0, 0, pageWidth, 45, 'F');
      doc.setTextColor(14, 165, 233);
      doc.setFontSize(22);
      doc.setFont('helvetica', 'bold');
      doc.text('AI MOCK INTERVIEW REPORT', pageWidth / 2, 20, { align: 'center' });
      doc.setTextColor(150, 150, 150);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Generated: ${new Date(data.report_generated_at).toLocaleString()}`, pageWidth / 2, 30, { align: 'center' });
      doc.setTextColor(0, 0, 0);
      yPos = 55;
      
      // Grade circle (simulated)
      const gradeColor = data.overall_performance.overall_score >= 80 ? [16, 185, 129] :
                         data.overall_performance.overall_score >= 60 ? [245, 158, 11] : [239, 68, 68];
      doc.setFillColor(...gradeColor);
      doc.circle(pageWidth / 2, yPos + 15, 18, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text(data.overall_performance.grade.letter, pageWidth / 2, yPos + 18, { align: 'center' });
      doc.setTextColor(0, 0, 0);
      doc.setFontSize(12);
      doc.text(`${data.overall_performance.grade.label} - ${data.overall_performance.overall_score?.toFixed(1) || 0}%`, pageWidth / 2, yPos + 38, { align: 'center' });
      yPos += 50;
      
      // Candidate & Interview Info side by side
      addSectionHeader('CANDIDATE & INTERVIEW DETAILS');
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      const col1 = margin;
      const col2 = pageWidth / 2 + 5;
      doc.text(`Name: ${data.candidate_info.name}`, col1, yPos);
      doc.text(`Type: ${data.interview_details.interview_type}`, col2, yPos);
      yPos += 6;
      doc.text(`Email: ${data.candidate_info.email}`, col1, yPos);
      doc.text(`Difficulty: ${data.interview_details.difficulty_level}`, col2, yPos);
      yPos += 6;
      doc.text(`Duration: ${data.interview_details.duration_minutes?.toFixed(1) || 0} minutes`, col1, yPos);
      doc.text(`Questions: ${data.interview_details.answered_questions}/${data.interview_details.total_questions}`, col2, yPos);
      yPos += 12;
      
      // Score Breakdown Table
      addSectionHeader('PERFORMANCE SCORES');
      const scores = [
        ['Content', `${data.overall_performance.content_score?.toFixed(1) || 0}%`],
        ['Clarity', `${data.overall_performance.clarity_score?.toFixed(1) || 0}%`],
        ['Fluency', `${data.overall_performance.fluency_score?.toFixed(1) || 0}%`],
        ['Confidence', `${data.overall_performance.confidence_score?.toFixed(1) || 0}%`],
        ['Emotion', `${data.overall_performance.emotion_score?.toFixed(1) || 0}%`],
      ];
      autoTable(doc, {
        startY: yPos,
        head: [['Metric', 'Score']],
        body: scores,
        theme: 'striped',
        headStyles: { fillColor: [14, 165, 233], textColor: 255 },
        margin: { left: margin, right: margin },
        tableWidth: pageWidth - 2 * margin,
      });
      yPos = (doc).lastAutoTable.finalY + 10;
      
      // Strong Areas
      if (data.analysis.strong_areas?.length > 0) {
        addSectionHeader('STRONG AREAS');
        doc.setFontSize(10);
        data.analysis.strong_areas.forEach(area => {
          checkPageBreak(8);
          doc.setTextColor(16, 185, 129);
          doc.text('✓', margin, yPos);
          doc.setTextColor(0, 0, 0);
          doc.text(`${area.area}: ${area.score?.toFixed(1) || 0}%`, margin + 6, yPos);
          yPos += 6;
          if (area.description) {
            doc.setTextColor(100, 100, 100);
            doc.text(`  ${area.description}`, margin + 6, yPos);
            doc.setTextColor(0, 0, 0);
            yPos += 6;
          }
        });
        yPos += 5;
      }
      
      // Weak Areas
      if (data.analysis.weak_areas?.length > 0) {
        addSectionHeader('AREAS FOR IMPROVEMENT');
        doc.setFontSize(10);
        data.analysis.weak_areas.forEach(area => {
          checkPageBreak(14);
          const areaScore = area.score ?? area.average_score ?? 0;
          const areaName = area.area || 'Unknown';
          const suggestion = area.suggestion || (areaScore < 50 
            ? `Focus on improving ${areaName} through practice.`
            : areaScore < 75 
              ? `Good foundation in ${areaName}. Add more depth.`
              : `Strong ${areaName}. Keep refining.`);
          doc.setTextColor(239, 68, 68);
          doc.text('•', margin, yPos);
          doc.setTextColor(0, 0, 0);
          doc.text(`${areaName}: ${areaScore.toFixed(1)}%`, margin + 6, yPos);
          yPos += 6;
          doc.setTextColor(100, 100, 100);
          const lines = doc.splitTextToSize(`Suggestion: ${suggestion}`, pageWidth - 2 * margin - 10);
          lines.forEach(line => {
            checkPageBreak(6);
            doc.text(line, margin + 6, yPos);
            yPos += 5;
          });
          doc.setTextColor(0, 0, 0);
        });
        yPos += 5;
      }
      
      // Overall Feedback
      if (data.analysis.feedback) {
        addSectionHeader('OVERALL FEEDBACK');
        doc.setFontSize(10);
        const feedbackLines = doc.splitTextToSize(data.analysis.feedback, pageWidth - 2 * margin);
        feedbackLines.forEach(line => {
          checkPageBreak(6);
          doc.text(line, margin, yPos);
          yPos += 5;
        });
        yPos += 5;
      }
      
      // Recommendations
      if (data.analysis.recommendations?.length > 0) {
        addSectionHeader('RECOMMENDATIONS');
        doc.setFontSize(10);
        data.analysis.recommendations.forEach((rec, i) => {
          checkPageBreak(8);
          const text = rec.text || rec.title || rec.description || (typeof rec === 'string' ? rec : 'See detailed feedback');
          const lines = doc.splitTextToSize(`${i + 1}. ${text}`, pageWidth - 2 * margin);
          lines.forEach(line => {
            checkPageBreak(6);
            doc.text(line, margin, yPos);
            yPos += 5;
          });
          yPos += 2;
        });
        yPos += 5;
      }
      
      // Questions Detail
      addSectionHeader('DETAILED QUESTION ANALYSIS');
      data.questions_detail.forEach((q, i) => {
        checkPageBreak(40);
        
        // Question header
        doc.setFillColor(240, 240, 240);
        doc.rect(margin, yPos, pageWidth - 2 * margin, 8, 'F');
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.text(`Q${i + 1}: ${q.question_type || 'General'} | ${q.category || 'N/A'} | ${q.difficulty || 'N/A'}`, margin + 2, yPos + 5.5);
        doc.setFont('helvetica', 'normal');
        yPos += 12;
        
        // Question text
        const qLines = doc.splitTextToSize(q.question_text, pageWidth - 2 * margin);
        qLines.forEach(line => {
          checkPageBreak(6);
          doc.text(line, margin, yPos);
          yPos += 5;
        });
        yPos += 3;
        
        if (q.user_answer) {
          // Answer
          doc.setTextColor(14, 165, 233);
          doc.text('Your Answer:', margin, yPos);
          doc.setTextColor(0, 0, 0);
          yPos += 5;
          const ansLines = doc.splitTextToSize(q.user_answer, pageWidth - 2 * margin - 5);
          ansLines.forEach(line => {
            checkPageBreak(6);
            doc.text(line, margin + 3, yPos);
            yPos += 5;
          });
          yPos += 3;
          
          // Scores row
          if (q.scores) {
            checkPageBreak(10);
            const scoreText = `Content: ${q.scores.content_score?.toFixed(0) || '-'}% | Relevance: ${q.scores.relevance_score?.toFixed(0) || '-'}% | Clarity: ${q.scores.clarity_score?.toFixed(0) || '-'}% | Fluency: ${q.scores.fluency_score?.toFixed(0) || '-'}% | Confidence: ${q.scores.confidence_score?.toFixed(0) || '-'}%`;
            doc.setFontSize(9);
            doc.setTextColor(100, 100, 100);
            doc.text(scoreText, margin, yPos);
            doc.setTextColor(0, 0, 0);
            doc.setFontSize(10);
            yPos += 6;
          }
          
          // Feedback
          if (q.feedback) {
            checkPageBreak(10);
            doc.setTextColor(16, 185, 129);
            doc.text('Feedback:', margin, yPos);
            doc.setTextColor(0, 0, 0);
            yPos += 5;
            const fbLines = doc.splitTextToSize(q.feedback, pageWidth - 2 * margin - 5);
            fbLines.forEach(line => {
              checkPageBreak(6);
              doc.text(line, margin + 3, yPos);
              yPos += 5;
            });
          }
          
          // Suggestions
          if (q.improvement_suggestions?.length > 0) {
            checkPageBreak(10);
            doc.setTextColor(245, 158, 11);
            doc.text('Suggestions:', margin, yPos);
            doc.setTextColor(0, 0, 0);
            yPos += 5;
            q.improvement_suggestions.forEach(s => {
              checkPageBreak(6);
              doc.text(`• ${s}`, margin + 3, yPos);
              yPos += 5;
            });
          }
        } else {
          doc.setTextColor(150, 150, 150);
          doc.text('(Not answered)', margin, yPos);
          doc.setTextColor(0, 0, 0);
          yPos += 6;
        }
        
        yPos += 8;
      });
      
      // Footer on last page
      doc.setFontSize(8);
      doc.setTextColor(150, 150, 150);
      doc.text('AI Mock Interview Platform - Interview Report', pageWidth / 2, pageHeight - 10, { align: 'center' });
      
      // Save PDF
      doc.save(`interview_report_${id}_${new Date().toISOString().split('T')[0]}.pdf`);
      
    } catch (err) {
      console.error('Export error:', err);
      alert('Failed to export report: ' + err.message);
    } finally {
      setExporting(false);
    }
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
                {/* Content */}
                <Grid item>
                  <ScoreCircle
                    score={results?.content_score}
                    label="Content"
                    color={getScoreColor(results?.content_score)}
                  />
                </Grid>
                
                {/* Clarity */}
                <Grid item>
                  <ScoreCircle
                    score={results?.clarity_score}
                    label="Clarity"
                    color={getScoreColor(results?.clarity_score)}
                  />
                </Grid>
                
                {/* Fluency */}
                <Grid item>
                  <ScoreCircle
                    score={results?.fluency_score}
                    label="Fluency"
                    color={getScoreColor(results?.fluency_score)}
                  />
                </Grid>
                
                {/* Confidence */}
                <Grid item>
                  <ScoreCircle
                    score={results?.confidence_score}
                    label="Confidence"
                    color={getScoreColor(results?.confidence_score)}
                  />
                </Grid>
                
                {/* Expression */}
                <Grid item>
                  <ScoreCircle
                    score={results?.emotion_score}
                    label="Expression"
                    color={getScoreColor(results?.emotion_score)}
                  />
                </Grid>
              </Grid>
              
              {/* Mode indicator */}
              {results?.emotion_score != null && results?.emotion_score > 0 ? (
                <Typography variant="caption" sx={{ color: '#10B981', display: 'block', textAlign: 'center', mt: 2 }}>
                  Full evaluation mode: All metrics scored.
                </Typography>
              ) : (
                <Typography variant="caption" sx={{ color: '#888', display: 'block', textAlign: 'center', mt: 2 }}>
                  Enable camera for enhanced Expression scoring.
                </Typography>
              )}
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
              {(results?.feedback || 'Great job completing the interview! Review the detailed scores above to understand your performance.')
                .split('\n\n')
                .map((paragraph, index) => (
                  <Typography key={index} variant="body1" sx={{ color: '#E0E0E0', lineHeight: 1.8, mb: index < (results?.feedback || '').split('\n\n').length - 1 ? 2 : 0 }}>
                    {paragraph}
                  </Typography>
                ))
              }
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
                    <ListItem key={index} sx={{ px: 0, alignItems: 'flex-start' }}>
                      <ListItemIcon sx={{ minWidth: 36, mt: 0.5 }}>
                        <TrendingUp sx={{ color: '#10B981' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <span>{area.area || area}</span>
                            {area.score && (
                              <Chip 
                                label={`${Math.round(area.score)}%`}
                                size="small"
                                sx={{ 
                                  height: 20, 
                                  fontSize: '0.7rem', 
                                  fontWeight: 600,
                                  bgcolor: 'rgba(16, 185, 129, 0.15)', 
                                  color: '#10B981', 
                                  border: '1px solid rgba(16, 185, 129, 0.3)' 
                                }} 
                              />
                            )}
                          </Box>
                        }
                        secondary={area.description}
                        primaryTypographyProps={{ sx: { color: '#FFFFFF', fontWeight: 500 } }}
                        secondaryTypographyProps={{ sx: { color: '#999999', mt: 0.5, lineHeight: 1.6 } }}
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
                  results.weak_areas.map((area, index) => {
                    const areaScore = area.score ?? area.average_score ?? 0;
                    const areaName = area.area || area;
                    const suggestion = area.suggestion || (areaScore < 50 
                      ? `Focus on improving your ${areaName} skills through targeted practice.`
                      : areaScore < 75 
                        ? `Good foundation in ${areaName}. Work on adding more depth and examples.`
                        : `Strong ${areaName} skills. Keep refining for excellence.`);
                    return (
                      <ListItem key={index} sx={{ px: 0, alignItems: 'flex-start' }}>
                        <ListItemIcon sx={{ minWidth: 36, mt: 0.5 }}>
                          <Lightbulb sx={{ color: '#F59E0B' }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <span>{areaName}</span>
                              <Chip 
                                label={`${Math.round(areaScore)}%`}
                                size="small"
                                sx={{ 
                                  height: 20, 
                                  fontSize: '0.7rem', 
                                  fontWeight: 600,
                                  bgcolor: area.severity === 'high' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)', 
                                  color: area.severity === 'high' ? '#EF4444' : '#F59E0B', 
                                  border: `1px solid ${area.severity === 'high' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(245, 158, 11, 0.3)'}` 
                                }} 
                              />
                            </Box>
                          }
                          secondary={suggestion}
                          primaryTypographyProps={{ sx: { color: '#FFFFFF', fontWeight: 500 } }}
                          secondaryTypographyProps={{ sx: { color: '#999999', mt: 0.5, lineHeight: 1.6 } }}
                        />
                      </ListItem>
                    );
                  })
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
              
              {results?.recommendations?.length > 0 ? (
                <>
                  {/* Mode Recommendations (Mic/Camera) */}
                  {results.recommendations.filter(r => r.type === 'mode').length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle2" sx={{ color: '#F59E0B', mb: 1, fontWeight: 600 }}>
                        Enhance Your Evaluation
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {results.recommendations.filter(r => r.type === 'mode').map((rec, index) => (
                          <Box 
                            key={`mode-${index}`}
                            sx={{ 
                              p: 2, 
                              borderRadius: 2, 
                              bgcolor: rec.action === 'enable_audio' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(139, 92, 246, 0.1)',
                              border: `1px solid ${rec.action === 'enable_audio' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(139, 92, 246, 0.3)'}`,
                              display: 'flex',
                              alignItems: 'flex-start',
                              gap: 2
                            }}
                          >
                            {rec.action === 'enable_audio' ? (
                              <Mic sx={{ color: '#F59E0B', mt: 0.3 }} />
                            ) : (
                              <Videocam sx={{ color: '#8B5CF6', mt: 0.3 }} />
                            )}
                            <Typography variant="body2" sx={{ color: '#E0E0E0' }}>
                              {rec.text}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  )}
                  
                  {/* Other Recommendations */}
                  {results.recommendations.filter(r => r.type !== 'mode').length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" sx={{ color: '#10B981', mb: 1, fontWeight: 600 }}>
                        Tips for Improvement
                      </Typography>
                      <List sx={{ py: 0 }}>
                        {results.recommendations.filter(r => r.type !== 'mode').map((rec, index) => {
                          let iconColor = '#10B981';
                          if (rec.priority === 'high') iconColor = '#EF4444';
                          else if (rec.priority === 'medium') iconColor = '#F59E0B';
                          
                          return (
                            <ListItem key={`tip-${index}`} sx={{ px: 0, py: 0.5 }}>
                              <ListItemIcon sx={{ minWidth: 32 }}>
                                <CheckCircle sx={{ color: iconColor, fontSize: 20 }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={rec.text || rec.title || rec}
                                primaryTypographyProps={{ sx: { color: '#E0E0E0', fontSize: '0.9rem' } }}
                              />
                            </ListItem>
                          );
                        })}
                      </List>
                    </Box>
                  )}
                </>
              ) : (
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#10B981', mb: 1, fontWeight: 600 }}>
                    Tips for Improvement
                  </Typography>
                  <List sx={{ py: 0 }}>
                    <ListItem sx={{ px: 0, py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}><CheckCircle sx={{ color: '#10B981', fontSize: 20 }} /></ListItemIcon>
                      <ListItemText primary="Practice more interviews to build confidence" primaryTypographyProps={{ sx: { color: '#E0E0E0', fontSize: '0.9rem' } }} />
                    </ListItem>
                    <ListItem sx={{ px: 0, py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}><CheckCircle sx={{ color: '#10B981', fontSize: 20 }} /></ListItemIcon>
                      <ListItemText primary="Review common interview questions in your field" primaryTypographyProps={{ sx: { color: '#E0E0E0', fontSize: '0.9rem' } }} />
                    </ListItem>
                    <ListItem sx={{ px: 0, py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}><CheckCircle sx={{ color: '#10B981', fontSize: 20 }} /></ListItemIcon>
                      <ListItemText primary="Work on structuring your answers using the STAR method" primaryTypographyProps={{ sx: { color: '#E0E0E0', fontSize: '0.9rem' } }} />
                    </ListItem>
                  </List>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Course Recommendations */}
          {results?.course_recommendations && results.course_recommendations.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#A855F7', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <School sx={{ color: '#A855F7' }} />
                  Recommended Learning Resources
                </Typography>
                <Typography variant="body2" sx={{ color: '#888888', mb: 3 }}>
                  Based on your performance, we recommend these courses to help you improve:
                </Typography>
                <Divider sx={{ mb: 3, borderColor: '#262626' }} />
                <Grid container spacing={2}>
                  {results.course_recommendations.map((rec, index) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Card 
                        sx={{ 
                          bgcolor: '#0B0B0B', 
                          border: '1px solid #262626',
                          height: '100%',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            borderColor: '#A855F7',
                            transform: 'translateY(-2px)',
                          }
                        }}
                      >
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Chip 
                              label={rec.topic}
                              size="small"
                              sx={{
                                bgcolor: rec.severity === 'high' ? 'rgba(239, 68, 68, 0.15)' : rec.severity === 'medium' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(14, 165, 233, 0.15)',
                                color: rec.severity === 'high' ? '#EF4444' : rec.severity === 'medium' ? '#F59E0B' : '#0EA5E9',
                                border: `1px solid ${rec.severity === 'high' ? 'rgba(239, 68, 68, 0.3)' : rec.severity === 'medium' ? 'rgba(245, 158, 11, 0.3)' : 'rgba(14, 165, 233, 0.3)'}`,
                                fontWeight: 600,
                              }}
                            />
                            <Chip 
                              label={rec.course?.level || 'All Levels'}
                              size="small"
                              sx={{
                                bgcolor: 'rgba(168, 85, 247, 0.15)',
                                color: '#A855F7',
                                border: '1px solid rgba(168, 85, 247, 0.3)',
                                fontSize: '0.7rem',
                              }}
                            />
                          </Box>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#FFFFFF', mt: 2, mb: 1 }}>
                            {rec.course?.title}
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#888888', mb: 2 }}>
                            Platform: <span style={{ color: '#E0E0E0' }}>{rec.course?.platform}</span>
                          </Typography>
                          <Button
                            variant="outlined"
                            size="small"
                            component="a"
                            endIcon={<OpenInNew sx={{ fontSize: '16px !important' }} />}
                            onClick={() => {
                              const url = rec.course?.url;
                              if (url) window.open(url, '_blank', 'noopener,noreferrer');
                            }}
                            sx={{
                              borderColor: '#A855F7',
                              color: '#A855F7',
                              textTransform: 'none',
                              cursor: 'pointer',
                              '&:hover': {
                                borderColor: '#9333EA',
                                bgcolor: 'rgba(168, 85, 247, 0.1)',
                              }
                            }}
                          >
                            Start Learning
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          )}

          {/* Questions Summary */}
          {results?.questions_summary && results.questions_summary.length > 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, bgcolor: '#1A1A1A', border: '1px solid #262626' }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <RecordVoiceOver sx={{ color: '#0EA5E9' }} />
                  Interview Questions &amp; Analysis
                </Typography>
                <Typography variant="body2" sx={{ color: '#888888', mb: 3 }}>
                  Here are all the questions asked during your interview along with your performance on each.
                </Typography>
                <Divider sx={{ mb: 3, borderColor: '#262626' }} />
                {results.questions_summary.map((q, index) => (
                  <Card key={index} sx={{ mb: 2, bgcolor: '#0B0B0B', border: '1px solid #262626' }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#FFFFFF', flex: 1, mr: 2 }}>
                          Q{index + 1}: {q.question}
                        </Typography>
                        <Chip 
                          label={q.user_answer ? `${q.score}%` : 'Skipped'} 
                          size="small"
                          sx={{
                            bgcolor: !q.user_answer ? 'rgba(156, 163, 175, 0.15)' : q.score >= 80 ? 'rgba(16, 185, 129, 0.15)' : q.score >= 60 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                            color: !q.user_answer ? '#9CA3AF' : q.score >= 80 ? '#10B981' : q.score >= 60 ? '#F59E0B' : '#EF4444',
                            border: `1px solid ${!q.user_answer ? 'rgba(156, 163, 175, 0.3)' : q.score >= 80 ? 'rgba(16, 185, 129, 0.3)' : q.score >= 60 ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                          }}
                        />
                      </Box>
                      {/* Question metadata tags */}
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1, mb: 2 }}>
                        {q.question_type && (
                          <Chip size="small" label={q.question_type.charAt(0).toUpperCase() + q.question_type.slice(1)} sx={{ bgcolor: 'rgba(14, 165, 233, 0.1)', color: '#0EA5E9', border: '1px solid rgba(14, 165, 233, 0.2)', fontSize: '0.7rem', height: 22 }} />
                        )}
                        {q.category && (
                          <Chip size="small" label={q.category} sx={{ bgcolor: 'rgba(168, 85, 247, 0.1)', color: '#A855F7', border: '1px solid rgba(168, 85, 247, 0.2)', fontSize: '0.7rem', height: 22 }} />
                        )}
                        {q.difficulty && (
                          <Chip size="small" label={q.difficulty.charAt(0).toUpperCase() + q.difficulty.slice(1)} sx={{ bgcolor: q.difficulty === 'hard' ? 'rgba(239, 68, 68, 0.1)' : q.difficulty === 'medium' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)', color: q.difficulty === 'hard' ? '#EF4444' : q.difficulty === 'medium' ? '#F59E0B' : '#10B981', border: `1px solid ${q.difficulty === 'hard' ? 'rgba(239, 68, 68, 0.2)' : q.difficulty === 'medium' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.2)'}`, fontSize: '0.7rem', height: 22 }} />
                        )}
                      </Box>
                      <Box sx={{ mt: 2 }}>
                        {q.feedback && q.feedback !== 'Not answered' && (
                          <Typography variant="body2" sx={{ color: '#888888', mb: 1 }}>
                            <strong style={{ color: '#E0E0E0' }}>Feedback:</strong> {q.feedback}
                          </Typography>
                        )}
                        {!q.user_answer && (
                          <Typography variant="body2" sx={{ color: '#9CA3AF', fontStyle: 'italic', mb: 1 }}>
                            This question was not answered.
                          </Typography>
                        )}
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
        <Box sx={{ mt: 5, display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
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
            variant="outlined"
            size="large"
            startIcon={exporting ? <CircularProgress size={20} sx={{ color: '#10B981' }} /> : <PictureAsPdf />}
            onClick={exportReport}
            disabled={exporting}
            sx={{ 
              borderColor: '#10B981', 
              color: '#10B981',
              '&:hover': { borderColor: '#059669', bgcolor: 'rgba(16, 185, 129, 0.08)' },
              '&:disabled': { borderColor: '#333333', color: '#666666' },
            }}
          >
            {exporting ? 'Exporting...' : 'Export PDF'}
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
