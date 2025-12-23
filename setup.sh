#!/bin/bash

# AI Mock Interview Platform - Setup Script
# This script sets up the entire project including backend and frontend

set -e  # Exit on error

echo "======================================"
echo "AI Mock Interview Platform - Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! python3 -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
    echo -e "${RED}Error: Python 3.9 or higher is required${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}"
echo ""

# Check Node.js
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Warning: Node.js not found. Frontend setup will be skipped.${NC}"
    echo "Install Node.js from https://nodejs.org/"
    SKIP_FRONTEND=true
else
    node_version=$(node --version)
    echo "Node.js version: $node_version"
    echo -e "${GREEN}✓ Node.js installed${NC}"
fi
echo ""

# Backend Setup
echo "======================================"
echo "Setting up Backend"
echo "======================================"
echo ""

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo -e "${GREEN}✓ Pip upgraded${NC}"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Download spaCy models (using direct pip install for reliability)
echo "Downloading spaCy language models..."
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
echo -e "${GREEN}✓ spaCy models downloaded${NC}"
echo ""

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
echo -e "${GREEN}✓ NLTK data downloaded${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file with your configuration${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping creation${NC}"
fi
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/uploads data/recordings data/videos data/models
echo -e "${GREEN}✓ Data directories created${NC}"
echo ""

# Initialize database
echo "Initializing database..."
python backend/init_db.py
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Frontend Setup
if [ "$SKIP_FRONTEND" != true ]; then
    echo "======================================"
    echo "Setting up Frontend"
    echo "======================================"
    echo ""
    
    cd frontend
    
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
    echo ""
    
    cd ..
fi

# Final instructions
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo ""
echo "1. Backend (API Server):"
echo "   source venv/bin/activate"
echo "   python backend/main.py"
echo "   or: uvicorn backend.main:app --reload"
echo ""

if [ "$SKIP_FRONTEND" != true ]; then
    echo "2. Frontend (React App):"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
fi

echo "3. Access the application:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
if [ "$SKIP_FRONTEND" != true ]; then
    echo "   Frontend: http://localhost:3000"
fi
echo ""

if grep -q "your-secret-key" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠ IMPORTANT: Update the SECRET_KEY in .env file before production use${NC}"
fi

echo ""
echo "For demo account:"
echo "  Username: demo_user"
echo "  Password: demo123"
echo ""
echo "======================================"
