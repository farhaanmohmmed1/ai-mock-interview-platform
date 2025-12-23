# API Architecture Documentation

## Resume Upload and Skill Extraction Module

This document describes the complete API architecture for the Resume Upload and Skill Extraction functionality in the AI-Powered Adaptive Mock Interview Platform.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT (React.js)                                 │
│                           WebRTC | Axios/Fetch | TailwindCSS                        │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTPS/REST
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   API GATEWAY                                        │
│                            FastAPI + Uvicorn Server                                  │
│                         CORS | Auth Middleware | Rate Limiting                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              │                           │                           │
              ▼                           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   AUTH MODULE       │     │   RESUME MODULE     │     │   INTERVIEW MODULE  │
│   /api/auth/*       │     │   /api/resume/*     │     │   /api/interview/*  │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               AI PROCESSING LAYER                                    │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │ Resume Parser │  │   NLP Engine  │  │Speech Analyzer│  │Emotion Analyzer│        │
│  │  (spaCy/PDF)  │  │   (GPT/BERT)  │  │  (Whisper)    │  │  (FER/DeepFace)│        │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE (PostgreSQL/SQLite)                            │
│                     Users | Resumes | Interviews | Responses | Metrics              │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Resume Module API Endpoints

### Base URL: `/api/resume`

---

### 1. Upload Resume

**POST** `/api/resume/upload`

Upload and parse a resume file. Extracts skills, education, experience, and projects.

#### Request

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Body (FormData):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Resume file (PDF, DOCX, TXT) |

**Constraints:**
- Max file size: 10 MB
- Allowed extensions: `.pdf`, `.docx`, `.txt`

#### Response

**Success (201 Created):**
```json
{
  "message": "Resume uploaded and parsed successfully",
  "resume": {
    "id": 1,
    "filename": "john_doe_resume.pdf",
    "skills": [
      "python",
      "javascript",
      "react",
      "machine learning",
      "sql",
      "aws",
      "docker"
    ],
    "experience_years": 5.5,
    "education": {
      "degree": "Master of Science in Computer Science",
      "institution": "Stanford University",
      "graduation_year": 2019,
      "gpa": 3.9
    },
    "projects": [
      {
        "name": "AI Chatbot Platform",
        "description": "Built an NLP-powered customer service chatbot",
        "technologies": ["Python", "TensorFlow", "FastAPI"],
        "duration": "8 months"
      }
    ],
    "uploaded_at": "2025-12-23T10:30:00Z",
    "is_active": true
  }
}
```

**Error Responses:**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_FILE_TYPE` | File type not allowed |
| 400 | `FILE_TOO_LARGE` | File exceeds size limit |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 500 | `PARSE_ERROR` | Failed to parse resume |

---

### 2. List User Resumes

**GET** `/api/resume/list`

Retrieve all resumes uploaded by the authenticated user.

#### Request

**Headers:**
```http
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**
```json
[
  {
    "id": 1,
    "filename": "john_doe_resume_v2.pdf",
    "skills": ["python", "javascript", "react", "aws"],
    "experience_years": 5.5,
    "education": {...},
    "projects": [...],
    "uploaded_at": "2025-12-23T10:30:00Z",
    "is_active": true
  },
  {
    "id": 2,
    "filename": "john_doe_resume_v1.pdf",
    "skills": ["python", "django", "postgresql"],
    "experience_years": 4.0,
    "education": {...},
    "projects": [...],
    "uploaded_at": "2025-11-15T08:20:00Z",
    "is_active": false
  }
]
```

---

### 3. Get Specific Resume

**GET** `/api/resume/{resume_id}`

Retrieve detailed information about a specific resume.

#### Request

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `resume_id` | integer | Unique resume identifier |

#### Response

**Success (200 OK):**
```json
{
  "id": 1,
  "filename": "john_doe_resume.pdf",
  "skills": ["python", "javascript", "react", "machine learning"],
  "experience_years": 5.5,
  "education": {
    "degree": "Master of Science in Computer Science",
    "institution": "Stanford University",
    "graduation_year": 2019
  },
  "projects": [
    {
      "name": "AI Chatbot Platform",
      "description": "Built an NLP-powered chatbot",
      "technologies": ["Python", "TensorFlow"]
    }
  ],
  "uploaded_at": "2025-12-23T10:30:00Z",
  "is_active": true
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Resume not found"
}
```

---

### 4. Get Active Resume

**GET** `/api/resume/active/current`

Retrieve the currently active resume for the authenticated user.

#### Request

**Headers:**
```http
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**
```json
{
  "id": 1,
  "filename": "john_doe_resume.pdf",
  "skills": ["python", "javascript", "react"],
  "experience_years": 5.5,
  "education": {...},
  "projects": [...],
  "uploaded_at": "2025-12-23T10:30:00Z",
  "is_active": true
}
```

**Error (404 Not Found):**
```json
{
  "detail": "No active resume found. Please upload a resume first."
}
```

---

### 5. Delete Resume

**DELETE** `/api/resume/{resume_id}`

Delete a specific resume and its associated file.

#### Request

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `resume_id` | integer | Unique resume identifier |

#### Response

**Success (204 No Content):** Empty response

**Error (404 Not Found):**
```json
{
  "detail": "Resume not found"
}
```

---

### 6. Extract Skills (Standalone)

**POST** `/api/resume/extract-skills`

Extract skills from raw text without saving a resume.

#### Request

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "text": "Experienced software engineer with 5 years of Python, JavaScript, and React development. Proficient in AWS, Docker, and Kubernetes."
}
```

#### Response

**Success (200 OK):**
```json
{
  "skills": {
    "technical": [
      "python",
      "javascript",
      "react",
      "aws",
      "docker",
      "kubernetes"
    ],
    "soft": [],
    "tools": ["docker", "kubernetes"],
    "frameworks": ["react"],
    "languages": ["python", "javascript"],
    "cloud": ["aws"]
  },
  "experience_years": 5.0,
  "skill_categories": {
    "backend": ["python"],
    "frontend": ["javascript", "react"],
    "devops": ["docker", "kubernetes", "aws"]
  }
}
```

---

### 7. Analyze Resume for Interview

**POST** `/api/resume/analyze/{resume_id}`

Deep analysis of resume to prepare for interview question generation.

#### Request

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `resume_id` | integer | Unique resume identifier |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `interview_type` | string | `all` | Type: `general`, `technical`, `hr`, `all` |

#### Response

**Success (200 OK):**
```json
{
  "resume_id": 1,
  "analysis": {
    "primary_skills": ["python", "machine learning", "aws"],
    "skill_proficiency": {
      "python": "expert",
      "javascript": "intermediate",
      "machine learning": "advanced"
    },
    "experience_level": "mid-senior",
    "recommended_difficulty": "medium-hard",
    "focus_areas": {
      "technical": [
        "machine learning algorithms",
        "system design",
        "python optimization"
      ],
      "behavioral": [
        "leadership experience",
        "project management",
        "team collaboration"
      ],
      "hr": [
        "career goals",
        "work-life balance",
        "salary expectations"
      ]
    },
    "potential_questions_preview": {
      "technical": [
        "Explain how you would design a distributed ML pipeline",
        "What optimization techniques have you used in Python?"
      ],
      "behavioral": [
        "Tell me about a challenging project you led",
        "How do you handle disagreements with team members?"
      ],
      "hr": [
        "Where do you see yourself in 5 years?",
        "Why are you interested in this role?"
      ]
    },
    "gap_analysis": {
      "missing_common_skills": ["kubernetes", "graphql"],
      "improvement_areas": ["frontend depth", "database optimization"]
    }
  }
}
```

---

## Skill Extraction Module

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              SKILL EXTRACTION PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 │                                 │
        ▼                                 ▼                                 ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│  TEXT EXTRACTION  │        │  NLP PROCESSING   │        │  SKILL MATCHING   │
│                   │        │                   │        │                   │
│  • PDF Parser     │───────▶│  • Tokenization   │───────▶│  • Keyword Match  │
│  • DOCX Parser    │        │  • NER            │        │  • Fuzzy Match    │
│  • TXT Reader     │        │  • POS Tagging    │        │  • ML Classifier  │
└───────────────────┘        └───────────────────┘        └───────────────────┘
                                          │
                                          ▼
                             ┌───────────────────┐
                             │  CATEGORIZATION   │
                             │                   │
                             │  • Technical      │
                             │  • Languages      │
                             │  • Frameworks     │
                             │  • Tools          │
                             │  • Soft Skills    │
                             └───────────────────┘
```

### Processing Flow

1. **File Upload** → Validate file type and size
2. **Text Extraction** → Parse PDF/DOCX/TXT to raw text
3. **Preprocessing** → Clean text, normalize formatting
4. **NLP Analysis** → Named Entity Recognition, tokenization
5. **Skill Extraction** → Pattern matching + ML classification
6. **Categorization** → Group skills by type
7. **Storage** → Save to database with parsed data

---

## Data Models (Pydantic Schemas)

### Request Schemas

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SkillExtractionRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=50000,
                      description="Resume text content")

class ResumeAnalysisRequest(BaseModel):
    interview_type: str = Field(default="all", 
                                 pattern="^(general|technical|hr|all)$")
```

### Response Schemas

```python
class ResumeResponse(BaseModel):
    id: int
    filename: str
    skills: Optional[List[str]]
    experience_years: Optional[float]
    education: Optional[dict]
    projects: Optional[List[dict]]
    uploaded_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    message: str
    resume: ResumeResponse

class SkillExtractionResponse(BaseModel):
    skills: dict
    experience_years: Optional[float]
    skill_categories: dict

class ResumeAnalysisResponse(BaseModel):
    resume_id: int
    analysis: dict
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-12-23T10:30:00Z",
  "path": "/api/resume/upload"
}
```

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_FILE_TYPE` | Unsupported file format |
| 400 | `FILE_TOO_LARGE` | File exceeds 10MB limit |
| 400 | `EMPTY_FILE` | Uploaded file is empty |
| 400 | `INVALID_REQUEST` | Malformed request body |
| 401 | `UNAUTHORIZED` | Missing or invalid auth token |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resume not found |
| 409 | `CONFLICT` | Resource conflict |
| 422 | `VALIDATION_ERROR` | Request validation failed |
| 500 | `PARSE_ERROR` | Resume parsing failed |
| 500 | `INTERNAL_ERROR` | Server error |

---

## Authentication

All resume endpoints require JWT authentication.

### Token Structure

```json
{
  "sub": "user@example.com",
  "user_id": 1,
  "exp": 1735019400,
  "iat": 1735017600
}
```

### Authentication Flow

```
1. Client sends login request → /api/auth/login
2. Server validates credentials, returns JWT
3. Client includes JWT in Authorization header
4. Server validates JWT on each request
5. Refresh token when needed → /api/auth/refresh
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/resume/upload` | 10 requests | 1 hour |
| `/api/resume/*` (other) | 100 requests | 1 minute |
| `/api/resume/extract-skills` | 30 requests | 1 hour |

---

## File Storage Structure

```
data/
├── uploads/
│   ├── user_1/
│   │   ├── 20251223_103000_resume.pdf
│   │   └── 20251120_154500_resume.docx
│   ├── user_2/
│   │   └── 20251222_091500_cv.pdf
│   └── ...
├── recordings/
├── videos/
└── models/
```

---

## Integration with Interview Module

### Flow After Resume Upload

```
1. Resume uploaded and parsed → skills extracted
2. User initiates interview session
3. Interview module fetches active resume
4. Question generator uses skills for:
   - Technical question relevance
   - Difficulty calibration
   - Topic selection
5. Adaptive system tracks performance per skill
6. Feedback references resume skills
```

### Sample Integration Call

```python
# Interview service calling resume data
async def prepare_interview(user_id: int, interview_type: str):
    # Get active resume
    resume = await get_active_resume(user_id)
    
    # Extract skills for question generation
    skills = resume.skills
    experience = resume.experience_years
    
    # Generate tailored questions
    questions = await question_generator.generate(
        skills=skills,
        experience_level=experience,
        interview_type=interview_type
    )
    
    return questions
```

---

## Example Usage (cURL)

### Upload Resume

```bash
curl -X POST "http://localhost:8000/api/resume/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/resume.pdf"
```

### List Resumes

```bash
curl -X GET "http://localhost:8000/api/resume/list" \
  -H "Authorization: Bearer <token>"
```

### Get Active Resume

```bash
curl -X GET "http://localhost:8000/api/resume/active/current" \
  -H "Authorization: Bearer <token>"
```

### Delete Resume

```bash
curl -X DELETE "http://localhost:8000/api/resume/1" \
  -H "Authorization: Bearer <token>"
```

---

## Frontend Integration (React)

```javascript
// Resume upload component
const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('/api/resume/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      },
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Upload failed');
    }
    
    const data = await response.json();
    return data.resume;
  } catch (error) {
    console.error('Resume upload error:', error);
    throw error;
  }
};

// Fetch extracted skills
const getResumeSkills = async () => {
  const response = await fetch('/api/resume/active/current', {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  });
  
  const resume = await response.json();
  return resume.skills;
};
```

---

## Testing

### Unit Test Example

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_upload_resume_success(auth_headers, sample_pdf):
    response = client.post(
        "/api/resume/upload",
        headers=auth_headers,
        files={"file": ("resume.pdf", sample_pdf, "application/pdf")}
    )
    
    assert response.status_code == 201
    assert "resume" in response.json()
    assert "skills" in response.json()["resume"]

def test_upload_invalid_file_type(auth_headers):
    response = client.post(
        "/api/resume/upload",
        headers=auth_headers,
        files={"file": ("resume.exe", b"invalid", "application/exe")}
    )
    
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]
```

---

## Performance Considerations

- **PDF parsing**: ~1-3 seconds for typical resumes
- **Skill extraction**: ~0.5-1 second
- **Database operations**: ~50-100ms
- **Total upload flow**: ~2-5 seconds

### Optimization Strategies

1. **Async processing**: Use background tasks for heavy parsing
2. **Caching**: Cache skill taxonomy and patterns
3. **Batch processing**: Support bulk resume uploads
4. **CDN**: Serve static assets via CDN

---

## Security Measures

1. **File validation**: Check MIME type, not just extension
2. **Virus scanning**: Integrate with antivirus API
3. **Path traversal prevention**: Sanitize filenames
4. **Size limits**: Enforce server-side limits
5. **Rate limiting**: Prevent abuse
6. **Audit logging**: Track all file operations
