<p align="center">
  <h1 align="center">AI-Powered Adaptive Mock Interview Platform</h1>
  <p align="center">
    <strong>Intelligent interview preparation powered by NLP, Speech Analysis, and Emotion Recognition</strong>
  </p>
  <p align="center">
    <a href="https://ai-mock-interview-platform-t8ph.vercel.app/">Live Demo</a> •
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#documentation">Documentation</a>
  </p>
</p>

---

## Overview

A comprehensive AI-powered mock interview platform that conducts adaptive interviews using cutting-edge technologies. The platform supports multiple interview types including **Technical**, **Behavioral**, **HR**, and **UPSC Civil Services** interviews with intelligent question generation, real-time speech analysis, and emotion-based confidence assessment.

### Key Highlights

| Feature | Technology | Capability |
|---------|------------|------------|
| **Speech Recognition** | OpenAI Whisper (small) | 90% accuracy transcription |
| **Emotion Analysis** | FER + MTCNN | 7-emotion facial detection |
| **Question Banks** | Curated Datasets | 350+ interview questions |
| **AI Agent** | LangGraph + GPT-4 | Adaptive conversation flow |
| **Answer Evaluation** | NLP + LLMs | Multi-dimensional scoring |

---

## Features

### Interview Types

| Type | Description | Question Bank |
|------|-------------|---------------|
| **Technical** | Coding, system design, algorithms | 60 questions |
| **Behavioral** | STAR method, leadership, teamwork | 35 questions |
| **HR** | Salary, career goals, culture fit | 25 questions |
| **General** | Comprehensive mix | 30 questions |
| **UPSC** | Indian Civil Services preparation | 200 questions (11 categories) |

### Company-Specific Preparation

- **Google** - Technical & behavioral focus
- **Amazon** - Leadership principles emphasis
- **Microsoft** - Problem-solving oriented
- **Meta** - System design & culture fit
- **Apple** - Innovation & user experience
- **Netflix** - Culture & autonomy
- **Goldman Sachs** - Analytical & case-based

### Core Capabilities

#### Speech Analysis
- **Real-time transcription** using OpenAI Whisper (small model, 90% accuracy)
- **Words-per-minute** calculation for pacing feedback
- **Filler word detection** ("um", "uh", "like", etc.)
- **Clarity and fluency scoring**

#### Emotion Recognition
- **7-emotion classification**: happy, sad, angry, surprised, fearful, disgusted, neutral
- **Confidence level assessment** via facial analysis
- **MTCNN face detection** for accurate tracking
- **Emotion timeline** throughout interview

#### Intelligent Evaluation
- **Relevance scoring** (0-100)
- **Technical depth analysis**
- **STAR method evaluation** for behavioral questions
- **Persona-based grading** (strict/balanced/lenient)
- **Contextual follow-up questions**

#### Adaptive Learning
- **Performance-based difficulty adjustment**
- **Weak area identification**
- **Personalized improvement recommendations**
- **Progress tracking over time**

---

## Architecture

```
ai-mock-interview-platform/
├── backend/                    # FastAPI Server
│   ├── api/                   # REST API Endpoints
│   │   ├── auth.py           # Authentication (JWT)
│   │   ├── interview.py      # Interview management
│   │   ├── evaluation.py     # Answer evaluation
│   │   ├── resume.py         # Resume processing
│   │   └── dashboard.py      # Analytics & history
│   ├── core/                  # Configuration
│   └── models.py             # SQLAlchemy models
│
├── ai_modules/                 # AI Processing Layer
│   ├── nlp/                   # Natural Language Processing
│   │   ├── question_generator.py
│   │   ├── answer_evaluator.py
│   │   ├── resume_parser.py
│   │   ├── company_questions_loader.py
│   │   └── upsc_questions_loader.py
│   ├── speech/                # Speech Analysis
│   │   └── speech_analyzer.py  # Whisper integration
│   ├── emotion/               # Emotion Detection
│   │   └── emotion_analyzer.py # FER + MTCNN
│   ├── agent/                 # LangGraph Agent
│   │   ├── interview_agent.py
│   │   ├── agent_state.py
│   │   └── tools.py
│   └── adaptive/              # Adaptive Learning
│       ├── adaptive_system.py
│       └── report_generator.py
│
├── data/                       # Data Storage
│   ├── company_questions.json  # 150 company questions
│   ├── upsc_questions.json    # 200 UPSC questions
│   ├── uploads/               # User resumes
│   └── recordings/            # Audio/video files
│
├── frontend/                   # React Application
│   └── src/
│       ├── pages/
│       │   ├── Interview.jsx
│       │   ├── InterviewSetup.jsx
│       │   ├── Dashboard.jsx
│       │   └── Results.jsx
│       └── components/
│
└── docs/                       # Documentation
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- FFmpeg (for audio processing)

### Installation

**Windows:**
```cmd
setupforwindows.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh && ./setup.sh
```

### Manual Setup

1. **Clone and setup virtual environment:**
```bash
git clone https://github.com/farhaanmohmmed1/ai-mock-interview-platform.git
cd ai-mock-interview-platform
python -m venv .venv
```

2. **Activate virtual environment:**

| OS | Command |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| Linux/macOS | `source .venv/bin/activate` |

3. **Install dependencies:**
```bash
pip install -r requirements-full.txt
python -m spacy download en_core_web_sm
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

5. **Initialize database:**
```bash
python backend/init_db.py
```

6. **Start backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

7. **Start frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Question Banks

### Company Questions (150 total)

| Category | Count | Examples |
|----------|-------|----------|
| Behavioral | 35 | Leadership, conflict resolution, teamwork |
| Technical | 60 | System design, algorithms, coding |
| HR | 25 | Salary, career goals, availability |
| General | 30 | Strengths, weaknesses, motivation |

### UPSC Questions (200 total)

| Category | Count | Topics |
|----------|-------|--------|
| Current Affairs | 20 | National & international events |
| Indian Polity | 20 | Constitution, governance |
| Ethics & Integrity | 20 | Moral dilemmas, public service |
| Economy | 18 | Fiscal policy, development |
| Environment | 18 | Climate, sustainability |
| Science & Technology | 18 | Innovation, digital governance |
| International Relations | 16 | Diplomacy, foreign policy |
| Social Issues | 20 | Education, healthcare, poverty |
| Personality | 20 | Self-assessment, aspirations |
| Opinion-Based | 15 | Critical thinking, analysis |
| Administrative | 15 | Governance, public policy |

---

## AI Models

### Speech Recognition

| Model | Size | Accuracy | Speed | Status |
|-------|------|----------|-------|--------|
| tiny | 75MB | 72% | 32x realtime | Available |
| **small** | 466MB | **90%** | 6x realtime | **Active** |
| medium | 1.5GB | 95% | 2x realtime | Available |
| large | 2.9GB | 97% | 1x realtime | Available |

### Emotion Detection

Using **FER (Facial Expression Recognition)** with **MTCNN** backend:
- Real-time face detection
- 7-class emotion classification
- Confidence scoring per frame
- Timeline aggregation

---

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User authentication |
| POST | `/api/resume/upload` | Upload resume (PDF) |
| POST | `/api/interview/start` | Start new interview |
| POST | `/api/interview/{id}/answer` | Submit answer |
| POST | `/api/interview/{id}/end` | End interview |
| GET | `/api/interview/{id}/report` | Get interview report |
| GET | `/api/dashboard/interviews` | Interview history |
| GET | `/api/dashboard/stats` | Performance analytics |

### Interview Types

```json
{
  "interview_type": "technical | behavioral | hr | upsc",
  "job_role": "Software Engineer",
  "company": "google | amazon | meta | microsoft | general",
  "difficulty": "easy | medium | hard",
  "num_questions": 5
}
```

---

## Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# Optional
DATABASE_URL=sqlite:///./data/interview.db
JWT_SECRET_KEY=your-secret-key
WHISPER_MODEL=small
USE_GPU=false
```

---

## Testing

### Quick Verification
```bash
python -c "
from ai_modules.nlp.company_questions_loader import get_company_questions_loader
from ai_modules.nlp.upsc_questions_loader import get_upsc_questions_loader
from ai_modules.speech.speech_analyzer import SpeechAnalyzer
from ai_modules.emotion.emotion_analyzer import EmotionAnalyzer

print('Company questions:', get_company_questions_loader().total_questions)
print('UPSC questions:', get_upsc_questions_loader().total_questions)
print('Whisper model:', SpeechAnalyzer().whisper_model_name)
print('FER active:', EmotionAnalyzer().emotion_detector is not None)
"
```

Expected output:
```
Company questions: 150
UPSC questions: 200
Whisper model: small
FER active: True
```

### Run Test Suite
```bash
pytest tests/ -v
```

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | FastAPI, SQLAlchemy, Pydantic |
| **AI/ML** | LangChain, LangGraph, OpenAI GPT-4 |
| **Speech** | OpenAI Whisper, SpeechRecognition |
| **Vision** | OpenCV, FER, MTCNN, TensorFlow |
| **NLP** | spaCy, NLTK, Transformers |
| **Frontend** | React, Vite, Tailwind CSS |
| **Database** | SQLite/PostgreSQL |
| **Auth** | JWT, bcrypt |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md) | System design and data flow |
| [API Documentation](API_DOCUMENTATION.md) | Complete API reference |
| [Database Schema](docs/DATABASE_SCHEMA.md) | Database structure |
| [How It Works](docs/HOW_IT_WORKS.md) | Technical implementation details |
| [Beginner Guide](docs/BEGINNER_GUIDE.md) | Getting started tutorial |
| [Verification Prompts](docs/AI_AGENT_VERIFICATION_PROMPT.md) | AI agent testing guide |

---

## Roadmap

- [x] Multi-company question banks
- [x] UPSC interview support
- [x] Whisper model upgrade (small)
- [x] FER emotion detection
- [x] LangGraph interview agent
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Video interview recording
- [ ] AI interviewer avatar
- [ ] Integration with job platforms

