"""
UPSC Questions Loader

Loads and manages the UPSC Civil Services Interview Question Bank.
Provides filtering by category, difficulty, and prevents duplicate questions.
"""

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class UPSCQuestionsLoader:
    """Load and manage UPSC interview questions from the JSON dataset."""
    
    def __init__(self, questions_file: str = None):
        """Initialize the loader with the questions file path."""
        if questions_file is None:
            # Default path relative to this file
            base_path = Path(__file__).parent.parent.parent
            questions_file = base_path / "data" / "upsc_questions.json"
        
        self.questions_file = Path(questions_file)
        self.questions: List[Dict] = []
        self.metadata: Dict = {}
        self.categories: Set[str] = set()
        self._used_question_ids: Set[str] = set()  # Track used questions to avoid duplicates
        
        self._load_questions()
    
    def _load_questions(self):
        """Load questions from the JSON file."""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = data.get("metadata", {})
            self.questions = data.get("questions", [])
            
            # Extract unique categories
            self.categories = set(q.get("category", "") for q in self.questions)
            
            logger.info(f"Loaded {len(self.questions)} UPSC questions from {self.questions_file}")
            logger.info(f"Categories: {sorted(self.categories)}")
            
        except FileNotFoundError:
            logger.error(f"UPSC questions file not found: {self.questions_file}")
            self.questions = []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing UPSC questions JSON: {e}")
            self.questions = []
    
    def get_questions(
        self,
        count: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        exclude_ids: Optional[Set[str]] = None
    ) -> List[Dict]:
        """
        Get questions filtered by category and difficulty.
        
        Args:
            count: Number of questions to return
            category: Filter by category (e.g., 'ethics_integrity', 'indian_polity')
            difficulty: Filter by difficulty ('easy', 'medium', 'hard')
            exclude_ids: Set of question IDs to exclude (already asked)
        
        Returns:
            List of question dictionaries
        """
        filtered = self.questions.copy()
        
        # Apply filters
        if category:
            filtered = [q for q in filtered if q.get("category", "").lower() == category.lower()]
        
        if difficulty:
            filtered = [q for q in filtered if q.get("difficulty", "").lower() == difficulty.lower()]
        
        # Exclude already used questions
        if exclude_ids:
            filtered = [q for q in filtered if q.get("id") not in exclude_ids]
        
        # Exclude questions used in this session
        filtered = [q for q in filtered if q.get("id") not in self._used_question_ids]
        
        # Shuffle for variety
        random.shuffle(filtered)
        
        # Select requested count
        selected = filtered[:count]
        
        # Track used questions
        for q in selected:
            if q.get("id"):
                self._used_question_ids.add(q["id"])
        
        return selected
    
    def get_questions_by_categories(
        self,
        categories: List[str],
        count_per_category: int = 2,
        difficulty: Optional[str] = None,
        exclude_ids: Optional[Set[str]] = None
    ) -> List[Dict]:
        """
        Get a balanced mix of questions from multiple categories.
        
        Args:
            categories: List of categories to include
            count_per_category: How many questions per category
            difficulty: Filter by difficulty
            exclude_ids: Set of question IDs to exclude
        
        Returns:
            List of question dictionaries
        """
        all_questions = []
        
        for category in categories:
            category_qs = self.get_questions(
                count=count_per_category,
                category=category,
                difficulty=difficulty,
                exclude_ids=exclude_ids
            )
            all_questions.extend(category_qs)
        
        # Shuffle the combined list
        random.shuffle(all_questions)
        
        return all_questions
    
    def get_formatted_questions(
        self,
        count: int = 10,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        exclude_ids: Optional[Set[str]] = None
    ) -> List[Dict]:
        """
        Get questions formatted for the interview system.
        
        Returns questions in the same format as company questions,
        compatible with the question generator.
        """
        questions = self.get_questions(
            count=count,
            category=category,
            difficulty=difficulty,
            exclude_ids=exclude_ids
        )
        
        formatted = []
        for q in questions:
            formatted.append({
                "text": q["text"],
                "type": "upsc",
                "category": q.get("category", "general"),
                "difficulty": q.get("difficulty", "medium"),
                "keywords": q.get("keywords", []),
                "tags": [q.get("category", "upsc"), q.get("difficulty", "medium")],
                "source": "UPSC Question Bank",
                "company": "",  # Not applicable for UPSC
                "company_name": "",
                "from_dataset": True,
                "follow_up": q.get("follow_up", ""),
                "question_id": q.get("id", "")
            })
        
        return formatted
    
    def get_mixed_difficulty_questions(
        self,
        total_count: int = 10,
        categories: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get a mix of easy, medium, and hard questions.
        
        Distribution: ~30% easy, ~50% medium, ~20% hard
        """
        easy_count = max(1, int(total_count * 0.3))
        medium_count = max(1, int(total_count * 0.5))
        hard_count = total_count - easy_count - medium_count
        
        all_questions = []
        
        for difficulty, count in [("easy", easy_count), ("medium", medium_count), ("hard", hard_count)]:
            if categories:
                # Get from specified categories
                per_cat = max(1, count // len(categories))
                for cat in categories:
                    qs = self.get_formatted_questions(
                        count=per_cat,
                        category=cat,
                        difficulty=difficulty
                    )
                    all_questions.extend(qs)
            else:
                # Get from all categories
                qs = self.get_formatted_questions(
                    count=count,
                    difficulty=difficulty
                )
                all_questions.extend(qs)
        
        random.shuffle(all_questions)
        return all_questions[:total_count]
    
    def reset_used_questions(self):
        """Reset the tracking of used questions for a new session."""
        self._used_question_ids.clear()
    
    def get_available_categories(self) -> List[str]:
        """Get list of available categories."""
        return sorted(list(self.categories))
    
    def get_question_count(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> int:
        """Get count of available questions matching criteria."""
        filtered = self.questions.copy()
        
        if category:
            filtered = [q for q in filtered if q.get("category", "").lower() == category.lower()]
        
        if difficulty:
            filtered = [q for q in filtered if q.get("difficulty", "").lower() == difficulty.lower()]
        
        return len(filtered)


# Singleton instance
_upsc_loader_instance = None


def get_upsc_questions_loader() -> UPSCQuestionsLoader:
    """Get the singleton UPSC questions loader instance."""
    global _upsc_loader_instance
    if _upsc_loader_instance is None:
        _upsc_loader_instance = UPSCQuestionsLoader()
    return _upsc_loader_instance
