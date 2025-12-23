# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register User

**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "is_active": true
  }
}
```

### Login

**POST** `/api/auth/login`

Login to get access token.

**Request Body:**
```json
{
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username"
  }
}
```

### Get Current User

**GET** `/api/auth/me`

Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe"
}
```

---

## Resume Endpoints

### Upload Resume

**POST** `/api/resume/upload`

Upload and parse a resume file.

**Headers:** `Authorization: Bearer <token>`

**Form Data:**
- `file`: Resume file (PDF, DOCX, or TXT)

**Response:**
```json
{
  "message": "Resume uploaded and parsed successfully",
  "resume": {
    "id": 1,
    "filename": "resume.pdf",
    "skills": ["Python", "JavaScript", "React"],
    "experience_years": 3.5,
    "education": {...},
    "uploaded_at": "2024-01-01T00:00:00"
  }
}
```

### List Resumes

**GET** `/api/resume/list`

Get all user resumes.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "filename": "resume.pdf",
    "skills": ["Python", "JavaScript"],
    "uploaded_at": "2024-01-01T00:00:00"
  }
]
```

---

## Interview Endpoints

### Create Interview

**POST** `/api/interview/create`

Start a new interview session.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "interview_type": "technical",
  "resume_id": 1,
  "difficulty_level": "medium"
}
```

**Response:**
```json
{
  "interview_id": 1,
  "questions": [
    {
      "id": 1,
      "question_text": "Explain polymorphism in OOP",
      "question_type": "technical",
      "difficulty": "medium"
    }
  ],
  "message": "Interview started successfully"
}
```

### List Interviews

**GET** `/api/interview/list?skip=0&limit=20`

Get user's interview history.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "interview_type": "technical",
    "status": "completed",
    "overall_score": 75.5,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Get Interview Details

**GET** `/api/interview/{interview_id}`

Get detailed interview information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "interview_type": "technical",
  "status": "completed",
  "overall_score": 75.5,
  "content_score": 80.0,
  "clarity_score": 72.0,
  "questions": [...],
  "weak_areas": [...],
  "recommendations": [...]
}
```

### Complete Interview

**POST** `/api/interview/{interview_id}/complete`

Complete interview and generate final report.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  "overall_score": 75.5,
  "content_score": 80.0,
  "clarity_score": 72.0,
  "completed_at": "2024-01-01T00:00:00"
}
```

---

## Evaluation Endpoints

### Submit Text Response

**POST** `/api/evaluation/submit-text`

Submit text-only response to a question.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "question_id": 1,
  "text_response": "Polymorphism allows objects...",
  "thinking_time_seconds": 5.0
}
```

**Response:**
```json
{
  "response_id": 1,
  "message": "Response submitted successfully",
  "scores": {
    "content_score": 85.0,
    "relevance_score": 90.0
  }
}
```

### Submit Audio Response

**POST** `/api/evaluation/submit-audio/{question_id}`

Submit audio response with analysis.

**Headers:** `Authorization: Bearer <token>`

**Form Data:**
- `audio_file`: Audio file (WAV format)
- `thinking_time`: Thinking time in seconds

**Response:**
```json
{
  "response_id": 1,
  "message": "Audio response analyzed successfully",
  "scores": {
    "content_score": 85.0,
    "clarity_score": 78.0,
    "fluency_score": 82.0
  }
}
```

### Submit Video Response

**POST** `/api/evaluation/submit-video/{question_id}`

Submit video response with emotion analysis.

**Headers:** `Authorization: Bearer <token>`

**Form Data:**
- `video_file`: Video file (WebM format)
- `audio_file`: Audio file (WAV format)
- `thinking_time`: Thinking time in seconds

**Response:**
```json
{
  "response_id": 1,
  "message": "Video response analyzed successfully",
  "scores": {
    "content_score": 85.0,
    "clarity_score": 78.0,
    "fluency_score": 82.0,
    "confidence_score": 75.0
  }
}
```

---

## Dashboard Endpoints

### Get Dashboard Stats

**GET** `/api/dashboard/stats`

Get comprehensive dashboard statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "stats": {
    "total_interviews": 10,
    "average_score": 75.5,
    "improvement_rate": 12.3
  },
  "performance_history": [...],
  "skill_analysis": [...],
  "weak_areas": [...],
  "recommendations": [...]
}
```

### Get Performance Metrics

**GET** `/api/dashboard/performance-metrics`

Get detailed performance metrics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "total_interviews": 10,
  "average_score": 75.5,
  "communication_score": 80.0,
  "technical_knowledge_score": 78.0,
  "skill_gaps": [...],
  "learning_path": [...]
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid input data"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

(To be implemented in production)

## Pagination

List endpoints support pagination:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 20)

Example: `/api/interview/list?skip=10&limit=5`
