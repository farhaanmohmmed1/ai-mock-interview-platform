import random
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from backend.models import Interview, Response


class QuestionGenerator:
    """Generate interview questions based on type and context"""
    
    def __init__(self):
        self.question_bank = self._initialize_question_bank()
        self.upsc_question_bank = self._initialize_upsc_questions()
    
    def _initialize_upsc_questions(self) -> Dict:
        """Initialize UPSC/Civil Services style questions"""
        return {
            "current_affairs": {
                "easy": [
                    {"text": "What do you understand by sustainable development? Why is it important for India?", "type": "upsc", "category": "current_affairs", "keywords": ["sustainability", "environment", "development"]},
                    {"text": "What are the major initiatives taken by the government for digital India?", "type": "upsc", "category": "current_affairs", "keywords": ["digital", "technology", "governance"]},
                    {"text": "Discuss the importance of renewable energy in India's energy security.", "type": "upsc", "category": "current_affairs", "keywords": ["renewable", "energy", "security"]},
                ],
                "medium": [
                    {"text": "Analyze the impact of climate change on Indian agriculture and suggest measures to address it.", "type": "upsc", "category": "current_affairs", "keywords": ["climate", "agriculture", "adaptation"]},
                    {"text": "What are the challenges faced by India in achieving its Sustainable Development Goals (SDGs)?", "type": "upsc", "category": "current_affairs", "keywords": ["SDG", "development", "challenges"]},
                    {"text": "Discuss India's foreign policy challenges in the current geopolitical scenario.", "type": "upsc", "category": "current_affairs", "keywords": ["foreign policy", "diplomacy", "geopolitics"]},
                ],
                "hard": [
                    {"text": "Critically analyze India's neighborhood first policy and its effectiveness.", "type": "upsc", "category": "current_affairs", "keywords": ["foreign policy", "neighborhood", "diplomacy"]},
                    {"text": "Examine the role of technology in transforming governance. What are the ethical concerns?", "type": "upsc", "category": "current_affairs", "keywords": ["technology", "governance", "ethics"]},
                ]
            },
            "ethics_integrity": {
                "easy": [
                    {"text": "What do you understand by ethics in public administration?", "type": "upsc", "category": "ethics", "keywords": ["ethics", "administration", "values"]},
                    {"text": "What are the qualities you think a civil servant should possess?", "type": "upsc", "category": "ethics", "keywords": ["qualities", "civil servant", "integrity"]},
                    {"text": "Define integrity and explain its importance in public service.", "type": "upsc", "category": "ethics", "keywords": ["integrity", "honesty", "public service"]},
                ],
                "medium": [
                    {"text": "You are posted as a District Collector. A powerful politician asks you to transfer a file favorably. How would you handle this?", "type": "upsc", "category": "ethics", "keywords": ["ethics", "pressure", "decision-making"]},
                    {"text": "Discuss the role of conscience in ethical decision-making with examples.", "type": "upsc", "category": "ethics", "keywords": ["conscience", "ethics", "morality"]},
                    {"text": "What are the ethical dilemmas faced by civil servants? How can they be resolved?", "type": "upsc", "category": "ethics", "keywords": ["dilemma", "ethics", "resolution"]},
                ],
                "hard": [
                    {"text": "A subordinate reports corruption by your superior officer who is well-connected. What would you do?", "type": "upsc", "category": "ethics", "keywords": ["corruption", "whistleblowing", "integrity"]},
                    {"text": "Discuss the conflict between following rules and achieving outcomes in administration.", "type": "upsc", "category": "ethics", "keywords": ["rules", "outcomes", "governance"]},
                ]
            },
            "personality": {
                "easy": [
                    {"text": "Tell us about yourself and what motivated you to join civil services.", "type": "upsc", "category": "personality", "keywords": ["motivation", "background", "aspiration"]},
                    {"text": "What are your hobbies and how do they contribute to your personality?", "type": "upsc", "category": "personality", "keywords": ["hobbies", "personality", "interests"]},
                    {"text": "Who has been your role model and why?", "type": "upsc", "category": "personality", "keywords": ["role model", "inspiration", "values"]},
                ],
                "medium": [
                    {"text": "What would you do if you were posted in a conflict-affected area?", "type": "upsc", "category": "personality", "keywords": ["conflict", "administration", "challenges"]},
                    {"text": "How would you handle a situation where your personal beliefs conflict with your official duties?", "type": "upsc", "category": "personality", "keywords": ["beliefs", "duty", "conflict"]},
                    {"text": "Describe a challenging situation you faced and how you overcame it.", "type": "upsc", "category": "personality", "keywords": ["challenge", "resilience", "problem-solving"]},
                ],
                "hard": [
                    {"text": "If you had to implement an unpopular but necessary policy, how would you gain public support?", "type": "upsc", "category": "personality", "keywords": ["policy", "communication", "leadership"]},
                    {"text": "What are your views on the role of bureaucracy in a democracy?", "type": "upsc", "category": "personality", "keywords": ["bureaucracy", "democracy", "governance"]},
                ]
            },
            "administrative": {
                "easy": [
                    {"text": "What do you understand by good governance?", "type": "upsc", "category": "administrative", "keywords": ["governance", "administration", "principles"]},
                    {"text": "What is the role of a District Magistrate?", "type": "upsc", "category": "administrative", "keywords": ["DM", "administration", "responsibilities"]},
                ],
                "medium": [
                    {"text": "How would you ensure effective implementation of a welfare scheme at the grassroots level?", "type": "upsc", "category": "administrative", "keywords": ["implementation", "welfare", "grassroots"]},
                    {"text": "Discuss the importance of coordination between different government departments.", "type": "upsc", "category": "administrative", "keywords": ["coordination", "governance", "efficiency"]},
                    {"text": "How can e-governance improve public service delivery in rural areas?", "type": "upsc", "category": "administrative", "keywords": ["e-governance", "rural", "technology"]},
                ],
                "hard": [
                    {"text": "During a natural disaster, you have limited resources. How would you prioritize relief distribution?", "type": "upsc", "category": "administrative", "keywords": ["disaster", "prioritization", "management"]},
                    {"text": "Propose reforms for improving efficiency in public administration.", "type": "upsc", "category": "administrative", "keywords": ["reforms", "efficiency", "administration"]},
                ]
            },
            "opinion": {
                "easy": [
                    {"text": "What are your views on reservation policy in India?", "type": "upsc", "category": "opinion", "keywords": ["reservation", "policy", "equality"]},
                    {"text": "Should social media be regulated? Share your opinion.", "type": "upsc", "category": "opinion", "keywords": ["social media", "regulation", "freedom"]},
                ],
                "medium": [
                    {"text": "What is your opinion on the balance between development and environmental conservation?",  "type": "upsc", "category": "opinion", "keywords": ["development", "environment", "balance"]},
                    {"text": "Do you think capital punishment should be abolished? Justify your view.", "type": "upsc", "category": "opinion", "keywords": ["capital punishment", "justice", "ethics"]},
                    {"text": "What are your views on One Nation One Election?", "type": "upsc", "category": "opinion", "keywords": ["election", "democracy", "reform"]},
                ],
                "hard": [
                    {"text": "Critically examine the statement: 'Democracy is the best form of government'.", "type": "upsc", "category": "opinion", "keywords": ["democracy", "government", "analysis"]},
                    {"text": "Should there be a uniform civil code in India? Present arguments for and against.", "type": "upsc", "category": "opinion", "keywords": ["uniform civil code", "law", "secularism"]},
                ]
            }
        }
    
    def _initialize_question_bank(self) -> Dict:
        """Initialize question bank with different categories"""
        return {
            "general": {
                "easy": [
                    {"text": "Tell me about yourself.", "type": "behavioral", "keywords": ["background", "experience", "skills"]},
                    {"text": "What are your greatest strengths?", "type": "behavioral", "keywords": ["skills", "abilities", "strengths"]},
                    {"text": "Why do you want to work here?", "type": "behavioral", "keywords": ["motivation", "company", "interest"]},
                    {"text": "Where do you see yourself in 5 years?", "type": "behavioral", "keywords": ["goals", "career", "future"]},
                    {"text": "What makes you a good fit for this role?", "type": "behavioral", "keywords": ["fit", "qualifications", "skills"]},
                ],
                "medium": [
                    {"text": "Describe a challenging situation you faced and how you handled it.", "type": "situational", "keywords": ["challenge", "problem-solving", "resolution"]},
                    {"text": "How do you handle working under pressure?", "type": "behavioral", "keywords": ["stress", "pressure", "coping"]},
                    {"text": "Describe a time when you had to work with a difficult team member.", "type": "situational", "keywords": ["teamwork", "conflict", "resolution"]},
                    {"text": "What is your biggest weakness and how are you working on it?", "type": "behavioral", "keywords": ["weakness", "improvement", "self-awareness"]},
                    {"text": "Tell me about a time you failed and what you learned from it.", "type": "situational", "keywords": ["failure", "learning", "growth"]},
                ],
                "hard": [
                    {"text": "Describe a situation where you had to make a decision with incomplete information.", "type": "situational", "keywords": ["decision-making", "uncertainty", "judgment"]},
                    {"text": "How do you prioritize when you have multiple urgent tasks?", "type": "behavioral", "keywords": ["prioritization", "time management", "organization"]},
                    {"text": "Tell me about a time you had to convince someone to see things your way.", "type": "situational", "keywords": ["persuasion", "communication", "influence"]},
                ]
            },
            "technical": {
                "programming": {
                    "python": [
                        {"text": "Explain the difference between lists and tuples in Python.", "type": "technical", "difficulty": "easy", "keywords": ["mutable", "immutable", "data structures"]},
                        {"text": "What are decorators in Python and how do you use them?", "type": "technical", "difficulty": "medium", "keywords": ["decorator", "function", "wrapper"]},
                        {"text": "Explain the Global Interpreter Lock (GIL) in Python.", "type": "technical", "difficulty": "hard", "keywords": ["GIL", "threading", "concurrency"]},
                        {"text": "How do you manage memory in Python?", "type": "technical", "difficulty": "medium", "keywords": ["garbage collection", "memory", "references"]},
                    ],
                    "java": [
                        {"text": "What is the difference between abstract classes and interfaces in Java?", "type": "technical", "difficulty": "easy", "keywords": ["abstract", "interface", "inheritance"]},
                        {"text": "Explain the concept of multithreading in Java.", "type": "technical", "difficulty": "medium", "keywords": ["threads", "concurrency", "synchronization"]},
                        {"text": "What are the different types of memory areas in JVM?", "type": "technical", "difficulty": "hard", "keywords": ["heap", "stack", "JVM", "memory"]},
                    ],
                    "javascript": [
                        {"text": "Explain closures in JavaScript.", "type": "technical", "difficulty": "medium", "keywords": ["closure", "scope", "function"]},
                        {"text": "What is the difference between == and === in JavaScript?", "type": "technical", "difficulty": "easy", "keywords": ["equality", "comparison", "type coercion"]},
                        {"text": "Explain the event loop in JavaScript.", "type": "technical", "difficulty": "hard", "keywords": ["event loop", "async", "callback"]},
                    ]
                },
                "algorithms": [
                    {"text": "Explain the difference between linear and binary search.", "type": "technical", "difficulty": "easy", "keywords": ["search", "complexity", "algorithm"]},
                    {"text": "How would you detect a cycle in a linked list?", "type": "technical", "difficulty": "medium", "keywords": ["cycle", "linked list", "two pointers"]},
                    {"text": "Explain different sorting algorithms and their time complexities.", "type": "technical", "difficulty": "medium", "keywords": ["sorting", "time complexity", "algorithms"]},
                    {"text": "Describe dynamic programming and when to use it.", "type": "technical", "difficulty": "hard", "keywords": ["dynamic programming", "optimization", "memoization"]},
                ],
                "databases": [
                    {"text": "What is the difference between SQL and NoSQL databases?", "type": "technical", "difficulty": "easy", "keywords": ["SQL", "NoSQL", "database"]},
                    {"text": "Explain database normalization and its forms.", "type": "technical", "difficulty": "medium", "keywords": ["normalization", "1NF", "2NF", "3NF"]},
                    {"text": "What is database indexing and how does it improve performance?", "type": "technical", "difficulty": "medium", "keywords": ["indexing", "performance", "optimization"]},
                    {"text": "Explain ACID properties in databases.", "type": "technical", "difficulty": "medium", "keywords": ["ACID", "transactions", "consistency"]},
                ],
                "system_design": [
                    {"text": "How would you design a URL shortening service like bit.ly?", "type": "technical", "difficulty": "hard", "keywords": ["system design", "scalability", "architecture"]},
                    {"text": "Explain the concept of load balancing.", "type": "technical", "difficulty": "medium", "keywords": ["load balancing", "distribution", "scalability"]},
                    {"text": "What is caching and when would you use it?", "type": "technical", "difficulty": "medium", "keywords": ["caching", "performance", "Redis"]},
                ]
            },
            "hr": {
                "easy": [
                    {"text": "What attracted you to apply for this position?", "type": "hr", "keywords": ["motivation", "interest", "position"]},
                    {"text": "How would your colleagues describe you?", "type": "hr", "keywords": ["personality", "teamwork", "perception"]},
                    {"text": "What do you know about our company?", "type": "hr", "keywords": ["research", "company", "knowledge"]},
                    {"text": "What are your salary expectations?", "type": "hr", "keywords": ["salary", "compensation", "expectations"]},
                ],
                "medium": [
                    {"text": "Why are you leaving your current job?", "type": "hr", "keywords": ["career change", "motivation", "growth"]},
                    {"text": "How do you handle feedback and criticism?", "type": "hr", "keywords": ["feedback", "growth mindset", "adaptation"]},
                    {"text": "Describe your ideal work environment.", "type": "hr", "keywords": ["environment", "culture", "preferences"]},
                    {"text": "What are your long-term career goals?", "type": "hr", "keywords": ["career", "goals", "ambition"]},
                    {"text": "How do you maintain work-life balance?", "type": "hr", "keywords": ["balance", "well-being", "management"]},
                ],
                "hard": [
                    {"text": "Tell me about a time you disagreed with management and how you handled it.", "type": "hr", "keywords": ["conflict", "management", "communication"]},
                    {"text": "How would you handle an ethical dilemma at work?", "type": "hr", "keywords": ["ethics", "integrity", "decision-making"]},
                    {"text": "What would you do if you were asked to work on something outside your job description?", "type": "hr", "keywords": ["flexibility", "boundaries", "adaptation"]},
                ]
            }
        }
    
    def generate_questions(
        self,
        interview_type: str,
        difficulty: str,
        interview_mode: str = "standard",
        resume_data: Optional[Dict] = None,
        skills: Optional[List[str]] = None,
        user_id: int = None,
        db: Session = None
    ) -> List[Dict]:
        """Generate questions for interview"""
        questions = []
        
        # UPSC mode has different question generation
        if interview_mode == "upsc":
            questions = self._generate_upsc_questions(difficulty)
        elif interview_type == "general":
            questions = self._generate_general_questions(difficulty)
        elif interview_type == "technical":
            questions = self._generate_technical_questions(difficulty, skills, resume_data)
        elif interview_type == "hr":
            questions = self._generate_hr_questions(difficulty)
        
        # Add adaptive questions based on past performance if available
        if user_id and db and interview_mode != "upsc":
            adaptive_questions = self._get_adaptive_questions(user_id, interview_type, db)
            questions.extend(adaptive_questions)
        
        # Apply rule-based difficulty classification
        questions = self._classify_difficulty(questions)
        
        return questions
    
    def _classify_difficulty(self, questions: List[Dict]) -> List[Dict]:
        """Rule-based difficulty classification"""
        for q in questions:
            text = q["text"].lower()
            
            # Easy indicators
            easy_indicators = ["what is", "define", "tell me about", "what do you understand", "what are", "who is", "describe"]
            # Medium indicators  
            medium_indicators = ["how would you", "discuss", "explain", "compare", "analyze", "what would you do"]
            # Hard indicators
            hard_indicators = ["critically", "evaluate", "propose", "examine", "justify", "if you had to", "during a crisis"]
            
            # Count indicators
            easy_count = sum(1 for ind in easy_indicators if ind in text)
            medium_count = sum(1 for ind in medium_indicators if ind in text)
            hard_count = sum(1 for ind in hard_indicators if ind in text)
            
            # Classify based on dominant indicator
            if hard_count > 0 or len(text) > 200:
                q["difficulty"] = "hard"
            elif medium_count > easy_count:
                q["difficulty"] = "medium"
            elif easy_count > 0:
                q["difficulty"] = "easy"
            # Keep existing difficulty if already set and no clear indicator
        
        return questions
    
    def _generate_upsc_questions(self, difficulty: str) -> List[Dict]:
        """Generate UPSC style interview questions"""
        questions = []
        categories = ["current_affairs", "ethics_integrity", "personality", "administrative", "opinion"]
        
        for category in categories:
            bank = self.upsc_question_bank.get(category, {})
            
            if difficulty == "easy":
                # More easy questions
                if "easy" in bank:
                    questions.extend(random.sample(bank["easy"], min(2, len(bank["easy"]))))
                if "medium" in bank:
                    questions.extend(random.sample(bank["medium"], min(1, len(bank["medium"]))))
            elif difficulty == "medium":
                # Balanced mix
                if "easy" in bank:
                    questions.extend(random.sample(bank["easy"], min(1, len(bank["easy"]))))
                if "medium" in bank:
                    questions.extend(random.sample(bank["medium"], min(2, len(bank["medium"]))))
                if "hard" in bank:
                    questions.extend(random.sample(bank["hard"], min(1, len(bank["hard"]))))
            else:  # hard
                # More challenging questions
                if "medium" in bank:
                    questions.extend(random.sample(bank["medium"], min(1, len(bank["medium"]))))
                if "hard" in bank:
                    questions.extend(random.sample(bank["hard"], min(2, len(bank["hard"]))))
        
        # Shuffle and limit
        random.shuffle(questions)
        return questions[:10]  # Return max 10 questions for UPSC
    
    def _generate_general_questions(self, difficulty: str) -> List[Dict]:
        """Generate general interview questions"""
        questions = []
        bank = self.question_bank["general"]
        
        # Get questions from different difficulty levels
        if difficulty == "easy":
            questions.extend(random.sample(bank["easy"], min(3, len(bank["easy"]))))
            questions.extend(random.sample(bank["medium"], min(2, len(bank["medium"]))))
        elif difficulty == "medium":
            questions.extend(random.sample(bank["easy"], min(1, len(bank["easy"]))))
            questions.extend(random.sample(bank["medium"], min(3, len(bank["medium"]))))
            questions.extend(random.sample(bank["hard"], min(1, len(bank["hard"]))))
        else:  # hard
            questions.extend(random.sample(bank["medium"], min(2, len(bank["medium"]))))
            questions.extend(random.sample(bank["hard"], min(3, len(bank["hard"]))))
        
        # Add difficulty level to each question
        for q in questions:
            q["difficulty"] = difficulty
        
        return questions
    
    def _generate_technical_questions(
        self,
        difficulty: str,
        skills: Optional[List[str]],
        resume_data: Optional[Dict]
    ) -> List[Dict]:
        """Generate technical questions based on resume"""
        questions = []
        bank = self.question_bank["technical"]
        
        # Identify relevant technical categories based on skills
        relevant_categories = []
        
        if skills:
            skills_lower = [s.lower() for s in skills]
            
            # Programming languages
            for lang in ["python", "java", "javascript"]:
                if lang in skills_lower:
                    relevant_categories.append(("programming", lang))
            
            # Other categories
            if any(s in skills_lower for s in ["algorithm", "data structure", "dsa"]):
                relevant_categories.append("algorithms")
            
            if any(s in skills_lower for s in ["sql", "mongodb", "database", "postgresql", "mysql"]):
                relevant_categories.append("databases")
            
            if any(s in skills_lower for s in ["system design", "architecture", "scalability"]):
                relevant_categories.append("system_design")
        
        # If no skills identified, use general technical questions
        if not relevant_categories:
            relevant_categories = ["algorithms", "databases"]
        
        # Generate questions from relevant categories
        for category in relevant_categories[:3]:  # Max 3 categories
            if isinstance(category, tuple):  # Programming language
                cat_type, lang = category
                if lang in bank[cat_type]:
                    lang_questions = bank[cat_type][lang]
                    questions.extend(random.sample(lang_questions, min(2, len(lang_questions))))
            else:
                if category in bank:
                    cat_questions = bank[category]
                    questions.extend(random.sample(cat_questions, min(3, len(cat_questions))))
        
        # Ensure we have at least 8 questions
        while len(questions) < 8:
            # Add random technical questions
            all_tech_questions = []
            for cat in ["algorithms", "databases"]:
                all_tech_questions.extend(bank[cat])
            
            if all_tech_questions:
                questions.append(random.choice(all_tech_questions))
        
        # Add difficulty level
        for q in questions:
            if "difficulty" not in q:
                q["difficulty"] = difficulty
        
        return questions[:8]  # Return max 8 questions
    
    def _generate_hr_questions(self, difficulty: str) -> List[Dict]:
        """Generate HR interview questions"""
        questions = []
        bank = self.question_bank["hr"]
        
        if difficulty == "easy":
            questions.extend(random.sample(bank["easy"], min(3, len(bank["easy"]))))
            questions.extend(random.sample(bank["medium"], min(2, len(bank["medium"]))))
        elif difficulty == "medium":
            questions.extend(random.sample(bank["easy"], min(2, len(bank["easy"]))))
            questions.extend(random.sample(bank["medium"], min(2, len(bank["medium"]))))
            questions.extend(random.sample(bank["hard"], min(1, len(bank["hard"]))))
        else:  # hard
            questions.extend(random.sample(bank["medium"], min(2, len(bank["medium"]))))
            questions.extend(random.sample(bank["hard"], min(3, len(bank["hard"]))))
        
        for q in questions:
            q["difficulty"] = difficulty
        
        return questions
    
    def _get_adaptive_questions(self, user_id: int, interview_type: str, db: Session) -> List[Dict]:
        """Get adaptive questions based on past performance"""
        # Get user's past weak areas
        from backend.models import Interview
        
        past_interviews = db.query(Interview).filter(
            Interview.user_id == user_id,
            Interview.interview_type == interview_type,
            Interview.status == "completed"
        ).order_by(Interview.completed_at.desc()).limit(3).all()
        
        weak_areas = []
        for interview in past_interviews:
            if interview.weak_areas:
                weak_areas.extend([area.get("area") for area in interview.weak_areas])
        
        # Generate targeted questions for weak areas
        # This is a simplified version - can be enhanced with ML models
        adaptive_questions = []
        
        # For now, return empty list - to be enhanced
        return adaptive_questions
