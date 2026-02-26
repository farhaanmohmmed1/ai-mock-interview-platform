# AI Agent Verification Prompt for AI Mock Interview Platform

## Overview
This document contains structured prompts for an AI agent to systematically verify all features of the AI Mock Interview Platform. Each section should be tested independently and results documented.

---

## PROMPT 1: Project Setup Verification

```
You are a QA verification agent. Verify the project setup for the AI Mock Interview Platform.

TASKS:
1. Check if all required files exist:
   - backend/main.py
   - frontend/src/App.jsx
   - ai_modules/__init__.py
   - requirements.txt
   - requirements-full.txt

2. Verify Python dependencies can be imported:
   - fastapi, uvicorn, sqlalchemy
   - openai, langchain, langgraph
   - whisper, fer, cv2
   - pydantic, python-jose

3. Check environment configuration:
   - .env file exists with required keys
   - OPENAI_API_KEY is set
   - DATABASE_URL is configured

4. Verify database initialization:
   - SQLite database can be created
   - All tables exist (users, resumes, interviews, questions)

EXPECTED OUTPUT:
- List of missing files (if any)
- List of import failures (if any)
- Configuration status
- Database schema validation
```

---

## PROMPT 2: Authentication System Verification

```
You are a QA verification agent. Test the authentication system.

TASKS:
1. User Registration:
   - POST /api/auth/register with valid data
   - Verify user is created in database
   - Test duplicate email rejection
   - Test password validation (min 6 chars)

2. User Login:
   - POST /api/auth/login with valid credentials
   - Verify JWT token is returned
   - Test invalid password rejection
   - Test non-existent user rejection

3. Protected Routes:
   - Access /api/auth/me without token (should fail 401)
   - Access /api/auth/me with valid token (should succeed)
   - Test expired token handling

TEST DATA:
{
  "email": "test@example.com",
  "password": "testpass123",
  "full_name": "Test User"
}

EXPECTED OUTPUT:
- Registration: 201 Created
- Login: 200 OK with token
- Protected route: 200 OK with user data
- All error cases return appropriate status codes
```

---

## PROMPT 3: Resume Management Verification

```
You are a QA verification agent. Test the resume management system.

TASKS:
1. Resume Upload:
   - POST /api/resume/upload with PDF file
   - Verify file is saved to data/uploads/user_{id}/
   - Test file size limits
   - Test invalid file type rejection

2. Resume Parsing:
   - Verify text extraction from PDF
   - Check skills extraction accuracy
   - Check experience extraction
   - Verify education parsing

3. Resume Retrieval:
   - GET /api/resume/latest
   - Verify parsed data is returned
   - Check extracted skills list
   - Verify experience years calculation

TEST SCENARIOS:
- Upload valid PDF resume
- Upload non-PDF file (should reject)
- Upload empty file (should reject)
- Retrieve resume for user without upload

EXPECTED OUTPUT:
- Upload success with file path
- Parsed skills array (e.g., ["Python", "JavaScript", "SQL"])
- Experience summary
- Education details
```

---

## PROMPT 4: Interview Setup Verification

```
You are a QA verification agent. Test the interview setup system.

TASKS:
1. Interview Types:
   - Verify "technical" type works
   - Verify "behavioral" type works
   - Verify "hr" type works
   - Verify "upsc" type works

2. Company Selection:
   - Test Google questions loading
   - Test Amazon questions loading
   - Test Meta questions loading
   - Test Microsoft questions loading
   - Test "general" (no company) option

3. Difficulty Levels:
   - Test "easy" difficulty
   - Test "medium" difficulty
   - Test "hard" difficulty

4. Interview Creation:
   - POST /api/interview/start
   - Verify interview ID is returned
   - Check initial status is "in_progress"

TEST PAYLOAD:
{
  "interview_type": "technical",
  "job_role": "Software Engineer",
  "company": "google",
  "difficulty": "medium",
  "num_questions": 5
}

EXPECTED OUTPUT:
- Interview ID returned
- First question generated
- Question matches interview type and company
```

---

## PROMPT 5: Question Generation Verification

```
You are a QA verification agent. Test the question generation system.

TASKS:
1. Company Questions Bank:
   - Load data/company_questions.json
   - Verify 150 total questions exist
   - Check categories: behavioral (35), technical (60), HR (25), general (30)
   - Test duplicate prevention across batches

2. UPSC Questions Bank:
   - Load data/upsc_questions.json
   - Verify 200 total questions exist
   - Check 11 categories present
   - Test duplicate prevention

3. Question Loading:
   - Test CompanyQuestionsLoader
   - Test UPSCQuestionsLoader
   - Verify get_questions() returns requested count
   - Verify reset_used_questions() clears tracking

4. UPSC Interview Isolation:
   - Start UPSC interview
   - Verify NO company questions appear
   - Verify ONLY UPSC-relevant questions appear

TEST SCRIPT:
```python
from ai_modules.nlp.company_questions_loader import get_company_questions_loader
from ai_modules.nlp.upsc_questions_loader import get_upsc_questions_loader

company_loader = get_company_questions_loader()
upsc_loader = get_upsc_questions_loader()

# Test counts
company_q = company_loader.get_questions(count=10)
upsc_q = upsc_loader.get_questions(count=10)

# Test no duplicates
batch1 = company_loader.get_questions(count=5)
batch2 = company_loader.get_questions(count=5)
overlap = set(q['id'] for q in batch1) & set(q['id'] for q in batch2)
assert len(overlap) == 0, "Duplicates found!"
```

EXPECTED OUTPUT:
- Company loader: 150 questions loaded
- UPSC loader: 200 questions loaded
- No duplicate questions in consecutive batches
- UPSC interviews exclude company-specific questions
```

---

## PROMPT 6: Speech Analysis Verification

```
You are a QA verification agent. Test the speech analysis system.

TASKS:
1. Whisper Model Loading:
   - Verify "small" model is configured (not "base")
   - Check model loads successfully
   - Verify ~466MB model size

2. Audio Transcription:
   - Test WAV file transcription
   - Test MP3 file transcription
   - Test WEBM file transcription
   - Verify accuracy > 85%

3. Speech Metrics:
   - Words per minute calculation
   - Filler words detection ("um", "uh", "like")
   - Speaking pace analysis

TEST SCRIPT:
```python
from ai_modules.speech.speech_analyzer import SpeechAnalyzer

analyzer = SpeechAnalyzer()
print(f"Model: {analyzer.whisper_model_name}")  # Should be "small"
print(f"Whisper available: {analyzer.whisper_model is not None}")

# Test with sample audio
result = analyzer.analyze_audio("test_audio.wav")
print(f"Transcript: {result['transcript']}")
print(f"WPM: {result['words_per_minute']}")
```

EXPECTED OUTPUT:
- Model: small
- Whisper available: True
- Transcript with >85% accuracy
- Valid WPM calculation (100-180 typical range)
```

---

## PROMPT 7: Emotion Analysis Verification

```
You are a QA verification agent. Test the emotion analysis system.

TASKS:
1. FER Initialization:
   - Verify FER library imports successfully
   - Check MTCNN detector initializes
   - Confirm NO "FER not installed" warning

2. Video Analysis:
   - Test face detection in video frames
   - Verify emotion classification (angry, disgust, fear, happy, sad, surprise, neutral)
   - Check confidence scores (0-1 range)

3. Aggregate Metrics:
   - Test emotion timeline generation
   - Verify dominant emotion calculation
   - Check confidence averaging

TEST SCRIPT:
```python
from ai_modules.emotion.emotion_analyzer import EmotionAnalyzer

analyzer = EmotionAnalyzer()
print(f"Detector initialized: {analyzer.emotion_detector is not None}")

# Test with sample video
result = analyzer.analyze_video("test_video.mp4")
print(f"Dominant emotion: {result['dominant_emotion']}")
print(f"Average confidence: {result['average_confidence']}")
print(f"Emotions: {result['emotions_detected']}")
```

EXPECTED OUTPUT:
- Detector initialized: True
- Valid dominant emotion (one of 7 categories)
- Confidence: 0.0 to 1.0
- No warnings about missing dependencies
```

---

## PROMPT 8: Answer Evaluation Verification

```
You are a QA verification agent. Test the answer evaluation system.

TASKS:
1. Relevance Scoring:
   - Test answer relevance to question
   - Verify score range 0-100
   - Test irrelevant answer (should score < 30)

2. Depth Analysis:
   - Test technical depth scoring
   - Verify example detection
   - Check explanation quality metrics

3. Persona-Based Grading:
   - Test grading_style parameter
   - Verify "strict" produces lower scores
   - Verify "lenient" produces higher scores
   - Test "balanced" gives moderate scores

4. Follow-up Generation:
   - Test follow-up question generation
   - Verify follow-ups are contextually relevant
   - Check follow-up difficulty progression

TEST PAYLOAD:
{
  "question": "Explain the difference between REST and GraphQL",
  "answer": "REST uses multiple endpoints while GraphQL uses single endpoint with queries",
  "job_role": "Backend Developer",
  "grading_style": "balanced"
}

EXPECTED OUTPUT:
- Relevance score: 60-80 (for basic answer)
- Depth score: 30-50 (lacks examples)
- Overall score: 50-70
- Follow-up question generated
```

---

## PROMPT 9: Interview Agent Verification

```
You are a QA verification agent. Test the LangGraph interview agent.

TASKS:
1. Agent Initialization:
   - Verify LangGraph state machine loads
   - Check all tools are registered
   - Confirm agent_state.py defines proper state

2. Conversation Flow:
   - Test question → answer → evaluation cycle
   - Verify state transitions
   - Check conversation context maintenance

3. Adaptive Behavior:
   - Test difficulty adjustment based on performance
   - Verify follow-up questions on weak answers
   - Check encouragement on strong answers

4. Tool Integration:
   - Test generate_question tool
   - Test evaluate_answer tool
   - Test generate_feedback tool
   - Test end_interview tool

TEST FLOW:
1. Start interview (generates first question)
2. Submit answer
3. Receive evaluation
4. Get next question (should adapt to performance)
5. Repeat 3 times
6. End interview (get summary)

EXPECTED OUTPUT:
- Smooth state transitions
- Contextual follow-up questions
- Adaptive difficulty
- Comprehensive end summary
```

---

## PROMPT 10: Proctoring System Verification

```
You are a QA verification agent. Test the proctoring system.

TASKS:
1. Tab Switch Detection:
   - Send tab_switch event
   - Verify event is logged
   - Check warning is generated

2. Face Detection:
   - Test single face detection
   - Test multiple faces detection (warning)
   - Test no face detection (warning)

3. Violation Tracking:
   - POST /api/proctoring/event
   - Verify violation count increments
   - Check violation types are categorized

4. Session Summary:
   - Get proctoring summary for interview
   - Verify total violations count
   - Check violation breakdown by type

TEST EVENTS:
- { "event_type": "tab_switch", "interview_id": 1 }
- { "event_type": "multiple_faces", "interview_id": 1 }
- { "event_type": "no_face", "interview_id": 1 }

EXPECTED OUTPUT:
- Events logged successfully
- Violation counts accurate
- Summary includes all event types
```

---

## PROMPT 11: Report Generation Verification

```
You are a QA verification agent. Test the report generation system.

TASKS:
1. Interview Summary:
   - Generate report for completed interview
   - Verify overall score calculation
   - Check section-wise breakdown

2. Feedback Quality:
   - Verify strengths identification
   - Check areas for improvement
   - Validate specific recommendations

3. Report Components:
   - Technical assessment (if applicable)
   - Communication assessment
   - Confidence assessment
   - Problem-solving assessment

4. Export Formats:
   - Test JSON report format
   - Verify all fields populated
   - Check report completeness

TEST ENDPOINT:
GET /api/interview/{id}/report

EXPECTED OUTPUT:
- Overall score: 0-100
- Section scores for each category
- At least 3 strengths listed
- At least 3 improvement areas
- Actionable recommendations
```

---

## PROMPT 12: Dashboard & Analytics Verification

```
You are a QA verification agent. Test the dashboard and analytics.

TASKS:
1. Interview History:
   - GET /api/dashboard/interviews
   - Verify past interviews listed
   - Check pagination works
   - Validate sorting by date

2. Performance Metrics:
   - Test score trends over time
   - Verify average score calculation
   - Check category-wise performance

3. Progress Tracking:
   - Test improvement trends
   - Verify milestone tracking
   - Check streak counting

4. Data Visualization Readiness:
   - Verify data format for charts
   - Check time-series data structure
   - Validate aggregation accuracy

TEST SCENARIOS:
- User with 0 interviews (empty state)
- User with 5+ interviews (pagination)
- User with mixed performance (trend calculation)

EXPECTED OUTPUT:
- Interview list with all required fields
- Accurate score calculations
- Proper data format for frontend charts
```

---

## PROMPT 13: API Integration Verification

```
You are a QA verification agent. Test all API endpoints.

TASKS:
1. Health Check:
   - GET /api/health
   - Verify 200 response
   - Check all services status

2. Authentication Endpoints:
   - POST /api/auth/register
   - POST /api/auth/login
   - GET /api/auth/me

3. Interview Endpoints:
   - POST /api/interview/start
   - POST /api/interview/{id}/answer
   - POST /api/interview/{id}/end
   - GET /api/interview/{id}/report

4. Resume Endpoints:
   - POST /api/resume/upload
   - GET /api/resume/latest

5. Dashboard Endpoints:
   - GET /api/dashboard/interviews
   - GET /api/dashboard/stats

6. Error Handling:
   - Test 400 Bad Request
   - Test 401 Unauthorized
   - Test 404 Not Found
   - Test 500 Internal Server Error

EXPECTED OUTPUT:
- All endpoints respond correctly
- Proper HTTP status codes
- Consistent error response format
- Valid JSON responses
```

---

## PROMPT 14: Frontend Integration Verification

```
You are a QA verification agent. Test frontend-backend integration.

TASKS:
1. Landing Page:
   - Verify page loads
   - Check login/register links work

2. Authentication Flow:
   - Test registration form submission
   - Test login form submission
   - Verify redirect after login

3. Interview Setup Page:
   - Verify interview type selection
   - Test company dropdown
   - Check difficulty selection
   - Validate form submission

4. Interview Page:
   - Test question display
   - Verify audio recording (if enabled)
   - Test answer submission
   - Check real-time feedback

5. Results Page:
   - Verify report display
   - Check score visualization
   - Test feedback sections

6. Dashboard Page:
   - Verify interview history loads
   - Test navigation to past interviews
   - Check stats display

EXPECTED OUTPUT:
- All pages render correctly
- Forms submit and validate properly
- API calls succeed
- State management works
```

---

## PROMPT 15: End-to-End Flow Verification

```
You are a QA verification agent. Run complete end-to-end test.

FULL USER JOURNEY:
1. Register new user
2. Login with credentials
3. Upload resume
4. Start technical interview for Google Software Engineer
5. Answer 5 questions
6. End interview
7. View report
8. Check dashboard for new interview
9. Logout

VERIFICATION CHECKPOINTS:
- [ ] Registration creates user in DB
- [ ] Login returns valid JWT
- [ ] Resume upload saves and parses file
- [ ] Interview starts with relevant question
- [ ] Each answer gets evaluated and scored
- [ ] Follow-up questions are contextual
- [ ] Report includes comprehensive feedback
- [ ] Dashboard shows interview in history
- [ ] All data persists correctly

EXPECTED OUTPUT:
- Complete flow without errors
- All data correctly stored
- Consistent user experience
- Proper error handling throughout
```

---

## PROMPT 16: Performance & Load Testing

```
You are a QA verification agent. Test system performance.

TASKS:
1. Response Times:
   - API endpoints < 200ms (simple queries)
   - Evaluation < 5s (with AI processing)
   - Transcription < 10s (for audio)

2. Concurrent Users:
   - Test 5 simultaneous interviews
   - Verify no data leakage between sessions
   - Check database connection handling

3. Memory Usage:
   - Monitor Whisper model memory
   - Check FER/TensorFlow memory
   - Verify no memory leaks

4. Resource Cleanup:
   - Verify temporary files deleted
   - Check audio/video cleanup
   - Validate session cleanup

EXPECTED OUTPUT:
- Response times within limits
- No errors under concurrent load
- Stable memory usage
- Clean resource management
```

---

## Quick Verification Command

```bash
# Run this to quickly verify core functionality
python -c "
from ai_modules.nlp.question_generator import QuestionGenerator
from ai_modules.nlp.answer_evaluator import AnswerEvaluator
from ai_modules.speech.speech_analyzer import SpeechAnalyzer
from ai_modules.emotion.emotion_analyzer import EmotionAnalyzer
from ai_modules.nlp.company_questions_loader import get_company_questions_loader
from ai_modules.nlp.upsc_questions_loader import get_upsc_questions_loader

print('=== AI Mock Interview Platform Verification ===')
print()

# Question banks
company = get_company_questions_loader()
upsc = get_upsc_questions_loader()
print(f'✓ Company questions: {company.total_questions}')
print(f'✓ UPSC questions: {upsc.total_questions}')

# Speech
speech = SpeechAnalyzer()
print(f'✓ Whisper model: {speech.whisper_model_name}')
print(f'✓ Whisper loaded: {speech.whisper_model is not None}')

# Emotion
emotion = EmotionAnalyzer()
print(f'✓ FER loaded: {emotion.emotion_detector is not None}')

# Evaluator
evaluator = AnswerEvaluator()
print(f'✓ Answer evaluator ready')

print()
print('=== All Core Modules Verified ===')
"
```

---

## Notes for Verification Agent

1. **Environment**: Ensure virtual environment is activated before testing
2. **API Key**: Some tests require valid OPENAI_API_KEY
3. **Database**: Tests may modify database; use test database if available
4. **Media Files**: Audio/video tests require sample media files
5. **Network**: Some features require internet connection for AI API calls

## Verification Status Template

| Feature | Status | Notes |
|---------|--------|-------|
| Authentication | ⬜ | |
| Resume Upload | ⬜ | |
| Interview Setup | ⬜ | |
| Question Generation | ⬜ | |
| Speech Analysis | ⬜ | |
| Emotion Analysis | ⬜ | |
| Answer Evaluation | ⬜ | |
| Interview Agent | ⬜ | |
| Proctoring | ⬜ | |
| Report Generation | ⬜ | |
| Dashboard | ⬜ | |
| API Endpoints | ⬜ | |
| Frontend | ⬜ | |
| E2E Flow | ⬜ | |
| Performance | ⬜ | |

Legend: ✅ Pass | ❌ Fail | ⬜ Not Tested
