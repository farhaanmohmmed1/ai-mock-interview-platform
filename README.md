# AI-Powered Adaptive Mock Interview Platform

🚀 **Live Demo**: [https://ai-mock-interview-platform-t8ph-okbn90n64.vercel.app/](https://ai-mock-interview-platform-t8ph-okbn90n64.vercel.app/)

A comprehensive mock interview platform that conducts adaptive interviews across three rounds (General, Technical, and HR) using advanced AI technologies including NLP, speech processing, and emotion analysis.

## Features

### 🎯 Core Capabilities
- **Three Interview Rounds**: General, Technical (resume-based), and HR rounds
- **NLP-Powered**: Automated question generation, resume parsing, and answer evaluation
- **Speech Analysis**: Real-time clarity and fluency detection
- **Emotion Recognition**: Confidence and emotional readiness assessment
- **Adaptive Learning**: System learns from performance and adapts future interviews
- **Comprehensive Reports**: Detailed performance reports with weak area identification
- **Personalized Feedback**: Tailored recommendations and learning paths

### 📊 Dashboard Features
- Performance history tracking
- Progress visualization
- Interview scheduling
- Real-time feedback
- Score analytics

## Architecture

```
tp/
├── backend/              # FastAPI backend server
│   ├── api/             # API endpoints
│   ├── core/            # Core configuration
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── main.py          # Application entry point
├── ai_modules/          # AI processing modules
│   ├── nlp/             # Natural Language Processing
│   ├── speech/          # Speech analysis
│   ├── emotion/         # Emotion detection
│   └── adaptive/        # Adaptive learning system
├── frontend/            # React dashboard
├── data/                # Data storage
└── tests/               # Test suite
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (or SQLite for development)
- FFmpeg (for audio processing)

### Backend Setup

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy models:
```bash
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Initialize the database:
```bash
python backend/init_db.py
```

7. Run the backend server:
```bash
python backend/main.py
# Or with uvicorn:
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## Usage

### Starting an Interview

1. **Register/Login**: Create an account or login to existing account
2. **Upload Resume**: Upload your resume (PDF/DOCX format)
3. **Select Interview Type**: Choose from General, Technical, or HR round
4. **Grant Permissions**: Allow camera and microphone access
5. **Begin Interview**: Start the adaptive interview session

### During Interview

- Answer questions clearly and naturally
- System analyzes speech clarity, fluency, and content
- Facial emotion recognition assesses confidence
- Real-time feedback on communication

### After Interview

- Receive comprehensive performance report
- View detailed scores across multiple dimensions
- Get personalized learning recommendations
- Track progress over time
- Access weak area analysis


## Key Technologies

- **Backend**: FastAPI, SQLAlchemy
- **NLP**: Transformers, spaCy, NLTK
- **Speech**: SpeechRecognition, librosa, Parselmouth
- **Emotion**: OpenCV, FER, DeepFace, MediaPipe
- **ML**: scikit-learn, PyTorch
- **Frontend**: React, Material-UI, Chart.js
- **Database**: PostgreSQL/SQLite

## Project Structure Details

### Backend Services
- `AuthService`: User authentication and authorization
- `ResumeService`: Resume parsing and skill extraction
- `QuestionService`: Dynamic question generation
- `EvaluationService`: Answer analysis and scoring
- `SpeechService`: Audio processing and analysis
- `EmotionService`: Facial emotion detection
- `AdaptiveService`: Personalized interview adaptation
- `ReportService`: Performance report generation

### AI Modules
- **NLP Module**: Question generation, answer evaluation, resume parsing
- **Speech Module**: Clarity detection, fluency analysis, speech-to-text
- **Emotion Module**: Confidence assessment, emotion classification
- **Adaptive Module**: Performance tracking, weakness identification, adaptation

## Configuration

Edit `.env` file to customize:
- Database connection
- API settings
- AI model parameters
- Interview configuration
- Security settings

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black backend/ ai_modules/

# Lint
flake8 backend/ ai_modules/

# Type checking
mypy backend/
```

## Performance Optimization

- Use GPU acceleration for AI models (set `USE_GPU=True`)
- Configure appropriate batch sizes
- Enable caching for frequently accessed data
- Use CDN for frontend assets in production

## Security Considerations

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Rate limiting on API endpoints
- Secure file upload handling
- Environment variable protection

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Cloud Deployment
- Compatible with AWS, GCP, Azure
- Use managed database services
- Configure auto-scaling
- Set up load balancing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


## Roadmap

- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Integration with job platforms
- [ ] Group interview sessions
- [ ] AI interviewer avatar
- [ ] Voice cloning for diverse interviewers
- [ ] Industry-specific interview templates

## Acknowledgments

- Hugging Face for transformer models
- OpenAI for inspiration
- Open-source community for excellent libraries
