import random
import logging
from typing import Dict, List, Optional, Set
from sqlalchemy.orm import Session
from backend.models import Interview, Response, Question
from .company_questions_loader import get_questions_loader, CompanyQuestionsLoader
from .upsc_questions_loader import get_upsc_questions_loader, UPSCQuestionsLoader

logger = logging.getLogger(__name__)

# Cache for user question history to avoid database hits
_user_question_cache: Dict[int, Set[str]] = {}


def _normalize_skills(skills: Optional[List]) -> List[str]:
    """Normalize skills to a list of lowercase strings.
    
    Handles cases where skills might be dicts, strings, or mixed.
    """
    if not skills:
        return []
    
    normalized = []
    for skill in skills:
        if isinstance(skill, str):
            normalized.append(skill.lower().strip())
        elif isinstance(skill, dict):
            # Extract skill name from dict (common keys: name, skill, value)
            for key in ['name', 'skill', 'value', 'text']:
                if key in skill and isinstance(skill[key], str):
                    normalized.append(skill[key].lower().strip())
                    break
        # Skip non-string, non-dict items
    
    return [s for s in normalized if s]  # Filter empty strings


class QuestionGenerator:
    """Generate interview questions based on type and context
    
    This generator combines:
    1. Company-sourced questions from top tech companies (Google, Amazon, Meta, etc.)
    2. AI-generated questions based on resume and skills
    3. Adaptive questions based on user's past performance
    
    Questions include tags showing company source and category.
    """
    
    def __init__(self):
        self.question_bank = self._initialize_question_bank()
        self.upsc_question_bank = self._initialize_upsc_questions()  # Fallback
        
        # Load company questions dataset
        try:
            self.company_loader = get_questions_loader()
            self.company_questions_available = True
            logger.info(f"Loaded {self.company_loader.metadata.get('total_questions', 0)} company questions")
        except Exception as e:
            logger.warning(f"Could not load company questions: {e}")
            self.company_questions_available = False
            self.company_loader = None
        
        # Load UPSC questions dataset
        try:
            self.upsc_loader = get_upsc_questions_loader()
            self.upsc_questions_available = True
            logger.info(f"Loaded {len(self.upsc_loader.questions)} UPSC questions")
        except Exception as e:
            logger.warning(f"Could not load UPSC questions: {e}")
            self.upsc_questions_available = False
            self.upsc_loader = None
    
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
        """Initialize expanded question bank with different categories - ~250 questions total"""
        return {
            "general": {
                "easy": [
                    {"text": "Tell me about yourself.", "type": "behavioral", "keywords": ["background", "experience", "skills"]},
                    {"text": "What are your greatest strengths?", "type": "behavioral", "keywords": ["skills", "abilities", "strengths"]},
                    {"text": "Why do you want to work here?", "type": "behavioral", "keywords": ["motivation", "company", "interest"]},
                    {"text": "Where do you see yourself in 5 years?", "type": "behavioral", "keywords": ["goals", "career", "future"]},
                    {"text": "What makes you a good fit for this role?", "type": "behavioral", "keywords": ["fit", "qualifications", "skills"]},
                    {"text": "What motivates you in your work?", "type": "behavioral", "keywords": ["motivation", "drive", "passion"]},
                    {"text": "How did you hear about this position?", "type": "behavioral", "keywords": ["source", "interest", "research"]},
                    {"text": "What do you know about our company?", "type": "behavioral", "keywords": ["research", "company", "knowledge"]},
                    {"text": "Why are you interested in this industry?", "type": "behavioral", "keywords": ["industry", "passion", "interest"]},
                    {"text": "What are your short-term career goals?", "type": "behavioral", "keywords": ["goals", "planning", "ambition"]},
                    {"text": "What excites you most about this opportunity?", "type": "behavioral", "keywords": ["excitement", "opportunity", "passion"]},
                    {"text": "How would you describe your work style?", "type": "behavioral", "keywords": ["work style", "productivity", "habits"]},
                    {"text": "What are three words that describe you best?", "type": "behavioral", "keywords": ["self-awareness", "personality", "traits"]},
                    {"text": "What do you enjoy doing outside of work?", "type": "behavioral", "keywords": ["hobbies", "interests", "balance"]},
                    {"text": "What kind of manager brings out the best in you?", "type": "behavioral", "keywords": ["management", "leadership", "preferences"]},
                    {"text": "How do you define success?", "type": "behavioral", "keywords": ["success", "values", "goals"]},
                ],
                "medium": [
                    {"text": "Describe a challenging situation you faced and how you handled it.", "type": "situational", "keywords": ["challenge", "problem-solving", "resolution"]},
                    {"text": "How do you handle working under pressure?", "type": "behavioral", "keywords": ["stress", "pressure", "coping"]},
                    {"text": "Describe a time when you had to work with a difficult team member.", "type": "situational", "keywords": ["teamwork", "conflict", "resolution"]},
                    {"text": "What is your biggest weakness and how are you working on it?", "type": "behavioral", "keywords": ["weakness", "improvement", "self-awareness"]},
                    {"text": "Tell me about a time you failed and what you learned from it.", "type": "situational", "keywords": ["failure", "learning", "growth"]},
                    {"text": "Describe how you handle working under pressure with tight deadlines.", "type": "situational", "keywords": ["pressure", "deadlines", "stress"]},
                    {"text": "Tell me about a project you're particularly proud of.", "type": "behavioral", "keywords": ["achievement", "pride", "success"]},
                    {"text": "How do you approach learning new technologies or skills?", "type": "behavioral", "keywords": ["learning", "growth", "adaptability"]},
                    {"text": "Describe your typical approach to problem-solving.", "type": "behavioral", "keywords": ["problem-solving", "methodology", "thinking"]},
                    {"text": "How do you ensure diversity and inclusion in your team or projects?", "type": "situational", "keywords": ["diversity", "inclusion", "teamwork"]},
                    {"text": "Describe a situation where you had to work with limited resources.", "type": "situational", "keywords": ["resourcefulness", "constraints", "creativity"]},
                    {"text": "What would you do if you disagreed with your manager's decision?", "type": "situational", "keywords": ["conflict", "communication", "professionalism"]},
                    {"text": "Tell me about a time you had to adapt to a major change at work.", "type": "situational", "keywords": ["adaptability", "change", "flexibility"]},
                    {"text": "How do you handle receiving constructive feedback?", "type": "behavioral", "keywords": ["feedback", "growth", "improvement"]},
                    {"text": "Describe a time when you took initiative to improve a process.", "type": "situational", "keywords": ["initiative", "improvement", "proactive"]},
                    {"text": "Tell me about a time you had to meet a tight deadline.", "type": "situational", "keywords": ["deadline", "time management", "pressure"]},
                    {"text": "How do you keep yourself organized when managing multiple tasks?", "type": "behavioral", "keywords": ["organization", "multitasking", "productivity"]},
                    {"text": "Describe a time when you had to collaborate with a remote team.", "type": "situational", "keywords": ["remote", "collaboration", "communication"]},
                    {"text": "Tell me about a time you had to deliver bad news to a stakeholder.", "type": "situational", "keywords": ["communication", "difficult conversations", "professionalism"]},
                    {"text": "How do you approach setting and achieving goals?", "type": "behavioral", "keywords": ["goals", "planning", "achievement"]},
                ],
                "hard": [
                    {"text": "Describe a situation where you had to make a decision with incomplete information.", "type": "situational", "keywords": ["decision-making", "uncertainty", "judgment"]},
                    {"text": "How do you prioritize when you have multiple urgent tasks?", "type": "behavioral", "keywords": ["prioritization", "time management", "organization"]},
                    {"text": "Tell me about a time you had to convince someone to see things your way.", "type": "situational", "keywords": ["persuasion", "communication", "influence"]},
                    {"text": "Describe a time when you had to lead a team through a crisis.", "type": "situational", "keywords": ["leadership", "crisis", "management"]},
                    {"text": "How would you handle a situation where you identified a major flaw in your team's approach?", "type": "situational", "keywords": ["critical thinking", "communication", "courage"]},
                    {"text": "Tell me about a time you had to balance competing stakeholder interests.", "type": "situational", "keywords": ["stakeholders", "negotiation", "balance"]},
                    {"text": "Describe how you've driven innovation in your previous role.", "type": "behavioral", "keywords": ["innovation", "creativity", "impact"]},
                    {"text": "What's the most difficult feedback you've received and how did you respond?", "type": "situational", "keywords": ["feedback", "growth", "resilience"]},
                    {"text": "Tell me about a time you turned a failure into a success.", "type": "situational", "keywords": ["failure", "recovery", "resilience"]},
                    {"text": "Describe a complex project you managed from start to finish.", "type": "situational", "keywords": ["project management", "leadership", "execution"]},
                    {"text": "How do you handle situations where you need to say no to requests?", "type": "behavioral", "keywords": ["boundaries", "communication", "prioritization"]},
                    {"text": "Tell me about a time you had to work with incomplete requirements.", "type": "situational", "keywords": ["ambiguity", "problem-solving", "clarification"]},
                    {"text": "Describe a situation where you had to influence without authority.", "type": "situational", "keywords": ["influence", "leadership", "collaboration"]},
                    {"text": "How have you handled a situation where team morale was low?", "type": "situational", "keywords": ["morale", "leadership", "motivation"]},
                    {"text": "Tell me about a risk you took that didn't pay off.", "type": "situational", "keywords": ["risk", "failure", "learning"]},
                    {"text": "Describe a time you had to make a trade-off between quality and speed.", "type": "situational", "keywords": ["trade-offs", "decision-making", "priorities"]},
                ]
            },
            "technical": {
                "programming": {
                    "python": [
                        {"text": "Explain the difference between lists and tuples in Python.", "type": "technical", "difficulty": "easy", "keywords": ["mutable", "immutable", "data structures"]},
                        {"text": "What are decorators in Python and how do you use them?", "type": "technical", "difficulty": "medium", "keywords": ["decorator", "function", "wrapper"]},
                        {"text": "Explain the Global Interpreter Lock (GIL) in Python.", "type": "technical", "difficulty": "hard", "keywords": ["GIL", "threading", "concurrency"]},
                        {"text": "How do you manage memory in Python?", "type": "technical", "difficulty": "medium", "keywords": ["garbage collection", "memory", "references"]},
                        {"text": "What is the difference between *args and **kwargs?", "type": "technical", "difficulty": "easy", "keywords": ["arguments", "functions", "parameters"]},
                        {"text": "Explain Python's context managers and the 'with' statement.", "type": "technical", "difficulty": "medium", "keywords": ["context manager", "with", "resource management"]},
                        {"text": "Explain the singleton pattern in Python and different ways to achieve it.", "type": "technical", "difficulty": "medium", "keywords": ["singleton", "design pattern", "metaclass"]},
                        {"text": "What are generators in Python and when would you use them?", "type": "technical", "difficulty": "medium", "keywords": ["generator", "yield", "iteration"]},
                        {"text": "Explain the difference between shallow copy and deep copy.", "type": "technical", "difficulty": "easy", "keywords": ["copy", "shallow", "deep"]},
                        {"text": "What are metaclasses in Python?", "type": "technical", "difficulty": "hard", "keywords": ["metaclass", "class", "type"]},
                        {"text": "How do you handle exceptions in Python? Explain try-except-finally.", "type": "technical", "difficulty": "easy", "keywords": ["exception", "try", "except"]},
                        {"text": "What are list comprehensions and when should you use them?", "type": "technical", "difficulty": "easy", "keywords": ["list comprehension", "iteration", "syntax"]},
                        {"text": "Explain Python's method resolution order (MRO).", "type": "technical", "difficulty": "hard", "keywords": ["MRO", "inheritance", "diamond problem"]},
                        {"text": "What is the difference between __str__ and __repr__?", "type": "technical", "difficulty": "easy", "keywords": ["str", "repr", "dunder methods"]},
                        {"text": "Explain the difference between multithreading and multiprocessing in Python. When would you use each?", "type": "technical", "difficulty": "hard", "keywords": ["threading", "multiprocessing", "parallelism"]},
                    ],
                    "java": [
                        {"text": "What is the difference between abstract classes and interfaces in Java?", "type": "technical", "difficulty": "easy", "keywords": ["abstract", "interface", "inheritance"]},
                        {"text": "Explain the concept of multithreading in Java.", "type": "technical", "difficulty": "medium", "keywords": ["threads", "concurrency", "synchronization"]},
                        {"text": "What are the different types of memory areas in JVM?", "type": "technical", "difficulty": "hard", "keywords": ["heap", "stack", "JVM", "memory"]},
                        {"text": "Explain the difference between HashMap and TreeMap.", "type": "technical", "difficulty": "medium", "keywords": ["HashMap", "TreeMap", "collections"]},
                        {"text": "What is the purpose of the 'final' keyword in Java?", "type": "technical", "difficulty": "easy", "keywords": ["final", "immutable", "constant"]},
                        {"text": "Explain Java's garbage collection mechanism.", "type": "technical", "difficulty": "medium", "keywords": ["garbage collection", "GC", "memory"]},
                        {"text": "What are Java Streams and how do you use them?", "type": "technical", "difficulty": "medium", "keywords": ["streams", "functional", "lambda"]},
                        {"text": "Explain the difference between checked and unchecked exceptions.", "type": "technical", "difficulty": "easy", "keywords": ["exceptions", "checked", "unchecked"]},
                        {"text": "What is the volatile keyword in Java?", "type": "technical", "difficulty": "hard", "keywords": ["volatile", "concurrency", "visibility"]},
                        {"text": "Explain the Java memory model and happens-before relationship.", "type": "technical", "difficulty": "hard", "keywords": ["memory model", "happens-before", "concurrency"]},
                        {"text": "What are lambda expressions and functional interfaces?", "type": "technical", "difficulty": "medium", "keywords": ["lambda", "functional interface", "Java 8"]},
                        {"text": "Explain dependency injection and its benefits.", "type": "technical", "difficulty": "medium", "keywords": ["DI", "dependency injection", "IoC"]},
                    ],
                    "javascript": [
                        {"text": "Explain closures in JavaScript.", "type": "technical", "difficulty": "medium", "keywords": ["closure", "scope", "function"]},
                        {"text": "What is the difference between == and === in JavaScript?", "type": "technical", "difficulty": "easy", "keywords": ["equality", "comparison", "type coercion"]},
                        {"text": "Explain the event loop in JavaScript.", "type": "technical", "difficulty": "hard", "keywords": ["event loop", "async", "callback"]},
                        {"text": "What is the difference between var, let, and const?", "type": "technical", "difficulty": "easy", "keywords": ["var", "let", "const", "scope"]},
                        {"text": "Explain prototypal inheritance in JavaScript.", "type": "technical", "difficulty": "medium", "keywords": ["prototype", "inheritance", "__proto__"]},
                        {"text": "What are Promises and how do they work?", "type": "technical", "difficulty": "medium", "keywords": ["Promise", "async", "then"]},
                        {"text": "Explain async/await and how it differs from Promises.", "type": "technical", "difficulty": "medium", "keywords": ["async", "await", "Promise"]},
                        {"text": "What is 'this' keyword in JavaScript and how does it work?", "type": "technical", "difficulty": "medium", "keywords": ["this", "context", "binding"]},
                        {"text": "Explain the concept of hoisting in JavaScript.", "type": "technical", "difficulty": "easy", "keywords": ["hoisting", "var", "function"]},
                        {"text": "What are higher-order functions? Give examples.", "type": "technical", "difficulty": "easy", "keywords": ["higher-order", "map", "filter", "reduce"]},
                        {"text": "Explain the difference between null and undefined.", "type": "technical", "difficulty": "easy", "keywords": ["null", "undefined", "types"]},
                        {"text": "What is event delegation and why is it useful?", "type": "technical", "difficulty": "medium", "keywords": ["event delegation", "DOM", "bubbling"]},
                        {"text": "Explain how JavaScript handles memory management.", "type": "technical", "difficulty": "hard", "keywords": ["memory", "garbage collection", "leaks"]},
                        {"text": "What are WeakMap and WeakSet?", "type": "technical", "difficulty": "hard", "keywords": ["WeakMap", "WeakSet", "memory"]},
                    ],
                    "typescript": [
                        {"text": "What are the benefits of using TypeScript over JavaScript?", "type": "technical", "difficulty": "easy", "keywords": ["TypeScript", "types", "safety"]},
                        {"text": "Explain the difference between interfaces and types in TypeScript.", "type": "technical", "difficulty": "medium", "keywords": ["interface", "type", "TypeScript"]},
                        {"text": "What are generics in TypeScript and how do you use them?", "type": "technical", "difficulty": "medium", "keywords": ["generics", "TypeScript", "type parameters"]},
                        {"text": "Explain TypeScript's union and intersection types.", "type": "technical", "difficulty": "medium", "keywords": ["union", "intersection", "types"]},
                        {"text": "What are decorators in TypeScript?", "type": "technical", "difficulty": "hard", "keywords": ["decorators", "metadata", "TypeScript"]},
                        {"text": "How does TypeScript's type inference work?", "type": "technical", "difficulty": "easy", "keywords": ["inference", "types", "TypeScript"]},
                        {"text": "Explain utility types in TypeScript (Partial, Required, Pick, Omit).", "type": "technical", "difficulty": "medium", "keywords": ["utility types", "Partial", "Pick"]},
                        {"text": "What is the 'never' type in TypeScript?", "type": "technical", "difficulty": "hard", "keywords": ["never", "TypeScript", "exhaustiveness"]},
                    ],
                    "react": [
                        {"text": "What is the Virtual DOM and how does it work?", "type": "technical", "difficulty": "easy", "keywords": ["Virtual DOM", "React", "reconciliation"]},
                        {"text": "Explain the difference between state and props.", "type": "technical", "difficulty": "easy", "keywords": ["state", "props", "React"]},
                        {"text": "What are React hooks and why were they introduced?", "type": "technical", "difficulty": "medium", "keywords": ["hooks", "useState", "useEffect"]},
                        {"text": "Explain the useEffect hook and its dependency array.", "type": "technical", "difficulty": "medium", "keywords": ["useEffect", "side effects", "dependencies"]},
                        {"text": "What is the Context API and when would you use it?", "type": "technical", "difficulty": "medium", "keywords": ["Context", "state management", "props drilling"]},
                        {"text": "Explain React's reconciliation algorithm.", "type": "technical", "difficulty": "hard", "keywords": ["reconciliation", "diffing", "keys"]},
                        {"text": "What are the differences between controlled and uncontrolled components?", "type": "technical", "difficulty": "easy", "keywords": ["controlled", "uncontrolled", "forms"]},
                        {"text": "How do you optimize performance in React applications?", "type": "technical", "difficulty": "hard", "keywords": ["performance", "memo", "useMemo", "useCallback"]},
                        {"text": "Explain how error boundaries work in React.", "type": "technical", "difficulty": "medium", "keywords": ["error boundary", "componentDidCatch", "error handling"]},
                        {"text": "What is prop drilling and how can you avoid it?", "type": "technical", "difficulty": "medium", "keywords": ["prop drilling", "Context", "state management"]},
                    ],
                    "cpp": [
                        {"text": "What is the difference between stack and heap memory allocation in C++?", "type": "technical", "difficulty": "easy", "keywords": ["stack", "heap", "memory"]},
                        {"text": "Explain RAII (Resource Acquisition Is Initialization).", "type": "technical", "difficulty": "medium", "keywords": ["RAII", "resource management", "destructor"]},
                        {"text": "What are smart pointers in C++? Explain unique_ptr, shared_ptr, and weak_ptr.", "type": "technical", "difficulty": "medium", "keywords": ["smart pointers", "unique_ptr", "shared_ptr"]},
                        {"text": "Explain virtual functions and vtable in C++.", "type": "technical", "difficulty": "hard", "keywords": ["virtual", "vtable", "polymorphism"]},
                        {"text": "What is the Rule of Three/Five in C++?", "type": "technical", "difficulty": "hard", "keywords": ["Rule of Three", "copy", "move"]},
                        {"text": "Explain move semantics and rvalue references.", "type": "technical", "difficulty": "hard", "keywords": ["move semantics", "rvalue", "&&"]},
                        {"text": "What are templates in C++ and how do they work?", "type": "technical", "difficulty": "medium", "keywords": ["templates", "generic", "metaprogramming"]},
                        {"text": "Explain the difference between struct and class in C++.", "type": "technical", "difficulty": "easy", "keywords": ["struct", "class", "access"]},
                    ],
                    "go": [
                        {"text": "What are goroutines and how do they differ from threads?", "type": "technical", "difficulty": "medium", "keywords": ["goroutines", "concurrency", "threads"]},
                        {"text": "Explain channels in Go and their use cases.", "type": "technical", "difficulty": "medium", "keywords": ["channels", "communication", "concurrency"]},
                        {"text": "What is the difference between slices and arrays in Go?", "type": "technical", "difficulty": "easy", "keywords": ["slices", "arrays", "Go"]},
                        {"text": "How does error handling work in Go?", "type": "technical", "difficulty": "easy", "keywords": ["error", "handling", "Go"]},
                        {"text": "Explain interfaces in Go and how they differ from other languages.", "type": "technical", "difficulty": "medium", "keywords": ["interfaces", "implicit", "Go"]},
                        {"text": "What is the defer statement and when would you use it?", "type": "technical", "difficulty": "easy", "keywords": ["defer", "cleanup", "Go"]},
                        {"text": "How does garbage collection work in Go?", "type": "technical", "difficulty": "hard", "keywords": ["GC", "garbage collection", "Go"]},
                        {"text": "Explain the purpose of the select statement in Go.", "type": "technical", "difficulty": "medium", "keywords": ["select", "channels", "concurrency"]},
                    ],
                    "rust": [
                        {"text": "Explain Rust's ownership system.", "type": "technical", "difficulty": "medium", "keywords": ["ownership", "borrowing", "Rust"]},
                        {"text": "What is the difference between borrowing and moving in Rust?", "type": "technical", "difficulty": "medium", "keywords": ["borrowing", "moving", "ownership"]},
                        {"text": "Explain lifetimes in Rust.", "type": "technical", "difficulty": "hard", "keywords": ["lifetimes", "references", "Rust"]},
                        {"text": "What are traits in Rust and how do they compare to interfaces?", "type": "technical", "difficulty": "medium", "keywords": ["traits", "interfaces", "Rust"]},
                        {"text": "How does Rust achieve memory safety without garbage collection?", "type": "technical", "difficulty": "hard", "keywords": ["memory safety", "ownership", "RAII"]},
                        {"text": "What is the difference between Option and Result in Rust?", "type": "technical", "difficulty": "easy", "keywords": ["Option", "Result", "error handling"]},
                    ],
                    "csharp": [
                        {"text": "What is the difference between value types and reference types in C#?", "type": "technical", "difficulty": "easy", "keywords": ["value type", "reference type", "C#"]},
                        {"text": "Explain async/await in C#.", "type": "technical", "difficulty": "medium", "keywords": ["async", "await", "Task"]},
                        {"text": "What is LINQ and how do you use it?", "type": "technical", "difficulty": "medium", "keywords": ["LINQ", "query", "C#"]},
                        {"text": "Explain delegates and events in C#.", "type": "technical", "difficulty": "medium", "keywords": ["delegates", "events", "callbacks"]},
                        {"text": "What are extension methods in C#?", "type": "technical", "difficulty": "easy", "keywords": ["extension methods", "C#", "static"]},
                        {"text": "Explain the IDisposable interface and the using statement.", "type": "technical", "difficulty": "medium", "keywords": ["IDisposable", "using", "resource management"]},
                    ],
                    "sql": [
                        {"text": "What is the difference between INNER JOIN and OUTER JOIN?", "type": "technical", "difficulty": "easy", "keywords": ["JOIN", "INNER", "OUTER"]},
                        {"text": "Explain the difference between WHERE and HAVING clauses.", "type": "technical", "difficulty": "easy", "keywords": ["WHERE", "HAVING", "GROUP BY"]},
                        {"text": "What are indexes and how do they improve query performance?", "type": "technical", "difficulty": "medium", "keywords": ["indexes", "performance", "B-tree"]},
                        {"text": "Explain the different types of SQL indexes.", "type": "technical", "difficulty": "medium", "keywords": ["clustered", "non-clustered", "indexes"]},
                        {"text": "What is a stored procedure and when would you use it?", "type": "technical", "difficulty": "medium", "keywords": ["stored procedure", "performance", "reusability"]},
                        {"text": "Explain window functions in SQL.", "type": "technical", "difficulty": "hard", "keywords": ["window functions", "OVER", "PARTITION BY"]},
                        {"text": "What is a common table expression (CTE)?", "type": "technical", "difficulty": "medium", "keywords": ["CTE", "WITH", "recursive"]},
                        {"text": "How do you optimize slow SQL queries?", "type": "technical", "difficulty": "hard", "keywords": ["optimization", "EXPLAIN", "indexes"]},
                    ]
                },
                "algorithms": [
                    {"text": "Explain the difference between linear and binary search.", "type": "technical", "difficulty": "easy", "keywords": ["search", "complexity", "algorithm"]},
                    {"text": "How would you detect a cycle in a linked list?", "type": "technical", "difficulty": "medium", "keywords": ["cycle", "linked list", "two pointers"]},
                    {"text": "Explain different sorting algorithms and their time complexities.", "type": "technical", "difficulty": "medium", "keywords": ["sorting", "time complexity", "algorithms"]},
                    {"text": "Describe dynamic programming and when to use it.", "type": "technical", "difficulty": "hard", "keywords": ["dynamic programming", "optimization", "memoization"]},
                    {"text": "What is the time complexity of common operations on arrays, linked lists, and hash tables?", "type": "technical", "difficulty": "medium", "keywords": ["time complexity", "Big O", "data structures"]},
                    {"text": "Explain how a hash table works internally.", "type": "technical", "difficulty": "medium", "keywords": ["hash table", "collision", "hashing"]},
                    {"text": "What is the difference between BFS and DFS?", "type": "technical", "difficulty": "easy", "keywords": ["BFS", "DFS", "graph traversal"]},
                    {"text": "How would you find the shortest path in a weighted graph?", "type": "technical", "difficulty": "hard", "keywords": ["Dijkstra", "shortest path", "graph"]},
                    {"text": "Explain the concept of recursion and tail recursion.", "type": "technical", "difficulty": "easy", "keywords": ["recursion", "tail recursion", "base case"]},
                    {"text": "What is a binary search tree and what are its properties?", "type": "technical", "difficulty": "easy", "keywords": ["BST", "binary tree", "search"]},
                    {"text": "Explain the difference between a tree and a graph.", "type": "technical", "difficulty": "easy", "keywords": ["tree", "graph", "data structures"]},
                    {"text": "Explain the approach to implement an LRU cache. What data structures would you use?", "type": "technical", "difficulty": "hard", "keywords": ["LRU", "cache", "linked list", "hash map"]},
                    {"text": "What is the difference between greedy and dynamic programming approaches?", "type": "technical", "difficulty": "medium", "keywords": ["greedy", "dynamic programming", "optimization"]},
                    {"text": "Explain Dijkstra's algorithm and its time complexity.", "type": "technical", "difficulty": "hard", "keywords": ["Dijkstra", "shortest path", "priority queue"]},
                    {"text": "What is backtracking and when would you use it?", "type": "technical", "difficulty": "medium", "keywords": ["backtracking", "recursion", "constraint satisfaction"]},
                    {"text": "Explain how you would reverse a linked list. Walk through the approach.", "type": "technical", "difficulty": "easy", "keywords": ["reverse", "linked list", "pointers"]},
                    {"text": "Explain the sliding window technique.", "type": "technical", "difficulty": "medium", "keywords": ["sliding window", "subarray", "optimization"]},
                    {"text": "What is a heap and where is it used?", "type": "technical", "difficulty": "medium", "keywords": ["heap", "priority queue", "heapify"]},
                    {"text": "Explain the approach to merge two sorted arrays efficiently.", "type": "technical", "difficulty": "easy", "keywords": ["merge", "sorted", "two pointers"]},
                    {"text": "Explain the difference between a stack and a queue.", "type": "technical", "difficulty": "easy", "keywords": ["stack", "queue", "LIFO", "FIFO"]},
                ],
                "databases": [
                    {"text": "What is the difference between SQL and NoSQL databases?", "type": "technical", "difficulty": "easy", "keywords": ["SQL", "NoSQL", "database"]},
                    {"text": "Explain database normalization and its forms.", "type": "technical", "difficulty": "medium", "keywords": ["normalization", "1NF", "2NF", "3NF"]},
                    {"text": "What is database indexing and how does it improve performance?", "type": "technical", "difficulty": "medium", "keywords": ["indexing", "performance", "optimization"]},
                    {"text": "Explain ACID properties in databases.", "type": "technical", "difficulty": "medium", "keywords": ["ACID", "transactions", "consistency"]},
                    {"text": "What are database transactions and isolation levels?", "type": "technical", "difficulty": "hard", "keywords": ["transactions", "isolation", "ACID"]},
                    {"text": "Explain the CAP theorem.", "type": "technical", "difficulty": "hard", "keywords": ["CAP", "consistency", "availability", "partition tolerance"]},
                    {"text": "What is sharding and when would you use it?", "type": "technical", "difficulty": "hard", "keywords": ["sharding", "horizontal scaling", "partitioning"]},
                    {"text": "Explain the difference between primary key and foreign key.", "type": "technical", "difficulty": "easy", "keywords": ["primary key", "foreign key", "constraints"]},
                    {"text": "What is database replication and its types?", "type": "technical", "difficulty": "medium", "keywords": ["replication", "master-slave", "availability"]},
                    {"text": "How do you handle database migrations?", "type": "technical", "difficulty": "medium", "keywords": ["migrations", "schema changes", "versioning"]},
                    {"text": "What is a deadlock in databases and how do you prevent it?", "type": "technical", "difficulty": "hard", "keywords": ["deadlock", "locking", "prevention"]},
                    {"text": "Explain the concept of eventual consistency.", "type": "technical", "difficulty": "medium", "keywords": ["eventual consistency", "distributed", "CAP"]},
                    {"text": "What are the differences between Redis and Memcached?", "type": "technical", "difficulty": "medium", "keywords": ["Redis", "Memcached", "caching"]},
                    {"text": "Explain database connection pooling.", "type": "technical", "difficulty": "medium", "keywords": ["connection pooling", "performance", "resources"]},
                    {"text": "What is a materialized view?", "type": "technical", "difficulty": "medium", "keywords": ["materialized view", "caching", "performance"]},
                ],
                "system_design": [
                    {"text": "How would you design a URL shortening service like bit.ly?", "type": "technical", "difficulty": "hard", "keywords": ["system design", "scalability", "architecture"]},
                    {"text": "Explain the concept of load balancing.", "type": "technical", "difficulty": "medium", "keywords": ["load balancing", "distribution", "scalability"]},
                    {"text": "What is caching and when would you use it?", "type": "technical", "difficulty": "medium", "keywords": ["caching", "performance", "Redis"]},
                    {"text": "How would you design a rate limiter?", "type": "technical", "difficulty": "medium", "keywords": ["rate limiter", "throttling", "API"]},
                    {"text": "Explain microservices architecture and its benefits.", "type": "technical", "difficulty": "medium", "keywords": ["microservices", "architecture", "distributed"]},
                    {"text": "How would you design a notification system?", "type": "technical", "difficulty": "hard", "keywords": ["notification", "push", "real-time"]},
                    {"text": "What is a message queue and when would you use it?", "type": "technical", "difficulty": "medium", "keywords": ["message queue", "async", "RabbitMQ", "Kafka"]},
                    {"text": "How would you design a distributed cache?", "type": "technical", "difficulty": "hard", "keywords": ["distributed cache", "consistency", "partitioning"]},
                    {"text": "Explain the concept of horizontal vs vertical scaling.", "type": "technical", "difficulty": "easy", "keywords": ["scaling", "horizontal", "vertical"]},
                    {"text": "How would you design a chat application like WhatsApp?", "type": "technical", "difficulty": "hard", "keywords": ["chat", "real-time", "messaging"]},
                    {"text": "What is a CDN and how does it work?", "type": "technical", "difficulty": "medium", "keywords": ["CDN", "content delivery", "edge servers"]},
                    {"text": "How would you design Twitter's timeline feature?", "type": "technical", "difficulty": "hard", "keywords": ["timeline", "feed", "fan-out"]},
                    {"text": "Explain the concept of database sharding strategies.", "type": "technical", "difficulty": "hard", "keywords": ["sharding", "partitioning", "consistent hashing"]},
                    {"text": "How would you handle distributed transactions?", "type": "technical", "difficulty": "hard", "keywords": ["distributed transactions", "two-phase commit", "saga"]},
                    {"text": "What is a circuit breaker pattern?", "type": "technical", "difficulty": "medium", "keywords": ["circuit breaker", "resilience", "fault tolerance"]},
                    {"text": "How would you design an API rate limiting system?", "type": "technical", "difficulty": "medium", "keywords": ["rate limiting", "token bucket", "sliding window"]},
                    {"text": "Explain event-driven architecture.", "type": "technical", "difficulty": "medium", "keywords": ["event-driven", "pub/sub", "decoupling"]},
                    {"text": "How would you design a search autocomplete system?", "type": "technical", "difficulty": "hard", "keywords": ["autocomplete", "trie", "typeahead"]},
                ],
                "devops": [
                    {"text": "What is CI/CD and why is it important?", "type": "technical", "difficulty": "easy", "keywords": ["CI/CD", "continuous integration", "deployment"]},
                    {"text": "Explain Docker and containerization.", "type": "technical", "difficulty": "medium", "keywords": ["Docker", "containers", "images"]},
                    {"text": "What is Kubernetes and when would you use it?", "type": "technical", "difficulty": "hard", "keywords": ["Kubernetes", "orchestration", "containers"]},
                    {"text": "Explain the difference between Docker and virtual machines.", "type": "technical", "difficulty": "easy", "keywords": ["Docker", "VM", "virtualization"]},
                    {"text": "What is Infrastructure as Code (IaC)?", "type": "technical", "difficulty": "medium", "keywords": ["IaC", "Terraform", "automation"]},
                    {"text": "Explain blue-green deployment strategy.", "type": "technical", "difficulty": "medium", "keywords": ["blue-green", "deployment", "zero downtime"]},
                    {"text": "What is a service mesh?", "type": "technical", "difficulty": "hard", "keywords": ["service mesh", "Istio", "sidecar"]},
                    {"text": "Describe your approach to implementing monitoring and alerting in a distributed system.", "type": "technical", "difficulty": "medium", "keywords": ["monitoring", "alerting", "Prometheus", "Grafana"]},
                    {"text": "Explain the 12-factor app methodology.", "type": "technical", "difficulty": "medium", "keywords": ["12-factor", "cloud-native", "best practices"]},
                    {"text": "What is GitOps?", "type": "technical", "difficulty": "medium", "keywords": ["GitOps", "declarative", "Git"]},
                ],
                "security": [
                    {"text": "What is SQL injection and how do you prevent it?", "type": "technical", "difficulty": "easy", "keywords": ["SQL injection", "security", "parameterized queries"]},
                    {"text": "Explain the difference between authentication and authorization.", "type": "technical", "difficulty": "easy", "keywords": ["authentication", "authorization", "security"]},
                    {"text": "What is CORS and why is it important?", "type": "technical", "difficulty": "medium", "keywords": ["CORS", "cross-origin", "security"]},
                    {"text": "Explain JWT (JSON Web Tokens) and how they work.", "type": "technical", "difficulty": "medium", "keywords": ["JWT", "token", "authentication"]},
                    {"text": "What is XSS (Cross-Site Scripting) and how do you prevent it?", "type": "technical", "difficulty": "medium", "keywords": ["XSS", "scripting", "sanitization"]},
                    {"text": "Explain HTTPS and TLS/SSL.", "type": "technical", "difficulty": "medium", "keywords": ["HTTPS", "TLS", "encryption"]},
                    {"text": "What is OAuth 2.0 and how does it work?", "type": "technical", "difficulty": "hard", "keywords": ["OAuth", "authorization", "tokens"]},
                    {"text": "How do you securely store passwords?", "type": "technical", "difficulty": "medium", "keywords": ["password", "hashing", "bcrypt"]},
                    {"text": "What is CSRF and how do you prevent it?", "type": "technical", "difficulty": "medium", "keywords": ["CSRF", "token", "security"]},
                    {"text": "Explain the principle of least privilege.", "type": "technical", "difficulty": "easy", "keywords": ["least privilege", "security", "access control"]},
                ],
                "api_design": [
                    {"text": "What are the principles of RESTful API design?", "type": "technical", "difficulty": "easy", "keywords": ["REST", "API", "HTTP"]},
                    {"text": "Explain the difference between REST and GraphQL.", "type": "technical", "difficulty": "medium", "keywords": ["REST", "GraphQL", "API"]},
                    {"text": "What are HTTP status codes and their categories?", "type": "technical", "difficulty": "easy", "keywords": ["HTTP", "status codes", "API"]},
                    {"text": "How do you version an API?", "type": "technical", "difficulty": "medium", "keywords": ["versioning", "API", "backwards compatibility"]},
                    {"text": "What is HATEOAS in REST?", "type": "technical", "difficulty": "hard", "keywords": ["HATEOAS", "REST", "hypermedia"]},
                    {"text": "Explain pagination strategies for APIs.", "type": "technical", "difficulty": "medium", "keywords": ["pagination", "offset", "cursor"]},
                    {"text": "What is idempotency in API design?", "type": "technical", "difficulty": "medium", "keywords": ["idempotency", "PUT", "POST"]},
                    {"text": "How do you handle API deprecation?", "type": "technical", "difficulty": "medium", "keywords": ["deprecation", "versioning", "migration"]},
                ]
            },
            "hr": {
                "easy": [
                    {"text": "What attracted you to apply for this position?", "type": "hr", "keywords": ["motivation", "interest", "position"]},
                    {"text": "How would your colleagues describe you?", "type": "hr", "keywords": ["personality", "teamwork", "perception"]},
                    {"text": "What do you know about our company?", "type": "hr", "keywords": ["research", "company", "knowledge"]},
                    {"text": "What are your salary expectations?", "type": "hr", "keywords": ["salary", "compensation", "expectations"]},
                    {"text": "When can you start if selected?", "type": "hr", "keywords": ["availability", "start date", "transition"]},
                    {"text": "Are you comfortable with the work location?", "type": "hr", "keywords": ["location", "commute", "relocation"]},
                    {"text": "Do you have any questions for us?", "type": "hr", "keywords": ["curiosity", "engagement", "research"]},
                    {"text": "What type of work environment do you prefer?", "type": "hr", "keywords": ["environment", "culture", "fit"]},
                    {"text": "Are you open to working overtime when needed?", "type": "hr", "keywords": ["flexibility", "commitment", "availability"]},
                    {"text": "What are your expectations from this role?", "type": "hr", "keywords": ["expectations", "role", "fit"]},
                    {"text": "How do you prefer to receive recognition for your work?", "type": "hr", "keywords": ["recognition", "motivation", "reward"]},
                    {"text": "Are you comfortable working in a team environment?", "type": "hr", "keywords": ["teamwork", "collaboration", "preference"]},
                    {"text": "What tools or software are you proficient in?", "type": "hr", "keywords": ["tools", "skills", "software"]},
                    {"text": "Do you have any concerns about this position?", "type": "hr", "keywords": ["concerns", "questions", "clarity"]},
                ],
                "medium": [
                    {"text": "Why are you leaving your current job?", "type": "hr", "keywords": ["career change", "motivation", "growth"]},
                    {"text": "How do you handle feedback and criticism?", "type": "hr", "keywords": ["feedback", "growth mindset", "adaptation"]},
                    {"text": "Describe your ideal work environment.", "type": "hr", "keywords": ["environment", "culture", "preferences"]},
                    {"text": "What are your long-term career goals?", "type": "hr", "keywords": ["career", "goals", "ambition"]},
                    {"text": "How do you maintain work-life balance?", "type": "hr", "keywords": ["balance", "well-being", "management"]},
                    {"text": "What would you do in your first 90 days in this role?", "type": "hr", "keywords": ["planning", "onboarding", "impact"]},
                    {"text": "How do you handle working with people from different backgrounds?", "type": "hr", "keywords": ["diversity", "inclusion", "collaboration"]},
                    {"text": "What makes you unique compared to other candidates?", "type": "hr", "keywords": ["differentiation", "value", "skills"]},
                    {"text": "How do you stay updated with industry trends?", "type": "hr", "keywords": ["learning", "industry", "growth"]},
                    {"text": "Describe a time when you went above and beyond your job duties.", "type": "hr", "keywords": ["initiative", "dedication", "impact"]},
                    {"text": "How do you handle multiple competing priorities?", "type": "hr", "keywords": ["prioritization", "organization", "time management"]},
                    {"text": "What steps do you take to continuously improve your skills?", "type": "hr", "keywords": ["learning", "development", "growth"]},
                    {"text": "How would you handle a conflict with a coworker?", "type": "hr", "keywords": ["conflict resolution", "communication", "teamwork"]},
                    {"text": "What role do you typically take in team projects?", "type": "hr", "keywords": ["teamwork", "leadership", "collaboration"]},
                    {"text": "How do you approach tasks that are outside your comfort zone?", "type": "hr", "keywords": ["adaptability", "learning", "growth"]},
                    {"text": "What motivates you to do your best work?", "type": "hr", "keywords": ["motivation", "drive", "performance"]},
                    {"text": "How do you handle setbacks or disappointments at work?", "type": "hr", "keywords": ["resilience", "coping", "growth"]},
                    {"text": "What's your approach to meeting tight deadlines?", "type": "hr", "keywords": ["deadlines", "time management", "pressure"]},
                ],
                "hard": [
                    {"text": "Tell me about a time you disagreed with management and how you handled it.", "type": "hr", "keywords": ["conflict", "management", "communication"]},
                    {"text": "How would you handle an ethical dilemma at work?", "type": "hr", "keywords": ["ethics", "integrity", "decision-making"]},
                    {"text": "What would you do if you were asked to work on something outside your job description?", "type": "hr", "keywords": ["flexibility", "boundaries", "adaptation"]},
                    {"text": "How would you handle a situation where a colleague is taking credit for your work?", "type": "hr", "keywords": ["conflict", "assertion", "professionalism"]},
                    {"text": "What would you do if you discovered your company was doing something unethical?", "type": "hr", "keywords": ["ethics", "integrity", "courage"]},
                    {"text": "How would you handle a major failure that impacted your team?", "type": "hr", "keywords": ["accountability", "resilience", "leadership"]},
                    {"text": "Describe a situation where you had to make an unpopular decision.", "type": "hr", "keywords": ["decision-making", "courage", "leadership"]},
                    {"text": "How would you handle a situation where you had to fire someone?", "type": "hr", "keywords": ["difficult conversations", "leadership", "empathy"]},
                    {"text": "What would you do if you disagreed with company policy?", "type": "hr", "keywords": ["policy", "disagreement", "professionalism"]},
                    {"text": "How do you handle situations where you need to give negative feedback to a peer?", "type": "hr", "keywords": ["feedback", "communication", "professionalism"]},
                    {"text": "Describe a time when you had to make a decision that benefited the company but not yourself.", "type": "hr", "keywords": ["sacrifice", "company first", "integrity"]},
                    {"text": "How would you handle discovering a security breach?", "type": "hr", "keywords": ["crisis", "security", "responsibility"]},
                    {"text": "What would you do if a supervisor asked you to do something you believed was wrong?", "type": "hr", "keywords": ["ethics", "integrity", "assertiveness"]},
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
        db: Session = None,
        company_question_ratio: float = 0.6
    ) -> List[Dict]:
        """Generate questions for interview with company questions mixed in
        
        Args:
            interview_type: Type of interview (general, technical, hr)
            difficulty: Difficulty level (easy, medium, hard)
            interview_mode: Mode (standard, upsc)
            resume_data: Parsed resume data
            skills: User's skills
            user_id: User ID for adaptive questions
            db: Database session
            company_question_ratio: Ratio of questions from company dataset (0.0 to 1.0)
        
        Returns:
            List of questions with tags and company information
        """
        questions = []
        generated_questions = []
        company_questions = []
        
        # Normalize skills to handle different input types
        normalized_skills = _normalize_skills(skills)
        
        # Get user's past questions to avoid repetition
        exclude_texts = set()
        if user_id and db:
            # Clear cache to get fresh history for this session
            self.clear_user_cache(user_id)
            exclude_texts = self._get_user_question_history(user_id, db)
            logger.info(f"Excluding {len(exclude_texts)} previously asked questions for user {user_id}")
        
        # Determine total question count
        if interview_type == "full":
            total_questions = 12  # 4 general + 4 technical + 4 hr
        elif interview_type == "upsc":
            total_questions = 10
        elif interview_type == "technical":
            total_questions = 8
        else:
            total_questions = 5
        
        # Calculate how many from each source
        # UPSC should NOT use company questions (they're tech companies, not civil services)
        if interview_type == "upsc":
            company_count = 0
            generated_count = total_questions
        else:
            company_count = int(total_questions * company_question_ratio)
            generated_count = total_questions - company_count
        
        # Try to get company questions if available (not for UPSC)
        if self.company_questions_available and interview_type != "upsc":
            try:
                if interview_type == "full":
                    # For full interview, get company questions from all three types
                    per_type_count = max(1, company_count // 3)
                    all_company_qs = []
                    round_map = {
                        "behavioral": "General Round",
                        "technical": "Technical Round", 
                        "hr": "HR Round"
                    }
                    for q_type in ["behavioral", "technical", "hr"]:
                        # Use skill-based filtering for technical questions
                        if q_type == "technical" and normalized_skills:
                            type_qs = self.company_loader.get_questions_by_skills(
                                skills=normalized_skills,
                                count=per_type_count,
                                question_type=q_type,
                                difficulty=difficulty
                            )
                        else:
                            type_qs = self.company_loader.get_formatted_questions(
                                count=per_type_count,
                                question_type=q_type,
                                difficulty=difficulty
                            )
                        # Tag with round info
                        for q in type_qs:
                            q['round'] = round_map.get(q_type, 'General Round')
                        all_company_qs.extend(type_qs)
                    company_questions = all_company_qs
                else:
                    # Map interview type to question type for the dataset
                    question_type_map = {
                        "general": "behavioral",
                        "technical": "technical",
                        "hr": "hr"
                    }
                    mapped_type = question_type_map.get(interview_type, "behavioral")
                    
                    # Use skill-based filtering for technical interviews
                    if interview_type == "technical" and normalized_skills:
                        logger.info(f"[Question Generation] Using skill-filtered questions for skills: {normalized_skills[:5]}...")
                        company_questions = self.company_loader.get_questions_by_skills(
                            skills=normalized_skills,
                            count=company_count,
                            question_type=mapped_type,
                            difficulty=difficulty
                        )
                    else:
                        # Get company questions without skill filtering
                        company_questions = self.company_loader.get_formatted_questions(
                            count=company_count,
                            question_type=mapped_type,
                            difficulty=difficulty
                        )
                
                # Ensure tags are properly set
                for q in company_questions:
                    if 'tags' not in q or not q['tags']:
                        q['tags'] = []
                    # Add company as a tag if present
                    if q.get('company') and q['company'] not in q['tags']:
                        q['tags'].insert(0, q['company'])
                    # Add difficulty as a tag
                    if q.get('difficulty') and q['difficulty'] not in q['tags']:
                        q['tags'].append(q['difficulty'])
                
                logger.info(f"Loaded {len(company_questions)} company questions for {interview_type} interview")
                
            except Exception as e:
                logger.warning(f"Could not load company questions: {e}")
                company_questions = []
                generated_count = total_questions  # Fall back to all generated
        
        # Generate remaining questions
        if interview_type == "full":
            # Full interview: combine questions from all three types
            full_gen_count = max(1, generated_count // 3)
            general_qs = self._generate_general_questions(difficulty)[:full_gen_count]
            technical_qs = self._generate_technical_questions(difficulty, normalized_skills, resume_data)[:full_gen_count]
            hr_qs = self._generate_hr_questions(difficulty)[:full_gen_count]
            # Tag each question with its round type
            for q in general_qs:
                q['round'] = 'General Round'
            for q in technical_qs:
                q['round'] = 'Technical Round'
            for q in hr_qs:
                q['round'] = 'HR Round'
            generated_questions = general_qs + technical_qs + hr_qs
        elif interview_type == "general":
            generated_questions = self._generate_general_questions(difficulty)[:generated_count]
        elif interview_type == "technical":
            generated_questions = self._generate_technical_questions(difficulty, normalized_skills, resume_data)[:generated_count]
        elif interview_type == "hr":
            generated_questions = self._generate_hr_questions(difficulty)[:generated_count]
        elif interview_type == "upsc":
            generated_questions = self._generate_upsc_questions(difficulty)
            for q in generated_questions:
                q['round'] = 'UPSC Round'
        
        # Add default tags to generated questions
        for q in generated_questions:
            if 'tags' not in q:
                q['tags'] = []
            if 'from_dataset' not in q:
                q['from_dataset'] = False
                q['tags'].append('ai-generated')
            # Add source info
            if not q.get('source'):
                q['source'] = 'AI Generated'
            if not q.get('company'):
                q['company'] = ''
            if not q.get('company_name'):
                q['company_name'] = ''
        
        # Combine questions
        questions = company_questions + generated_questions
        
        # For full interview, sort by round order instead of shuffling
        if interview_type == "full":
            round_order = {'General Round': 0, 'Technical Round': 1, 'HR Round': 2}
            questions.sort(key=lambda q: round_order.get(q.get('round', 'General Round'), 0))
        else:
            random.shuffle(questions)
        
        # Add adaptive questions based on past performance if available
        if user_id and db and interview_mode != "upsc":
            adaptive_questions = self._get_adaptive_questions(user_id, interview_type, db)
            for q in adaptive_questions:
                q['tags'] = q.get('tags', []) + ['adaptive', 'personalized']
                q['from_dataset'] = False
            questions.extend(adaptive_questions)
        
        # Apply rule-based difficulty classification
        questions = self._classify_difficulty(questions)
        
        # Store original questions before filtering (in case we need to restore)
        original_questions = questions.copy()
        
        # Filter out questions the user has already seen
        if exclude_texts:
            filtered_questions = [q for q in questions if q['text'].lower().strip() not in exclude_texts]
            repeated_questions = [q for q in questions if q['text'].lower().strip() in exclude_texts]
            filtered_count = len(questions) - len(filtered_questions)
            
            if len(filtered_questions) >= total_questions:
                # Enough unique questions — use only those
                questions = filtered_questions
                if filtered_count > 0:
                    logger.info(f"Filtered out {filtered_count} repeated questions, {len(questions)} remaining")
            elif len(filtered_questions) > 0:
                # Not enough unique questions but some are available
                # Use all unique ones first, then fill with least-recently-asked repeats
                shortfall = total_questions - len(filtered_questions)
                logger.info(f"Only {len(filtered_questions)} unique questions available (need {total_questions}), adding {shortfall} repeats")
                questions = filtered_questions + repeated_questions[:shortfall]
            else:
                logger.info(f"No unique questions available, using all {len(questions)} questions")
        
        # Deduplicate within the same interview - avoid similar questions
        # But ensure we maintain minimum count
        deduplicated = self._deduplicate_questions(questions)
        
        # If deduplication removed too many, use original filtered list
        if len(deduplicated) < total_questions and len(questions) >= total_questions:
            logger.info(f"Restoring {len(questions) - len(deduplicated)} questions after aggressive dedup")
            # Keep deduplicated but add back enough to reach target
            remaining_needed = total_questions - len(deduplicated)
            extra_qs = [q for q in questions if q not in deduplicated][:remaining_needed]
            deduplicated.extend(extra_qs)
        
        # Final safety: if still short, add back from originals (prefer unique ones first)
        if len(deduplicated) < total_questions and len(original_questions) >= total_questions:
            logger.warning(f"Dedup left only {len(deduplicated)} questions, filling to {total_questions}")
            existing_texts = {q['text'].lower().strip() for q in deduplicated}
            for q in original_questions:
                if len(deduplicated) >= total_questions:
                    break
                if q['text'].lower().strip() not in existing_texts:
                    deduplicated.append(q)
                    existing_texts.add(q['text'].lower().strip())
            # If still short, allow repeats from originals as last resort
            if len(deduplicated) < total_questions:
                for q in original_questions:
                    if len(deduplicated) >= total_questions:
                        break
                    if q not in deduplicated:
                        deduplicated.append(q)
        
        return deduplicated
    
    def _deduplicate_questions(self, questions: List[Dict]) -> List[Dict]:
        """Remove similar questions from the batch to ensure variety.
        
        Uses keyword overlap and phrase matching to identify similar questions.
        """
        if len(questions) <= 1:
            return questions
        
        deduplicated = []
        seen_patterns = set()
        
        # Extract key phrases that indicate question topics
        topic_keywords = [
            'decorator', 'metaclass', 'async', 'await', 'garbage collection',
            'context manager', 'generator', 'iterator', 'list comprehension',
            'exception', 'inheritance', 'polymorphism', 'encapsulation',
            'microservice', 'monolithic', 'rest', 'graphql', 'cache', 'lru',
            'rate limit', 'system design', 'binary tree', 'linked list',
            'array', 'hashmap', 'sql', 'nosql', 'thread', 'process',
            'tcp', 'udp', 'http', 'https', 'docker', 'kubernetes',
            'ci/cd', 'git', 'agile', 'scrum', 'dependency injection',
            'solid', 'design pattern', 'singleton', 'factory', 'observer'
        ]
        
        for q in questions:
            text_lower = q['text'].lower()
            
            # Extract first 5 significant words (skip common words)
            skip_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'explain', 
                         'describe', 'tell', 'me', 'about', 'would', 'you', 'in',
                         'do', 'does', 'can', 'could', 'and', 'or', 'to', 'of'}
            words = [w for w in text_lower.split()[:15] if w not in skip_words]
            phrase_key = ' '.join(words[:5])
            
            # Check for topic keywords
            found_topics = [kw for kw in topic_keywords if kw in text_lower]
            topic_key = tuple(sorted(found_topics[:3])) if found_topics else None
            
            # Skip if we've seen a very similar phrase or same topic combination
            is_duplicate = False
            
            # Check phrase similarity
            for seen in seen_patterns:
                if isinstance(seen, str) and len(seen) > 10:
                    # Compare first N words
                    if phrase_key[:30] == seen[:30]:
                        is_duplicate = True
                        logger.debug(f"Skipping similar question: {q['text'][:50]}...")
                        break
            
            # Check topic overlap (more than 2 same topic keywords = likely duplicate)
            if not is_duplicate and topic_key and len(topic_key) >= 2:
                for seen in seen_patterns:
                    if isinstance(seen, tuple):
                        overlap = len(set(topic_key) & set(seen))
                        if overlap >= 2:
                            is_duplicate = True
                            logger.debug(f"Skipping overlapping topic question: {q['text'][:50]}...")
                            break
            
            if not is_duplicate:
                deduplicated.append(q)
                seen_patterns.add(phrase_key)
                if topic_key:
                    seen_patterns.add(topic_key)
        
        if len(deduplicated) < len(questions):
            logger.info(f"Deduplicated {len(questions) - len(deduplicated)} similar questions within batch")
        
        return deduplicated
    
    def _get_user_question_history(self, user_id: int, db: Session) -> Set[str]:
        """Get set of question texts the user has already been asked recently.
        
        Excludes questions from the last 10 interviews to prevent repetition
        across consecutive interviews while still allowing recycling eventually.
        """
        global _user_question_cache
        
        # Check cache first
        if user_id in _user_question_cache:
            return _user_question_cache[user_id]
        
        try:
            # Get questions from the last 10 interviews to avoid repetition
            # With 250+ questions in the pool and 5-12 per interview,
            # this covers ~60-120 past questions, leaving plenty of fresh ones
            recent_interview_ids = db.query(Interview.id).filter(
                Interview.user_id == user_id,
                Interview.status.in_(["completed", "in_progress"])
            ).order_by(Interview.id.desc()).limit(10).all()
            
            recent_ids = [i[0] for i in recent_interview_ids]
            
            if not recent_ids:
                return set()
            
            past_questions = db.query(Question.question_text).filter(
                Question.interview_id.in_(recent_ids)
            ).all()
            
            # Normalize and cache
            question_texts = {q[0].lower().strip() for q in past_questions if q[0]}
            _user_question_cache[user_id] = question_texts
            
            return question_texts
        except Exception as e:
            logger.warning(f"Could not fetch user question history: {e}")
            return set()
    
    def clear_user_cache(self, user_id: int = None):
        """Clear the question history cache for a user or all users."""
        global _user_question_cache
        if user_id:
            _user_question_cache.pop(user_id, None)
        else:
            _user_question_cache.clear()
    
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
        """Generate UPSC style interview questions from the dedicated dataset.
        
        Uses the 200-question UPSC bank covering:
        - Current Affairs
        - Indian Polity & Governance  
        - Ethics & Integrity
        - Economy
        - Environment
        - Science & Technology
        - International Relations
        - Social Issues
        - Personality
        - Opinion-based
        - Administrative
        """
        # Try to use the UPSC loader first (200 questions)
        if self.upsc_questions_available and self.upsc_loader:
            try:
                # Get a balanced mix from different categories
                questions = self.upsc_loader.get_mixed_difficulty_questions(
                    total_count=10,
                    categories=[
                        "current_affairs",
                        "indian_polity", 
                        "ethics_integrity",
                        "personality",
                        "opinion_based",
                        "administrative",
                        "economy",
                        "international_relations"
                    ]
                )
                
                if questions:
                    logger.info(f"Generated {len(questions)} UPSC questions from dataset")
                    return questions
            except Exception as e:
                logger.warning(f"Error loading UPSC questions from dataset: {e}")
        
        # Fallback to hardcoded questions
        logger.info("Using fallback UPSC question bank")
        questions = []
        categories = ["current_affairs", "ethics_integrity", "personality", "administrative", "opinion"]
        
        for category in categories:
            bank = self.upsc_question_bank.get(category, {})
            
            if difficulty == "easy":
                if "easy" in bank:
                    questions.extend(random.sample(bank["easy"], min(2, len(bank["easy"]))))
                if "medium" in bank:
                    questions.extend(random.sample(bank["medium"], min(1, len(bank["medium"]))))
            elif difficulty == "medium":
                if "easy" in bank:
                    questions.extend(random.sample(bank["easy"], min(1, len(bank["easy"]))))
                if "medium" in bank:
                    questions.extend(random.sample(bank["medium"], min(2, len(bank["medium"]))))
                if "hard" in bank:
                    questions.extend(random.sample(bank["hard"], min(1, len(bank["hard"]))))
            else:  # hard
                if "medium" in bank:
                    questions.extend(random.sample(bank["medium"], min(1, len(bank["medium"]))))
                if "hard" in bank:
                    questions.extend(random.sample(bank["hard"], min(2, len(bank["hard"]))))
        
        random.shuffle(questions)
        return questions[:10]
    
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
        """Generate technical questions based on resume skills.
        
        This method prioritizes questions relevant to the user's skills.
        """
        questions = []
        bank = self.question_bank["technical"]
        
        # Identify relevant technical categories based on skills
        relevant_categories = []
        
        if skills:
            # Normalize skills to handle both strings and dicts
            skills_lower = _normalize_skills(skills)
            logger.info(f"[Technical Questions] Generating for skills: {skills_lower[:10]}...")
            
            # Programming languages - expanded with all supported languages
            lang_mappings = {
                'python': ('programming', 'python'),
                'java': ('programming', 'java'),
                'javascript': ('programming', 'javascript'),
                'typescript': ('programming', 'typescript'),
                'react': ('programming', 'react'),
                'reactjs': ('programming', 'react'),
                'react.js': ('programming', 'react'),
                'c++': ('programming', 'cpp'),
                'cpp': ('programming', 'cpp'),
                'go': ('programming', 'go'),
                'golang': ('programming', 'go'),
                'rust': ('programming', 'rust'),
                'c#': ('programming', 'csharp'),
                'csharp': ('programming', 'csharp'),
                '.net': ('programming', 'csharp'),
                'sql': ('programming', 'sql'),
            }
            
            for skill in skills_lower:
                if skill in lang_mappings:
                    relevant_categories.append(lang_mappings[skill])
            
            # Database skills
            db_skills = ['sql', 'mysql', 'postgresql', 'mongodb', 'database', 'redis', 
                        'elasticsearch', 'dynamodb', 'nosql', 'oracle', 'postgres', 'cassandra']
            if any(s in skills_lower for s in db_skills):
                relevant_categories.append("databases")
            
            # Algorithm/DSA skills
            algo_skills = ['algorithm', 'data structure', 'dsa', 'leetcode', 'competitive programming',
                          'sorting', 'searching', 'graph', 'tree', 'dynamic programming']
            if any(s in skills_lower for s in algo_skills):
                relevant_categories.append("algorithms")
            
            # System Design skills
            sysdesign_skills = ['system design', 'architecture', 'scalability', 'microservices',
                               'distributed systems', 'load balancing', 'caching']
            if any(s in skills_lower for s in sysdesign_skills):
                relevant_categories.append("system_design")
            
            # DevOps skills
            devops_skills = ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'devops',
                            'ci/cd', 'jenkins', 'terraform', 'ansible', 'helm', 'gitlab']
            if any(s in skills_lower for s in devops_skills):
                relevant_categories.append("devops")
            
            # Security skills
            security_skills = ['security', 'oauth', 'jwt', 'authentication', 'authorization',
                              'encryption', 'cybersecurity', 'penetration testing', 'owasp']
            if any(s in skills_lower for s in security_skills):
                relevant_categories.append("security")
            
            # API Design skills
            api_skills = ['rest', 'restful', 'api', 'graphql', 'grpc', 'swagger', 'openapi']
            if any(s in skills_lower for s in api_skills):
                relevant_categories.append("api_design")
            
            # Log matched categories
            logger.info(f"[Technical Questions] Matched categories: {relevant_categories}")
        
        # If no skills identified, use general technical questions from multiple categories
        if not relevant_categories:
            logger.info("[Technical Questions] No skill match, using default categories")
            relevant_categories = ["algorithms", "databases", "system_design"]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_categories = []
        for cat in relevant_categories:
            cat_key = cat if isinstance(cat, str) else cat[1]
            if cat_key not in seen:
                seen.add(cat_key)
                unique_categories.append(cat)
        relevant_categories = unique_categories[:4]  # Max 4 categories
        
        # Generate questions from relevant categories
        for category in relevant_categories:
            if isinstance(category, tuple):  # Programming language
                cat_type, lang = category
                if cat_type in bank and lang in bank[cat_type]:
                    lang_questions = bank[cat_type][lang]
                    sample_count = min(3, len(lang_questions))
                    if sample_count > 0:
                        questions.extend(random.sample(lang_questions, sample_count))
            else:
                if category in bank:
                    cat_questions = bank[category]
                    sample_count = min(3, len(cat_questions))
                    if sample_count > 0:
                        questions.extend(random.sample(cat_questions, sample_count))
        
        # Ensure we have at least 8 questions
        while len(questions) < 8:
            # Add random technical questions from all categories
            all_tech_questions = []
            for cat in ["algorithms", "databases", "system_design", "devops", "security", "api_design"]:
                if cat in bank:
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
