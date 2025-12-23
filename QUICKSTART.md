# AI Mock Interview Platform - Quick Start Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 16+**: [Download Node.js](https://nodejs.org/)
- **FFmpeg**: For audio processing
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: [Download FFmpeg](https://ffmpeg.org/download.html)

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Create Python virtual environment
- Install all dependencies
- Download required AI models
- Initialize the database
- Set up the frontend

### Option 2: Manual Setup

#### Backend Setup

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download AI Models**
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize Database**
   ```bash
   python backend/init_db.py
   ```

#### Frontend Setup

1. **Navigate to Frontend**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

## Running the Application

### Start Backend Server

```bash
# Activate virtual environment (if not already)
source venv/bin/activate

# Start the server
python backend/main.py

# Or use uvicorn directly:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Start Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:3000

## Using the Application

### 1. Register/Login

- Navigate to http://localhost:3000
- Register a new account or use demo credentials:
  - Username: `demo_user`
  - Password: `demo123`

### 2. Upload Resume (Optional)

- For technical interviews, upload your resume in PDF or DOCX format
- The system will automatically parse and extract your skills

### 3. Start an Interview

Choose from three interview types:

1. **General Interview**: Common behavioral questions (~20 min)
2. **Technical Interview**: Resume-based technical questions (~30 min)
3. **HR Interview**: Culture fit and soft skills (~15 min)

### 4. During the Interview

- Allow camera and microphone access
- Answer each question clearly
- The system analyzes:
  - Content quality and relevance
  - Speech clarity and fluency
  - Confidence and emotions

### 5. View Results

After completing the interview:
- Overall performance score
- Detailed breakdown by category
- Weak areas identification
- Personalized recommendations
- Progress tracking over time

## Project Structure

```
tp/
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints
│   ├── core/            # Configuration & database
│   ├── models/          # Database models
│   └── main.py          # Application entry
├── ai_modules/          # AI processing
│   ├── nlp/             # NLP (questions, evaluation)
│   ├── speech/          # Speech analysis
│   ├── emotion/         # Emotion detection
│   └── adaptive/        # Adaptive learning
├── frontend/            # React frontend
│   └── src/
│       ├── pages/       # Page components
│       └── App.jsx      # Main app
├── data/                # Data storage
│   ├── uploads/         # Resume files
│   ├── recordings/      # Audio recordings
│   └── videos/          # Video recordings
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── setup.sh            # Setup script
```

## Key Features

### AI-Powered Analysis

- **NLP**: Question generation, answer evaluation, resume parsing
- **Speech**: Clarity detection, fluency analysis, filler word detection
- **Emotion**: Confidence assessment, facial emotion recognition
- **Adaptive**: Personalized difficulty, weakness identification

### Performance Tracking

- Overall and category-wise scores
- Progress over time
- Skill gap analysis
- Personalized learning paths

### Interview Types

- **General**: Behavioral and situational questions
- **Technical**: Resume-based technical questions
- **HR**: Soft skills and culture fit

## Troubleshooting

### Backend Issues

**Import errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Database errors**:
```bash
# Reinitialize database
python backend/init_db.py
```

**Port already in use**:
```bash
# Change port in .env
API_PORT=8001
```

### Frontend Issues

**Module not found**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Proxy errors**:
- Ensure backend is running on port 8000
- Check vite.config.js proxy settings

### AI Model Issues

**spaCy model not found**:
```bash
python -m spacy download en_core_web_sm
```

**NLTK data missing**:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=sqlite:///./interview_platform.db

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=True

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Settings
USE_GPU=False
ENABLE_EMOTION_ANALYSIS=True

# Interview Configuration
GENERAL_QUESTIONS_COUNT=5
TECHNICAL_QUESTIONS_COUNT=8
HR_QUESTIONS_COUNT=5
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Resume
- `POST /api/resume/upload` - Upload resume
- `GET /api/resume/list` - List user resumes
- `GET /api/resume/{id}` - Get resume details

### Interview
- `POST /api/interview/create` - Start new interview
- `GET /api/interview/list` - List user interviews
- `GET /api/interview/{id}` - Get interview details
- `POST /api/interview/{id}/complete` - Complete interview

### Evaluation
- `POST /api/evaluation/submit-text` - Submit text response
- `POST /api/evaluation/submit-audio` - Submit audio response
- `POST /api/evaluation/submit-video` - Submit video response

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/performance-metrics` - Get performance metrics

## Next Steps

1. **Customize Questions**: Edit question banks in `ai_modules/nlp/question_generator.py`
2. **Adjust Scoring**: Modify evaluation criteria in `ai_modules/nlp/answer_evaluator.py`
3. **Enhance UI**: Develop comprehensive frontend pages
4. **Add Features**: Implement additional interview types or analysis methods
5. **Deploy**: Set up production deployment with proper security

## Support

For issues or questions:
- Check the documentation
- Review API docs at http://localhost:8000/docs
- Check logs in terminal output

## License

MIT License - See LICENSE file for details
