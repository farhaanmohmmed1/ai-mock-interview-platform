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
        
        # Length scoring (0-40 points) - more generous for typical spoken answers
        if word_count < 10:
            score += (word_count / 10) * 20  # Very short
        elif word_count < 20:
            score += 20 + ((word_count - 10) / 10) * 8  # 20-28
        elif word_count < 40:
            score += 28 + ((word_count - 20) / 20) * 7  # 28-35
        elif word_count < 80:
            score += 35 + ((word_count - 40) / 40) * 5  # 35-40
        else:
            score += 40
        
        # Structure scoring (0-25 points)
        if sentence_count >= 4:
            score += 25
        elif sentence_count >= 3:
            score += 22
        elif sentence_count >= 2:
            score += 18
        else:
            score += 12
        
        # Check for examples/specifics (0-20 points)
        example_indicators = ['for example', 'for instance', 'such as', 'like', 'specifically',
                              'in my experience', 'i have', 'i worked', 'i used', 'we implemented',
                              'the result', 'this led to', 'because', 'which means', 'i think',
                              'i believe', 'my approach', 'the way', 'in this case', 'when i',
                              'i would', 'to ensure', 'by using', 'through']
        matches = sum(1 for indicator in example_indicators if indicator in answer.lower())
        if matches >= 3:
            score += 20
        elif matches >= 2:
            score += 17
        elif matches >= 1:
            score += 13
        else:
            score += 7
        
        # Complexity & vocabulary (0-15 points)
        avg_word_length = sum(len(word) for word in answer.split()) / len(answer.split()) if answer.split() else 0
        if avg_word_length > 5.5:
            score += 15
        elif avg_word_length > 4.5:
            score += 13
        elif avg_word_length > 3.5:
            score += 10
        else:
            score += 7
        
        return min(score, 100)
    
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
        
        # Calculate overlap (0-50 points)
        if question_keywords:
            overlap = len(question_keywords & answer_keywords) / len(question_keywords)
            score += overlap * 50
        
        # Expected keywords (0-50 points)
        if expected_keywords and len(expected_keywords) > 0:
            keywords_lower = [k.lower() for k in expected_keywords]
            answer_lower = answer.lower()
            found_count = sum(1 for keyword in keywords_lower if keyword in answer_lower)
            keyword_ratio = found_count / len(expected_keywords)
            # Give partial credit more generously - even covering some keywords shows understanding
            if keyword_ratio >= 0.7:
                score += 50
            elif keyword_ratio >= 0.4:
                score += 35 + (keyword_ratio - 0.4) * 50
            else:
                score += 20 + keyword_ratio * 37.5
        else:
            # No expected keywords defined — score based on answer substance
            answer_tokens = answer_keywords  # already computed above (stopwords removed)
            if len(answer_tokens) >= 12:
                score += 48
            elif len(answer_tokens) >= 8:
                score += 42
            elif len(answer_tokens) >= 4:
                score += 35
            else:
                score += 25
        
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
        score = 75  # Base score
        
        sentences = self.sent_tokenize(answer)
        
        if len(sentences) < 2:
            return 68
        
        # Check for transition words
        transitions = ['however', 'therefore', 'furthermore', 'moreover', 'additionally',
                      'consequently', 'nevertheless', 'meanwhile', 'subsequently', 'thus',
                      'first', 'second', 'finally', 'also', 'because', 'since',
                      'so', 'then', 'next', 'after', 'before', 'while', 'although']
        
        answer_lower = answer.lower()
        transition_count = sum(1 for trans in transitions if trans in answer_lower)
        
        if transition_count >= 3:
            score += 20
        elif transition_count >= 2:
            score += 15
        elif transition_count >= 1:
            score += 10
        
        # Check for logical flow (sentences of similar length indicate good structure)
        sentence_lengths = [len(self.word_tokenize(s)) for s in sentences]
        if len(sentence_lengths) > 1:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            if variance < 100:  # Low variance = good structure
                score += 5
        
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
        
        if overall_score >= 75:
            feedback_parts.append("Excellent answer!")
        elif overall_score >= 60:
            feedback_parts.append("Good answer with room for improvement.")
        elif overall_score >= 45:
            feedback_parts.append("Decent answer. Adding more details would strengthen it.")
        else:
            feedback_parts.append("Your answer needs significant improvement.")
        
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
