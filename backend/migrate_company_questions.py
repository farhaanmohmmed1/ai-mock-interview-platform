#!/usr/bin/env python3
"""
Migration script to add new columns to the questions table for company questions support.

This script adds the following columns:
- tags: JSON array of tags (e.g., ["google", "system-design", "medium"])
- company: Source company code (e.g., "google", "amazon")
- company_name: Display name (e.g., "Google", "Amazon")
- source: Data source (e.g., "Glassdoor", "LeetCode", "AI Generated")
- from_dataset: Boolean flag indicating if question is from company dataset

Run this script after updating the models.py file.
"""

import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import text
from backend.core.database import engine


def migrate_questions_table():
    """Add new columns to questions table for company questions support"""
    
    columns_to_add = [
        ("tags", "TEXT"),  # JSON stored as TEXT for SQLite compatibility
        ("company", "VARCHAR(50)"),
        ("company_name", "VARCHAR(100)"),
        ("source", "VARCHAR(100)"),
        ("from_dataset", "BOOLEAN DEFAULT FALSE")
    ]
    
    with engine.connect() as conn:
        for column_name, column_type in columns_to_add:
            try:
                # Check if column exists (SQLite syntax)
                result = conn.execute(text(f"PRAGMA table_info(questions)"))
                columns = [row[1] for row in result.fetchall()]
                
                if column_name not in columns:
                    print(f"Adding column '{column_name}' to questions table...")
                    conn.execute(text(f"ALTER TABLE questions ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                    print(f"✅ Column '{column_name}' added successfully")
                else:
                    print(f"⚠️  Column '{column_name}' already exists, skipping")
                    
            except Exception as e:
                print(f"❌ Error adding column '{column_name}': {e}")
                # Try PostgreSQL syntax
                try:
                    conn.execute(text(f"ALTER TABLE questions ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))
                    conn.commit()
                    print(f"✅ Column '{column_name}' added successfully (PostgreSQL)")
                except Exception as e2:
                    print(f"❌ Failed with both SQLite and PostgreSQL syntax: {e2}")


def verify_migration():
    """Verify that the migration was successful"""
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(questions)"))
            columns = [row[1] for row in result.fetchall()]
            
            expected_columns = ['tags', 'company', 'company_name', 'source', 'from_dataset']
            missing = [col for col in expected_columns if col not in columns]
            
            if missing:
                print(f"\n⚠️  Missing columns: {missing}")
                return False
            else:
                print("\n✅ All new columns are present in the questions table")
                print(f"   Columns: {columns}")
                return True
                
        except Exception as e:
            print(f"❌ Error verifying migration: {e}")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add company questions support to questions table")
    print("=" * 60)
    print()
    
    migrate_questions_table()
    print()
    verify_migration()
    
    print()
    print("=" * 60)
    print("Migration complete!")
    print("=" * 60)
