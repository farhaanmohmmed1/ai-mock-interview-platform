"""
Vercel serverless entrypoint for FastAPI application.
This file exports the FastAPI app for Vercel deployment.
"""

import sys
import os

# Set environment variable to indicate Vercel deployment (lightweight mode)
os.environ["VERCEL_DEPLOYMENT"] = "true"

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app from the backend module
from backend.main import app

# Vercel looks for an 'app' variable
# The app is already imported above
