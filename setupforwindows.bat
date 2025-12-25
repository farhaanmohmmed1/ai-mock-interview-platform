@echo off
REM AI Mock Interview Platform - Setup Script for Windows
REM This script sets up the entire project including backend and frontend

echo ======================================
echo AI Mock Interview Platform - Setup
echo ======================================
echo.

REM Check Python version
echo Checking Python version...
python --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Check Node.js
echo Checking Node.js...
node --version 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Node.js not found. Frontend setup will be skipped.
    echo Install Node.js from https://nodejs.org/
    set SKIP_FRONTEND=true
) else (
    echo [OK] Node.js installed
)
echo.

REM Backend Setup
echo ======================================
echo Setting up Backend
echo ======================================
echo.

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo [OK] Pip upgraded
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed
echo.

REM Download spaCy models
echo Downloading spaCy language models...
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
echo [OK] spaCy models downloaded
echo.

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
echo [OK] NLTK data downloaded
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    if exist .env.example (
        copy .env.example .env
        echo [OK] .env file created from .env.example
        echo WARNING: Please edit .env file with your configuration
    ) else (
        echo WARNING: .env.example not found, please create .env manually
    )
) else (
    echo WARNING: .env file already exists, skipping creation
)
echo.

REM Create data directories
echo Creating data directories...
if not exist data\uploads mkdir data\uploads
if not exist data\recordings mkdir data\recordings
if not exist data\videos mkdir data\videos
if not exist data\models mkdir data\models
if not exist backend\data\uploads mkdir backend\data\uploads
if not exist backend\data\recordings mkdir backend\data\recordings
if not exist backend\data\videos mkdir backend\data\videos
if not exist backend\data\models mkdir backend\data\models
echo [OK] Data directories created
echo.

REM Initialize database
echo Initializing database...
python -m backend.init_db
echo [OK] Database initialized
echo.

REM Frontend Setup
if defined SKIP_FRONTEND (
    echo Skipping frontend setup - Node.js not found
) else (
    echo ======================================
    echo Setting up Frontend
    echo ======================================
    echo.
    
    cd frontend
    
    echo Installing Node.js dependencies...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Node.js dependencies
        cd ..
        pause
        exit /b 1
    )
    echo [OK] Node.js dependencies installed
    
    cd ..
)
echo.

echo ======================================
echo Setup Complete!
echo ======================================
echo.
echo To start the application:
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Start the backend server:
echo    python -m uvicorn backend.main:app --reload
echo.
echo 3. In another terminal, start the frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open your browser to http://localhost:5173
echo.
pause
