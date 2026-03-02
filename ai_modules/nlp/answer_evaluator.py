import re
from typing import Dict, List
import nltk
from collections import Counter


class AnswerEvaluator:
    """Evaluate interview answers using NLP"""
    
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
        
        # Estimate clarity, fluency, confidence, and expression from text analysis
        clarity_score = self._estimate_clarity_from_text(answer, coherence_score, word_count, sentence_count)
        fluency_score = self._estimate_fluency_from_text(answer, word_count, sentence_count)
        confidence_score = self._estimate_confidence_from_text(answer)
        expression_score = self._estimate_expression_from_text(answer, sentiment)
        
        return {
            "content_score": round(content_score, 2),
            "relevance_score": round(relevance_score, 2),
            "clarity_score": round(clarity_score, 2),
            "fluency_score": round(fluency_score, 2),
            "confidence_score": round(confidence_score, 2),
            "expression_score": round(expression_score, 2),
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
    
    def _estimate_clarity_from_text(self, answer: str, coherence_score: float, word_count: int, sentence_count: int) -> float:
        """Estimate clarity score from text analysis (how clear and understandable the answer is)"""
        score = 60  # Base score
        
        # Coherence contributes to clarity
        score += (coherence_score - 60) * 0.3
        
        # Average sentence length: 10-20 words is ideal for clarity
        avg_len = word_count / sentence_count if sentence_count > 0 else word_count
        if 10 <= avg_len <= 20:
            score += 15
        elif 7 <= avg_len <= 25:
            score += 10
        elif 5 <= avg_len <= 30:
            score += 5
        # Very long or very short sentences reduce clarity
        
        # Multiple sentences show structured thinking
        if sentence_count >= 4:
            score += 10
        elif sentence_count >= 3:
            score += 7
        elif sentence_count >= 2:
            score += 4
        
        # Check for clear structure indicators
        structure_words = ['first', 'second', 'third', 'finally', 'in conclusion',
                          'to begin', 'next', 'lastly', 'in summary', 'overall',
                          'the reason', 'because', 'therefore', 'this means']
        answer_lower = answer.lower()
        structure_count = sum(1 for w in structure_words if w in answer_lower)
        score += min(structure_count * 3, 10)
        
        # Penalize very short answers
        if word_count < 15:
            score -= 10
        
        return max(30, min(score, 100))
    
    def _estimate_fluency_from_text(self, answer: str, word_count: int, sentence_count: int) -> float:
        """Estimate fluency score from text analysis (how smooth and well-flowing the writing is)"""
        score = 60  # Base score
        
        # Vocabulary diversity (type-token ratio)
        tokens = self.word_tokenize(answer.lower())
        if tokens:
            unique_words = set(tokens) - self.stopwords
            all_content = [t for t in tokens if t not in self.stopwords and t.isalpha()]
            if all_content:
                ttr = len(unique_words) / len(all_content) if all_content else 0
                if ttr >= 0.7:
                    score += 15
                elif ttr >= 0.5:
                    score += 10
                elif ttr >= 0.3:
                    score += 5
        
        # Transition words indicate smooth flow
        transitions = ['however', 'therefore', 'furthermore', 'moreover', 'additionally',
                       'consequently', 'thus', 'also', 'because', 'since', 'so', 'then',
                       'next', 'after', 'before', 'while', 'although', 'for example',
                       'as a result', 'in addition', 'on the other hand', 'meanwhile']
        answer_lower = answer.lower()
        trans_count = sum(1 for t in transitions if t in answer_lower)
        if trans_count >= 3:
            score += 12
        elif trans_count >= 2:
            score += 8
        elif trans_count >= 1:
            score += 5
        
        # Sentence variety (different lengths = more fluent)
        if sentence_count >= 3:
            sentences = self.sent_tokenize(answer)
            lengths = [len(s.split()) for s in sentences]
            if lengths:
                length_variety = max(lengths) - min(lengths)
                if length_variety >= 5:
                    score += 8
                elif length_variety >= 3:
                    score += 5
        
        # Word count contribution
        if word_count >= 50:
            score += 5
        elif word_count >= 30:
            score += 3
        
        # Penalize very short
        if word_count < 15:
            score -= 10
        
        return max(30, min(score, 100))
    
    def _estimate_confidence_from_text(self, answer: str) -> float:
        """Estimate confidence score from text analysis (how assertive and confident the language is)"""
        score = 60  # Base score
        
        answer_lower = answer.lower()
        tokens = self.word_tokenize(answer_lower)
        
        # Confident/assertive language
        confident_words = ['i believe', 'i am confident', 'my experience', 'i have successfully',
                          'i achieved', 'i led', 'i managed', 'i implemented', 'i created',
                          'i designed', 'i built', 'i delivered', 'i ensured', 'i established',
                          'effectively', 'efficiently', 'successfully', 'strong', 'proven',
                          'expertise', 'proficient', 'skilled', 'capable', 'accomplished',
                          'definitely', 'certainly', 'clearly', 'absolutely', 'demonstrated']
        confident_count = sum(1 for phrase in confident_words if phrase in answer_lower)
        if confident_count >= 4:
            score += 20
        elif confident_count >= 2:
            score += 14
        elif confident_count >= 1:
            score += 8
        
        # Hedging/uncertain language (reduces confidence)
        hedging_words = ['maybe', 'perhaps', 'i think', 'i guess', 'probably', 'possibly',
                        'sort of', 'kind of', 'might', 'not sure', 'i suppose', 'hopefully',
                        'try to', 'attempted to', 'somewhat', 'fairly', 'quite']
        hedge_count = sum(1 for phrase in hedging_words if phrase in answer_lower)
        if hedge_count >= 3:
            score -= 12
        elif hedge_count >= 2:
            score -= 8
        elif hedge_count >= 1:
            score -= 4
        
        # Specific/quantified statements show confidence
        import re
        numbers = re.findall(r'\d+', answer)
        if len(numbers) >= 2:
            score += 8
        elif len(numbers) >= 1:
            score += 4
        
        # Length indicates thoroughness/confidence
        word_count = len(tokens)
        if word_count >= 60:
            score += 8
        elif word_count >= 40:
            score += 5
        elif word_count >= 25:
            score += 3
        elif word_count < 15:
            score -= 8
        
        return max(30, min(score, 100))
    
    def _estimate_expression_from_text(self, answer: str, sentiment: str) -> float:
        """Estimate expression score from text analysis (emotional expressiveness, enthusiasm, engagement)"""
        score = 58  # Base score
        
        answer_lower = answer.lower()
        
        # Positive/enthusiastic language shows good expression
        expressive_words = ['passionate', 'excited', 'love', 'enjoy', 'thrilled', 'proud',
                           'inspired', 'motivated', 'enthusiastic', 'eager', 'fascinated',
                           'amazing', 'wonderful', 'incredible', 'outstanding', 'fantastic',
                           'grateful', 'rewarding', 'fulfilling', 'satisfying', 'meaningful',
                           'deeply', 'truly', 'really', 'strongly', 'firmly',
                           'i am passionate', 'i love', 'i enjoy', 'it was rewarding',
                           'i was thrilled', 'i am excited', 'great experience',
                           'really enjoyed', 'very proud', 'great opportunity']
        expressive_count = sum(1 for phrase in expressive_words if phrase in answer_lower)
        if expressive_count >= 4:
            score += 20
        elif expressive_count >= 2:
            score += 14
        elif expressive_count >= 1:
            score += 8
        
        # Sentiment contributes to expression
        if sentiment == 'positive':
            score += 10
        elif sentiment == 'neutral':
            score += 4
        # Negative sentiment can still show expression (passion about problems)
        elif sentiment == 'negative':
            score += 5
        
        # Storytelling/narrative elements show expressiveness
        narrative_words = ['when i', 'one time', 'i remember', 'there was', 'it happened',
                          'the moment', 'i felt', 'it was interesting', 'surprisingly',
                          'the challenge', 'the exciting part', 'what stood out',
                          'i realized', 'it taught me', 'looking back']
        narrative_count = sum(1 for phrase in narrative_words if phrase in answer_lower)
        if narrative_count >= 3:
            score += 10
        elif narrative_count >= 2:
            score += 7
        elif narrative_count >= 1:
            score += 4
        
        # Punctuation variety shows expressiveness (!, ?, emphasis)
        if '!' in answer:
            score += 3
        
        # Answer length - more elaborate = more expressive
        word_count = len(answer.split())
        if word_count >= 60:
            score += 8
        elif word_count >= 40:
            score += 5
        elif word_count >= 25:
            score += 3
        elif word_count < 15:
            score -= 8
        
        # Personal pronouns show engagement
        personal_words = ['i ', 'my ', 'me ', 'we ', 'our ']
        personal_count = sum(answer_lower.count(p) for p in personal_words)
        if personal_count >= 5:
            score += 5
        elif personal_count >= 3:
            score += 3
        
        return max(30, min(score, 100))
    
    def _calculate_content_score(self, answer: str, word_count: int, sentence_count: int) -> float:
        """Calculate content quality score - GENEROUS VERSION"""
        
        # Check for gibberish first (Lorem Ipsum, random chars, etc.)
        answer_lower = answer.lower()
        lorem_indicators = ['lorem', 'ipsum', 'dolor sit', 'amet', 'consectetur', 'adipiscing', 'elit', 'sed do', 'eiusmod', 'tempor incididunt', 'labore et dolore', 'magna aliqua']
        lorem_matches = sum(1 for indicator in lorem_indicators if indicator in answer_lower)
        if lorem_matches >= 2:  # If 2+ Lorem Ipsum words found, it's gibberish
            return 10
        
        # Start with base score of 65 - any reasonable answer deserves this
        score = 65
        
        # Length bonus (up to +18 points)
        if word_count >= 100:
            score += 18
        elif word_count >= 70:
            score += 15
        elif word_count >= 50:
            score += 12
        elif word_count >= 35:
            score += 9
        elif word_count >= 25:
            score += 6
        elif word_count >= 15:
            score += 3
        else:
            score += 0
        
        # Structure bonus (up to +10 points)
        if sentence_count >= 5:
            score += 10
        elif sentence_count >= 4:
            score += 8
        elif sentence_count >= 3:
            score += 6
        elif sentence_count >= 2:
            score += 4
        else:
            score += 2  # Single sentence still gets credit
        
        # Quality indicators bonus (up to +7 points)
        example_indicators = ['for example', 'for instance', 'such as', 'like', 'specifically',
                              'in my experience', 'i have', 'i worked', 'i used', 'we implemented',
                              'the result', 'this led to', 'because', 'which means', 'therefore',
                              'my approach', 'i believe', 'in particular', 'one example', 'instance',
                              'additionally', 'furthermore', 'moreover', 'first', 'second', 'finally',
                              'this means', 'as a result', 'consequently', 'thus', 'however']
        matches = sum(1 for indicator in example_indicators if indicator in answer.lower())
        if matches >= 4:
            score += 7
        elif matches >= 3:
            score += 5
        elif matches >= 2:
            score += 4
        elif matches >= 1:
            score += 3
        # No penalty for no matches - base score is generous
        
        # Total max: 65 (base) + 18 (length) + 10 (structure) + 7 (quality) = 100
        return min(score, 100)
    
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
        """Calculate answer relevance to question - GENEROUS VERSION"""
        
        # Check for gibberish/Lorem Ipsum text - return low score immediately
        answer_lower = answer.lower()
        lorem_indicators = ['lorem', 'ipsum', 'dolor sit', 'amet', 'consectetur', 'adipiscing', 'elit', 'sed do', 'eiusmod', 'tempor incididunt', 'labore et dolore', 'magna aliqua']
        lorem_matches = sum(1 for indicator in lorem_indicators if indicator in answer_lower)
        if lorem_matches >= 2:  # If 2+ Lorem Ipsum words found, it's gibberish
            return 10
        
        # Start with generous base score based on answer length
        word_count = len(answer.split())
        
        if word_count >= 80:
            score = 88
        elif word_count >= 50:
            score = 85
        elif word_count >= 35:
            score = 80
        elif word_count >= 25:
            score = 75
        elif word_count >= 15:
            score = 70
        else:
            score = 65
        
        # Small bonus for question word overlap (up to +5)
        question_words = set(self.word_tokenize(question.lower())) - self.stopwords
        answer_words = set(self.word_tokenize(answer.lower())) - self.stopwords
        
        if question_words:
            overlap = len(question_words & answer_words) / len(question_words)
            score += min(overlap * 5, 5)
        
        # Small bonus for keyword matches (up to +7)
        if expected_keywords:
            answer_lower = answer.lower()
            found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
            keyword_ratio = found / len(expected_keywords) if expected_keywords else 0
            score += keyword_ratio * 7
        
        return min(score, 100)
    
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
        """Generate warm, constructive, human-friendly per-question feedback"""
        feedback_parts = []
        
        overall_score = (content_score + relevance_score + coherence_score) / 3
        
        # --- Opening: warm and specific rather than generic ---
        if overall_score >= 85:
            feedback_parts.append("Excellent answer! You covered the key points really well and your response was well-organized.")
        elif overall_score >= 75:
            feedback_parts.append("Good job on this one! You touched on the important aspects and communicated clearly.")
        elif overall_score >= 65:
            feedback_parts.append("Solid answer with some good points. A few additions would make it even stronger.")
        elif overall_score >= 55:
            feedback_parts.append("You're on the right track here, but there's room to make this answer more complete.")
        elif overall_score >= 45:
            feedback_parts.append("This answer covers some basics, but could use more depth and structure to really stand out.")
        else:
            feedback_parts.append("This one needs more work — try to address the question more directly and include specific details.")
        
        # --- Content-specific feedback ---
        if content_score < 50:
            if word_count < 20:
                feedback_parts.append("Your answer was quite short. Try to elaborate more — aim for at least 3-4 sentences to give a complete response.")
            elif word_count < 40:
                feedback_parts.append("Try to add more substance — include a specific example from your experience or explain your reasoning in more detail.")
            else:
                feedback_parts.append("While you wrote enough, the content could be more focused. Try structuring it with a clear point, supporting evidence, and a conclusion.")
        elif content_score < 70:
            feedback_parts.append("Good foundation — now try to strengthen it with a concrete example or quantifiable result (like \"reduced load time by 40%\").")
        
        # --- Relevance feedback ---
        if relevance_score < 50:
            feedback_parts.append("Make sure you're directly addressing what the question is asking before adding context.")
            if keyword_analysis["missing"]:
                missing = keyword_analysis["missing"][:3]
                feedback_parts.append(f"Try to incorporate these key concepts: {', '.join(missing)}.")
        elif relevance_score < 70 and keyword_analysis["missing"]:
            missing = keyword_analysis["missing"][:2]
            feedback_parts.append(f"Consider also mentioning: {', '.join(missing)} — these are important aspects the interviewer likely expects.")
        
        # --- Coherence feedback ---
        if coherence_score < 55:
            feedback_parts.append("Try connecting your ideas with transition phrases like \"for example,\" \"as a result,\" or \"building on this\" to create a smoother flow.")
        elif coherence_score < 70:
            feedback_parts.append("Your ideas are good — using clearer transitions between them would make the answer easier to follow.")
        
        # --- Positive reinforcement for keywords found ---
        if keyword_analysis.get("found") and len(keyword_analysis["found"]) >= 2 and overall_score >= 60:
            feedback_parts.append(f"Nice use of relevant concepts like {', '.join(keyword_analysis['found'][:2])}!")
        
        return " ".join(feedback_parts)
    
    def _generate_suggestions(
        self,
        content_score: float,
        relevance_score: float,
        keyword_analysis: Dict,
        question_type: str
    ) -> List[str]:
        """Generate specific, actionable improvement suggestions"""
        suggestions = []
        
        # Content improvements
        if content_score < 50:
            suggestions.append("Add a concrete example from your personal experience — even a brief one makes your answer much more convincing")
            suggestions.append("Try to explain your thought process step by step — this shows depth of understanding")
        elif content_score < 70:
            suggestions.append("Strengthen your answer by quantifying results (e.g., 'reduced errors by 25%' or 'served 1000+ users')")
        elif content_score < 85:
            suggestions.append("Consider adding a comparison or trade-off discussion to show advanced understanding")
        
        # Relevance improvements
        if relevance_score < 60:
            suggestions.append("Start by directly answering the question in your first sentence, then expand with details")
            if keyword_analysis.get("missing"):
                missing = keyword_analysis["missing"][:2]
                suggestions.append(f"Try to naturally include these concepts: {', '.join(missing)}")
        elif relevance_score < 80 and keyword_analysis.get("missing"):
            missing = keyword_analysis["missing"][:2]
            suggestions.append(f"Mentioning {', '.join(missing)} would make your answer more complete")
        
        # Question-type specific guidance
        if question_type == "behavioral":
            suggestions.append("Use the STAR method: set the Scene, describe your Task, explain your Actions, and share the Results")
            if content_score < 70:
                suggestions.append("End with what you learned from the experience — interviewers love seeing growth mindset")
        elif question_type == "technical":
            suggestions.append("Walk through your reasoning — explain why you'd choose one approach over alternatives")
            if content_score >= 70:
                suggestions.append("Discuss edge cases or limitations to show thorough understanding")
        elif question_type == "situational":
            suggestions.append("Paint a clear picture of the situation first, then describe how you'd handle it step by step")
            suggestions.append("Connect your approach to a past experience if possible — it adds credibility")
        elif question_type == "hr" or question_type == "general":
            suggestions.append("Be specific rather than generic — replace 'I'm a hard worker' with a specific example that proves it")
        
        return suggestions[:5]
