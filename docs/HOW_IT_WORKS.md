# How the AI Mock Interview Platform Works

> A conceptual guide explaining the methods, algorithms, and intelligent processes that power this platform — without diving into specific technologies or libraries.

---

## Table of Contents

1. [Overview](#overview)
2. [Interview Agent Architecture](#interview-agent-architecture)
3. [Resume Intelligence](#resume-intelligence)
4. [Question Generation Engine](#question-generation-engine)
5. [Answer Evaluation System](#answer-evaluation-system)
6. [Speech Analysis Pipeline](#speech-analysis-pipeline)
7. [Emotion & Confidence Detection](#emotion--confidence-detection)
8. [Weak Area Identification](#weak-area-identification)
9. [Personalized Suggestion System](#personalized-suggestion-system)
10. [Anti-Cheat & Proctoring System](#anti-cheat--proctoring-system)
11. [Adaptive Learning System](#adaptive-learning-system)
12. [Report Generation](#report-generation)
13. [Agent Integration & APIs](#agent-integration--apis)

---

## Overview

The AI Mock Interview Platform is designed to simulate realistic interview experiences while providing intelligent feedback. **At the heart of the system is an AI Interview Agent** that orchestrates the entire interview process, making intelligent decisions at each stage.

### Agent-Centric Architecture

Unlike traditional rule-based systems, this platform uses an **AI Agent** that:
- **Observes**: Gathers context from user profiles, resumes, and past performance
- **Thinks**: Analyzes patterns, identifies weaknesses, and plans responses
- **Acts**: Generates questions, evaluates answers, and provides personalized feedback

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
│                                                                      │
│   Resume Upload → Interview Session → Audio/Video Response           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      🤖 INTERVIEW AGENT                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Agent State & Context                       │  │
│  │  • User History  • Current Session  • Running Metrics          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                               │                                      │
│              ┌────────────────┼────────────────┐                     │
│              ▼                ▼                ▼                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐        │
│  │    OBSERVE      │ │     THINK       │ │      ACT        │        │
│  │  • Evaluations  │ │  • Analyze      │ │  • Generate Qs  │        │
│  │  • User Input   │ │  • Identify     │ │  • Provide Tips │        │
│  │  • Performance  │ │  • Decide       │ │  • Adjust Flow  │        │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘        │
│                               │                                      │
│              ┌────────────────┴────────────────┐                     │
│              ▼                                 ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                     AGENT TOOLS                              │    │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐    │    │
│  │  │ Question  │ │  Answer   │ │  Weak     │ │Suggestion │    │    │
│  │  │ Generator │ │ Evaluator │ │ Identifier│ │ Generator │    │    │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────┘    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PERSONALIZED OUTPUT                              │
│                                                                      │
│   Scores → Feedback → Weak Areas → Suggestions → Learning Path       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Interview Agent Architecture

The Interview Agent is the central intelligence that coordinates all interview activities. It operates through distinct phases and maintains context throughout the session.

### Agent Phases

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│INITIALIZATION│───►│  QUESTION    │───►│   ANSWER     │
│              │    │ GENERATION   │    │ COLLECTION   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                    ┌──────────────────────────┘
                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ANALYSIS   │◄───│  EVALUATION  │◄───│   (repeat    │
│              │    │              │    │  per answer) │
└──────┬───────┘    └──────────────┘    └──────────────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐
│  SUGGESTION  │───►│   REPORT     │───► COMPLETED
│  GENERATION  │    │  GENERATION  │
└──────────────┘    └──────────────┘
```

### Phase Details

| Phase | Agent Actions | Tools Used |
|-------|--------------|------------|
| **Initialization** | Load user profile, fetch past performance, determine difficulty | Adaptive System |
| **Question Generation** | Create personalized questions based on context | Question Generator |
| **Answer Collection** | Present questions, capture responses | - |
| **Evaluation** | Score content, relevance, speech quality | Answer Evaluator, Speech Analyzer |
| **Analysis** | Identify weak/strong areas, patterns | Weak Area Identifier |
| **Suggestion Generation** | Create actionable improvement recommendations | Suggestion Generator |
| **Report Generation** | Compile comprehensive performance report | Report Generator |

### Agent State Management

The agent maintains rich context throughout the interview:

```
Interview Context
├── User Profile
│   ├── Resume Data
│   ├── Skills
│   └── Experience Level
│
├── Historical Data
│   ├── Past Weak Areas
│   ├── Past Strong Areas
│   └── Improvement Trends
│
├── Current Session
│   ├── Questions Asked
│   ├── Answers Received
│   ├── Running Scores
│   └── Emerging Patterns
│
└── Agent Memory
    ├── Observations
    └── Decisions Made
```

### Agent Decision Making

The agent makes intelligent decisions at each step:

**Question Selection Decision:**
```
IF user has known weak areas THEN
    Prioritize questions from weak areas
ELSE IF resume shows specific skills THEN
    Generate skill-relevant questions
ELSE
    Use balanced question distribution
END IF
```

**Difficulty Adjustment Decision:**
```
AFTER 3 answers:
    IF average_score >= 85% AND difficulty != "hard" THEN
        Increase difficulty
    ELSE IF average_score <= 45% AND difficulty != "easy" THEN
        Decrease difficulty
    END IF
```

---

## Resume Intelligence

### How Resume Parsing Works

The resume parsing system extracts structured information from unstructured documents through a multi-stage process:

#### 1. Document Text Extraction

**PDF Documents:**
- The system reads the document page by page
- **Position clustering** is applied to understand layout (columns, headers, sections)
- Text elements are grouped based on their spatial proximity
- Reading order is determined by analyzing vertical and horizontal positioning

**Word Documents:**
- Paragraphs are extracted while preserving structural formatting
- Tables and lists are converted to processable text blocks

#### 2. Section Identification

The system identifies resume sections using:

- **Header Pattern Recognition**: Looks for common section headers like "Experience", "Education", "Skills", "Projects"
- **Structural Cues**: Blank lines, font changes, and indentation patterns signal section boundaries
- **Contextual Analysis**: Content patterns help classify ambiguous sections

```
Resume Document
      │
      ▼
┌─────────────────────────────────────────┐
│        Section Boundary Detection        │
│                                         │
│  "EXPERIENCE" ───────► Work Section     │
│  "EDUCATION"  ───────► Education Section│
│  "SKILLS"     ───────► Skills Section   │
└─────────────────────────────────────────┘
```

#### 3. Entity Extraction

**Skills Extraction:**
- **Keyword Matching**: Compares resume text against a curated skills vocabulary
- **Context Window Analysis**: Checks surrounding words to confirm skill relevance
- **Skill Categorization**: Groups skills into technical, soft skills, tools, etc.

**Experience Calculation:**
- **Date Pattern Recognition**: Identifies date ranges in formats like "2019-2023" or "Jan 2020 - Present"
- **Duration Computation**: Calculates total years by summing all employment periods
- **Overlap Detection**: Handles concurrent positions without double-counting

**Education Parsing:**
- **Degree Recognition**: Matches educational qualifications (Bachelor's, Master's, PhD)
- **Institution Identification**: Extracts university/college names using named entity recognition
- **Field of Study Extraction**: Identifies academic majors and specializations

**Contact Information:**
- **Email Pattern Matching**: Recognizes email formats using structural patterns
- **Phone Normalization**: Extracts phone numbers in various formats
- **LinkedIn/Portfolio Detection**: Identifies professional profile URLs

#### 4. Named Entity Recognition (NER)

The system uses linguistic analysis to identify:
- **Organization Names**: Companies, universities, institutions
- **Location Names**: Cities, countries
- **Person Names**: For contact information
- **Technical Terms**: Programming languages, frameworks, methodologies

---

## Question Generation Engine

### How Questions Are Generated

The question generation system creates contextually relevant interview questions through intelligent selection and customization.

#### 1. Question Bank Architecture

Questions are organized by **type** and **difficulty**:

| Category | What It Covers | Difficulty Levels |
|----------|----------------|-------------------|
| **General/Behavioral** | "Tell me about yourself", strengths, teamwork stories | Easy → Medium → Hard |
| **Technical** | Coding, algorithms, system design, databases | Easy → Medium → Hard |
| **HR/Cultural** | Motivation, salary, career goals, work-life balance | Easy → Medium → Hard |
| **Domain-Specific** | Industry questions (e.g., UPSC: ethics, current affairs) | Easy → Medium → Hard |

**How difficulty works:**

```
EASY          →        MEDIUM           →         HARD
"What is X?"      "Explain how X works"     "Design X for scale"
Simple recall     Apply knowledge           Complex scenarios
```

#### 2. Context-Aware Selection

**Resume-Based Personalization:**
- Questions are weighted based on skills found in the resume
- If a resume mentions "Python", Python-related questions get priority
- Project descriptions trigger follow-up scenario questions

**Difficulty Calibration:**
- Initial questions start at medium difficulty
- System adapts based on user's previous performance
- Gradual progression from foundational to advanced topics

#### 3. Question Metadata

Each question carries metadata for intelligent processing:

```
Question Object
├── Question Text
├── Question Type (behavioral/technical/situational)
├── Difficulty Level (easy/medium/hard)
├── Expected Keywords (for evaluation)
├── Category/Topic
└── Follow-up Question Links
```

#### 4. Dynamic Follow-up Generation

The system generates contextual follow-ups based on:
- Previous answer content
- Detected weak points in response
- Unexplored aspects of the topic

---

## Answer Evaluation System

### How Answers Are Analyzed and Scored

The answer evaluation employs multiple analytical techniques to assess response quality.

#### 1. Text Preprocessing

Before analysis, answers undergo:
- **Tokenization**: Breaking text into words and sentences
- **Normalization**: Converting to lowercase, handling contractions
- **Stopword Filtering**: Removing common words that don't carry meaning ("the", "is", "and")

#### 2. Content Quality Assessment

**Length and Depth Analysis:**
```
Scoring Criteria:
├── Word Count
│   └── <20 words: Insufficient depth
│   └── 20-50 words: Developing response
│   └── 50-100 words: Good detail
│   └── >100 words: Comprehensive (if relevant)
│
├── Sentence Structure
│   └── Multiple sentences indicate structured thinking
│   └── Varied sentence length shows sophistication
│
└── Specificity Indicators
    └── Examples ("for instance", "such as")
    └── Numbers and metrics
    └── Named references
```

**Vocabulary Complexity:**
- Average word length analysis
- Technical terminology detection
- Professional language usage

#### 3. Relevance Scoring

**Question-Answer Alignment:**
- Extracts key terms from the question
- Measures overlap with answer content
- Identifies if core question elements are addressed

**Expected Keyword Coverage:**
- Each question has expected concepts
- System checks if these concepts appear in the answer
- Missing keywords are flagged for feedback

```
Question: "What are decorators in Python?"
Expected Keywords: ["function", "wrapper", "decorator", "@"]

Answer Analysis:
├── Keywords Found: ["function", "decorator"]
├── Keywords Missing: ["wrapper", "@"]
└── Coverage Score: 50%
```

#### 4. Coherence Analysis

**Logical Flow Detection:**
- Checks for transition words ("however", "therefore", "furthermore")
- Analyzes sentence connectivity
- Measures structural consistency

**Structure Scoring:**
- Introduction-Body-Conclusion pattern detection
- Paragraph organization
- Idea progression logic

#### 5. Sentiment Analysis

The system classifies answer tone:
- **Positive Indicators**: "achieved", "successful", "improved", "effective"
- **Negative Indicators**: "failed", "struggled", "difficult", "problem"
- **Neutral**: Balanced or factual responses

This helps identify:
- Confidence level in responses
- Potential negativity that might concern interviewers
- Appropriate professional tone

---

## Speech Analysis Pipeline

### How Voice Is Analyzed

The speech analysis system processes audio recordings to evaluate verbal communication skills.

#### 1. Speech-to-Text Conversion

**Audio Processing Flow:**
```
Audio Recording
      │
      ▼
┌─────────────────┐
│ Noise Reduction │  ← Ambient noise filtering
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Speech Detection│  ← Identify speech vs silence
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Transcription  │  ← Convert speech to text
└────────┬────────┘
         │
         ▼
    Text Output
```

#### 2. Clarity Score Calculation

**Audio Quality Metrics:**
- **Signal-to-Noise Ratio**: Measures audio clarity
- **Volume Consistency**: Detects if speaker maintains steady volume
- **Zero-Crossing Rate**: Identifies noise interference patterns

**Articulation Assessment:**
- Clear pronunciation leads to better transcription confidence
- Mumbled or unclear speech shows lower recognition certainty

#### 3. Fluency Analysis

**Speaking Rate Measurement:**
```
Words Per Minute (WPM) Calculation:
├── Optimal Range: 120-150 WPM
├── Too Slow (<100 WPM): May indicate hesitation
├── Too Fast (>180 WPM): May indicate nervousness
└── Score adjusted based on deviation from optimal
```

**Pause Detection:**
- **Silence Threshold**: Identifies gaps in speech
- **Short Pauses (<0.5s)**: Natural breathing, good
- **Medium Pauses (0.5-2s)**: Thinking time, acceptable
- **Long Pauses (>2s)**: May indicate uncertainty

**Filler Word Detection:**
Common fillers identified:
- Verbal pauses: "um", "uh", "er"
- Hedge words: "like", "you know", "basically"
- Repetitions: "so so", "and and"

```
Fluency Score Formula:
Base Score: 100
- (Filler Words × 2)
- (Long Pauses × 5)
- (Speaking Rate Deviation × 0.5)
= Final Fluency Score
```

#### 4. Volume and Energy Analysis

**Amplitude Tracking:**
- RMS (Root Mean Square) energy computed over time
- Consistent energy indicates confident delivery
- Large variations may suggest nervousness or disengagement

---

## Emotion & Confidence Detection

### How Facial Expressions Are Analyzed

The emotion detection system processes video to assess non-verbal communication.

#### 1. Face Detection

**Detection Process:**
- Scans video frames at regular intervals (e.g., every 2 seconds)
- Identifies human faces using facial landmark detection
- Tracks face visibility throughout the interview

#### 2. Facial Landmark Analysis

Key points analyzed on the face:
```
        Facial Landmarks
             │
    ┌────────┼────────┐
    │        │        │
 Eyebrows  Eyes    Mouth
    │        │        │
    ▼        ▼        ▼
 Concern   Focus   Emotion
  Level   Level   Expression
```

**Expression Classification:**
- **Happy/Confident**: Raised cheeks, slight smile
- **Neutral**: Relaxed facial muscles
- **Anxious/Nervous**: Furrowed brows, tense features
- **Confused**: Asymmetric expressions, raised eyebrows

#### 3. Emotion Timeline Construction

The system builds a timeline of emotional states:

```
Time:   0s────30s────60s────90s────120s
        │      │      │      │       │
State: [N]───[N]───[C]───[N]───[C]
        │      │      │      │       │
       Neutral    Confident      Confident

Legend: N=Neutral, C=Confident, A=Anxious
```

#### 4. Confidence Score Calculation

**Aggregation Method:**
- Dominant emotion weighted by duration
- Positive emotions (confidence, engagement) boost score
- Negative emotions (anxiety, confusion) reduce score
- Face visibility percentage affects reliability

**Emotional Stability Metric:**
- Low variance in emotions = High stability
- Frequent emotion changes = Lower stability score
- Sustained confidence = Higher overall score

---

## Weak Area Identification

### How the Agent Identifies Areas Needing Improvement

The Interview Agent continuously monitors performance to identify patterns and weak areas. This is a core capability that enables personalized coaching.

#### 1. Real-Time Pattern Recognition

**During the Interview:**
```
Answer Submitted
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│              AGENT EVALUATION PIPELINE                   │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Content   │  │  Category   │  │   Running   │      │
│  │   Scoring   │─►│   Mapping   │─►│  Aggregation│      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                           │              │
│                                           ▼              │
│                          ┌─────────────────────────┐    │
│                          │  Weak Area Detection    │    │
│                          │  (Score < Threshold)    │    │
│                          └─────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Category-Based Analysis:**
The agent groups questions by category and tracks scores:

| Category | Questions | Avg Score | Status |
|----------|-----------|-----------|--------|
| Technical - Python | 3 | 82% | ✅ Strong |
| Behavioral - Leadership | 2 | 58% | ⚠️ Weak |
| System Design | 2 | 45% | 🔴 Critical |

#### 2. Weakness Classification

**Severity Levels:**
```
Score Range          Severity         Priority
─────────────────────────────────────────────────
< 50%               CRITICAL         Immediate Focus
50% - 65%           WEAK             High Priority
65% - 75%           DEVELOPING       Medium Priority
≥ 75%               ADEQUATE         Maintenance
```

#### 3. Gap Analysis

**Keyword Gap Detection:**
- Tracks expected keywords vs. found keywords
- Identifies concepts the user consistently misses
- Maps gaps to specific knowledge areas

```
Example Gap Analysis:
├── Question: "Explain microservices architecture"
│   ├── Expected: [scalability, decoupling, API, containers, services]
│   ├── Found: [services, API]
│   └── Missing: [scalability, decoupling, containers]
│
└── Identified Gap: Container/orchestration knowledge
```

#### 4. Historical Pattern Integration

**Cross-Session Analysis:**
```
Session 1: Technical score 55%  →  Flagged as weak
Session 2: Technical score 58%  →  Still weak, minimal improvement
Session 3: Technical score 62%  →  Improving but still below target

Agent Decision: "Technical" remains a focus area
               Recommend intensive practice
```

#### 5. Skill Gap Mapping

The agent maps weak areas to specific skills:

```
Weak Area Detected          Mapped Skills
────────────────────────────────────────────────────
"System Design"      →      Architecture, Scalability
"Behavioral"         →      Communication, STAR Method
"Problem Solving"    →      Analytical Thinking
"Technical Coding"   →      Algorithms, Data Structures
```

---

## Personalized Suggestion System

### How the Agent Creates Tailored Recommendations

The suggestion system is one of the agent's most valuable capabilities, transforming analysis into actionable improvement plans.

#### 1. Suggestion Categories

**The Agent Generates Four Types of Suggestions:**

```
┌─────────────────────────────────────────────────────────────┐
│                 SUGGESTION GENERATION                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   AREA       │  │   PATTERN    │  │  LEVERAGE    │       │
│  │  SPECIFIC    │  │    BASED     │  │  STRENGTH    │       │
│  │              │  │              │  │              │       │
│  │ "Improve X"  │  │ "You tend    │  │ "Use your    │       │
│  │              │  │  to..."      │  │  strength    │       │
│  │              │  │              │  │  in Y"       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│                    ┌──────────────┐                         │
│                    │   LEARNING   │                         │
│                    │     PATH     │                         │
│                    │              │                         │
│                    │ "Follow this │                         │
│                    │  roadmap"    │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

#### 2. Area-Specific Suggestions

**Generated Based on Weak Areas:**

For **Technical Weaknesses:**
```json
{
  "type": "improvement",
  "area": "System Design",
  "priority": "high",
  "title": "Strengthen System Design Skills",
  "description": "Your system design answers lack depth.",
  "action_items": [
    "Study common architecture patterns",
    "Practice explaining trade-offs",
    "Learn about scalability concepts"
  ],
  "resources": [
    "System Design Primer",
    "Architecture case studies"
  ]
}
```

For **Behavioral Weaknesses:**
```json
{
  "type": "improvement",
  "area": "Leadership Stories",
  "priority": "medium",
  "title": "Enhance Behavioral Responses",
  "action_items": [
    "Prepare 3 STAR method examples",
    "Quantify your achievements",
    "Practice storytelling"
  ]
}
```

#### 3. Pattern-Based Suggestions

**The Agent Detects Common Patterns:**

| Pattern Detected | Suggestion Generated |
|-----------------|---------------------|
| Short answers (<30 words avg) | "Elaborate more with examples" |
| Low relevance scores | "Address the question directly first" |
| Missing keywords | "Cover key concepts: [list]" |
| Inconsistent performance | "Focus on consistency" |

#### 4. Strength Leverage Suggestions

**Using Strengths to Improve Weaknesses:**
```
Agent Observation:
├── Strong Area: "Python Programming" (Score: 88%)
└── Weak Area: "System Design" (Score: 52%)

Suggestion Generated:
"Use your Python expertise to explain system design concepts.
 When discussing architectures, relate them to Python frameworks
 and patterns you know well."
```

#### 5. Learning Path Generation

**Structured Improvement Plan:**

```
┌─────────────────────────────────────────────────────────────┐
│                  PERSONALIZED LEARNING PATH                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  WEEK 1: Foundation Building                                │
│  ├── Focus: System Design basics                            │
│  ├── Activities: Read tutorials, watch videos               │
│  └── Target: Complete foundational review                   │
│                                                              │
│  WEEKS 2-3: Active Practice                                 │
│  ├── Focus: Daily mock interviews (15-30 min)               │
│  ├── Activities: Record and review answers                  │
│  └── Target: Achieve 70% on practice questions              │
│                                                              │
│  WEEK 4: Refinement                                         │
│  ├── Focus: Full mock interviews                            │
│  ├── Activities: Peer feedback sessions                     │
│  └── Target: Achieve target scores                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 6. Real-Time Feedback

**During the Interview:**
```
After Each Answer:
├── Immediate Level: "excellent" / "good" / "fair" / "needs_improvement"
├── Quick Message: "Good answer with room for minor improvements."
└── Tips: ["Consider addressing: scalability, trade-offs"]
```

---

## Anti-Cheat & Proctoring System

### Overview

The platform includes a comprehensive AI-powered proctoring system to ensure interview integrity. This is particularly important for remote assessments where traditional supervision isn't possible.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROCTORING ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────────────┐      ┌──────────────────────┐            │
│   │   Client-Side        │      │   Server-Side        │            │
│   │   Monitoring         │      │   Analysis           │            │
│   ├──────────────────────┤      ├──────────────────────┤            │
│   │ • Tab Switch         │ ──→  │ • Face Detection     │            │
│   │ • Window Blur        │      │ • Multiple Faces     │            │
│   │ • Copy/Paste         │      │ • Gaze Tracking      │            │
│   │ • DevTools Access    │      │ • Head Pose          │            │
│   │ • Keyboard Shortcuts │      │ • Person Verify      │            │
│   └──────────────────────┘      └──────────────────────┘            │
│              │                            │                          │
│              └────────────┬───────────────┘                          │
│                           ▼                                          │
│               ┌──────────────────────┐                               │
│               │   Violation Tracker  │                               │
│               │   & Integrity Score  │                               │
│               └──────────────────────┘                               │
│                           │                                          │
│                           ▼                                          │
│               ┌──────────────────────┐                               │
│               │   Proctoring Report  │                               │
│               │   & Recommendation   │                               │
│               └──────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Detection Technologies & Accuracy

| Feature | Technology | Accuracy | Description |
|---------|------------|----------|-------------|
| **Face Presence** | MediaPipe Face Detection | ~99% | Ensures user's face is visible |
| **Multiple Faces** | MediaPipe | ~95% | Detects if someone else is helping |
| **Gaze Tracking** | MediaPipe Face Mesh + Iris | ~85-90% | Tracks where user is looking |
| **Head Pose** | Face Mesh + PnP Solver | ~90% | Detects if looking at notes |
| **Person Verification** | DeepFace (Facenet) | ~97% | Verifies same person throughout |
| **Tab Switching** | Browser Visibility API | 100% | Detects browser tab changes |
| **Window Focus** | Browser Focus API | 100% | Detects window blur events |

### Face Detection & Presence

The system uses neural network-based face detection to ensure the candidate remains visible throughout the interview.

```
Face Detection Pipeline:
┌──────────────┐
│ Video Frame  │
│  (Webcam)    │
└──────┬───────┘
       │ BGR → RGB conversion
       ▼
┌──────────────┐
│  MediaPipe   │
│Face Detection│◄── min_confidence: 0.6
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Detection Results:                    │
│ • Bounding box (face location)        │
│ • Confidence score                    │
│ • Face count (detect multiple)        │
└──────────────────────────────────────┘
```

**Violation Triggers:**
- No face detected for 30+ consecutive frames → "NO_FACE" violation (Medium severity)
- 2+ faces detected → "MULTIPLE_FACES" violation (High severity)
- Face not centered in frame → Alert to reposition

### Gaze & Eye Tracking

Using 468 facial landmarks from MediaPipe Face Mesh, the system tracks eye movement to determine where the user is looking.

```
Gaze Estimation Process:

1. Extract Iris Landmarks
   Left Eye:  [468, 469, 470, 471, 472]
   Right Eye: [473, 474, 475, 476, 477]

2. Calculate Iris Position Relative to Eye Corners
   ┌─────────────────────────────────┐
   │    Inner Corner    Outer Corner │
   │         ●               ●       │
   │              ◉ (iris)           │
   │                                 │
   └─────────────────────────────────┘
   
   Horizontal Position = (iris_x - inner_x) / eye_width
   
   Position < 0.35 → Looking LEFT
   Position > 0.65 → Looking RIGHT
   Otherwise       → Looking CENTER

3. Threshold Check
   Looking away for 20+ frames → "LOOKING_AWAY" violation
```

### Head Pose Estimation

Using Perspective-n-Point (PnP) algorithm, the system estimates 3D head orientation from 2D facial landmarks.

```
Head Pose Calculation:

1. Define 6 Key Facial Points (3D Model)
   ┌────────────────────────────────┐
   │  • Nose tip (0, 0, 0)         │
   │  • Chin (0, -330, -65)        │
   │  • Left eye (-225, 170, -135) │
   │  • Right eye (225, 170, -135) │
   │  • Left mouth (-150, -150)    │
   │  • Right mouth (150, -150)    │
   └────────────────────────────────┘

2. Map to 2D Image Coordinates

3. Solve PnP (Perspective-n-Point)
   cv2.solvePnP(model_3d, image_2d, camera_matrix, dist_coeffs)

4. Convert Rotation Vector to Euler Angles
   ┌─────────────────────────────────┐
   │ Yaw   (Y-axis): Left/Right turn│
   │ Pitch (X-axis): Up/Down tilt   │
   │ Roll  (Z-axis): Head tilt      │
   └─────────────────────────────────┘

5. Threshold Check
   |Yaw| > 30° OR |Pitch| > 30° → Looking Away
```

### Person Verification

To prevent identity fraud (someone else taking the interview), the system uses face embeddings to verify the same person throughout.

```
Person Verification Flow:

1. Reference Capture (at session start)
   ┌──────────────┐      ┌──────────────┐
   │ User Photo   │ ──→  │   Facenet    │ ──→ Reference Embedding
   │              │      │   Model      │     (512-dim vector)
   └──────────────┘      └──────────────┘

2. Periodic Verification (every 30 frames)
   ┌──────────────┐      ┌──────────────┐
   │Current Frame │ ──→  │   Facenet    │ ──→ Current Embedding
   └──────────────┘      └──────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │  Cosine Similarity   │
                    │                      │
                    │  sim = A·B / |A||B|  │
                    │                      │
                    │  sim > 0.6 → MATCH   │
                    │  sim ≤ 0.6 → ALERT   │
                    └──────────────────────┘

3. Violation on Mismatch
   "DIFFERENT_PERSON" → Critical severity
```

### Client-Side Monitoring

The frontend JavaScript module monitors browser events that can't be detected server-side.

```javascript
// Tab Switch Detection
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // User switched tabs → Report to server
    }
});

// Window Blur Detection  
window.addEventListener('blur', () => {
    // User clicked outside browser → Report
});

// Copy/Paste Detection
document.addEventListener('copy', handler);
document.addEventListener('paste', handler);

// DevTools Detection
if (event.key === 'F12' || 
    (event.ctrlKey && event.shiftKey && event.key === 'I')) {
    // DevTools shortcut detected → Log violation
}
```

### Violation Severity Levels

| Severity | Description | Impact on Score |
|----------|-------------|-----------------|
| **Low** | Minor issue (looking away briefly) | -2 points |
| **Medium** | Moderate concern (tab switch, no face) | -5 points |
| **High** | Significant issue (multiple faces) | -10 points |
| **Critical** | Major violation (different person) | -20 points |

### Integrity Score Calculation

```
Base Score = 100

Deductions:
├── Face Visibility < 95%: -(95 - visibility) × 0.5
├── Attention Ratio < 90%: -(90 - attention) × 0.3
├── Per Violation:
│   ├── Low:      -2
│   ├── Medium:   -5
│   ├── High:    -10
│   └── Critical: -20

Final Score = max(0, min(100, adjusted_score))

Interpretation:
├── 90-100: PASSED - No significant concerns
├── 70-89:  PASSED WITH NOTES - Minor issues
├── 50-69:  FLAGGED - Manual review recommended
└── 0-49:   FAILED - Investigation required
```

### Sensitivity Levels

The system supports three sensitivity levels:

| Setting | Face Confidence | Gaze Threshold | Head Pose Threshold | No-Face Frames |
|---------|----------------|----------------|---------------------|----------------|
| **Low** | 0.7 | 35° | 40° | 60 frames (~2s) |
| **Medium** | 0.6 | 25° | 30° | 30 frames (~1s) |
| **High** | 0.5 | 20° | 25° | 15 frames (~0.5s) |

### Proctoring Session Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                     SESSION LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. START SESSION                                                │
│     POST /api/proctoring/session/start                          │
│     └── Returns: session_id                                     │
│                                                                  │
│  2. SET REFERENCE PHOTO (Optional)                              │
│     POST /api/proctoring/session/reference-photo                │
│     └── Enables person verification                             │
│                                                                  │
│  3. INITIALIZE WEBCAM (Client)                                  │
│     proctoringClient.initializeWebcam()                         │
│     proctoringClient.startFrameCapture()                        │
│                                                                  │
│  4. CONTINUOUS MONITORING                                        │
│     ┌──────────────────────────────────────────────────────┐    │
│     │ Every 2 seconds:                                      │    │
│     │ POST /api/proctoring/analyze-frame                    │    │
│     │ └── Returns: face_detected, violations, alerts        │    │
│     └──────────────────────────────────────────────────────┘    │
│                                                                  │
│  5. END SESSION                                                  │
│     POST /api/proctoring/session/{id}/end                       │
│     └── Returns: final report with integrity score              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Sample Proctoring Report

```json
{
  "session_id": "proctor_123_456_1706540800",
  "metrics": {
    "face_visibility_ratio": 97.5,
    "attention_ratio": 92.3,
    "integrity_score": 85.0
  },
  "violation_summary": {
    "looking_away": 3,
    "tab_switch": 1
  },
  "total_violations": 4,
  "critical_violations": 0,
  "recommendation": "PASSED WITH NOTES: Minor issues detected."
}
```

---

## Adaptive Learning System

### How the Platform Learns and Adapts

The adaptive system personalizes the interview experience based on user performance patterns.

#### 1. Performance Tracking

**Metrics Collected:**
```
User Performance Profile
├── Overall Score Trends
│   └── Improvement rate over time
├── Category Performance
│   ├── Technical questions accuracy
│   ├── Behavioral questions quality
│   └── HR questions responses
├── Skill-Specific Scores
│   └── Per-topic performance tracking
└── Temporal Patterns
    └── Performance at different times
```

#### 2. Difficulty Recommendation Algorithm

**Adaptive Selection Logic:**
```
Recent Performance Analysis:
│
├── If average score ≥ 80%
│   └── Recommend: HARD difficulty
│
├── If average score 60-79%
│   └── Recommend: MEDIUM difficulty
│
└── If average score < 60%
    └── Recommend: EASY difficulty
```

**Weighted Scoring:**
- Recent interviews weighted more heavily
- Difficulty of past questions factored in
- Category-specific calibration applied

#### 3. Weakness Identification

**Topic Analysis:**
- Groups questions by category
- Calculates per-category scores
- Flags categories with scores below threshold (e.g., 65%)

**Severity Classification:**
- **High Priority**: Score < 50%
- **Medium Priority**: Score 50-65%
- **Improvement Suggested**: Score 65-75%

#### 4. Strength Recognition

Identifies areas where user consistently excels:
- Scores above 80% in a category
- Multiple successful responses on similar topics
- Positive feedback patterns

#### 5. Personalized Learning Path

Based on analysis, the system generates:
- **Focus Areas**: Topics needing immediate attention
- **Practice Recommendations**: Specific question types to practice
- **Resource Suggestions**: Learning materials for weak areas
- **Goal Setting**: Incremental improvement targets

---

## Report Generation

### How Performance Reports Are Created

The reporting system synthesizes all analysis into actionable insights.

#### 1. Score Aggregation

**Weighted Overall Score:**
```
Overall Score = 
    (Content Quality × 0.40) +
    (Speech Quality × 0.30) +
    (Confidence/Emotion × 0.30)
```

**Component Breakdown:**
- Content Score = (Content Quality × 0.6) + (Relevance × 0.4)
- Speech Score = (Clarity + Fluency) / 2
- Confidence Score = Emotion analysis output

#### 2. Feedback Generation

**Rule-Based Feedback:**
```
If content_score < 60:
    → "Provide more details and examples"
    
If relevance_score < 60:
    → "Address the question more directly"
    → Suggest missing keywords
    
If fluency_score < 70:
    → "Work on speaking pace and reduce filler words"
    
If confidence_score < 60:
    → "Maintain eye contact and project confidence"
```

#### 3. Recommendation Engine

**Actionable Suggestions:**
- Specific improvement actions
- Practice question recommendations
- Behavioral adjustments

**Question-Type Specific Advice:**
- Behavioral: "Use the STAR method"
- Technical: "Explain trade-offs and alternatives"
- Situational: "Describe context clearly"

---

## Agent Integration & APIs

### How the Interview Agent Interfaces with the System

The Interview Agent is the central orchestrator. Here's how it integrates with all platform components and exposes capabilities for external use.

#### 1. Agent Core Methods

The Interview Agent exposes these primary methods:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     INTERVIEW AGENT API                              │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  start_interview(user_id, type, resume_data, ...)           │    │
│  │  → Creates session, generates questions, returns setup       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  process_answer(interview_id, question_id, answer_text)     │    │
│  │  → Evaluates answer, updates metrics, returns feedback       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  complete_interview(interview_id)                            │    │
│  │  → Analyzes session, identifies weak areas, generates report │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  get_interview_status(interview_id)                          │    │
│  │  → Returns current phase, progress, running performance      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  get_agent_insights(interview_id)                            │    │
│  │  → Returns agent observations and decision history           │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

#### 2. Agent Tools Interface

The agent uses specialized tools for each capability:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `generate_questions` | Create interview questions | Type, difficulty, resume, focus areas | Question list |
| `evaluate_answer` | Score a response | Question, answer, keywords | Scores + feedback |
| `identify_weak_areas` | Find performance gaps | Evaluations, context | Weak area list |
| `identify_strong_areas` | Find strengths | Evaluations, context | Strong area list |
| `generate_suggestions` | Create recommendations | Weak/strong areas, type | Suggestion list |
| `generate_learning_path` | Create improvement plan | Gaps, time available | Learning roadmap |
| `generate_final_report` | Complete report | Interview ID | Full report |

#### 3. Complete Agent Workflow Example

```python
# Initialize the Interview Agent
from ai_modules.agent import InterviewAgent

agent = InterviewAgent()

# Step 1: Start a new interview session
session = agent.start_interview(
    interview_id=123,
    user_id=456,
    interview_type="technical",
    resume_data={"skills": ["Python", "AWS"]},
    difficulty_level=None  # Let agent decide adaptively
)

# session contains:
# - Generated questions (personalized based on resume)
# - Recommended difficulty (based on past performance)
# - Context summary

# Step 2: Process each answer as user responds
for question in session["questions"]:
    # User provides answer
    user_answer = get_user_answer()  
    
    result = agent.process_answer(
        interview_id=123,
        question_id=question["order"],
        answer_text=user_answer
    )
    
    # result contains:
    # - Evaluation scores
    # - Real-time feedback
    # - Running performance metrics
    # - Questions remaining

# Step 3: Complete and get final analysis
report = agent.complete_interview(interview_id=123)

# report contains:
# - Final scores (overall, content, clarity, etc.)
# - Identified weak areas with severity
# - Identified strong areas
# - Skill gaps analysis
# - Personalized suggestions
# - Structured learning path
# - Agent insights (observations, decisions)
```

#### 4. Agent State Inspection

For transparency, you can inspect the agent's reasoning:

```python
# Get agent's observations and decisions
insights = agent.get_agent_insights(interview_id=123)

# insights["observations"]:
# [
#   {"timestamp": "...", "observation": "User struggling with system design"},
#   {"timestamp": "...", "observation": "Strong performance in Python questions"}
# ]

# insights["decisions"]:
# [
#   {"decision": "Increase difficulty", "reasoning": "High scores on easy questions"},
#   {"decision": "Add follow-up", "reasoning": "Missing key concepts"}
# ]
```

#### 5. External Integration Points

External systems can integrate with the agent:

**REST API Endpoints:**
```
POST /api/agent/start          → Start interview via agent
POST /api/agent/answer         → Submit answer for processing
POST /api/agent/complete       → Complete interview
GET  /api/agent/status/{id}    → Get interview status
GET  /api/agent/insights/{id}  → Get agent reasoning
```

**Event Webhooks:**
```
on_interview_started    → Interview session created
on_answer_evaluated     → Answer processed with scores
on_weak_area_detected   → New weak area identified
on_interview_completed  → Final report generated
```

#### 6. Agent Configuration

The agent behavior can be customized:

```python
agent.state.max_questions_per_interview = 15
agent.state.weak_area_threshold = 60.0  # Below 60% is weak
agent.state.strong_area_threshold = 85.0  # Above 85% is strong
agent.state.enable_adaptive_difficulty = True
agent.state.enable_real_time_feedback = True
```

---

## Summary

The AI Mock Interview Platform is powered by an **intelligent Interview Agent** that orchestrates the entire interview process:

| Component | What It Does | Agent Integration |
|-----------|--------------|-------------------|
| **Interview Agent** | Central orchestrator | Coordinates all components |
| **Resume Parser** | Extracts candidate information | Provides context to agent |
| **Question Generator** | Creates personalized questions | Agent tool for question creation |
| **Answer Evaluator** | Scores response quality | Agent tool for evaluation |
| **Weak Area Identifier** | Finds performance gaps | Agent analyzes patterns |
| **Suggestion Generator** | Creates recommendations | Agent generates personalized advice |
| **Speech Analyzer** | Assesses verbal communication | Feeds data to agent |
| **Emotion Detector** | Measures confidence | Feeds data to agent |
| **Adaptive System** | Personalizes experience | Agent uses for decisions |
| **Report Generator** | Synthesizes insights | Agent compiles final output |

### Key Agent Capabilities:

1. **Question Generation**: Creates context-aware, personalized interview questions
2. **Answer Evaluation**: Provides comprehensive scoring and feedback
3. **Weak Area Identification**: Continuously monitors for performance patterns
4. **Personalized Suggestions**: Generates actionable improvement recommendations
5. **Adaptive Behavior**: Adjusts difficulty and focus based on performance
6. **Transparent Reasoning**: Exposes observations and decisions for inspection

The agent-based architecture enables sophisticated, personalized interview coaching that adapts in real-time to each user's performance.

---

*This document explains the conceptual workings of the platform. For implementation details and API specifications, see the [API Documentation](./API_DOCUMENTATION.md) and [Architecture Overview](./ARCHITECTURE_OVERVIEW.md).*
