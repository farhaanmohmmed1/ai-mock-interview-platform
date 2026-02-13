#!/usr/bin/env python3
"""
Test script to demonstrate the company questions integration.
Shows how questions are generated with tags from different tech companies.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def test_company_questions_loader():
    """Test the company questions loader"""
    print("=" * 70)
    print("Testing Company Questions Loader")
    print("=" * 70)
    print()
    
    from ai_modules.nlp.company_questions_loader import get_questions_loader
    
    loader = get_questions_loader()
    
    # Get stats
    stats = loader.get_question_stats()
    print(f"📊 Dataset Statistics:")
    print(f"   Total Questions: {stats['total']}")
    print(f"   Sources: {', '.join(stats['sources'])}")
    print()
    print(f"   By Type:")
    for q_type, count in stats['by_type'].items():
        print(f"      - {q_type}: {count}")
    print()
    print(f"   By Difficulty:")
    for diff, count in stats['by_difficulty'].items():
        print(f"      - {diff}: {count}")
    print()
    print(f"   By Company:")
    for company, count in stats['by_company'].items():
        print(f"      - {company}: {count}")
    print()
    
    # Show available companies
    print(f"🏢 Available Companies:")
    for company_id, company_info in loader.companies.items():
        print(f"   {company_info.get('logo', '')} {company_info.get('name', company_id)}")
    print()
    
    # Show available tags
    tags = loader.get_available_tags()
    print(f"🏷️  Available Tags ({len(tags)}):")
    print(f"   {', '.join(tags[:20])}...")
    print()


def test_question_generation():
    """Test question generation with company questions"""
    print("=" * 70)
    print("Testing Question Generation with Company Questions")
    print("=" * 70)
    print()
    
    from ai_modules.nlp.question_generator import QuestionGenerator
    
    generator = QuestionGenerator()
    
    # Test different interview types
    test_cases = [
        ("general", "medium"),
        ("technical", "medium"),
        ("hr", "easy"),
    ]
    
    for interview_type, difficulty in test_cases:
        print(f"\n{'='*60}")
        print(f"📝 {interview_type.upper()} Interview - {difficulty.title()} Difficulty")
        print(f"{'='*60}\n")
        
        questions = generator.generate_questions(
            interview_type=interview_type,
            difficulty=difficulty
        )
        
        for i, q in enumerate(questions, 1):
            print(f"Question {i}:")
            print(f"   📌 {q['text'][:100]}{'...' if len(q['text']) > 100 else ''}")
            print(f"   Type: {q.get('type', 'N/A')}")
            print(f"   Difficulty: {q.get('difficulty', 'N/A')}")
            print(f"   Category: {q.get('category', 'N/A')}")
            
            # Tags
            tags = q.get('tags', [])
            if tags:
                print(f"   🏷️  Tags: {', '.join(tags)}")
            
            # Company info
            if q.get('company'):
                print(f"   🏢 Company: {q.get('company_name', q.get('company'))}")
                
            # Source
            if q.get('source'):
                print(f"   📖 Source: {q.get('source')}")
            
            # Dataset flag
            if q.get('from_dataset'):
                print(f"   ✅ From Company Dataset")
            else:
                print(f"   🤖 AI Generated")
            
            print()


def test_formatted_output():
    """Test formatted JSON output"""
    print("=" * 70)
    print("Sample JSON Output for Frontend")
    print("=" * 70)
    print()
    
    from ai_modules.nlp.question_generator import QuestionGenerator
    
    generator = QuestionGenerator()
    
    questions = generator.generate_questions(
        interview_type="technical",
        difficulty="medium"
    )
    
    # Show first 3 questions as JSON
    sample_questions = questions[:3]
    print(json.dumps(sample_questions, indent=2))


if __name__ == "__main__":
    test_company_questions_loader()
    print("\n" + "="*70 + "\n")
    test_question_generation()
    print("\n" + "="*70 + "\n")
    test_formatted_output()
