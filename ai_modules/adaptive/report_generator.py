from sqlalchemy.orm import Session
from typing import Dict, List
from backend.models import Interview, Response, Question
import numpy as np


# Course recommendations database - maps topics/skills to learning resources
COURSE_DATABASE = {

    # Programming Languages
    "java": [
        {
            "title": "Java Programming Masterclass",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/",
            "level": "Beginner to Advanced"
        },
        {
            "title": "Java Fundamentals",
            "platform": "Pluralsight",
            "url": "https://www.pluralsight.com/courses/java-fundamentals-language",
            "level": "Beginner"
        },
        {
            "title": "Java Programming and Software Engineering Fundamentals",
            "platform": "Coursera",
            "url": "https://www.coursera.org/specializations/java-programming",
            "level": "Beginner"
        },
    ],

    "python": [
        {
            "title": "Complete Python Bootcamp",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/complete-python-bootcamp/",
            "level": "Beginner to Advanced"
        },
        {
            "title": "Python for Everybody",
            "platform": "Coursera",
            "url": "https://www.coursera.org/specializations/python",
            "level": "Beginner"
        },
        {
            "title": "Python Official Tutorial",
            "platform": "Official",
            "url": "https://docs.python.org/3/tutorial/",
            "level": "All Levels"
        },
    ],

    "javascript": [
        {
            "title": "The Complete JavaScript Course",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/the-complete-javascript-course/",
            "level": "Beginner to Advanced"
        },
        {
            "title": "JavaScript Algorithms and Data Structures",
            "platform": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
            "level": "Beginner"
        },
        {
            "title": "MDN JavaScript Guide",
            "platform": "MDN",
            "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            "level": "Beginner to Intermediate"
        },
    ],

    "typescript": [
        {
            "title": "Understanding TypeScript",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/understanding-typescript/",
            "level": "Beginner to Intermediate"
        },
        {
            "title": "TypeScript Official Documentation",
            "platform": "Official",
            "url": "https://www.typescriptlang.org/docs/",
            "level": "All Levels"
        },
    ],

    "c++": [
        {
            "title": "Beginning C++ Programming",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/beginning-c-plus-plus-programming/",
            "level": "Beginner"
        },
        {
            "title": "C++ Tutorial",
            "platform": "W3Schools",
            "url": "https://www.w3schools.com/cpp/",
            "level": "Beginner"
        },
    ],

    "c#": [
        {
            "title": "C# Fundamentals",
            "platform": "Microsoft Learn",
            "url": "https://learn.microsoft.com/en-us/training/paths/csharp-first-steps/",
            "level": "Beginner"
        },
        {
            "title": "C# Documentation",
            "platform": "Microsoft",
            "url": "https://learn.microsoft.com/en-us/dotnet/csharp/",
            "level": "Beginner"
        },
    ],

    "go": [
        {
            "title": "Go: The Complete Developer's Guide",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/go-the-complete-developers-guide/",
            "level": "Beginner"
        },
        {
            "title": "Go Documentation",
            "platform": "Official",
            "url": "https://go.dev/doc/",
            "level": "All Levels"
        },
    ],

    "rust": [
        {
            "title": "The Rust Programming Language",
            "platform": "Official",
            "url": "https://doc.rust-lang.org/book/",
            "level": "Beginner"
        },
        {
            "title": "Rust by Example",
            "platform": "Official",
            "url": "https://doc.rust-lang.org/rust-by-example/",
            "level": "Beginner"
        },
    ],

    # Data Structures & Algorithms
    "data structures": [
        {
            "title": "Data Structures and Algorithms Specialization",
            "platform": "Coursera",
            "url": "https://www.coursera.org/specializations/data-structures-algorithms",
            "level": "Intermediate"
        },
        {
            "title": "MIT Data Structures and Algorithms",
            "platform": "MIT OCW",
            "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
            "level": "Intermediate"
        },
        {
            "title": "LeetCode Practice",
            "platform": "LeetCode",
            "url": "https://leetcode.com/problemset/",
            "level": "All Levels"
        },
    ],

    "algorithms": [
        {
            "title": "Algorithms Specialization",
            "platform": "Coursera",
            "url": "https://www.coursera.org/specializations/algorithms",
            "level": "Intermediate"
        },
        {
            "title": "Introduction to Algorithms",
            "platform": "MIT OCW",
            "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/",
            "level": "Intermediate"
        },
        {
            "title": "HackerRank Algorithms Practice",
            "platform": "HackerRank",
            "url": "https://www.hackerrank.com/domains/algorithms",
            "level": "All Levels"
        },
    ],

    # Databases
    "sql": [
        {
            "title": "SQL for Data Science",
            "platform": "Coursera",
            "url": "https://www.coursera.org/learn/sql-for-data-science",
            "level": "Beginner"
        },
        {
            "title": "SQL Tutorial",
            "platform": "W3Schools",
            "url": "https://www.w3schools.com/sql/",
            "level": "Beginner"
        },
        {
            "title": "SQLZoo Interactive Tutorials",
            "platform": "SQLZoo",
            "url": "https://sqlzoo.net/wiki/SQL_Tutorial",
            "level": "Beginner to Intermediate"
        },
    ],

    "mongodb": [
        {
            "title": "MongoDB Basics",
            "platform": "MongoDB University",
            "url": "https://learn.mongodb.com/",
            "level": "Beginner"
        },
        {
            "title": "MongoDB Official Documentation",
            "platform": "Official",
            "url": "https://www.mongodb.com/docs/",
            "level": "All Levels"
        },
    ],

    # Web Development
    "react": [
        {
            "title": "React - The Complete Guide",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
            "level": "Beginner to Advanced"
        },
        {
            "title": "React Official Docs",
            "platform": "Official",
            "url": "https://react.dev/learn",
            "level": "All Levels"
        },
        {
            "title": "freeCodeCamp React Course",
            "platform": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/",
            "level": "Beginner"
        },
    ],

    "node": [
        {
            "title": "Node.js Developer Course",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/",
            "level": "Beginner to Advanced"
        },
        {
            "title": "Node.js Official Documentation",
            "platform": "Official",
            "url": "https://nodejs.org/en/docs/",
            "level": "All Levels"
        },
    ],

    "html": [
        {
            "title": "Responsive Web Design",
            "platform": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
            "level": "Beginner"
        },
        {
            "title": "HTML Tutorial",
            "platform": "MDN",
            "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML",
            "level": "Beginner"
        },
    ],

    "css": [
        {
            "title": "Advanced CSS and Sass",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/advanced-css-and-sass/",
            "level": "Intermediate"
        },
        {
            "title": "CSS Documentation",
            "platform": "MDN",
            "url": "https://developer.mozilla.org/en-US/docs/Web/CSS",
            "level": "Beginner"
        },
    ],

    # Cloud
    "aws": [
        {
            "title": "AWS Cloud Practitioner Essentials",
            "platform": "AWS",
            "url": "https://explore.skillbuilder.aws/learn/course/134/aws-cloud-practitioner-essentials",
            "level": "Beginner"
        },
        {
            "title": "AWS Training and Certification",
            "platform": "AWS",
            "url": "https://aws.amazon.com/training/",
            "level": "All Levels"
        },
    ],

    "azure": [
        {
            "title": "Microsoft Azure Fundamentals",
            "platform": "Microsoft Learn",
            "url": "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/",
            "level": "Beginner"
        },
    ],

    # AI / ML
    "machine learning": [
        {
            "title": "Machine Learning by Andrew Ng",
            "platform": "Coursera",
            "url": "https://www.coursera.org/learn/machine-learning",
            "level": "Beginner to Intermediate"
        },
        {
            "title": "Machine Learning Crash Course",
            "platform": "Google",
            "url": "https://developers.google.com/machine-learning/crash-course",
            "level": "Beginner"
        },
    ],

    "deep learning": [
        {
            "title": "Deep Learning Specialization",
            "platform": "Coursera",
            "url": "https://www.coursera.org/specializations/deep-learning",
            "level": "Intermediate"
        },
    ],

    # Soft Skills
    "communication": [
        {
            "title": "Improving Communication Skills",
            "platform": "Coursera",
            "url": "https://www.coursera.org/learn/wharton-communication-skills",
            "level": "All Levels"
        },
        {
            "title": "Business Communication Skills",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/business-communication-skills/",
            "level": "Beginner"
        },
    ],

    # General Interview Prep
    "behavioral": [
        {"title": "Successful Interviewing", "platform": "Coursera", "url": "https://www.coursera.org/learn/successful-interviewing", "level": "All Levels"},
        {"title": "The Art of the Job Interview", "platform": "Coursera", "url": "https://www.coursera.org/learn/art-of-job-interview", "level": "All Levels"},
        {"title": "Complete Interview Preparation (GD & Interviews)", "platform": "Coursera", "url": "https://www.coursera.org/learn/complete-interview-prep", "level": "All Levels"},
        {"title": "Job Interview Skills Training Course", "platform": "Udemy", "url": "https://www.udemy.com/course/job-interview-skills-training-course/", "level": "All Levels"},
        {"title": "Interview Master Class", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/interview-master-class", "level": "All Levels"},
    ],
    "general": [
        {"title": "Successful Interviewing", "platform": "Coursera", "url": "https://www.coursera.org/learn/successful-interviewing", "level": "All Levels"},
        {"title": "The Art of the Job Interview", "platform": "Coursera", "url": "https://www.coursera.org/learn/art-of-job-interview", "level": "All Levels"},
        {"title": "Complete Interview Preparation (GD & Interviews)", "platform": "Coursera", "url": "https://www.coursera.org/learn/complete-interview-prep", "level": "All Levels"},
        {"title": "Job Interview Skills Training Course", "platform": "Udemy", "url": "https://www.udemy.com/course/job-interview-skills-training-course/", "level": "All Levels"},
        {"title": "Interview Master Class", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/interview-master-class", "level": "All Levels"},
    ],
    
    # Object-Oriented Programming
    "oop": [
        {"title": "Object-Oriented Programming in Java", "platform": "Coursera", "url": "https://www.coursera.org/learn/object-oriented-java", "level": "Beginner"},
        {"title": "OOP Fundamentals", "platform": "Pluralsight", "url": "https://www.pluralsight.com/courses/object-oriented-programming-fundamentals-csharp", "level": "Beginner"},
    ],
    
    # API & Web Services
    "api": [
        {"title": "REST API Design", "platform": "Udemy", "url": "https://www.udemy.com/course/rest-api/", "level": "Intermediate"},
        {"title": "Postman API Fundamentals", "platform": "Postman", "url": "https://www.postman.com/postman/workspace/postman-api-fundamentals-student-expert/overview", "level": "Beginner"},
    ],
    "rest": [
        {"title": "RESTful Web Services", "platform": "Udemy", "url": "https://www.udemy.com/course/restful-web-services/", "level": "Intermediate"},
    ],
    
    # Version Control
    "git": [
        {"title": "Git Complete", "platform": "Udemy", "url": "https://www.udemy.com/course/git-complete/", "level": "Beginner to Advanced"},
        {"title": "Git Documentation", "platform": "Official", "url": "https://git-scm.com/doc", "level": "All Levels"},
    ],
}


class ReportGenerator:
    """Generate comprehensive interview performance reports"""
    
    def __init__(self):
        self.course_database = COURSE_DATABASE
    
    
    def generate_final_report(self, interview_id: int, db: Session) -> Dict:
        """Generate final interview report"""
        
        interview = db.query(Interview).filter(Interview.id == interview_id).first()
        
        if not interview:
            raise ValueError("Interview not found")
        
        # Get all responses
        responses = db.query(Response).filter(
            Response.interview_id == interview_id
        ).all()
        
        if not responses:
            return self._generate_empty_report()
        
        # Get total questions for this interview
        total_questions = interview.total_questions or len(responses)
        answered_count = len(responses)
        
        print(f"[ReportGenerator] Total questions: {total_questions}, Answered: {answered_count}")
        
        # Calculate scores based on answered questions
        scores = self._calculate_all_scores(responses, total_questions, answered_count)
        
        print(f"[ReportGenerator] Raw scores (before completion ratio): overall={scores['overall']}, content={scores['content']}")
        
        # Identify weak and strong areas
        weak_areas = self._identify_weak_areas(responses, db)
        strong_areas = self._identify_strong_areas(responses, db)
        
        # Generate feedback
        feedback = self._generate_comprehensive_feedback(scores, weak_areas, strong_areas)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, weak_areas, interview.interview_type)
        
        # Generate course recommendations based on weak areas
        course_recommendations = self._get_course_recommendations(weak_areas, interview.interview_type)
        
        return {
            "overall_score": scores["overall"],
            "content_score": scores["content"],
            "clarity_score": scores["clarity"],
            "fluency_score": scores["fluency"],
            "confidence_score": scores["confidence"],
            "emotion_score": scores["emotion"],
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
            "feedback": feedback,
            "recommendations": recommendations,
            "course_recommendations": course_recommendations,
            "detailed_scores": scores["detailed"]
        }
    
    def _generate_empty_report(self) -> Dict:
        """Generate report when no responses available"""
        return {
            "overall_score": 0,
            "content_score": 0,
            "clarity_score": 0,
            "fluency_score": 0,
            "confidence_score": 0,
            "emotion_score": 0,
            "weak_areas": [{"area": "All Areas", "score": 0, "suggestion": "No questions were answered. Please attempt the interview again."}],
            "strong_areas": [],
            "feedback": "No responses were recorded for this interview. Please attempt answering the questions to receive a proper evaluation.",
            "recommendations": [
                {"type": "general", "text": "Please try completing the interview again to receive personalized feedback"}
            ],
            "course_recommendations": [
                {
                    "topic": "Interview Skills",
                    "severity": "medium",
                    "course": {
                        "title": "Interview Skills: How to Get the Job",
                        "platform": "Udemy",
                        "url": "https://www.udemy.com/course/interview-skills-that-win-the-job/",
                        "level": "All Levels"
                    }
                }
            ]
        }
    
    def _calculate_all_scores(self, responses: List[Response], total_questions: int = None, answered_count: int = None) -> Dict:
        """Calculate all performance scores - each question contributes equally"""
        
        # Content scores
        content_scores = [r.content_score for r in responses if r.content_score is not None]
        relevance_scores = [r.relevance_score for r in responses if r.relevance_score is not None]
        
        # Speech scores
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        
        # Emotion scores
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        
        # Expression scores from video emotion_analysis
        # emotion_analysis contains: confidence_score, dominant_emotion, emotional_stability, etc.
        expression_scores = []
        for r in responses:
            if r.emotion_analysis and isinstance(r.emotion_analysis, dict):
                # Video was used - extract expression score from emotion analysis
                expr_score = r.emotion_analysis.get("confidence_score")
                if expr_score is not None and not r.emotion_analysis.get("error"):
                    expression_scores.append(expr_score)
        
        # Calculate completion ratio (skipped questions count as 0)
        if total_questions and answered_count:
            completion_ratio = answered_count / total_questions
        else:
            completion_ratio = 1.0  # Default to full credit if not specified
        
        # Calculate averages of answered questions only
        avg_content = sum(content_scores) / len(content_scores) if content_scores else 0
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        avg_expression = sum(expression_scores) / len(expression_scores) if expression_scores else 0
        
        # Combined scores - weight content heavily (keyword matching can be strict with synonyms)
        # If content is strong but relevance is weak, boost relevance (likely using synonyms)
        adjusted_relevance = avg_relevance
        if avg_content >= 75 and avg_relevance < 50:
            # Strong content but low keyword match - boost relevance
            adjusted_relevance = max(avg_relevance, avg_content * 0.6)
        
        content_combined = (avg_content * 0.70 + adjusted_relevance * 0.30) if (content_scores or relevance_scores) else 0
        
        # Check if we have speech/emotion data
        has_speech_data = bool(clarity_scores and fluency_scores)
        has_confidence_data = bool(confidence_scores)
        has_expression_data = bool(expression_scores)  # True only if video was used
        
        print(f"[ReportGenerator] has_speech_data={has_speech_data}, has_confidence_data={has_confidence_data}, has_expression_data={has_expression_data}")
        print(f"[ReportGenerator] expression_scores={expression_scores}")
        
        # STRICT SCORING based on input mode:
        # Text-only: ONLY Content scored (overall = content)
        # Audio: Content, Clarity, Fluency, Confidence scored
        # Video+Audio: All 5 metrics including Expression
        
        # Determine interview mode from available data
        if has_speech_data:
            # Has audio data (audio or video mode)
            speech_combined = (avg_clarity + avg_fluency) / 2
            final_clarity = avg_clarity
            final_fluency = avg_fluency
            final_confidence = avg_confidence if has_confidence_data else speech_combined
        else:
            # Text-only mode - ONLY content is scored
            speech_combined = None
            final_clarity = None  # Not scored without audio
            final_fluency = None  # Not scored without audio
            final_confidence = None  # Not scored without audio/video
        
        # Expression requires video - use emotion analysis data
        final_expression = avg_expression if has_expression_data else None
        
        # Calculate overall based ONLY on available metrics
        if has_speech_data and has_expression_data:
            # Full video mode: 35% content, 25% speech, 20% confidence, 20% expression
            raw_overall = (
                content_combined * 0.35 +
                speech_combined * 0.25 +
                final_confidence * 0.20 +
                final_expression * 0.20
            )
        elif has_speech_data and has_confidence_data:
            # Full audio mode: 40% content, 30% speech, 30% confidence
            raw_overall = (
                content_combined * 0.40 +
                speech_combined * 0.30 +
                final_confidence * 0.30
            )
        elif has_speech_data:
            # Audio without confidence: 50% content, 50% speech
            raw_overall = (
                content_combined * 0.50 +
                speech_combined * 0.50
            )
        else:
            # TEXT-ONLY: Overall = Content score directly
            raw_overall = content_combined
        
        # NOTE: Completion ratio is applied in interview.py AFTER getting report
        # This ensures both agent and generator reports are treated equally
        # Raw scores are returned here without completion penalty
        overall = raw_overall
        
        # Return raw scores - completion ratio applied in interview.py
        final_content = content_combined
        
        return {
            "overall": round(overall, 2),
            "content": round(final_content, 2),
            "clarity": round(final_clarity, 2) if final_clarity is not None else None,
            "fluency": round(final_fluency, 2) if final_fluency is not None else None,
            "confidence": round(final_confidence, 2) if final_confidence is not None else None,
            "emotion": round(final_expression, 2) if final_expression is not None else None,
            "interview_mode": "video" if has_expression_data else ("audio" if has_speech_data else "text"),
            "detailed": {
                "average_content": round(avg_content, 2),
                "average_relevance": round(avg_relevance, 2),
                "average_clarity": round(avg_clarity, 2) if clarity_scores else None,
                "average_fluency": round(avg_fluency, 2) if fluency_scores else None,
                "average_confidence": round(avg_confidence, 2) if confidence_scores else None,
                "average_expression": round(avg_expression, 2) if expression_scores else None,
                "completion_ratio": round(completion_ratio, 2),
                "has_speech_data": has_speech_data,
                "has_confidence_data": has_confidence_data,
                "has_expression_data": has_expression_data
            }
        }
    
    def _get_suggestion_for_area(self, area: str, score: float) -> str:
        """Get a specific improvement suggestion based on area and score"""
        suggestions = {
            "Speech Clarity": {
                "high": "Practice speaking slowly and enunciating each word. Record yourself and listen back to identify unclear parts.",
                "medium": "Work on articulation and pacing. Try tongue twisters and reading aloud daily.",
                "low": "Your clarity is good but can be polished further. Focus on complex technical terms pronunciation."
            },
            "Speech Fluency": {
                "high": "Reduce filler words (um, uh, like). Practice structured responses using the STAR method.",
                "medium": "Work on smoother transitions between ideas. Practice answering without long pauses.",
                "low": "Your fluency is solid. Try to maintain this consistency even with unexpected questions."
            },
            "Confidence": {
                "high": "Build confidence by practicing more interviews. Start with easier questions and gradually increase difficulty.",
                "medium": "Practice power posing and positive self-talk before interviews. Prepare thoroughly to boost confidence.",
                "low": "Your confidence level is decent. Work on maintaining steady eye contact and a firm voice throughout."
            }
        }
        
        if area in suggestions:
            if score < 50:
                return suggestions[area]["high"]
            elif score < 75:
                return suggestions[area]["medium"]
            else:
                return suggestions[area]["low"]
        
        # Generic suggestions for content categories
        if score < 50:
            return f"Focus on studying {area} topics thoroughly. Practice with sample questions and review model answers."
        elif score < 65:
            return f"Review key concepts in {area}. Try to include more specific examples and data points in your answers."
        elif score < 80:
            return f"Good foundation in {area}. To improve further, add more depth and real-world examples to your responses."
        else:
            return f"Strong performance in {area}. To reach excellence, focus on providing unique insights and structured frameworks."

    def _identify_weak_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify areas for improvement — always provides feedback regardless of score level"""
        
        all_areas = []
        
        # Analyze by question type/category
        category_scores = {}
        
        for response in responses:
            question = db.query(Question).filter(Question.id == response.question_id).first()
            
            if not question:
                continue
            
            category = question.category or question.question_type or "General"
            score = response.content_score or 0
            
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        
        # Collect areas that need improvement (score < 75%)
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 75:  # Only include areas that actually need improvement
                severity = "high" if avg_score < 50 else "medium"
                all_areas.append({
                    "area": category,
                    "score": round(avg_score, 2),
                    "responses_count": len(scores),
                    "severity": severity,
                    "suggestion": self._get_suggestion_for_area(category, avg_score)
                })
        
        # Check specific skills
        # Speech clarity - only add if needs improvement
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        if clarity_scores:
            avg_clarity = sum(clarity_scores) / len(clarity_scores)
            if avg_clarity < 75:
                all_areas.append({
                    "area": "Speech Clarity",
                    "score": round(avg_clarity, 2),
                    "responses_count": len(clarity_scores),
                    "severity": "high" if avg_clarity < 50 else "medium",
                    "suggestion": self._get_suggestion_for_area("Speech Clarity", avg_clarity)
                })
        
        # Speech fluency - only add if needs improvement
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        if fluency_scores:
            avg_fluency = sum(fluency_scores) / len(fluency_scores)
            if avg_fluency < 75:
                all_areas.append({
                    "area": "Speech Fluency",
                    "score": round(avg_fluency, 2),
                    "responses_count": len(fluency_scores),
                    "severity": "high" if avg_fluency < 50 else "medium",
                    "suggestion": self._get_suggestion_for_area("Speech Fluency", avg_fluency)
                })
        
        # Confidence - only add if needs improvement
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence < 75:
                all_areas.append({
                    "area": "Confidence",
                    "score": round(avg_confidence, 2),
                    "responses_count": len(confidence_scores),
                    "severity": "high" if avg_confidence < 50 else "medium",
                    "suggestion": self._get_suggestion_for_area("Confidence", avg_confidence)
                })
        
        # Sort: lowest scores first (most room for improvement)
        all_areas.sort(key=lambda x: x["score"])
        
        return all_areas[:5]  # Top 5 areas for improvement
    
    def _identify_strong_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify strong performance areas — always provides feedback"""
        
        all_areas = []
        
        # Analyze by question type/category
        category_scores = {}
        
        for response in responses:
            question = db.query(Question).filter(Question.id == response.question_id).first()
            
            if not question:
                continue
            
            category = question.category or question.question_type or "General"
            score = response.content_score or 0
            
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        
        # Collect truly STRONG areas (score >= 75%) - mutually exclusive with improvement areas
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 75:  # Only truly strong areas
                description = ""
                if avg_score >= 90:
                    description = f"Exceptional performance! You demonstrated mastery in {category}."
                elif avg_score >= 80:
                    description = f"Great job! Your {category} answers were well-structured and detailed."
                else:  # 75-79
                    description = f"Good performance in {category}. You showed solid understanding."
                
                all_areas.append({
                    "area": category,
                    "score": round(avg_score, 2),
                    "responses_count": len(scores),
                    "description": description
                })
        
        # Check specific skills - only add as strong if >= 75%
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        if clarity_scores:
            avg_clarity = sum(clarity_scores) / len(clarity_scores)
            if avg_clarity >= 75:
                all_areas.append({
                    "area": "Speech Clarity",
                    "score": round(avg_clarity, 2),
                    "responses_count": len(clarity_scores),
                    "description": "Your speech was clear and easy to understand."
                })
        
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        if fluency_scores:
            avg_fluency = sum(fluency_scores) / len(fluency_scores)
            if avg_fluency >= 75:
                all_areas.append({
                    "area": "Speech Fluency",
                    "score": round(avg_fluency, 2),
                    "responses_count": len(fluency_scores),
                    "description": "You spoke fluently with minimal hesitation."
                })
        
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence >= 75:
                all_areas.append({
                    "area": "Confidence",
                    "score": round(avg_confidence, 2),
                    "responses_count": len(confidence_scores),
                    "description": "You presented yourself confidently and assertively."
                })
        
        # Expression scores from emotion_analysis (video mode)
        expression_scores = []
        for r in responses:
            if r.emotion_analysis and isinstance(r.emotion_analysis, dict):
                expr_score = r.emotion_analysis.get("confidence_score")
                if expr_score is not None and not r.emotion_analysis.get("error"):
                    expression_scores.append(expr_score)
        
        if expression_scores:
            avg_expression = sum(expression_scores) / len(expression_scores)
            if avg_expression >= 75:
                all_areas.append({
                    "area": "Expression",
                    "score": round(avg_expression, 2),
                    "responses_count": len(expression_scores),
                    "description": "Your facial expressions conveyed confidence and engagement."
                })
        
        # Sort by score (highest first)
        all_areas.sort(key=lambda x: x["score"], reverse=True)
        
        return all_areas[:5]  # Top 5 strong areas
    
    def _generate_comprehensive_feedback(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        strong_areas: List[Dict]
    ) -> str:
        """Generate comprehensive feedback for all score levels"""
        
        feedback_parts = []
        
        # Overall performance
        overall = scores["overall"]
        if overall >= 90:
            feedback_parts.append("Outstanding performance! You demonstrated exceptional skills and composure throughout the interview. You are well-prepared for real interviews.")
        elif overall >= 80:
            feedback_parts.append("Excellent performance! You showed strong skills across multiple areas. With minor refinements, you'll be very well-positioned for interviews.")
        elif overall >= 70:
            feedback_parts.append("Good performance! You demonstrated solid understanding and communication. There are some areas where targeted practice can elevate your responses further.")
        elif overall >= 60:
            feedback_parts.append("Decent performance with clear room for growth. You have a good foundation — focus on the improvement areas below to strengthen your interview skills.")
        elif overall >= 40:
            feedback_parts.append("Fair performance. Focus on improving key skills to enhance your interview readiness. Review the suggestions below for specific guidance.")
        else:
            feedback_parts.append("Your performance needs significant improvement. Don't be discouraged — consistent practice and preparation will help you succeed.")
        
        # Strong areas
        if strong_areas:
            areas_text = ", ".join([area["area"] for area in strong_areas[:3]])
            if overall >= 80:
                feedback_parts.append(f"You excelled in: {areas_text}. Keep leveraging these strengths in your interviews.")
            else:
                feedback_parts.append(f"Your strengths include: {areas_text}. Build on these while working on weaker areas.")
        
        # Areas for improvement (always shown)
        if weak_areas:
            areas_text = ", ".join([area["area"] for area in weak_areas[:3]])
            if overall >= 80:
                feedback_parts.append(f"To go from great to exceptional, focus on refining: {areas_text}.")
            elif overall >= 60:
                feedback_parts.append(f"Key areas to improve: {areas_text}. Targeted practice here will make a big difference.")
            else:
                feedback_parts.append(f"Priority areas needing attention: {areas_text}. Start with these for the most impact.")
        
        # Specific skill feedback based on scores
        content = scores.get("content") or 0
        if content >= 80:
            feedback_parts.append("Your answer content was strong — detailed, relevant, and well-structured.")
        elif content >= 60:
            feedback_parts.append("Your answers had good substance but could benefit from more specific examples and structured frameworks like STAR.")
        else:
            feedback_parts.append("Work on providing more detailed and relevant answers with concrete examples.")
        
        # Only provide clarity/confidence feedback if audio was used
        clarity = scores.get("clarity")
        if clarity is not None:
            if clarity >= 80:
                feedback_parts.append("Your speech clarity was excellent — you communicated ideas effectively.")
            elif clarity >= 60:
                feedback_parts.append("Your clarity was decent. Practice enunciating clearly, especially for technical terminology.")
            else:
                feedback_parts.append("Practice speaking more clearly and at a moderate pace.")
        
        confidence = scores.get("confidence")
        if confidence is not None:
            if confidence >= 80:
                feedback_parts.append("You projected strong confidence throughout the interview.")
            elif confidence >= 60:
                feedback_parts.append("Your confidence level was reasonable. Regular mock interviews will help you feel more self-assured.")
            else:
                feedback_parts.append("Build confidence through regular practice and thorough preparation.")
        
        return " ".join(feedback_parts)
    
    def _generate_recommendations(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        interview_type: str
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Check if audio/video was used - recommend using them if not
        interview_mode = scores.get("interview_mode", "text")
        detailed = scores.get("detailed", {})
        has_audio = detailed.get("has_speech_data", False)
        has_video = scores.get("emotion") is not None
        
        # Recommend using audio if not used
        if not has_audio:
            recommendations.append({
                "type": "mode",
                "priority": "high",
                "text": "Enable microphone in your next interview to get feedback on speech clarity, fluency, and confidence. This provides a more realistic interview experience.",
                "action": "enable_audio",
                "icon": "mic"
            })
        
        # Recommend using video if not used
        if not has_video:
            recommendations.append({
                "type": "mode",
                "priority": "medium",
                "text": "Enable camera in your next interview to receive feedback on facial expressions, eye contact, and body language. Non-verbal communication is crucial in real interviews.",
                "action": "enable_video",
                "icon": "videocam"
            })
        
        # Based on overall score — provide recommendations at ALL levels
        overall = scores["overall"]
        if overall >= 90:
            recommendations.append({
                "type": "general",
                "priority": "low",
                "text": "Challenge yourself with harder difficulty levels or try different interview types to broaden your skills",
                "action": "increase_difficulty"
            })
        elif overall >= 80:
            recommendations.append({
                "type": "general",
                "priority": "low",
                "text": "Practice with time constraints to simulate real interview pressure and refine your responses further",
                "action": "timed_practice"
            })
        elif overall >= 70:
            recommendations.append({
                "type": "general",
                "priority": "medium",
                "text": "Focus on adding specific examples and metrics to your answers to make them more impactful",
                "action": "enhance_answers"
            })
        elif overall >= 60:
            recommendations.append({
                "type": "general",
                "priority": "medium",
                "text": "Practice the STAR method (Situation, Task, Action, Result) to structure your answers better",
                "action": "star_method"
            })
        else:
            recommendations.append({
                "type": "general",
                "priority": "high",
                "text": "Schedule more practice interviews to build fundamental skills",
                "action": "practice_interview"
            })
        
        # Based on weak areas
        for weak_area in weak_areas[:3]:
            area = weak_area["area"]
            score = weak_area["score"]
            
            if area == "Speech Clarity":
                recommendations.append({
                    "type": "speech",
                    "priority": "high" if score < 50 else "medium",
                    "text": "Practice vocal exercises and record yourself speaking",
                    "action": "speech_practice"
                })
            elif area == "Speech Fluency":
                recommendations.append({
                    "type": "speech",
                    "priority": "high" if score < 50 else "medium",
                    "text": "Work on reducing filler words and improving flow",
                    "action": "fluency_practice"
                })
            elif area == "Confidence":
                recommendations.append({
                    "type": "confidence",
                    "priority": "high" if score < 50 else "medium",
                    "text": "Practice stress management and positive visualization",
                    "action": "confidence_building"
                })
            else:
                recommendations.append({
                    "type": "content",
                    "priority": "high" if score < 50 else "medium",
                    "text": f"Study and practice {area} questions",
                    "action": "topic_study",
                    "topic": area
                })
        
        # Interview type specific recommendations
        if interview_type == "technical":
            if scores["content"] < 70:
                recommendations.append({
                    "type": "technical",
                    "priority": "high",
                    "text": "Practice coding problems on platforms like LeetCode or HackerRank",
                    "action": "coding_practice"
                })
        elif interview_type == "hr":
            recommendations.append({
                "type": "behavioral",
                "priority": "medium",
                "text": "Prepare STAR method responses for common HR questions",
                "action": "behavioral_prep"
            })
        
        # General best practices
        recommendations.append({
            "type": "general",
            "priority": "low",
            "text": "Review your recorded responses to identify improvement areas",
            "action": "self_review"
        })
        
        return recommendations

    def _get_course_recommendations(
        self,
        weak_areas: List[Dict],
        interview_type: str
    ) -> List[Dict]:
        """Get course recommendations based on weak areas"""
        
        course_recommendations = []
        added_topics = set()  # Track added topics to avoid duplicates
        
        # Process each weak area
        for weak_area in weak_areas:
            area = weak_area.get("area", "").lower()
            severity = weak_area.get("severity", "medium")
            
            # Find matching courses
            matched_courses = self._find_courses_for_topic(area)
            
            for course in matched_courses[:2]:  # Limit to 2 courses per weak area
                course_key = course["url"]
                if course_key not in added_topics:
                    added_topics.add(course_key)
                    course_recommendations.append({
                        "topic": weak_area.get("area", area.title()),
                        "severity": severity,
                        "course": course
                    })
        
        # Add general interview prep courses if few recommendations
        if len(course_recommendations) < 3:
            if interview_type == "technical":
                tech_courses = self._find_courses_for_topic("algorithms")
                for course in tech_courses[:1]:
                    if course["url"] not in added_topics:
                        added_topics.add(course["url"])
                        course_recommendations.append({
                            "topic": "Technical Interview Prep",
                            "severity": "medium",
                            "course": course
                        })
            
            general_courses = self._find_courses_for_topic("general")
            for course in general_courses[:1]:
                if course["url"] not in added_topics:
                    added_topics.add(course["url"])
                    course_recommendations.append({
                        "topic": "Interview Skills",
                        "severity": "low",
                        "course": course
                    })
        
        # Sort by severity (high first)
        severity_order = {"high": 0, "medium": 1, "low": 2}
        course_recommendations.sort(key=lambda x: severity_order.get(x["severity"], 1))
        
        return course_recommendations[:6]  # Return top 6 recommendations
    
    def _find_courses_for_topic(self, topic: str) -> List[Dict]:
        """Find courses matching a topic using fuzzy matching"""
        
        topic_lower = topic.lower().strip()
        matched_courses = []
        
        # Direct match
        if topic_lower in self.course_database:
            matched_courses.extend(self.course_database[topic_lower])
        
        # Partial/keyword matching
        topic_keywords = set(topic_lower.split())
        
        for db_topic, courses in self.course_database.items():
            if db_topic == topic_lower:
                continue  # Already added
            
            db_keywords = set(db_topic.split())
            
            # Check if any keywords match
            if topic_keywords & db_keywords:
                matched_courses.extend(courses)
            # Check if topic is contained in db_topic or vice versa
            elif topic_lower in db_topic or db_topic in topic_lower:
                matched_courses.extend(courses)
        
        # Remove duplicates while preserving order
        seen_urls = set()
        unique_courses = []
        for course in matched_courses:
            if course["url"] not in seen_urls:
                seen_urls.add(course["url"])
                unique_courses.append(course)
        
        return unique_courses
