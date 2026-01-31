# Test Configuration
import pytest
import sys
from pathlib import Path

# Add parent directory to path (OS-agnostic)
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.core.database import Base, engine
from sqlalchemy.orm import sessionmaker

# Create test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create test client"""
    from fastapi.testclient import TestClient
    from backend.main import app
    
    return TestClient(app)
