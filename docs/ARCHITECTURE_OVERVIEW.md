# AI-Powered Adaptive Mock Interview Platform

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND (React.js + Tailwind CSS)                            │
│                                                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│   │    Login     │  │   Resume     │  │  Interview   │  │   Results    │  │  Dashboard   │      │
│   │   Register   │  │   Upload     │  │   Session    │  │   Report     │  │  Analytics   │      │
│   └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘      │
│                           │                  │                                    │              │
│                           │         ┌────────┴────────┐                          │              │
│                           │         │   WebRTC        │                          │              │
│                           │         │  Audio/Video    │                          │              │
│                           │         └────────┬────────┘                          │              │
└───────────────────────────┼──────────────────┼───────────────────────────────────┼──────────────┘
                            │                  │                                    │
                            │ REST API         │ WebSocket                          │ REST API
                            ▼                  ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BACKEND (FastAPI + Python)                                    │
│                                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                    API GATEWAY                                           │   │
│   │                     CORS | JWT Authentication | Rate Limiting                            │   │
│   └─────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                               │                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│   │ /api/auth   │  │ /api/resume │  │/api/interview│ │/api/evaluate│  │/api/dashboard│          │
│   │             │  │             │  │             │  │             │  │             │          │
│   │ • Register  │  │ • Upload    │  │ • Start     │  │ • Score     │  │ • Progress  │          │
│   │ • Login     │  │ • Parse     │  │ • Question  │  │ • Feedback  │  │ • Analytics │          │
│   │ • Refresh   │  │ • Analyze   │  │ • Response  │  │ • Report    │  │ • History   │          │
│   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                               │                                                  │
└───────────────────────────────────────────────┼──────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    AI PROCESSING LAYER                                           │
│                                                                                                  │
│   ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐                     │
│   │   NLP MODULE        │  │   SPEECH MODULE     │  │   EMOTION MODULE    │                     │
│   │                     │  │                     │  │                     │                     │
│   │ • Resume Parser     │  │ • Speech-to-Text    │  │ • Facial Analysis   │                     │
│   │ • Skill Extractor   │  │ • Clarity Analysis  │  │ • Emotion Detection │                     │
│   │ • Question Gen      │  │ • Fluency Scoring   │  │ • Confidence Meter  │                     │
│   │ • Answer Evaluator  │  │ • Filler Detection  │  │ • Stress Indicators │                     │
│   └─────────────────────┘  └─────────────────────┘  └─────────────────────┘                     │
│                                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                ADAPTIVE LEARNING SYSTEM                                  │   │
│   │                                                                                          │   │
│   │  • Performance Tracking    • Difficulty Adjustment    • Personalized Recommendations    │   │
│   │  • Skill Gap Analysis      • Learning Path Generation • Resource Suggestions            │   │
│   └─────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                  │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA LAYER                                                    │
│                                                                                                  │
│   ┌─────────────────────────────────────────┐  ┌─────────────────────────────────────────┐      │
│   │          PostgreSQL/SQLite              │  │           File Storage                   │      │
│   │                                         │  │                                         │      │
│   │  • Users         • Questions            │  │  • Resumes (PDF/DOCX)                   │      │
│   │  • Resumes       • Responses            │  │  • Audio Recordings                     │      │
│   │  • Interviews    • Performance          │  │  • Video Recordings                     │      │
│   │  • Adaptive      • Metrics              │  │  • AI Model Weights                     │      │
│   └─────────────────────────────────────────┘  └─────────────────────────────────────────┘      │
│                                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Interview Flow Sequence

```
┌─────────┐          ┌─────────┐          ┌─────────┐          ┌─────────┐          ┌─────────┐
│  User   │          │Frontend │          │ Backend │          │   AI    │          │Database │
└────┬────┘          └────┬────┘          └────┬────┘          └────┬────┘          └────┬────┘
     │                    │                    │                    │                    │
     │  1. Register/Login │                    │                    │                    │
     │───────────────────▶│                    │                    │                    │
     │                    │  POST /auth/login  │                    │                    │
     │                    │───────────────────▶│                    │                    │
     │                    │                    │  Validate & Token  │                    │
     │                    │                    │───────────────────▶│                    │
     │                    │◀───────────────────│                    │                    │
     │  JWT Token         │                    │                    │                    │
     │◀───────────────────│                    │                    │                    │
     │                    │                    │                    │                    │
     │  2. Upload Resume  │                    │                    │                    │
     │───────────────────▶│                    │                    │                    │
     │                    │ POST /resume/upload│                    │                    │
     │                    │───────────────────▶│                    │                    │
     │                    │                    │  Parse Resume      │                    │
     │                    │                    │───────────────────▶│                    │
     │                    │                    │  Extracted Skills  │                    │
     │                    │                    │◀───────────────────│                    │
     │                    │                    │                    │  Store Resume      │
     │                    │                    │───────────────────────────────────────▶│
     │                    │◀───────────────────│                    │                    │
     │  Skills & Analysis │                    │                    │                    │
     │◀───────────────────│                    │                    │                    │
     │                    │                    │                    │                    │
     │  3. Start Interview│                    │                    │                    │
     │───────────────────▶│                    │                    │                    │
     │                    │POST /interview/start                    │                    │
     │                    │───────────────────▶│                    │                    │
     │                    │                    │  Generate Questions│                    │
     │                    │                    │───────────────────▶│                    │
     │                    │                    │◀───────────────────│                    │
     │                    │                    │                    │  Create Session    │
     │                    │                    │───────────────────────────────────────▶│
     │                    │◀───────────────────│                    │                    │
     │  First Question    │                    │                    │                    │
     │◀───────────────────│                    │                    │                    │
     │                    │                    │                    │                    │
     │  4. Answer (WebRTC)│                    │                    │                    │
     │───────────────────▶│                    │                    │                    │
     │                    │ POST /interview/respond                 │                    │
     │                    │───────────────────▶│                    │                    │
     │                    │                    │  Multimodal Analysis                    │
     │                    │                    │───────────────────▶│                    │
     │                    │                    │  • Speech-to-Text  │                    │
     │                    │                    │  • NLP Evaluation  │                    │
     │                    │                    │  • Emotion Analysis│                    │
     │                    │                    │◀───────────────────│                    │
     │                    │                    │                    │  Store Response    │
     │                    │                    │───────────────────────────────────────▶│
     │                    │◀───────────────────│                    │                    │
     │  Next Question     │                    │                    │                    │
     │◀───────────────────│                    │                    │                    │
     │                    │                    │                    │                    │
     │  ... (Repeat for all questions)        │                    │                    │
     │                    │                    │                    │                    │
     │  5. Complete       │                    │                    │                    │
     │───────────────────▶│                    │                    │                    │
     │                    │POST /interview/complete                 │                    │
     │                    │───────────────────▶│                    │                    │
     │                    │                    │  Generate Report   │                    │
     │                    │                    │───────────────────▶│                    │
     │                    │                    │◀───────────────────│                    │
     │                    │                    │                    │  Update Metrics    │
     │                    │                    │───────────────────────────────────────▶│
     │                    │◀───────────────────│                    │                    │
     │  Detailed Report   │                    │                    │                    │
     │◀───────────────────│                    │                    │                    │
     │                    │                    │                    │                    │
```

## Three-Round Interview Structure

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    INTERVIEW ROUNDS                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ROUND 1: GENERAL INTERVIEW                                                    Duration: 15 min │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  Questions: 5                                                                                    │
│                                                                                                  │
│  Focus Areas:                                                                                    │
│  ├── Self-Introduction                                                                           │
│  ├── Career Background                                                                           │
│  ├── Motivation & Goals                                                                          │
│  └── General Problem-Solving                                                                     │
│                                                                                                  │
│  Evaluation Criteria:                                                                            │
│  ├── Communication Clarity ────────────────────────── 30%                                        │
│  ├── Confidence Level ─────────────────────────────── 25%                                        │
│  ├── Response Coherence ───────────────────────────── 25%                                        │
│  └── Professional Presentation ────────────────────── 20%                                        │
│                                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ROUND 2: TECHNICAL INTERVIEW                                                  Duration: 30 min │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  Questions: 8 (Adaptive based on resume skills)                                                  │
│                                                                                                  │
│  Focus Areas (Dynamic based on resume):                                                          │
│  ├── Core Programming Concepts                                                                   │
│  ├── Data Structures & Algorithms                                                                │
│  ├── System Design (if senior)                                                                   │
│  ├── Technology-Specific (Python, React, etc.)                                                   │
│  └── Problem-Solving Approach                                                                    │
│                                                                                                  │
│  Evaluation Criteria:                                                                            │
│  ├── Technical Accuracy ───────────────────────────── 35%                                        │
│  ├── Problem-Solving Approach ─────────────────────── 25%                                        │
│  ├── Concept Understanding ────────────────────────── 20%                                        │
│  ├── Code Quality (if applicable) ─────────────────── 10%                                        │
│  └── Communication ────────────────────────────────── 10%                                        │
│                                                                                                  │
│  Adaptive Features:                                                                              │
│  ├── Difficulty adjusts based on performance                                                     │
│  ├── Follow-up questions on weak areas                                                           │
│  └── Skip basic if demonstrating expertise                                                       │
│                                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ROUND 3: HR INTERVIEW                                                         Duration: 15 min │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  Questions: 5                                                                                    │
│                                                                                                  │
│  Focus Areas:                                                                                    │
│  ├── Cultural Fit                                                                                │
│  ├── Teamwork & Collaboration                                                                    │
│  ├── Conflict Resolution                                                                         │
│  ├── Career Aspirations                                                                          │
│  └── Work-Life Balance                                                                           │
│                                                                                                  │
│  Evaluation Criteria:                                                                            │
│  ├── Emotional Intelligence ───────────────────────── 30%                                        │
│  ├── Cultural Alignment ───────────────────────────── 25%                                        │
│  ├── Communication Skills ─────────────────────────── 25%                                        │
│  └── Self-Awareness ───────────────────────────────── 20%                                        │
│                                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Multimodal Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               REAL-TIME MULTIMODAL ANALYSIS                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

    User Response (Audio + Video)
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CAPTURE LAYER (WebRTC)                                        │
│                                                                                                  │
│   Audio Stream ────────────────────────────────┬─────────────────────────── Video Stream        │
│        │                                       │                                  │              │
│        ▼                                       │                                  ▼              │
│  ┌───────────────┐                             │                         ┌───────────────┐      │
│  │ Audio Buffer  │                             │                         │ Video Frames  │      │
│  │   16kHz       │                             │                         │   30 FPS      │      │
│  └───────┬───────┘                             │                         └───────┬───────┘      │
│          │                                     │                                 │              │
└──────────┼─────────────────────────────────────┼─────────────────────────────────┼──────────────┘
           │                                     │                                 │
           ▼                                     │                                 ▼
┌─────────────────────┐                          │                   ┌─────────────────────┐
│   SPEECH ANALYSIS   │                          │                   │   EMOTION ANALYSIS  │
│                     │                          │                   │                     │
│ ┌─────────────────┐ │                          │                   │ ┌─────────────────┐ │
│ │ Speech-to-Text  │ │                          │                   │ │ Face Detection  │ │
│ │  (Whisper)      │ │                          │                   │ │                 │ │
│ └────────┬────────┘ │                          │                   │ └────────┬────────┘ │
│          ▼          │                          │                   │          ▼          │
│ ┌─────────────────┐ │                          │                   │ ┌─────────────────┐ │
│ │ Fluency Score   │ │                          │                   │ │ Emotion Detect  │ │
│ │ • WPM           │ │                          │                   │ │ • Happy         │ │
│ │ • Pauses        │ │                          │                   │ │ • Nervous       │ │
│ │ • Filler words  │ │                          │                   │ │ • Confident     │ │
│ └────────┬────────┘ │                          │                   │ │ • Stressed      │ │
│          ▼          │                          │                   │ └────────┬────────┘ │
│ ┌─────────────────┐ │                          │                   │          ▼          │
│ │ Clarity Score   │ │                          │                   │ ┌─────────────────┐ │
│ │ • Pronunciation │ │                          │                   │ │ Confidence      │ │
│ │ • Volume        │ │                          │                   │ │ Timeline        │ │
│ │ • Pitch         │ │                          │                   │ │                 │ │
│ └─────────────────┘ │                          │                   │ └─────────────────┘ │
└─────────┬───────────┘                          │                   └──────────┬──────────┘
          │                                      │                              │
          │    ┌─────────────────────────────────┴─────────────────────────┐    │
          │    │                                                           │    │
          ▼    ▼                                                           ▼    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    NLP ANALYSIS ENGINE                                           │
│                                                                                                  │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│   │ Keyword Match   │    │ Sentiment       │    │ Coherence       │    │ Technical       │      │
│   │                 │    │ Analysis        │    │ Analysis        │    │ Accuracy        │      │
│   │ • Required kw   │    │ • Positive      │    │ • Logical flow  │    │ • Concept match │      │
│   │ • Bonus kw      │    │ • Negative      │    │ • Structure     │    │ • Correctness   │      │
│   │ • Missed kw     │    │ • Neutral       │    │ • Completeness  │    │ • Depth         │      │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│                                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    SCORING AGGREGATION                                           │
│                                                                                                  │
│   Overall Score = (Content × 0.30) + (Clarity × 0.20) + (Confidence × 0.20) +                   │
│                   (Technical × 0.20) + (Emotion × 0.10)                                          │
│                                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │                                Final Response Object                                     │   │
│   │                                                                                          │   │
│   │  {                                                                                       │   │
│   │    "content_score": 85.5,                                                                │   │
│   │    "clarity_score": 78.2,                                                                │   │
│   │    "confidence_score": 82.0,                                                             │   │
│   │    "technical_score": 88.0,                                                              │   │
│   │    "emotion_score": 75.0,                                                                │   │
│   │    "overall_score": 82.8,                                                                │   │
│   │    "feedback": "Strong technical explanation with good confidence...",                   │   │
│   │    "improvement_suggestions": ["Reduce filler words", "Elaborate on examples"]           │   │
│   │  }                                                                                       │   │
│   └─────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Adaptive Learning System

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ADAPTIVE LEARNING ENGINE                                      │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │   User Performance  │
                              │       Data          │
                              └──────────┬──────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              ▼                          ▼                          ▼
    ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
    │   Skill Gap     │        │   Progress      │        │   Behavioral    │
    │   Analysis      │        │   Tracking      │        │   Patterns      │
    │                 │        │                 │        │                 │
    │ • Weak areas    │        │ • Score trends  │        │ • Response time │
    │ • Strong areas  │        │ • Improvement   │        │ • Stress level  │
    │ • Missing skills│        │ • Consistency   │        │ • Confidence    │
    └────────┬────────┘        └────────┬────────┘        └────────┬────────┘
             │                          │                          │
             └──────────────────────────┼──────────────────────────┘
                                        │
                                        ▼
              ┌─────────────────────────────────────────────────────┐
              │              ADAPTIVE PROFILE UPDATE                 │
              │                                                      │
              │   ┌───────────────────────────────────────────┐     │
              │   │  {                                         │     │
              │   │    "learning_pace": "medium",              │     │
              │   │    "preferred_difficulty": "medium-hard",  │     │
              │   │    "question_difficulty_multiplier": 1.2,  │     │
              │   │    "focus_areas": ["system design", "SQL"],│     │
              │   │    "strong_topics": ["python", "react"],   │     │
              │   │    "weak_topics": ["database", "devops"]   │     │
              │   │  }                                         │     │
              │   └───────────────────────────────────────────┘     │
              └─────────────────────────────────────────────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
              ▼                         ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
    │   Difficulty    │       │   Question      │       │   Resource      │
    │   Adjustment    │       │   Selection     │       │   Suggestions   │
    │                 │       │                 │       │                 │
    │ Easy ◄──► Hard  │       │ Personalized    │       │ • Courses       │
    │  Based on       │       │ question bank   │       │ • Practice      │
    │  performance    │       │ targeting gaps  │       │ • Articles      │
    └─────────────────┘       └─────────────────┘       └─────────────────┘
                                        │
                                        ▼
              ┌─────────────────────────────────────────────────────┐
              │                  NEXT INTERVIEW                      │
              │                                                      │
              │   • Adjusted difficulty level                        │
              │   • Focus on weak areas                              │
              │   • Reinforce strong areas                           │
              │   • Personalized question flow                       │
              │   • Targeted feedback                                │
              └─────────────────────────────────────────────────────┘
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React.js | UI Components |
| | Tailwind CSS | Styling |
| | WebRTC | Audio/Video Capture |
| | Axios | API Communication |
| **Backend** | FastAPI | REST API Framework |
| | SQLAlchemy | ORM |
| | Pydantic | Data Validation |
| | JWT | Authentication |
| **Database** | PostgreSQL/SQLite | Data Persistence |
| **AI/ML** | spaCy | NLP Processing |
| | OpenAI GPT | Question Generation |
| | Whisper | Speech-to-Text |
| | FER/DeepFace | Emotion Analysis |
| **Storage** | Local/S3 | File Storage |

## Quick Links

- [Database Schema](DATABASE_SCHEMA.md) - Complete database structure
- [API Architecture](API_ARCHITECTURE.md) - Resume Upload API documentation
- [API Documentation](../API_DOCUMENTATION.md) - Full API reference
- [Quickstart Guide](../QUICKSTART.md) - Getting started
