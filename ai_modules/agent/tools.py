"""
Agent Tools

Provides the tools/capabilities that the Interview Agent can use
to perform its tasks: question generation, answer evaluation,
weak area identification, and suggestion generation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session
from datetime import datetime

# Import existing AI modules
from ai_modules.nlp.question_generator import QuestionGenerator
from ai_modules.nlp.answer_evaluator import AnswerEvaluator
from ai_modules.adaptive.adaptive_system import AdaptiveSystem
from ai_modules.adaptive.report_generator import ReportGenerator


@dataclass
class ToolResult:
    """Result from an agent tool execution"""
    success: bool
    data: Any
    message: str
    execution_time_ms: float = 0.0
    metadata: Dict = None


class AgentTools:
    """
    Collection of tools available to the Interview Agent.
    Each tool wraps underlying AI modules with agent-friendly interfaces.
    """
    
    def __init__(self):
        # Initialize underlying modules
        self.question_generator = QuestionGenerator()
        self.answer_evaluator = AnswerEvaluator()
        self.adaptive_system = AdaptiveSystem()
        self.report_generator = ReportGenerator()
    
    # ==================== QUESTION GENERATION TOOLS ====================
    
    def generate_questions(
        self,
        interview_type: str,
        difficulty: str,
        interview_mode: str = "standard",
        resume_data: Optional[Dict] = None,
        user_skills: Optional[List[str]] = None,
        focus_areas: Optional[List[str]] = None,
        avoid_topics: Optional[List[str]] = None,
        user_id: Optional[int] = None,
        db: Optional[Session] = None,
        num_questions: int = 10
    ) -> ToolResult:
        """
        Generate interview questions based on context and requirements.
        
        This tool considers:
        - Interview type and mode
        - User's resume and skills
        - Areas to focus on (weak areas from past)
        - Topics to avoid (already mastered)
        """
        start_time = datetime.utcnow()
        
        try:
            # Generate questions using the question generator
            questions = self.question_generator.generate_questions(
                interview_type=interview_type,
                difficulty=difficulty,
                interview_mode=interview_mode,
                resume_data=resume_data,
                skills=user_skills,
                user_id=user_id,
                db=db
            )
            
            # Post-process: filter based on focus areas and avoid topics
            if focus_areas:
                questions = self._prioritize_focus_areas(questions, focus_areas)
            
            if avoid_topics:
                questions = self._filter_avoid_topics(questions, avoid_topics)
            
            # Limit to requested number
            questions = questions[:num_questions]
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ToolResult(
                success=True,
                data=questions,
                message=f"Generated {len(questions)} questions for {interview_type} interview",
                execution_time_ms=execution_time,
                metadata={
                    "interview_type": interview_type,
                    "difficulty": difficulty,
                    "num_generated": len(questions)
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to generate questions: {str(e)}",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
    
    def generate_followup_question(
        self,
        original_question: str,
        user_answer: str,
        evaluation_result: Dict,
        category: str
    ) -> ToolResult:
        """
        Generate a follow-up question based on the user's answer.
        Used for adaptive interviewing when diving deeper into a topic.
        """
        start_time = datetime.utcnow()
        
        try:
            # Analyze what aspects need follow-up
            followup_type = self._determine_followup_type(evaluation_result)
            
            followup = self._create_followup_question(
                original_question,
                user_answer,
                evaluation_result,
                followup_type,
                category
            )
            
            return ToolResult(
                success=True,
                data=followup,
                message=f"Generated {followup_type} follow-up question",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to generate follow-up: {str(e)}"
            )
    
    def _prioritize_focus_areas(self, questions: List[Dict], focus_areas: List[str]) -> List[Dict]:
        """Reorder questions to prioritize focus areas"""
        focus_questions = []
        other_questions = []
        
        for q in questions:
            category = q.get("category", "").lower()
            keywords = [k.lower() for k in q.get("keywords", [])]
            
            is_focus = any(
                area.lower() in category or 
                any(area.lower() in kw for kw in keywords)
                for area in focus_areas
            )
            
            if is_focus:
                focus_questions.append(q)
            else:
                other_questions.append(q)
        
        return focus_questions + other_questions
    
    def _filter_avoid_topics(self, questions: List[Dict], avoid_topics: List[str]) -> List[Dict]:
        """Filter out questions from topics to avoid"""
        filtered = []
        avoid_lower = [t.lower() for t in avoid_topics]
        
        for q in questions:
            category = q.get("category", "").lower()
            keywords = [k.lower() for k in q.get("keywords", [])]
            
            should_avoid = any(
                topic in category or
                any(topic in kw for kw in keywords)
                for topic in avoid_lower
            )
            
            if not should_avoid:
                filtered.append(q)
        
        return filtered
    
    def _determine_followup_type(self, evaluation_result: Dict) -> str:
        """Determine what type of follow-up is needed"""
        content_score = evaluation_result.get("content_score", 0)
        relevance_score = evaluation_result.get("relevance_score", 0)
        keywords_missing = evaluation_result.get("nlp_analysis", {}).get("keywords_missing", [])
        
        if content_score < 50:
            return "clarification"  # Ask for more details
        elif relevance_score < 50:
            return "redirect"  # Guide back to the topic
        elif keywords_missing:
            return "probe"  # Dig into missing concepts
        else:
            return "extension"  # Extend to related topic
    
    def _create_followup_question(
        self,
        original: str,
        answer: str,
        evaluation: Dict,
        followup_type: str,
        category: str
    ) -> Dict:
        """Create a specific follow-up question"""
        templates = {
            "clarification": [
                "Could you elaborate more on that?",
                "Can you provide a specific example?",
                "What did you mean when you mentioned {topic}?"
            ],
            "redirect": [
                "That's interesting, but let's focus on the main question. {original}",
                "Could you specifically address {missing_aspect}?"
            ],
            "probe": [
                "You mentioned {mentioned_concept}. How does {missing_keyword} relate to this?",
                "What about {missing_keyword}? How would you approach that?"
            ],
            "extension": [
                "Great answer! How would this change in a {scenario} scenario?",
                "What would be the challenges if we scaled this approach?"
            ]
        }
        
        # Simple template selection (in production, use LLM for better generation)
        import random
        template = random.choice(templates.get(followup_type, templates["clarification"]))
        
        return {
            "text": template,
            "type": "followup",
            "difficulty": "medium",
            "category": category,
            "followup_type": followup_type,
            "keywords": []
        }
    
    # ==================== ANSWER EVALUATION TOOLS ====================
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_keywords: List[str] = None,
        question_type: str = "general"
    ) -> ToolResult:
        """
        Evaluate a user's answer comprehensively.
        
        Returns scores for:
        - Content quality
        - Relevance to question
        - Communication effectiveness
        Plus detailed feedback and suggestions.
        """
        start_time = datetime.utcnow()
        
        try:
            evaluation = self.answer_evaluator.evaluate_answer(
                question=question,
                answer=answer,
                expected_keywords=expected_keywords,
                question_type=question_type
            )
            
            return ToolResult(
                success=True,
                data=evaluation,
                message="Answer evaluated successfully",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={
                    "content_score": evaluation.get("content_score"),
                    "relevance_score": evaluation.get("relevance_score")
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Evaluation failed: {str(e)}"
            )
    
    def evaluate_with_speech_analysis(
        self,
        question: str,
        answer: str,
        audio_path: Optional[str] = None,
        expected_keywords: List[str] = None
    ) -> ToolResult:
        """
        Comprehensive evaluation including speech analysis.
        Combines text evaluation with audio metrics.
        """
        start_time = datetime.utcnow()
        
        try:
            # Text evaluation
            text_eval = self.answer_evaluator.evaluate_answer(
                question=question,
                answer=answer,
                expected_keywords=expected_keywords
            )
            
            # Speech evaluation (if audio provided)
            speech_eval = {}
            if audio_path:
                try:
                    from ai_modules.speech.speech_analyzer import SpeechAnalyzer
                    speech_analyzer = SpeechAnalyzer()
                    speech_eval = speech_analyzer.analyze_audio(audio_path)
                except ImportError:
                    speech_eval = {"error": "Speech analyzer not available"}
            
            # Combine results
            combined = {
                **text_eval,
                "speech_analysis": speech_eval,
                "clarity_score": speech_eval.get("clarity_score", 75),
                "fluency_score": speech_eval.get("fluency_score", 75),
                "speaking_pace": speech_eval.get("words_per_minute", 0)
            }
            
            return ToolResult(
                success=True,
                data=combined,
                message="Comprehensive evaluation completed",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Evaluation failed: {str(e)}"
            )
    
    # ==================== WEAK AREA IDENTIFICATION TOOLS ====================
    
    def identify_weak_areas(
        self,
        evaluations: List[Dict],
        questions_context: List[Dict],
        threshold: float = 65.0
    ) -> ToolResult:
        """
        Identify weak areas from a collection of evaluations.
        
        Analyzes patterns across multiple answers to find:
        - Topics with consistently low scores
        - Skill gaps
        - Areas needing improvement
        """
        start_time = datetime.utcnow()
        
        try:
            # Group scores by category
            category_scores = {}
            
            for eval_result, q_context in zip(evaluations, questions_context):
                category = q_context.get("category", "General")
                content_score = eval_result.get("content_score", 0)
                relevance_score = eval_result.get("relevance_score", 0)
                avg_score = (content_score + relevance_score) / 2
                
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append({
                    "score": avg_score,
                    "question": q_context.get("text", ""),
                    "keywords_missing": eval_result.get("nlp_analysis", {}).get("keywords_missing", [])
                })
            
            # Identify weak areas
            weak_areas = []
            for category, scores_data in category_scores.items():
                scores = [s["score"] for s in scores_data]
                avg_score = sum(scores) / len(scores)
                
                if avg_score < threshold:
                    # Collect missing keywords across all questions in this category
                    all_missing = []
                    for s in scores_data:
                        all_missing.extend(s["keywords_missing"])
                    
                    weak_areas.append({
                        "area": category,
                        "average_score": round(avg_score, 2),
                        "attempts": len(scores),
                        "severity": "high" if avg_score < 50 else "medium",
                        "common_gaps": list(set(all_missing))[:5],  # Top 5 missing concepts
                        "improvement_potential": round(threshold - avg_score, 2)
                    })
            
            # Sort by severity (lowest scores first)
            weak_areas.sort(key=lambda x: x["average_score"])
            
            return ToolResult(
                success=True,
                data=weak_areas,
                message=f"Identified {len(weak_areas)} weak areas",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                metadata={
                    "categories_analyzed": len(category_scores),
                    "weak_areas_count": len(weak_areas)
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to identify weak areas: {str(e)}"
            )
    
    def identify_strong_areas(
        self,
        evaluations: List[Dict],
        questions_context: List[Dict],
        threshold: float = 80.0
    ) -> ToolResult:
        """Identify strong areas where user excels"""
        start_time = datetime.utcnow()
        
        try:
            category_scores = {}
            
            for eval_result, q_context in zip(evaluations, questions_context):
                category = q_context.get("category", "General")
                content_score = eval_result.get("content_score", 0)
                relevance_score = eval_result.get("relevance_score", 0)
                avg_score = (content_score + relevance_score) / 2
                
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(avg_score)
            
            strong_areas = []
            for category, scores in category_scores.items():
                avg_score = sum(scores) / len(scores)
                
                if avg_score >= threshold:
                    strong_areas.append({
                        "area": category,
                        "average_score": round(avg_score, 2),
                        "attempts": len(scores),
                        "confidence_level": "high" if avg_score >= 90 else "good"
                    })
            
            strong_areas.sort(key=lambda x: x["average_score"], reverse=True)
            
            return ToolResult(
                success=True,
                data=strong_areas,
                message=f"Identified {len(strong_areas)} strong areas",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to identify strong areas: {str(e)}"
            )
    
    def analyze_skill_gaps(
        self,
        weak_areas: List[Dict],
        user_skills: Optional[List[str]] = None,
        interview_type: str = "general"
    ) -> ToolResult:
        """
        Perform deeper skill gap analysis.
        Maps weak areas to specific skills that need development.
        """
        start_time = datetime.utcnow()
        
        # Skill mapping for different interview types
        skill_mappings = {
            "technical": {
                "programming": ["coding", "algorithms", "data structures", "problem solving"],
                "system_design": ["architecture", "scalability", "databases"],
                "debugging": ["troubleshooting", "testing", "code review"]
            },
            "behavioral": {
                "communication": ["clarity", "articulation", "storytelling"],
                "leadership": ["decision making", "team management", "conflict resolution"],
                "problem_solving": ["analytical thinking", "creativity", "planning"]
            },
            "hr": {
                "self_awareness": ["strengths", "weaknesses", "goals"],
                "cultural_fit": ["values", "work style", "collaboration"],
                "motivation": ["career goals", "interest", "drive"]
            }
        }
        
        try:
            skill_gaps = []
            
            for weak_area in weak_areas:
                area = weak_area["area"].lower()
                
                # Find related skills
                for skill_type, mappings in skill_mappings.get(interview_type, skill_mappings["behavioral"]).items():
                    if any(keyword in area for keyword in mappings):
                        skill_gaps.append({
                            "skill": skill_type,
                            "related_area": weak_area["area"],
                            "current_score": weak_area["average_score"],
                            "gap_size": 80 - weak_area["average_score"],
                            "priority": weak_area["severity"]
                        })
            
            return ToolResult(
                success=True,
                data=skill_gaps,
                message=f"Identified {len(skill_gaps)} skill gaps",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to analyze skill gaps: {str(e)}"
            )
    
    # ==================== PERSONALIZED SUGGESTION TOOLS ====================
    
    def generate_suggestions(
        self,
        weak_areas: List[Dict],
        strong_areas: List[Dict],
        interview_type: str,
        evaluations: List[Dict]
    ) -> ToolResult:
        """
        Generate personalized improvement suggestions.
        
        Creates actionable recommendations based on:
        - Identified weak areas
        - Score patterns
        - Interview type specific advice
        """
        start_time = datetime.utcnow()
        
        try:
            suggestions = []
            
            # Suggestions for weak areas
            for weak_area in weak_areas[:5]:  # Top 5 weak areas
                area = weak_area["area"]
                severity = weak_area["severity"]
                gaps = weak_area.get("common_gaps", [])
                
                suggestion = self._create_area_suggestion(area, severity, gaps, interview_type)
                suggestions.append(suggestion)
            
            # General improvement suggestions based on evaluation patterns
            pattern_suggestions = self._analyze_patterns_for_suggestions(evaluations)
            suggestions.extend(pattern_suggestions)
            
            # Leverage strengths suggestions
            if strong_areas:
                suggestions.append({
                    "type": "leverage_strength",
                    "priority": "low",
                    "title": "Build on Your Strengths",
                    "description": f"You excel in {', '.join([s['area'] for s in strong_areas[:3]])}. Use examples from these areas to strengthen weaker responses.",
                    "action_items": [
                        "Reference your strong areas when answering challenging questions",
                        "Use successful patterns from strong areas in weaker ones"
                    ]
                })
            
            return ToolResult(
                success=True,
                data=suggestions,
                message=f"Generated {len(suggestions)} personalized suggestions",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to generate suggestions: {str(e)}"
            )
    
    def _create_area_suggestion(
        self,
        area: str,
        severity: str,
        gaps: List[str],
        interview_type: str
    ) -> Dict:
        """Create a specific suggestion for a weak area"""
        
        # Suggestion templates by area type
        suggestion_templates = {
            "technical": {
                "title": f"Improve Technical Knowledge: {area}",
                "description": f"Your performance in {area} needs attention.",
                "action_items": [
                    f"Review fundamental concepts in {area}",
                    "Practice coding problems related to this topic",
                    "Study real-world applications and examples"
                ],
                "resources": [
                    "LeetCode/HackerRank for practice",
                    "Technical documentation and tutorials",
                    "System design case studies"
                ]
            },
            "behavioral": {
                "title": f"Strengthen Behavioral Responses: {area}",
                "description": f"Your answers about {area} could be more compelling.",
                "action_items": [
                    "Prepare 2-3 specific examples using STAR method",
                    "Practice articulating your experiences clearly",
                    "Focus on measurable outcomes and impact"
                ],
                "resources": [
                    "STAR method guide",
                    "Common behavioral question practice",
                    "Mock interview recordings"
                ]
            },
            "communication": {
                "title": "Enhance Communication Skills",
                "description": "Focus on clearer, more structured responses.",
                "action_items": [
                    "Structure answers with clear beginning, middle, end",
                    "Reduce filler words and pauses",
                    "Practice speaking at a measured pace"
                ],
                "resources": [
                    "Public speaking courses",
                    "Recording and reviewing practice sessions",
                    "Toastmasters or similar groups"
                ]
            }
        }
        
        # Select template based on area and interview type
        if "technical" in area.lower() or interview_type == "technical":
            template = suggestion_templates["technical"]
        elif any(word in area.lower() for word in ["communication", "clarity", "fluency"]):
            template = suggestion_templates["communication"]
        else:
            template = suggestion_templates["behavioral"]
        
        # Add specific gaps to action items
        if gaps:
            template["action_items"].append(f"Focus on understanding: {', '.join(gaps[:3])}")
        
        return {
            "type": "improvement",
            "area": area,
            "priority": "high" if severity == "high" else "medium",
            **template
        }
    
    def _analyze_patterns_for_suggestions(self, evaluations: List[Dict]) -> List[Dict]:
        """Analyze evaluation patterns to generate suggestions"""
        suggestions = []
        
        # Check for common issues across evaluations
        low_content_count = sum(1 for e in evaluations if e.get("content_score", 100) < 60)
        low_relevance_count = sum(1 for e in evaluations if e.get("relevance_score", 100) < 60)
        short_answers = sum(1 for e in evaluations 
                          if e.get("nlp_analysis", {}).get("word_count", 100) < 30)
        
        total = len(evaluations) if evaluations else 1
        
        if low_content_count / total > 0.3:
            suggestions.append({
                "type": "pattern",
                "priority": "high",
                "title": "Add More Depth to Answers",
                "description": "Many of your answers lack sufficient detail.",
                "action_items": [
                    "Include specific examples and metrics",
                    "Explain your thought process",
                    "Provide context for your experiences"
                ]
            })
        
        if low_relevance_count / total > 0.3:
            suggestions.append({
                "type": "pattern",
                "priority": "high",
                "title": "Stay Focused on the Question",
                "description": "Some answers drifted from the main question.",
                "action_items": [
                    "Listen carefully to the full question",
                    "Address the main point before adding details",
                    "Ask for clarification if needed"
                ]
            })
        
        if short_answers / total > 0.4:
            suggestions.append({
                "type": "pattern",
                "priority": "medium",
                "title": "Elaborate Your Responses",
                "description": "Your answers tend to be brief.",
                "action_items": [
                    "Aim for 1-2 minute responses",
                    "Use the STAR method for behavioral questions",
                    "Prepare talking points for common topics"
                ]
            })
        
        return suggestions
    
    def generate_learning_path(
        self,
        weak_areas: List[Dict],
        skill_gaps: List[Dict],
        interview_type: str,
        time_available_weeks: int = 4
    ) -> ToolResult:
        """
        Generate a structured learning path to address gaps.
        """
        start_time = datetime.utcnow()
        
        try:
            learning_path = {
                "duration_weeks": time_available_weeks,
                "phases": [],
                "milestones": [],
                "daily_activities": []
            }
            
            # Phase 1: Foundation (Week 1)
            if weak_areas:
                learning_path["phases"].append({
                    "week": 1,
                    "focus": "Foundation Building",
                    "activities": [
                        f"Study fundamentals of {weak_areas[0]['area']}" if weak_areas else "Review basics",
                        "Watch tutorial videos on weak topics",
                        "Complete beginner-level practice questions"
                    ],
                    "target_improvement": 10
                })
            
            # Phase 2: Practice (Weeks 2-3)
            learning_path["phases"].append({
                "week": "2-3",
                "focus": "Active Practice",
                "activities": [
                    "Daily mock interviews (15-30 minutes)",
                    "Record and review your answers",
                    "Focus on weak areas identified"
                ],
                "target_improvement": 15
            })
            
            # Phase 3: Refinement (Week 4)
            learning_path["phases"].append({
                "week": 4,
                "focus": "Refinement & Confidence",
                "activities": [
                    "Full mock interviews",
                    "Peer feedback sessions",
                    "Fine-tune communication style"
                ],
                "target_improvement": 10
            })
            
            # Milestones
            learning_path["milestones"] = [
                {"week": 1, "milestone": "Complete foundational review"},
                {"week": 2, "milestone": "Achieve 70% on practice questions"},
                {"week": 3, "milestone": "Complete 5 mock interviews"},
                {"week": 4, "milestone": "Achieve target scores"}
            ]
            
            return ToolResult(
                success=True,
                data=learning_path,
                message="Learning path generated successfully",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to generate learning path: {str(e)}"
            )
    
    # ==================== REPORT GENERATION TOOLS ====================
    
    def generate_final_report(
        self,
        interview_id: int,
        db: Session
    ) -> ToolResult:
        """Generate comprehensive final interview report"""
        start_time = datetime.utcnow()
        
        try:
            report = self.report_generator.generate_final_report(interview_id, db)
            
            return ToolResult(
                success=True,
                data=report,
                message="Final report generated successfully",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"Failed to generate report: {str(e)}"
            )
    
    def get_adaptive_recommendation(
        self,
        user_id: int,
        interview_type: str,
        db: Session
    ) -> ToolResult:
        """Get adaptive difficulty and focus recommendations"""
        start_time = datetime.utcnow()
        
        try:
            difficulty = self.adaptive_system.get_recommended_difficulty(
                user_id=user_id,
                interview_type=interview_type,
                db=db
            )
            
            return ToolResult(
                success=True,
                data={"recommended_difficulty": difficulty},
                message=f"Recommended difficulty: {difficulty}",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={"recommended_difficulty": "medium"},
                message=f"Using default difficulty due to error: {str(e)}"
            )
