#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and optionally seeds with sample data
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import engine, Base
from backend.models import User, Resume, Interview, Question, Response, PerformanceMetric, AdaptiveProfile
from backend.core.security import get_password_hash


def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - resumes")
    print("  - interviews")
    print("  - questions")
    print("  - responses")
    print("  - performance_metrics")
    print("  - adaptive_profiles")


def seed_demo_user():
    """Create a demo user for testing"""
    from backend.core.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Check if demo user exists
        existing_user = db.query(User).filter(User.email == "demo@interview.com").first()
        
        if existing_user:
            print("\n⚠️  Demo user already exists")
            return
        
        # Create demo user
        demo_user = User(
            email="demo@interview.com",
            username="demo_user",
            hashed_password=get_password_hash("demo123"),
            full_name="Demo User",
            phone="+1234567890",
            is_active=True,
            is_verified=True
        )
        
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        # Create performance metric for demo user
        metric = PerformanceMetric(user_id=demo_user.id)
        db.add(metric)
        
        # Create adaptive profile for demo user
        profile = AdaptiveProfile(user_id=demo_user.id)
        db.add(profile)
        
        db.commit()
        
        print("\n✅ Demo user created successfully!")
        print("\nDemo credentials:")
        print("  Email: demo@interview.com")
        print("  Username: demo_user")
        print("  Password: demo123")
        
    except Exception as e:
        print(f"\n❌ Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("AI Mock Interview Platform - Database Setup")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Ask if user wants to create demo account
    create_demo = input("\nCreate demo user account? (y/n): ").lower().strip()
    
    if create_demo == 'y':
        seed_demo_user()
    
    print("\n" + "=" * 50)
    print("Setup complete! You can now start the application.")
    print("=" * 50)
