"""
Company Questions Dataset Loader

This module loads curated interview questions from top tech companies
(Google, Amazon, Microsoft, Meta, Apple, Netflix, Uber, etc.)
sourced from Glassdoor, LeetCode, InterviewBit, and other platforms.

Questions are categorized by:
- Company source
- Question type (behavioral, technical, hr)
- Difficulty level (easy, medium, hard)
- Tags for better categorization
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import logging

logger = logging.getLogger(__name__)

# Skill-to-question-topic mapping
# Maps user skills (from resume) to relevant question tags/keywords
SKILL_TO_TOPIC_MAP = {
    # Programming Languages -> Programming questions
    'python': ['programming', 'algorithms', 'data-structures', 'python'],
    'java': ['programming', 'algorithms', 'data-structures', 'java'],
    'javascript': ['programming', 'algorithms', 'frontend', 'javascript'],
    'typescript': ['programming', 'algorithms', 'frontend', 'typescript'],
    'c++': ['programming', 'algorithms', 'data-structures', 'c++'],
    'c#': ['programming', 'algorithms', '.net', 'csharp'],
    'go': ['programming', 'algorithms', 'backend', 'golang'],
    'rust': ['programming', 'algorithms', 'systems', 'rust'],
    
    # Frontend -> Frontend/Web questions
    'react': ['frontend', 'javascript', 'web', 'react'],
    'angular': ['frontend', 'javascript', 'web', 'angular'],
    'vue': ['frontend', 'javascript', 'web', 'vue'],
    'html': ['frontend', 'web'],
    'css': ['frontend', 'web', 'css'],
    'nextjs': ['frontend', 'javascript', 'react', 'web'],
    
    # Backend -> Backend/API questions
    'nodejs': ['backend', 'javascript', 'api', 'nodejs'],
    'django': ['backend', 'python', 'api', 'web'],
    'flask': ['backend', 'python', 'api'],
    'fastapi': ['backend', 'python', 'api'],
    'spring': ['backend', 'java', 'api', 'microservices'],
    'express': ['backend', 'javascript', 'api', 'nodejs'],
    
    # Databases -> Database questions
    'sql': ['databases', 'sql', 'data'],
    'mysql': ['databases', 'sql', 'data'],
    'postgresql': ['databases', 'sql', 'data'],
    'mongodb': ['databases', 'nosql', 'data'],
    'redis': ['databases', 'caching', 'data'],
    'elasticsearch': ['databases', 'search', 'data'],
    
    # Cloud/DevOps -> System Design/Infrastructure questions  
    'aws': ['cloud', 'system-design', 'infrastructure', 'aws'],
    'azure': ['cloud', 'system-design', 'infrastructure', 'azure'],
    'gcp': ['cloud', 'system-design', 'infrastructure', 'gcp'],
    'docker': ['devops', 'containers', 'infrastructure', 'docker'],
    'kubernetes': ['devops', 'containers', 'system-design', 'k8s'],
    'ci/cd': ['devops', 'automation', 'infrastructure'],
    'jenkins': ['devops', 'automation', 'ci/cd'],
    'terraform': ['devops', 'infrastructure', 'automation'],
    
    # Data Science/ML -> ML/Data questions
    'machine learning': ['machine-learning', 'data-science', 'algorithms', 'ml'],
    'deep learning': ['machine-learning', 'neural-networks', 'ml'],
    'tensorflow': ['machine-learning', 'deep-learning', 'ml'],
    'pytorch': ['machine-learning', 'deep-learning', 'ml'],
    'pandas': ['data-science', 'python', 'data'],
    'numpy': ['data-science', 'python', 'algorithms'],
    
    # System Design related
    'system design': ['system-design', 'architecture', 'distributed-systems'],
    'microservices': ['system-design', 'architecture', 'microservices'],
    'api': ['api', 'backend', 'system-design'],
    'rest': ['api', 'backend', 'web'],
    'graphql': ['api', 'backend', 'graphql'],
    
    # Data Structures & Algorithms
    'data structures': ['data-structures', 'algorithms', 'programming'],
    'algorithms': ['algorithms', 'data-structures', 'programming'],
    'dsa': ['data-structures', 'algorithms', 'programming'],
    
    # General categories
    'git': ['version-control', 'devops'],
    'linux': ['systems', 'devops', 'infrastructure'],
    'networking': ['networking', 'system-design', 'infrastructure'],
}


class CompanyQuestionsLoader:
    """Load and manage company-specific interview questions"""
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize the loader with the dataset path.
        
        Args:
            dataset_path: Path to the company_questions.json file.
                         If None, uses the default path in data directory.
        """
        if dataset_path is None:
            # Default path relative to project root
            self.dataset_path = Path(__file__).parent.parent.parent / "data" / "company_questions.json"
        else:
            self.dataset_path = Path(dataset_path)
        
        self._data = None
        self._questions_cache = {}
        self._load_dataset()
    
    def _load_dataset(self) -> None:
        """Load the dataset from JSON file"""
        try:
            if self.dataset_path.exists():
                with open(self.dataset_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                logger.info(f"Loaded {self._data['metadata']['total_questions']} company questions")
            else:
                logger.warning(f"Dataset not found at {self.dataset_path}")
                self._data = {"questions": {}, "companies": {}, "metadata": {"total_questions": 0}}
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            self._data = {"questions": {}, "companies": {}, "metadata": {"total_questions": 0}}
    
    @property
    def companies(self) -> Dict:
        """Get company metadata"""
        return self._data.get("companies", {})
    
    @property
    def metadata(self) -> Dict:
        """Get dataset metadata"""
        return self._data.get("metadata", {})
    
    def get_all_questions(self) -> List[Dict]:
        """Get all questions from the dataset"""
        all_questions = []
        for category, questions in self._data.get("questions", {}).items():
            all_questions.extend(questions)
        return all_questions
    
    def get_questions_by_type(self, question_type: str) -> List[Dict]:
        """
        Get questions filtered by type.
        
        Args:
            question_type: One of 'behavioral', 'technical', 'hr', 'general'
        
        Returns:
            List of questions matching the type
        """
        return self._data.get("questions", {}).get(question_type, [])
    
    def get_questions_by_company(self, company: str) -> List[Dict]:
        """
        Get questions from a specific company.
        
        Args:
            company: Company name (e.g., 'google', 'amazon', 'meta')
        
        Returns:
            List of questions from that company
        """
        company_lower = company.lower()
        all_questions = self.get_all_questions()
        return [q for q in all_questions if q.get("company", "").lower() == company_lower]
    
    def get_questions_by_tag(self, tag: str) -> List[Dict]:
        """
        Get questions with a specific tag.
        
        Args:
            tag: Tag to filter by (e.g., 'system-design', 'leadership')
        
        Returns:
            List of questions with that tag
        """
        tag_lower = tag.lower()
        all_questions = self.get_all_questions()
        return [q for q in all_questions if tag_lower in [t.lower() for t in q.get("tags", [])]]
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[Dict]:
        """
        Get questions filtered by difficulty level.
        
        Args:
            difficulty: One of 'easy', 'medium', 'hard'
        
        Returns:
            List of questions matching the difficulty
        """
        all_questions = self.get_all_questions()
        return [q for q in all_questions if q.get("difficulty", "").lower() == difficulty.lower()]
    
    def get_random_questions(
        self,
        count: int = 5,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        companies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        exclude_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get random questions with optional filters.
        
        Args:
            count: Number of questions to return
            question_type: Filter by question type
            difficulty: Filter by difficulty
            companies: Filter by company names
            tags: Filter by tags
            exclude_ids: Question IDs to exclude
        
        Returns:
            List of randomly selected questions
        """
        questions = self.get_all_questions()
        
        # Apply filters
        if question_type:
            questions = [q for q in questions if q.get("type", "") == question_type or 
                        question_type.lower() in q.get("category", "").lower()]
            # Also include from question type category
            type_questions = self.get_questions_by_type(question_type)
            questions = list({q.get("id", ""): q for q in questions + type_questions}.values())
        
        if difficulty:
            questions = [q for q in questions if q.get("difficulty", "").lower() == difficulty.lower()]
        
        if companies:
            companies_lower = [c.lower() for c in companies]
            questions = [q for q in questions if q.get("company", "").lower() in companies_lower or
                        any(c in [t.lower() for t in q.get("tags", [])] for c in companies_lower)]
        
        if tags:
            tags_lower = [t.lower() for t in tags]
            questions = [q for q in questions if 
                        any(t in [tag.lower() for tag in q.get("tags", [])] for t in tags_lower)]
        
        if exclude_ids:
            questions = [q for q in questions if q.get("id") not in exclude_ids]
        
        # Random selection
        if len(questions) <= count:
            return questions
        
        return random.sample(questions, count)
    
    def get_mixed_questions(
        self,
        count: int = 10,
        behavioral_ratio: float = 0.3,
        technical_ratio: float = 0.5,
        hr_ratio: float = 0.2,
        difficulty: str = "medium"
    ) -> List[Dict]:
        """
        Get a mixed set of questions with specified ratios.
        
        Args:
            count: Total number of questions
            behavioral_ratio: Ratio of behavioral questions
            technical_ratio: Ratio of technical questions  
            hr_ratio: Ratio of HR questions
            difficulty: Difficulty level
        
        Returns:
            Mixed list of questions
        """
        behavioral_count = int(count * behavioral_ratio)
        technical_count = int(count * technical_ratio)
        hr_count = count - behavioral_count - technical_count
        
        questions = []
        
        # Get behavioral questions
        behavioral_qs = self.get_random_questions(
            count=behavioral_count,
            question_type="behavioral",
            difficulty=difficulty
        )
        questions.extend(behavioral_qs)
        
        # Get technical questions
        technical_qs = self.get_random_questions(
            count=technical_count,
            question_type="technical",
            difficulty=difficulty,
            exclude_ids=[q.get("id") for q in questions]
        )
        questions.extend(technical_qs)
        
        # Get HR questions
        hr_qs = self.get_random_questions(
            count=hr_count,
            question_type="hr",
            difficulty=difficulty,
            exclude_ids=[q.get("id") for q in questions]
        )
        questions.extend(hr_qs)
        
        # Shuffle the final list
        random.shuffle(questions)
        return questions
    
    def format_question_for_interview(self, question: Dict) -> Dict:
        """
        Format a question for the interview system.
        
        Transforms the dataset format to match the existing question generator output.
        
        Args:
            question: Question from the dataset
        
        Returns:
            Formatted question dict compatible with interview system
        """
        company_info = self.companies.get(question.get("company", ""), {})
        
        return {
            "text": question.get("text", ""),
            "type": question.get("type", "general"),
            "difficulty": question.get("difficulty", "medium"),
            "category": question.get("category", "General"),
            "keywords": question.get("keywords", []),
            "tags": question.get("tags", []),
            "company": question.get("company", ""),
            "company_name": company_info.get("name", ""),
            "company_logo": company_info.get("logo", ""),
            "company_color": company_info.get("color", "#888888"),
            "source": question.get("source", ""),
            "from_dataset": True  # Flag to identify dataset questions
        }
    
    def get_formatted_questions(
        self,
        count: int = 5,
        **filters
    ) -> List[Dict]:
        """
        Get formatted questions ready for the interview system.
        
        Args:
            count: Number of questions
            **filters: Additional filters passed to get_random_questions
        
        Returns:
            List of formatted questions
        """
        questions = self.get_random_questions(count=count, **filters)
        return [self.format_question_for_interview(q) for q in questions]
    
    def get_available_companies(self) -> List[str]:
        """Get list of available company names"""
        return list(self.companies.keys())
    
    def get_available_tags(self) -> List[str]:
        """Get list of all unique tags in the dataset"""
        all_tags = set()
        for question in self.get_all_questions():
            all_tags.update(question.get("tags", []))
        return sorted(list(all_tags))
    
    def get_question_stats(self) -> Dict:
        """Get statistics about the dataset"""
        all_questions = self.get_all_questions()
        
        stats = {
            "total": len(all_questions),
            "by_type": {},
            "by_difficulty": {"easy": 0, "medium": 0, "hard": 0},
            "by_company": {},
            "sources": self.metadata.get("sources", [])
        }
        
        for q in all_questions:
            # By type
            q_type = q.get("type", "general")
            stats["by_type"][q_type] = stats["by_type"].get(q_type, 0) + 1
            
            # By difficulty
            difficulty = q.get("difficulty", "medium")
            stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1
            
            # By company
            company = q.get("company", "unknown")
            stats["by_company"][company] = stats["by_company"].get(company, 0) + 1
        
        return stats
    
    def _skills_to_topics(self, skills: List[str]) -> Set[str]:
        """Convert user skills to relevant question topics/tags.
        
        Args:
            skills: List of user skills (e.g., ['Python', 'React', 'AWS'])
        
        Returns:
            Set of relevant topics/tags for question matching
        """
        topics = set()
        skills_lower = [s.lower().strip() for s in skills if s]
        
        for skill in skills_lower:
            # Direct match
            if skill in SKILL_TO_TOPIC_MAP:
                topics.update(SKILL_TO_TOPIC_MAP[skill])
            else:
                # Partial match (e.g., "python3" matches "python")
                for key, values in SKILL_TO_TOPIC_MAP.items():
                    if key in skill or skill in key:
                        topics.update(values)
                        break
        
        return topics
    
    def get_questions_by_skills(
        self,
        skills: List[str],
        count: int = 5,
        question_type: str = "technical",
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """Get questions matched to user skills.
        
        This is the key method for skill-based question selection.
        Maps user skills to relevant topics and finds matching questions.
        
        Args:
            skills: User's skills from resume
            count: Number of questions to return
            question_type: Type of questions (technical, behavioral, hr)
            difficulty: Optional difficulty filter
        
        Returns:
            List of questions relevant to the user's skills
        """
        if not skills:
            # No skills provided, return random questions
            return self.get_formatted_questions(
                count=count,
                question_type=question_type,
                difficulty=difficulty
            )
        
        # Convert skills to topics
        topics = self._skills_to_topics(skills)
        logger.info(f"[Skills->Topics] Skills: {skills[:5]}... -> Topics: {list(topics)[:10]}...")
        
        # Get all questions of the requested type
        type_questions = self.get_questions_by_type(question_type)
        
        # Apply difficulty filter if provided
        if difficulty:
            type_questions = [q for q in type_questions 
                           if q.get("difficulty", "").lower() == difficulty.lower()]
        
        # Score questions by topic relevance
        scored_questions = []
        for q in type_questions:
            score = 0
            q_tags = set(t.lower() for t in q.get("tags", []))
            q_keywords = set(k.lower() for k in q.get("keywords", []))
            q_category = q.get("category", "").lower()
            
            # Check tags
            for topic in topics:
                if topic in q_tags:
                    score += 3  # High weight for tag match
                if topic in q_keywords:
                    score += 2  # Medium weight for keyword match
                if topic in q_category:
                    score += 1  # Low weight for category match
            
            if score > 0:
                scored_questions.append((score, q))
        
        # Shuffle before sorting to randomize among same-score questions
        random.shuffle(scored_questions)
        
        # Sort by score (highest first) - stable sort preserves shuffle order for ties
        scored_questions.sort(key=lambda x: x[0], reverse=True)
        
        # Take more than needed, then randomly select from top matches
        # This adds variety while still prioritizing relevant questions
        top_pool_size = min(len(scored_questions), count * 3)
        top_pool = [q for _, q in scored_questions[:top_pool_size]]
        
        if len(top_pool) > count:
            # Randomly select from top pool for variety
            random.shuffle(top_pool)
            matched_questions = top_pool[:count]
        else:
            matched_questions = top_pool
        
        logger.info(f"[Skill Matching] Found {len(matched_questions)} questions matching skills (pool: {len(top_pool)})")
        
        # If not enough skill-matched questions, fill with random
        if len(matched_questions) < count:
            remaining = count - len(matched_questions)
            matched_ids = {q.get("id") for q in matched_questions}
            
            # Get random questions not already selected
            filler = [q for q in type_questions if q.get("id") not in matched_ids]
            if filler:
                random.shuffle(filler)
                matched_questions.extend(filler[:remaining])
        
        # Format questions for interview
        return [self.format_question_for_interview(q) for q in matched_questions]


# Global instance for easy import
_loader_instance = None


def get_questions_loader() -> CompanyQuestionsLoader:
    """Get or create the global questions loader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = CompanyQuestionsLoader()
    return _loader_instance


# Convenience functions
def get_company_questions(
    count: int = 5,
    question_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    companies: Optional[List[str]] = None
) -> List[Dict]:
    """
    Convenience function to get formatted company questions.
    
    Args:
        count: Number of questions
        question_type: Question type filter
        difficulty: Difficulty filter
        companies: Company filter
    
    Returns:
        List of formatted questions
    """
    loader = get_questions_loader()
    return loader.get_formatted_questions(
        count=count,
        question_type=question_type,
        difficulty=difficulty,
        companies=companies
    )
