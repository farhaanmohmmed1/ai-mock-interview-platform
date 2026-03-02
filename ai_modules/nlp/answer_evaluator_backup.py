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
        """Calculate content quality score"""
        score = 0
        
        # First, check for gibberish/non-English content
        english_ratio = self._check_english_content(answer)
        if english_ratio < 0.25:
            # Severe penalty for gibberish (like Lorem Ipsum)
            return max(10, 30 * english_ratio)  # Max 7.5 points for mostly non-English
        
        # Length scoring (0-30 points) - generous for detailed answers
        if word_count < 15:
            score += (word_count / 15) * 15
        elif word_count < 40:
            score += 15 + ((word_count - 15) / 25) * 5  # 15-20
        elif word_count < 80:
            score += 20 + ((word_count - 40) / 40) * 5  # 20-25
        elif word_count < 150:
            score += 25 + ((word_count - 80) / 70) * 5  # 25-30
        else:
            score += 30  # Very detailed answer
        
        # Structure scoring (0-18 points)
        if sentence_count >= 6:
            score += 18
        elif sentence_count >= 5:
            score += 17
        elif sentence_count >= 4:
            score += 15
        elif sentence_count >= 3:
            score += 13
        elif sentence_count >= 2:
            score += 11
        else:
            score += 8  # Single sentence still gets credit
        
        # Check for examples/specifics (0-18 points)
        example_indicators = ['for example', 'for instance', 'such as', 'like', 'specifically',
                              'in my experience', 'i have', 'i worked', 'i used', 'we implemented',
                              'the result', 'this led to', 'because', 'which means', 'therefore',
                              'my approach', 'i believe', 'in particular', 'one example', 'instance',
                              'additionally', 'furthermore', 'moreover', 'first', 'second', 'finally',
                              'this means', 'as a result', 'consequently', 'thus', 'however']
        matches = sum(1 for indicator in example_indicators if indicator in answer.lower())
        if matches >= 5:
            score += 18
        elif matches >= 4:
            score += 16
        elif matches >= 3:
            score += 14
        elif matches >= 2:
            score += 12
        elif matches >= 1:
            score += 10
        else:
            score += 7  # Base credit
        
        # Complexity & vocabulary (0-10 points)
        avg_word_length = sum(len(word) for word in answer.split()) / len(answer.split()) if answer.split() else 0
        if avg_word_length > 5.5:
            score += 10
        elif avg_word_length > 5.0:
            score += 9
        elif avg_word_length > 4.5:
            score += 8
        elif avg_word_length > 4.0:
            score += 7
        else:
            score += 5
        
        # STAR method / structured response bonus (0-14 points)
        answer_lower = answer.lower()
        star_indicators = {
            'situation': ['situation', 'context', 'when i', 'at my', 'in my previous', 'there was', 'while working', 'during my'],
            'task': ['task', 'challenge', 'needed to', 'had to', 'responsible for', 'goal was', 'objective', 'required', 'aimed to'],
            'action': ['i decided', 'i implemented', 'i coordinated', 'my approach', 'i took', 'i created', 'i developed', 'i set', 'i used', 'i followed', 'i established', 'i focused'],
            'result': ['result', 'outcome', 'as a result', 'this led to', 'we achieved', 'improved by', 'reduced', 'increased', 'ultimately', 'consequently', 'success', 'accomplished']
        }
        star_count = 0
        for category, indicators in star_indicators.items():
            if any(ind in answer_lower for ind in indicators):
                star_count += 1
        
        if star_count >= 4:
            score += 14  # Full STAR method
        elif star_count >= 3:
            score += 11
        elif star_count >= 2:
            score += 8
        elif star_count >= 1:
            score += 5
        
        # Excellence bonus for comprehensive answers (0-15 points)
        # Reward answers that combine multiple quality indicators
        excellence_count = 0
        if word_count >= 120:
            excellence_count += 2  # Double credit for very detailed
        elif word_count >= 80:
            excellence_count += 1
        if sentence_count >= 6:
            excellence_count += 1
        if matches >= 4:
            excellence_count += 1
        if star_count >= 3:
            excellence_count += 1
        if avg_word_length > 5.0:
            excellence_count += 1
        
        if excellence_count >= 5:
            score += 15
        elif excellence_count >= 4:
            score += 12
        elif excellence_count >= 3:
            score += 8
        elif excellence_count >= 2:
            score += 5
        
        # Apply English content ratio as multiplier ONLY for suspected gibberish
        # Normal English text gets at least 0.35-0.5 ratio with our common word list
        # Only penalize if ratio is very low (likely non-English or gibberish)
        if english_ratio < 0.25:
            # Severe penalty for gibberish
            score *= (0.4 + english_ratio * 2)  # 0.4 to 0.9 multiplier
        elif english_ratio < 0.35:
            # Mild penalty for unusual text
            score *= 0.95
        # Otherwise, no penalty - normal English answers shouldn't be penalized
        
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
        """Calculate answer relevance to question"""
        score = 0
        
        # Extract key terms from question
        question_words = set(self.word_tokenize(question.lower()))
        answer_words = set(self.word_tokenize(answer.lower()))
        
        # Remove stopwords
        question_keywords = question_words - self.stopwords
        answer_keywords = answer_words - self.stopwords
        
        # Calculate overlap (0-25 points) - reduced weight, exact matching is too strict
        if question_keywords:
            overlap = len(question_keywords & answer_keywords) / len(question_keywords)
            score += overlap * 25
        
        # Base score for having substantial answer (0-30 points)
        # This rewards thoughtful answers even when they use different vocabulary
        if len(answer_keywords) >= 30:
            score += 30
        elif len(answer_keywords) >= 20:
            score += 28
        elif len(answer_keywords) >= 15:
            score += 25
        elif len(answer_keywords) >= 10:
            score += 20
        elif len(answer_keywords) >= 5:
            score += 15
        else:
            score += 8
        
        # Expected keywords (0-35 points) - with partial/stem matching and synonyms
        if expected_keywords and len(expected_keywords) > 0:
            keywords_lower = [k.lower() for k in expected_keywords]
            answer_lower = answer.lower()
            found_count = 0
            
            # Common synonyms for interview keywords
            synonym_map = {
                'teamwork': ['team', 'collaborate', 'together', 'cooperation', 'collective', 'group', 'joint'],
                'collaboration': ['team', 'work together', 'cooperate', 'partner', 'joint', 'collective'],
                'motivation': ['motivated', 'driven', 'passionate', 'enthusiastic', 'dedicated', 'focused', 'committed', 'engaged'],
                'persistence': ['persistent', 'persevere', 'determined', 'resilient', 'tenacity', 'consistent', 'sustained'],
                'attitude': ['approach', 'mindset', 'perspective', 'outlook', 'viewpoint', 'position', 'stance'],
                'leadership': ['lead', 'leader', 'manage', 'guide', 'direct', 'coordinate', 'oversee', 'head'],
                'communication': ['communicate', 'discuss', 'convey', 'explain', 'articulate', 'express', 'share', 'present'],
                'problem-solving': ['solve', 'solution', 'resolve', 'address', 'tackle', 'fix', 'handle', 'overcome'],
                'preference': ['prefer', 'choice', 'favor', 'inclined', 'comfortable', 'enjoy', 'like'],
                'goals': ['goal', 'objective', 'target', 'aim', 'milestone', 'outcome', 'result', 'achievement'],
                'experience': ['experienced', 'worked', 'previous', 'background', 'expertise', 'history', 'career'],
                'skills': ['skill', 'ability', 'capable', 'proficient', 'competent', 'expert', 'knowledge'],
                'strength': ['strong', 'strengths', 'excel', 'good at', 'proficient', 'capable', 'best'],
                'weakness': ['improve', 'improvement', 'working on', 'developing', 'learning', 'growth', 'area'],
                'challenge': ['difficult', 'challenging', 'hard', 'obstacle', 'problem', 'issue', 'hurdle'],
                'success': ['achieved', 'accomplished', 'successful', 'outcome', 'result', 'won', 'completed'],
            }
            
            for keyword in keywords_lower:
                # Check exact match
                if keyword in answer_lower:
                    found_count += 1
                else:
                    found = False
                    # Check if the stem appears (for words > 4 chars)
                    if len(keyword) > 4:
                        stem = keyword[:min(len(keyword)-1, 6)]
                        if stem in answer_lower:
                            found_count += 0.8  # Partial credit for stem match
                            found = True
                    # Check synonyms if not found yet
                    if not found and keyword in synonym_map:
                        if any(syn in answer_lower for syn in synonym_map[keyword]):
                            found_count += 0.85  # Good credit for synonym
                            found = True
                    # Check if any synonym map contains this keyword as a synonym
                    if not found:
                        for base_word, synonyms in synonym_map.items():
                            if keyword in synonyms and base_word in answer_lower:
                                found_count += 0.85
                                found = True
                                break
            
            keyword_ratio = min(found_count / len(expected_keywords), 1.0)
            # Give substantial base score - don't punish too hard for keyword misses
            score += keyword_ratio * 20 + 15  # Minimum 15 points, max 35
        else:
            # No expected keywords — generous scoring based on answer substance
            if len(answer_keywords) >= 15:
                score += 35
            elif len(answer_keywords) >= 10:
                score += 30
            elif len(answer_keywords) >= 5:
                score += 25
            else:
                score += 20
        
        # Bonus for comprehensive answers (0-15 points)
        word_count = len(answer.split())
        if word_count >= 120:
            score += 15
        elif word_count >= 80:
            score += 12
        elif word_count >= 50:
            score += 8
        elif word_count >= 30:
            score += 5
        
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
        """Generate comprehensive feedback"""
        feedback_parts = []
        
        # Overall assessment
        overall_score = (content_score + relevance_score + coherence_score) / 3
        
        if overall_score >= 85:
            feedback_parts.append("Outstanding answer! Excellent structure and content.")
        elif overall_score >= 75:
            feedback_parts.append("Excellent answer! Well-structured with good examples.")
        elif overall_score >= 65:
            feedback_parts.append("Very good answer with solid content.")
        elif overall_score >= 55:
            feedback_parts.append("Good answer with room for improvement.")
        elif overall_score >= 45:
            feedback_parts.append("Decent answer. Adding more details would strengthen it.")
        else:
            feedback_parts.append("Your answer needs more detail and structure.")
        
        # Specific feedback
        if content_score < 60:
            if word_count < 30:
                feedback_parts.append("Your answer is too brief. Provide more details and examples.")
            else:
                feedback_parts.append("Try to structure your answer better with clear examples.")
        
        if relevance_score < 60:
            feedback_parts.append("Make sure to directly address the question asked.")
            if keyword_analysis["missing"]:
                feedback_parts.append(f"Consider discussing: {', '.join(keyword_analysis['missing'][:3])}")
        
        if coherence_score < 70:
            feedback_parts.append("Work on connecting your thoughts more smoothly using transition words.")
        
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
