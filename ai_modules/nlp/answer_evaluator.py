import re
import os
from typing import Dict, List
import nltk
from collections import Counter
import numpy as np


class AnswerEvaluator:
    """Evaluate interview answers using NLP with semantic similarity"""
    
    # Class-level model to avoid reloading
    _embedding_model = None
    _model_load_attempted = False
    
    # Local model path (relative to project root)
    LOCAL_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'models', 'all-MiniLM-L6-v2')
    
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize, sent_tokenize
        
        self.stopwords = set(stopwords.words('english'))
        self.word_tokenize = word_tokenize
        self.sent_tokenize = sent_tokenize
        
        # Load sentence-transformers model (singleton pattern)
        self._load_embedding_model()
    
    @classmethod
    def _load_embedding_model(cls):
        """Load sentence-transformers model once (lazy loading with singleton)"""
        if cls._model_load_attempted:
            return
        
        cls._model_load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            
            # Try local model first (faster, no network needed)
            local_path = os.path.abspath(cls.LOCAL_MODEL_PATH)
            if os.path.exists(local_path) and os.path.isdir(local_path):
                cls._embedding_model = SentenceTransformer(local_path)
                print(f"[AnswerEvaluator] Loaded local sentence-transformers model from {local_path}")
            else:
                # Fallback to downloading from HuggingFace
                cls._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[AnswerEvaluator] Loaded sentence-transformers model from HuggingFace")
        except Exception as e:
            print(f"[AnswerEvaluator] Could not load embedding model, using heuristics: {e}")
            cls._embedding_model = None
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def _calculate_semantic_similarity(self, question: str, answer: str, expected_keywords: List[str] = None) -> float:
        """
        Calculate semantic similarity using embeddings with structured scoring bands:
        
        SCORING BANDS:
        0-20:  Lorem Ipsum / totally gibberish / nonsense text
        20-40: Proper English but obviously off-topic / no relevance
        40-60: Slightly off-topic / one or two keywords / little relevance
        60-80: On topic / few keyword matches / moderate relevance / moderate length
        80-100: Perfect alignment / keyword matching / high relevance / well-formed sentences
        """
        if self._embedding_model is None:
            return None  # Fallback to heuristics
        
        try:
            answer_lower = answer.lower()
            
            # BAND 0-20: Gibberish/Lorem Ipsum detection
            lorem_indicators = ['lorem', 'ipsum', 'dolor sit', 'amet', 'consectetur', 'adipiscing', 
                               'elit', 'sed do', 'eiusmod', 'tempor incididunt']
            lorem_matches = sum(1 for indicator in lorem_indicators if indicator in answer_lower)
            if lorem_matches >= 2:
                return 10 + (min(lorem_matches, 5) * 2)  # 10-20 range
            
            # BAND 0-20: Test/meta responses
            test_indicators = ['this is a test', 'gonna be a test', 'going to be a test', 'it is a test', 
                             'just a test', 'testing the system', 'sample text', 'placeholder', 
                             'non-relevant', 'non-vervent', 'off topic', 'off-topic', 'checking whether', 
                             'check whether', 'evaluation system', 'scoring system', 'test so far']
            test_matches = sum(1 for indicator in test_indicators if indicator in answer_lower)
            if test_matches >= 1:
                return 15  # Clearly a test response
            
            # Encode question and answer for semantic similarity
            q_embedding = self._embedding_model.encode(question, convert_to_numpy=True)
            a_embedding = self._embedding_model.encode(answer, convert_to_numpy=True)
            
            # Calculate cosine similarity (0.0 to 1.0)
            similarity = self._cosine_similarity(q_embedding, a_embedding)
            
            # Count keyword matches
            keyword_ratio = 0
            keywords_found = 0
            if expected_keywords:
                keywords_found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
                keyword_ratio = keywords_found / len(expected_keywords)
            
            # Word count for length assessment
            word_count = len(answer.split())
            
            # === DETERMINE SCORING BAND ===
            
            # BAND 80-100: High similarity + good keywords + decent length
            if similarity >= 0.5 and keyword_ratio >= 0.5 and word_count >= 25:
                base = 80
                # Bonus for higher similarity (up to +10)
                base += min((similarity - 0.5) * 20, 10)
                # Bonus for more keywords (up to +5)
                base += min(keyword_ratio * 5, 5)
                # Bonus for longer, detailed answers (up to +5)
                if word_count >= 50:
                    base += 5
                elif word_count >= 35:
                    base += 3
                return min(base, 100)
            
            # BAND 60-80: Moderate similarity OR good keywords
            if (similarity >= 0.35 and keyword_ratio >= 0.3) or (similarity >= 0.45) or (keyword_ratio >= 0.6):
                base = 60
                # Add based on similarity
                base += min((similarity - 0.35) * 30, 10)
                # Add based on keywords
                base += min(keyword_ratio * 10, 10)
                return min(max(base, 60), 79)
            
            # BAND 40-60: Some relevance OR some keywords
            if similarity >= 0.25 or keyword_ratio >= 0.2:
                base = 40
                # Add based on similarity
                base += min((similarity - 0.1) * 40, 12)
                # Add based on keywords
                base += min(keyword_ratio * 8, 8)
                return min(max(base, 40), 59)
            
            # BAND 20-40: Proper English but off-topic (low similarity, no keywords)
            if similarity >= 0.1:
                base = 20
                base += min(similarity * 100, 15)
                # Small bonus if answer is coherent English (length check)
                if word_count >= 20:
                    base += 5
                return min(max(base, 20), 39)
            
            # BAND 0-20: Very low similarity (essentially random/gibberish)
            return max(10, similarity * 100)
            
        except Exception as e:
            print(f"[AnswerEvaluator] Semantic similarity error: {e}")
            return None  # Fallback to heuristics
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_keywords: List[str] = None,
        question_type: str = "general"
    ) -> Dict:
        """Evaluate answer comprehensively"""
        
        if not answer or len(answer.strip()) < 10:
            return {
                "content_score": 0,
                "relevance_score": 0,
                "nlp_analysis": {
                    "word_count": 0,
                    "sentence_count": 0,
                    "keywords_found": [],
                    "sentiment": "neutral"
                },
                "feedback": "Answer is too short. Please provide a more detailed response.",
                "suggestions": ["Provide more details and examples", "Explain your thought process"]
            }
        
        # Perform various analyses
        word_count = len(self.word_tokenize(answer))
        sentence_count = len(self.sent_tokenize(answer))
        
        # Calculate scores
        content_score = self._calculate_content_score(answer, word_count, sentence_count)
        relevance_score = self._calculate_relevance_score(question, answer, expected_keywords)
        keyword_analysis = self._analyze_keywords(answer, expected_keywords)
        sentiment = self._analyze_sentiment(answer)
        coherence_score = self._calculate_coherence(answer)
        
        # Overall feedback
        feedback = self._generate_feedback(
            content_score, relevance_score, coherence_score,
            word_count, keyword_analysis
        )
        
        suggestions = self._generate_suggestions(
            content_score, relevance_score, keyword_analysis, question_type
        )
        
        return {
            "content_score": round(content_score, 2),
            "relevance_score": round(relevance_score, 2),
            "nlp_analysis": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "keywords_found": keyword_analysis["found"],
                "keywords_missing": keyword_analysis["missing"],
                "sentiment": sentiment,
                "coherence_score": round(coherence_score, 2),
                "avg_sentence_length": round(word_count / sentence_count if sentence_count > 0 else 0, 2)
            },
            "feedback": feedback,
            "suggestions": suggestions
        }
    
    def _calculate_content_score(self, answer: str, word_count: int, sentence_count: int) -> float:
        """
        Calculate content quality score with structured scoring bands:
        
        SCORING BANDS:
        0-20:  Lorem Ipsum / gibberish / test responses
        20-40: Very short or poorly structured
        40-60: Basic answer, minimal structure
        60-80: Good length and structure, some quality indicators
        80-100: Excellent length, structure, and quality indicators
        """
        answer_lower = answer.lower()
        
        # BAND 0-20: Gibberish detection
        lorem_indicators = ['lorem', 'ipsum', 'dolor sit', 'amet', 'consectetur', 'adipiscing', 
                           'elit', 'sed do', 'eiusmod', 'tempor incididunt']
        lorem_matches = sum(1 for indicator in lorem_indicators if indicator in answer_lower)
        if lorem_matches >= 2:
            return 10
        
        # BAND 0-20: Test/meta responses
        test_indicators = ['this is a test', 'gonna be a test', 'going to be a test', 'it is a test', 
                          'just a test', 'testing the system', 'sample text', 'placeholder', 
                          'non-relevant', 'non-vervent', 'off topic', 'off-topic', 'checking whether',
                          'check whether', 'evaluation system', 'scoring system', 'test so far']
        test_matches = sum(1 for indicator in test_indicators if indicator in answer_lower)
        if test_matches >= 1:
            return 15
        
        # Quality indicators
        quality_indicators = ['for example', 'for instance', 'such as', 'specifically',
                             'in my experience', 'i have', 'i worked', 'i used', 'we implemented',
                             'the result', 'this led to', 'because', 'which means', 'therefore',
                             'my approach', 'i believe', 'in particular', 'one example',
                             'additionally', 'furthermore', 'moreover', 'first', 'second', 'finally',
                             'this means', 'as a result', 'consequently', 'thus', 'however']
        quality_matches = sum(1 for indicator in quality_indicators if indicator in answer_lower)
        
        # === DETERMINE SCORING BAND ===
        
        # BAND 80-100: Excellent content
        if word_count >= 50 and sentence_count >= 4 and quality_matches >= 3:
            base = 80
            if word_count >= 80:
                base += 8
            elif word_count >= 60:
                base += 5
            if quality_matches >= 5:
                base += 7
            elif quality_matches >= 4:
                base += 5
            if sentence_count >= 6:
                base += 5
            return min(base, 100)
        
        # BAND 60-80: Good content
        if (word_count >= 30 and sentence_count >= 3) or (word_count >= 40 and quality_matches >= 2):
            base = 60
            if word_count >= 50:
                base += 8
            elif word_count >= 40:
                base += 5
            if quality_matches >= 3:
                base += 6
            elif quality_matches >= 2:
                base += 4
            if sentence_count >= 4:
                base += 5
            return min(max(base, 60), 79)
        
        # BAND 40-60: Basic content
        if word_count >= 15 and sentence_count >= 2:
            base = 40
            if word_count >= 25:
                base += 10
            elif word_count >= 20:
                base += 6
            if quality_matches >= 1:
                base += 5
            if sentence_count >= 3:
                base += 4
            return min(max(base, 40), 59)
        
        # BAND 20-40: Minimal content
        if word_count >= 8:
            base = 20
            base += min(word_count, 15)  # Up to +15 for word count
            if sentence_count >= 2:
                base += 4
            return min(max(base, 20), 39)
        
        # BAND 0-20: Too short
        return max(10, word_count * 2)
    
    def _check_english_content(self, answer: str) -> float:
        """
        Check if the answer contains real English words.
        Returns ratio of recognized English words (0.0 to 1.0).
        """
        # Expanded common English words list for better detection
        common_english = {
            # Articles, pronouns, prepositions
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
            'when', 'make', 'can', 'time', 'no', 'just', 'him', 'know', 'take', 'people',
            'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
            'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back',
            'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
            'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is',
            'was', 'are', 'were', 'been', 'being', 'had', 'has', 'did', 'does', 'done',
            'am', 'here', 'where', 'why', 'very', 'much', 'more', 'before', 'should', 'need',
            'like', 'used', 'using', 'working', 'worked', 'experience', 'team', 'project',
            'approach', 'example', 'situation', 'result', 'problem', 'solution', 'task',
            'believe', 'help', 'ensure', 'important', 'able', 'through', 'while', 'during',
            # Additional common interview/professional words
            'achieve', 'achieved', 'action', 'actions', 'additionally', 'address', 'addressed',
            'analysis', 'analyze', 'apply', 'based', 'became', 'become', 'began', 'begin',
            'better', 'both', 'bringing', 'build', 'building', 'business', 'called', 'came',
            'challenge', 'challenges', 'change', 'changed', 'clear', 'clearly', 'collaborate',
            'collaboration', 'combined', 'communication', 'company', 'complete', 'completed',
            'complex', 'confidence', 'confident', 'consider', 'consistent', 'context',
            'contribute', 'contributed', 'create', 'created', 'critical', 'current', 'data',
            'deadline', 'decision', 'decisions', 'define', 'defined', 'deliver', 'delivered',
            'demonstrate', 'demonstrated', 'design', 'designed', 'detail', 'details', 'develop',
            'developed', 'development', 'different', 'discuss', 'each', 'effective', 'effectively',
            'effort', 'enable', 'end', 'engagement', 'ensure', 'ensured', 'environment',
            'essential', 'establish', 'established', 'evaluate', 'evaluated', 'every', 'execution',
            'expand', 'expected', 'experience', 'explain', 'faced', 'fact', 'fast', 'feedback',
            'feel', 'final', 'finally', 'find', 'focus', 'focused', 'follow', 'following',
            'forward', 'found', 'framework', 'furthermore', 'future', 'gain', 'gave', 'goal',
            'goals', 'going', 'great', 'group', 'grow', 'growth', 'handle', 'handled', 'hard',
            'helped', 'high', 'however', 'idea', 'ideas', 'identify', 'identified', 'impact',
            'implement', 'implemented', 'implementing', 'improve', 'improved', 'improvement',
            'include', 'including', 'increase', 'increased', 'individual', 'information',
            'initially', 'initiative', 'instead', 'integrate', 'interest', 'issue', 'issues',
            'job', 'keep', 'key', 'large', 'last', 'lead', 'leadership', 'leading', 'learn',
            'learned', 'learning', 'led', 'let', 'level', 'long', 'maintain', 'maintained',
            'major', 'making', 'manage', 'managed', 'management', 'many', 'matter', 'may',
            'measurable', 'meet', 'meeting', 'member', 'members', 'method', 'might', 'milestones',
            'mind', 'mindset', 'minute', 'moment', 'moreover', 'move', 'multiple', 'must',
            'necessary', 'needed', 'never', 'next', 'number', 'objective', 'objectives', 'often',
            'once', 'open', 'opportunity', 'order', 'organization', 'organized', 'original',
            'others', 'outcome', 'outcomes', 'overall', 'own', 'part', 'particular', 'past',
            'path', 'pattern', 'performance', 'period', 'person', 'personal', 'perspective',
            'place', 'plan', 'planned', 'planning', 'plans', 'point', 'position', 'positive',
            'possible', 'potential', 'practice', 'present', 'previous', 'primary', 'priorities',
            'priority', 'proactive', 'process', 'processes', 'productive', 'professional',
            'progress', 'provide', 'provided', 'purpose', 'put', 'quality', 'question', 'questions',
            'quickly', 'rather', 'reach', 'reached', 'real', 'realize', 'really', 'reason',
            'receive', 'received', 'recognize', 'recommend', 'record', 'reduce', 'reduced',
            'regular', 'related', 'relationship', 'relevant', 'remain', 'report', 'required',
            'resource', 'resources', 'response', 'responsibility', 'responsible', 'results',
            'review', 'right', 'risk', 'role', 'run', 'running', 'same', 'scale', 'schedule',
            'seek', 'self', 'sense', 'set', 'setting', 'several', 'short', 'show', 'side',
            'significant', 'similar', 'simple', 'since', 'single', 'skill', 'skills', 'small',
            'specific', 'specifically', 'speed', 'spent', 'stage', 'stakeholder', 'stakeholders',
            'standard', 'start', 'started', 'state', 'stay', 'step', 'steps', 'still', 'strategy',
            'strength', 'strengths', 'strong', 'structure', 'structured', 'success', 'successful',
            'successfully', 'such', 'suggest', 'support', 'sure', 'system', 'systems', 'taken',
            'taking', 'target', 'team', 'teams', 'technical', 'technology', 'term', 'terms',
            'therefore', 'thing', 'things', 'third', 'those', 'thought', 'three', 'thus',
            'timeline', 'timelines', 'together', 'tool', 'tools', 'top', 'total', 'track',
            'tracking', 'training', 'translate', 'true', 'try', 'type', 'ultimately', 'under',
            'understand', 'understanding', 'unique', 'unit', 'until', 'update', 'upon', 'value',
            'various', 'view', 'want', 'wanted', 'week', 'weekly', 'whether', 'within', 'without',
            'word', 'words', 'worked', 'working', 'world', 'would', 'write', 'written', 'yet'
        }
        
        words = answer.lower().split()
        if not words:
            return 0.0
        
        # Count how many words are recognized English
        english_word_count = sum(1 for word in words if word.strip('.,!?;:()[]"\'') in common_english)
        
        # Calculate ratio
        ratio = english_word_count / len(words)
        return ratio
    
    def _calculate_relevance_score(
        self,
        question: str,
        answer: str,
        expected_keywords: List[str] = None
    ) -> float:
        """Calculate answer relevance using semantic similarity (with heuristic fallback)"""
        
        # Check for gibberish/Lorem Ipsum text - return low score immediately
        answer_lower = answer.lower()
        lorem_indicators = ['lorem', 'ipsum', 'dolor sit', 'amet', 'consectetur', 'adipiscing', 'elit', 'sed do', 'eiusmod', 'tempor incididunt', 'labore et dolore', 'magna aliqua']
        lorem_matches = sum(1 for indicator in lorem_indicators if indicator in answer_lower)
        if lorem_matches >= 2:  # If 2+ Lorem Ipsum words found, it's gibberish
            return 10
        
        # Check for test/meta responses
        test_indicators = ['this is a test', 'gonna be a test', 'going to be a test', 'it is a test', 
                          'just a test', 'testing', 'sample text', 'placeholder', 'non-relevant', 
                          'non-vervent', 'off topic', 'off-topic', 'checking whether', 'check whether',
                          'evaluation system', 'scoring system', 'test so far', 'sample piece']
        test_matches = sum(1 for indicator in test_indicators if indicator in answer_lower)
        if test_matches >= 1:
            return 20  # Very low score for test/meta responses
        
        # Try semantic similarity first (uses embeddings + cosine similarity)
        semantic_score = self._calculate_semantic_similarity(question, answer, expected_keywords)
        if semantic_score is not None:
            return semantic_score
        
        # === HEURISTIC FALLBACK (when embeddings unavailable) ===
        # Following the same scoring bands as semantic similarity
        
        word_count = len(answer.split())
        
        # Question word overlap
        question_words = set(self.word_tokenize(question.lower())) - self.stopwords
        answer_words = set(self.word_tokenize(answer.lower())) - self.stopwords
        
        overlap_ratio = 0
        if question_words:
            overlap_ratio = len(question_words & answer_words) / len(question_words)
        
        # Keyword analysis with stem matching
        keyword_ratio = 0
        keywords_found = 0
        if expected_keywords:
            for kw in expected_keywords:
                kw_lower = kw.lower()
                if kw_lower in answer_lower:
                    keywords_found += 1
                else:
                    # Stem matching
                    kw_stem = kw_lower[:4] if len(kw_lower) >= 4 else kw_lower
                    for word in answer_words:
                        if kw_stem in word or (len(word) >= 4 and word[:4] == kw_stem):
                            keywords_found += 1
                            break
            keyword_ratio = keywords_found / len(expected_keywords)
        
        # Combined relevance score (overlap + keywords)
        combined_relevance = (overlap_ratio * 0.4) + (keyword_ratio * 0.6)
        
        # === DETERMINE SCORING BAND ===
        
        # BAND 80-100: High relevance
        if combined_relevance >= 0.5 and word_count >= 25:
            base = 80
            base += min(combined_relevance * 15, 12)
            if word_count >= 50:
                base += 5
            return min(base, 100)
        
        # BAND 60-80: Moderate relevance
        if combined_relevance >= 0.3 or (keyword_ratio >= 0.4 and word_count >= 20):
            base = 60
            base += min(combined_relevance * 20, 12)
            if word_count >= 35:
                base += 5
            return min(max(base, 60), 79)
        
        # BAND 40-60: Some relevance
        if combined_relevance >= 0.15 or keyword_ratio >= 0.2:
            base = 40
            base += min(combined_relevance * 30, 12)
            if word_count >= 25:
                base += 5
            return min(max(base, 40), 59)
        
        # BAND 20-40: Low relevance (proper English but off-topic)
        if word_count >= 15:
            base = 25
            base += min(overlap_ratio * 10, 8)
            if word_count >= 30:
                base += 5
            return min(max(base, 20), 39)
        
        # BAND 0-20: Very low relevance
        return max(15, 20 + (combined_relevance * 10))
    
    def _analyze_keywords(self, answer: str, expected_keywords: List[str] = None) -> Dict:
        """Analyze keyword presence"""
        result = {"found": [], "missing": [], "score": 0}
        
        if not expected_keywords:
            return result
        
        answer_lower = answer.lower()
        
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                result["found"].append(keyword)
            else:
                result["missing"].append(keyword)
        
        if expected_keywords:
            result["score"] = (len(result["found"]) / len(expected_keywords)) * 100
        
        return result
    
    def _analyze_sentiment(self, answer: str) -> str:
        """Analyze sentiment of answer"""
        # Simple sentiment analysis based on keywords
        positive_words = ['good', 'great', 'excellent', 'successful', 'achieved', 'improved', 
                         'effective', 'efficient', 'productive', 'positive', 'satisfied']
        negative_words = ['bad', 'poor', 'failed', 'difficult', 'challenging', 'problem', 
                         'issue', 'struggled', 'negative', 'unfortunately']
        
        answer_lower = answer.lower()
        tokens = self.word_tokenize(answer_lower)
        
        positive_count = sum(1 for word in tokens if word in positive_words)
        negative_count = sum(1 for word in tokens if word in negative_words)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_coherence(self, answer: str) -> float:
        """Calculate answer coherence"""
        score = 80  # Higher base score - most answers have reasonable coherence
        
        sentences = self.sent_tokenize(answer)
        
        if len(sentences) < 2:
            return 75  # Single sentence still gets good coherence
        
        # Check for transition words
        transitions = ['however', 'therefore', 'furthermore', 'moreover', 'additionally',
                      'consequently', 'nevertheless', 'meanwhile', 'subsequently', 'thus',
                      'first', 'second', 'finally', 'also', 'because', 'since',
                      'so', 'then', 'next', 'after', 'before', 'while', 'although',
                      'for example', 'as a result', 'in addition', 'this means', 'which']
        
        answer_lower = answer.lower()
        transition_count = sum(1 for trans in transitions if trans in answer_lower)
        
        if transition_count >= 4:
            score += 15
        elif transition_count >= 3:
            score += 12
        elif transition_count >= 2:
            score += 8
        elif transition_count >= 1:
            score += 5
        
        # Bonus for multiple well-formed sentences
        if len(sentences) >= 5:
            score += 5
        elif len(sentences) >= 3:
            score += 3
        
        return min(score, 100)
    
    def _generate_feedback(
        self,
        content_score: float,
        relevance_score: float,
        coherence_score: float,
        word_count: int,
        keyword_analysis: Dict
    ) -> str:
        """
        Generate feedback based on scoring bands:
        0-20:  Gibberish/test response
        20-40: Off-topic response
        40-60: Slightly off-topic
        60-80: Good, on-topic
        80-100: Excellent
        """
        feedback_parts = []
        avg_score = (content_score + relevance_score) / 2
        
        # BAND 0-20: Gibberish or test
        if avg_score < 20:
            feedback_parts.append("This response appears to be a test or placeholder text.")
            feedback_parts.append("Please provide a genuine answer to the question.")
            return " ".join(feedback_parts)
        
        # BAND 20-40: Obviously off-topic
        if relevance_score < 40 or avg_score < 40:
            feedback_parts.append("Your answer does not address the question asked.")
            feedback_parts.append("Focus on the specific topic and provide relevant information.")
            if keyword_analysis["missing"]:
                feedback_parts.append(f"Key topics to cover: {', '.join(keyword_analysis['missing'][:3])}")
            return " ".join(feedback_parts)
        
        # BAND 40-60: Slightly off-topic
        if relevance_score < 60 or avg_score < 60:
            feedback_parts.append("Your answer is somewhat relevant but could be more focused.")
            if keyword_analysis["missing"]:
                feedback_parts.append(f"Consider discussing: {', '.join(keyword_analysis['missing'][:3])}")
            if content_score < 50:
                feedback_parts.append("Add more detail and specific examples.")
            return " ".join(feedback_parts)
        
        # BAND 60-80: Good, on-topic
        if avg_score < 80:
            feedback_parts.append("Good answer that addresses the question.")
            if relevance_score < 70:
                feedback_parts.append("Try to be more specific to the question asked.")
            if content_score < 70:
                feedback_parts.append("Adding more examples would strengthen your response.")
            if keyword_analysis["missing"] and len(keyword_analysis["missing"]) > 0:
                feedback_parts.append(f"You could also mention: {', '.join(keyword_analysis['missing'][:2])}")
            return " ".join(feedback_parts)
        
        # BAND 80-100: Excellent
        feedback_parts.append("Excellent answer! Well-structured and directly addresses the question.")
        if content_score >= 85 and relevance_score >= 85:
            feedback_parts.append("Your response demonstrates strong understanding of the topic.")
        if keyword_analysis["found"]:
            feedback_parts.append("Good use of relevant terminology.")
        
        return " ".join(feedback_parts)
    
    def _generate_suggestions(
        self,
        content_score: float,
        relevance_score: float,
        keyword_analysis: Dict,
        question_type: str
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if content_score < 70:
            suggestions.append("Provide more specific examples from your experience")
            suggestions.append("Elaborate on your thought process and reasoning")
        
        if relevance_score < 70:
            suggestions.append("Ensure you directly answer the question")
            if keyword_analysis.get("missing"):
                suggestions.append(f"Include key concepts like: {', '.join(keyword_analysis['missing'][:2])}")
        
        if question_type == "behavioral":
            suggestions.append("Use the STAR method: Situation, Task, Action, Result")
        elif question_type == "technical":
            suggestions.append("Include technical details and explain your reasoning")
            suggestions.append("Discuss trade-offs and alternative approaches")
        elif question_type == "situational":
            suggestions.append("Describe the context clearly")
            suggestions.append("Explain the impact of your actions")
        
        return suggestions[:5]  # Return top 5 suggestions
