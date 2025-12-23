# Database Schema Documentation

## AI-Powered Adaptive Mock Interview Platform

This document describes the complete database schema for the interview platform, including entity relationships and field specifications.

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USERS                                             │
│  (Primary user account with authentication and profile data)                         │
└─────────────────────────────────────────────────────────────────────────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐    ┌────────────────────┐    ┌──────────────────────────────────┐
│     RESUMES      │    │  PERFORMANCE       │    │    ADAPTIVE_PROFILES             │
│  (Uploaded       │    │  METRICS           │    │  (Personalized learning          │
│   resume files)  │    │  (Overall stats)   │    │   characteristics)               │
└──────────────────┘    └────────────────────┘    └──────────────────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  INTERVIEWS                                          │
│  (Individual interview sessions: General, Technical, HR)                             │
└─────────────────────────────────────────────────────────────────────────────────────┘
         │
         │ 1:N                                    1:N
         ▼                                         ▼
┌──────────────────────────────┐    ┌──────────────────────────────────────────────────┐
│         QUESTIONS            │    │                  RESPONSES                        │
│  (Interview questions)       │───▶│  (User answers with analysis)                    │
└──────────────────────────────┘    └──────────────────────────────────────────────────┘
```

---

## Table Definitions

### 1. USERS Table

Stores user account information and authentication data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User email address |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Username for login |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `full_name` | VARCHAR(255) | NULLABLE | User's full name |
| `phone` | VARCHAR(20) | NULLABLE | Contact phone number |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active status |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Email verification status |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `idx_users_email` on `email`
- `idx_users_username` on `username`

**Relationships:**
- `1:N` → Resumes
- `1:N` → Interviews
- `1:N` → PerformanceMetrics
- `1:1` → AdaptiveProfile

---

### 2. RESUMES Table

Stores uploaded resume files and extracted information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique resume identifier |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Reference to user |
| `filename` | VARCHAR(255) | NOT NULL | Original file name |
| `file_path` | VARCHAR(500) | NOT NULL | Server storage path |
| `parsed_data` | JSON | NULLABLE | Full parsed resume data |
| `skills` | JSON | NULLABLE | Extracted skills array |
| `experience_years` | FLOAT | NULLABLE | Years of experience |
| `education` | JSON | NULLABLE | Education details |
| `projects` | JSON | NULLABLE | Project information |
| `uploaded_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Upload timestamp |
| `is_active` | BOOLEAN | DEFAULT TRUE | Currently active resume |

**Indexes:**
- `idx_resumes_user_id` on `user_id`
- `idx_resumes_is_active` on `is_active`

**JSON Schema - skills:**
```json
["python", "javascript", "react", "machine learning", "sql"]
```

**JSON Schema - education:**
```json
{
  "degree": "Bachelor of Science in Computer Science",
  "institution": "MIT",
  "graduation_year": 2022,
  "gpa": 3.8
}
```

**JSON Schema - projects:**
```json
[
  {
    "name": "E-commerce Platform",
    "description": "Built a full-stack web application",
    "technologies": ["React", "Node.js", "MongoDB"],
    "duration": "6 months"
  }
]
```

---

### 3. INTERVIEWS Table

Stores interview session data and overall scores.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique interview identifier |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Reference to user |
| `resume_id` | INTEGER | FOREIGN KEY (resumes.id), NULLABLE | Reference to resume used |
| `interview_type` | VARCHAR(50) | NOT NULL | Type: `general`, `technical`, `hr` |
| `status` | VARCHAR(50) | DEFAULT 'pending' | Status: `pending`, `in_progress`, `completed`, `cancelled` |
| `difficulty_level` | VARCHAR(20) | DEFAULT 'medium' | Difficulty: `easy`, `medium`, `hard` |
| `total_questions` | INTEGER | DEFAULT 0 | Total questions in session |
| `answered_questions` | INTEGER | DEFAULT 0 | Questions answered |
| `scheduled_at` | TIMESTAMP | NULLABLE | Scheduled time |
| `started_at` | TIMESTAMP | NULLABLE | Actual start time |
| `completed_at` | TIMESTAMP | NULLABLE | Completion time |
| `duration_minutes` | FLOAT | NULLABLE | Total duration in minutes |
| `overall_score` | FLOAT | NULLABLE | Composite score (0-100) |
| `content_score` | FLOAT | NULLABLE | Content quality score |
| `clarity_score` | FLOAT | NULLABLE | Communication clarity score |
| `fluency_score` | FLOAT | NULLABLE | Speech fluency score |
| `confidence_score` | FLOAT | NULLABLE | Confidence level score |
| `emotion_score` | FLOAT | NULLABLE | Emotional readiness score |
| `weak_areas` | JSON | NULLABLE | Areas needing improvement |
| `strong_areas` | JSON | NULLABLE | Strengths identified |
| `feedback` | TEXT | NULLABLE | Overall feedback text |
| `recommendations` | JSON | NULLABLE | Learning recommendations |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- `idx_interviews_user_id` on `user_id`
- `idx_interviews_status` on `status`
- `idx_interviews_type` on `interview_type`

**JSON Schema - weak_areas/strong_areas:**
```json
["data structures", "system design", "behavioral questions"]
```

**JSON Schema - recommendations:**
```json
[
  {
    "area": "Data Structures",
    "priority": "high",
    "resources": [
      {"type": "course", "title": "LeetCode Practice", "url": "https://leetcode.com"},
      {"type": "book", "title": "Cracking the Coding Interview"}
    ]
  }
]
```

---

### 4. QUESTIONS Table

Stores individual interview questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique question identifier |
| `interview_id` | INTEGER | FOREIGN KEY (interviews.id), NOT NULL | Reference to interview |
| `question_text` | TEXT | NOT NULL | The question content |
| `question_type` | VARCHAR(50) | NULLABLE | Type: `behavioral`, `technical`, `situational`, `hr` |
| `category` | VARCHAR(100) | NULLABLE | Category: `programming`, `database`, `algorithms`, etc. |
| `difficulty` | VARCHAR(20) | NULLABLE | Difficulty level |
| `expected_keywords` | JSON | NULLABLE | Keywords expected in answer |
| `order_number` | INTEGER | NULLABLE | Question sequence number |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |

**JSON Schema - expected_keywords:**
```json
{
  "required": ["recursion", "base case", "stack"],
  "bonus": ["tail recursion", "memoization"],
  "weights": {"recursion": 0.3, "base case": 0.2, "stack": 0.2}
}
```

---

### 5. RESPONSES Table

Stores user responses with multimodal analysis.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique response identifier |
| `interview_id` | INTEGER | FOREIGN KEY (interviews.id), NOT NULL | Reference to interview |
| `question_id` | INTEGER | FOREIGN KEY (questions.id), NOT NULL | Reference to question |
| `text_response` | TEXT | NULLABLE | Transcribed text response |
| `audio_path` | VARCHAR(500) | NULLABLE | Path to audio recording |
| `video_path` | VARCHAR(500) | NULLABLE | Path to video recording |
| `content_score` | FLOAT | NULLABLE | Content accuracy score (0-100) |
| `relevance_score` | FLOAT | NULLABLE | Answer relevance score (0-100) |
| `clarity_score` | FLOAT | NULLABLE | Communication clarity (0-100) |
| `fluency_score` | FLOAT | NULLABLE | Speech fluency (0-100) |
| `confidence_score` | FLOAT | NULLABLE | Confidence level (0-100) |
| `speech_analysis` | JSON | NULLABLE | Speech quality metrics |
| `emotion_analysis` | JSON | NULLABLE | Emotion detection results |
| `nlp_analysis` | JSON | NULLABLE | NLP analysis results |
| `response_time_seconds` | FLOAT | NULLABLE | Time taken to respond |
| `thinking_time_seconds` | FLOAT | NULLABLE | Pause before speaking |
| `feedback` | TEXT | NULLABLE | Specific feedback for response |
| `improvement_suggestions` | JSON | NULLABLE | Suggestions for improvement |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |

**JSON Schema - speech_analysis:**
```json
{
  "words_per_minute": 145,
  "filler_words_count": 3,
  "filler_words": ["um", "uh", "like"],
  "pause_frequency": 0.15,
  "avg_pause_duration": 1.2,
  "volume_consistency": 0.85,
  "pitch_variation": 0.42
}
```

**JSON Schema - emotion_analysis:**
```json
{
  "dominant_emotion": "confident",
  "emotion_timeline": [
    {"timestamp": 0, "emotions": {"confident": 0.7, "nervous": 0.2, "neutral": 0.1}},
    {"timestamp": 5, "emotions": {"confident": 0.8, "nervous": 0.1, "neutral": 0.1}}
  ],
  "stress_level": 0.25,
  "engagement_score": 0.85
}
```

**JSON Schema - nlp_analysis:**
```json
{
  "keyword_match_score": 0.75,
  "matched_keywords": ["recursion", "base case"],
  "missed_keywords": ["stack"],
  "sentiment": "positive",
  "coherence_score": 0.82,
  "complexity_level": "intermediate",
  "technical_accuracy": 0.88
}
```

---

### 6. PERFORMANCE_METRICS Table

Tracks user performance over time for adaptive learning.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique metric identifier |
| `user_id` | INTEGER | FOREIGN KEY (users.id), NOT NULL | Reference to user |
| `total_interviews` | INTEGER | DEFAULT 0 | Total interviews completed |
| `average_score` | FLOAT | NULLABLE | Overall average score |
| `improvement_rate` | FLOAT | NULLABLE | Improvement percentage |
| `general_avg_score` | FLOAT | NULLABLE | General round average |
| `technical_avg_score` | FLOAT | NULLABLE | Technical round average |
| `hr_avg_score` | FLOAT | NULLABLE | HR round average |
| `communication_score` | FLOAT | NULLABLE | Communication skills score |
| `technical_knowledge_score` | FLOAT | NULLABLE | Technical knowledge score |
| `problem_solving_score` | FLOAT | NULLABLE | Problem-solving score |
| `confidence_score` | FLOAT | NULLABLE | Overall confidence score |
| `skill_gaps` | JSON | NULLABLE | Identified skill gaps |
| `learning_path` | JSON | NULLABLE | Recommended learning path |
| `next_focus_areas` | JSON | NULLABLE | Next areas to focus on |
| `last_updated` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

---

### 7. ADAPTIVE_PROFILES Table

Stores personalized learning profiles for adaptive questioning.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique profile identifier |
| `user_id` | INTEGER | FOREIGN KEY (users.id), UNIQUE, NOT NULL | Reference to user |
| `learning_pace` | VARCHAR(20) | DEFAULT 'medium' | Learning speed: `slow`, `medium`, `fast` |
| `preferred_difficulty` | VARCHAR(20) | DEFAULT 'medium' | Preferred difficulty |
| `strong_topics` | JSON | NULLABLE | Topics of strength |
| `weak_topics` | JSON | NULLABLE | Topics needing work |
| `avg_response_time` | FLOAT | NULLABLE | Average response time |
| `consistency_score` | FLOAT | NULLABLE | Performance consistency |
| `stress_indicators` | JSON | NULLABLE | Stress pattern data |
| `question_difficulty_multiplier` | FLOAT | DEFAULT 1.0 | Difficulty adjustment factor |
| `focus_areas` | JSON | NULLABLE | Current focus areas |
| `recommended_practice` | JSON | NULLABLE | Practice recommendations |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Profile creation time |
| `updated_at` | TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP | Last update time |

---

## SQL Creation Scripts

### PostgreSQL Schema

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Resumes Table
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    parsed_data JSONB,
    skills JSONB,
    experience_years FLOAT,
    education JSONB,
    projects JSONB,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_is_active ON resumes(is_active);

-- Interviews Table
CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_id INTEGER REFERENCES resumes(id),
    interview_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    difficulty_level VARCHAR(20) DEFAULT 'medium',
    total_questions INTEGER DEFAULT 0,
    answered_questions INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_minutes FLOAT,
    overall_score FLOAT,
    content_score FLOAT,
    clarity_score FLOAT,
    fluency_score FLOAT,
    confidence_score FLOAT,
    emotion_score FLOAT,
    weak_areas JSONB,
    strong_areas JSONB,
    feedback TEXT,
    recommendations JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_interviews_user_id ON interviews(user_id);
CREATE INDEX idx_interviews_status ON interviews(status);
CREATE INDEX idx_interviews_type ON interviews(interview_type);

-- Questions Table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50),
    category VARCHAR(100),
    difficulty VARCHAR(20),
    expected_keywords JSONB,
    order_number INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_questions_interview_id ON questions(interview_id);

-- Responses Table
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    text_response TEXT,
    audio_path VARCHAR(500),
    video_path VARCHAR(500),
    content_score FLOAT,
    relevance_score FLOAT,
    clarity_score FLOAT,
    fluency_score FLOAT,
    confidence_score FLOAT,
    speech_analysis JSONB,
    emotion_analysis JSONB,
    nlp_analysis JSONB,
    response_time_seconds FLOAT,
    thinking_time_seconds FLOAT,
    feedback TEXT,
    improvement_suggestions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_responses_interview_id ON responses(interview_id);
CREATE INDEX idx_responses_question_id ON responses(question_id);

-- Performance Metrics Table
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_interviews INTEGER DEFAULT 0,
    average_score FLOAT,
    improvement_rate FLOAT,
    general_avg_score FLOAT,
    technical_avg_score FLOAT,
    hr_avg_score FLOAT,
    communication_score FLOAT,
    technical_knowledge_score FLOAT,
    problem_solving_score FLOAT,
    confidence_score FLOAT,
    skill_gaps JSONB,
    learning_path JSONB,
    next_focus_areas JSONB,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_performance_metrics_user_id ON performance_metrics(user_id);

-- Adaptive Profiles Table
CREATE TABLE adaptive_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    learning_pace VARCHAR(20) DEFAULT 'medium',
    preferred_difficulty VARCHAR(20) DEFAULT 'medium',
    strong_topics JSONB,
    weak_topics JSONB,
    avg_response_time FLOAT,
    consistency_score FLOAT,
    stress_indicators JSONB,
    question_difficulty_multiplier FLOAT DEFAULT 1.0,
    focus_areas JSONB,
    recommended_practice JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_adaptive_profiles_user_id ON adaptive_profiles(user_id);
```

---

## Data Flow Summary

1. **User Registration** → Creates entry in `users` table
2. **Resume Upload** → Saves file, parses content, creates `resumes` entry with extracted skills
3. **Interview Start** → Creates `interviews` entry, generates `questions` based on resume skills
4. **Question Response** → Records in `responses` with multimodal analysis (speech, emotion, NLP)
5. **Interview Complete** → Updates `interviews` with scores, updates `performance_metrics`
6. **Adaptive Learning** → Updates `adaptive_profiles` based on performance patterns

---

## Notes

- All timestamps use timezone-aware datetime
- JSON fields use JSONB in PostgreSQL for better indexing and query performance
- Cascade deletes ensure data integrity when users are removed
- Indexes optimize common query patterns (user lookup, status filtering)
