from sqlalchemy.orm import Session
from typing import Dict, List
from backend.models import Interview, Response, Question
import numpy as np


# Course recommendations database - maps topics/skills to learning resources
COURSE_DATABASE = {
    # Programming Languages
    "java": [
        {"title": "Java Programming Masterclass", "platform": "Udemy", "url": "https://www.udemy.com/course/java-the-complete-java-developer-course/", "level": "Beginner to Advanced"},
        {"title": "Java Fundamentals", "platform": "Pluralsight", "url": "https://www.pluralsight.com/courses/java-fundamentals-language", "level": "Beginner"},
        {"title": "Java Programming", "platform": "Coursera", "url": "https://www.coursera.org/specializations/java-programming", "level": "Beginner"},
    ],
    "python": [
        {"title": "Complete Python Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/complete-python-bootcamp/", "level": "Beginner to Advanced"},
        {"title": "Python for Everybody", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python", "level": "Beginner"},
        {"title": "Python Documentation", "platform": "Official", "url": "https://docs.python.org/3/tutorial/", "level": "All Levels"},
    ],
    "javascript": [
        {"title": "The Complete JavaScript Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-javascript-course/", "level": "Beginner to Advanced"},
        {"title": "JavaScript: Understanding the Weird Parts", "platform": "Udemy", "url": "https://www.udemy.com/course/understand-javascript/", "level": "Intermediate"},
        {"title": "freeCodeCamp JavaScript", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "level": "Beginner"},
    ],
    "typescript": [
        {"title": "Understanding TypeScript", "platform": "Udemy", "url": "https://www.udemy.com/course/understanding-typescript/", "level": "Beginner to Intermediate"},
        {"title": "TypeScript Documentation", "platform": "Official", "url": "https://www.typescriptlang.org/docs/", "level": "All Levels"},
    ],
    "c++": [
        {"title": "Beginning C++ Programming", "platform": "Udemy", "url": "https://www.udemy.com/course/beginning-c-plus-plus-programming/", "level": "Beginner"},
        {"title": "C++ Tutorial", "platform": "W3Schools", "url": "https://www.w3schools.com/cpp/", "level": "Beginner"},
    ],
    "c#": [
        {"title": "C# Fundamentals", "platform": "Pluralsight", "url": "https://www.pluralsight.com/courses/csharp-fundamentals-dev", "level": "Beginner"},
        {"title": "C# Tutorial", "platform": "Microsoft Learn", "url": "https://learn.microsoft.com/en-us/dotnet/csharp/", "level": "Beginner"},
    ],
    "go": [
        {"title": "Go: The Complete Developer's Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/go-the-complete-developers-guide/", "level": "Beginner"},
        {"title": "Go Documentation", "platform": "Official", "url": "https://go.dev/doc/", "level": "All Levels"},
    ],
    "rust": [
        {"title": "The Rust Programming Language", "platform": "Official", "url": "https://doc.rust-lang.org/book/", "level": "Beginner"},
        {"title": "Rust by Example", "platform": "Official", "url": "https://doc.rust-lang.org/rust-by-example/", "level": "Beginner"},
    ],
    
    # Data Structures & Algorithms
    "data structures": [
        {"title": "Data Structures and Algorithms", "platform": "Coursera", "url": "https://www.coursera.org/specializations/data-structures-algorithms", "level": "Intermediate"},
        {"title": "Mastering Data Structures & Algorithms", "platform": "Udemy", "url": "https://www.udemy.com/course/datastructurescncpp/", "level": "Beginner to Advanced"},
        {"title": "LeetCode", "platform": "LeetCode", "url": "https://leetcode.com/", "level": "All Levels"},
    ],
    "algorithms": [
        {"title": "Algorithms Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/algorithms", "level": "Intermediate"},
        {"title": "Introduction to Algorithms (MIT)", "platform": "MIT OCW", "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/", "level": "Intermediate"},
        {"title": "HackerRank Algorithms", "platform": "HackerRank", "url": "https://www.hackerrank.com/domains/algorithms", "level": "All Levels"},
    ],
    
    # Databases
    "sql": [
        {"title": "The Complete SQL Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "level": "Beginner"},
        {"title": "SQL Tutorial", "platform": "W3Schools", "url": "https://www.w3schools.com/sql/", "level": "Beginner"},
        {"title": "SQLZoo", "platform": "SQLZoo", "url": "https://sqlzoo.net/", "level": "Beginner to Intermediate"},
    ],
    "database": [
        {"title": "Database Management Essentials", "platform": "Coursera", "url": "https://www.coursera.org/learn/database-management", "level": "Beginner"},
        {"title": "MongoDB University", "platform": "MongoDB", "url": "https://university.mongodb.com/", "level": "All Levels"},
    ],
    "mongodb": [
        {"title": "MongoDB - The Complete Developer's Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/mongodb-the-complete-developers-guide/", "level": "Beginner to Advanced"},
        {"title": "MongoDB University", "platform": "MongoDB", "url": "https://university.mongodb.com/", "level": "All Levels"},
    ],
    
    # Web Development
    "react": [
        {"title": "React - The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "level": "Beginner to Advanced"},
        {"title": "React Documentation", "platform": "Official", "url": "https://react.dev/learn", "level": "All Levels"},
        {"title": "freeCodeCamp React", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "level": "Beginner"},
    ],
    "angular": [
        {"title": "Angular - The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-guide-to-angular-2/", "level": "Beginner to Advanced"},
        {"title": "Angular Documentation", "platform": "Official", "url": "https://angular.io/docs", "level": "All Levels"},
    ],
    "vue": [
        {"title": "Vue - The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/vuejs-2-the-complete-guide/", "level": "Beginner to Advanced"},
        {"title": "Vue.js Documentation", "platform": "Official", "url": "https://vuejs.org/guide/introduction.html", "level": "All Levels"},
    ],
    "node": [
        {"title": "The Complete Node.js Developer Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/", "level": "Beginner to Advanced"},
        {"title": "Node.js Documentation", "platform": "Official", "url": "https://nodejs.org/en/docs/", "level": "All Levels"},
    ],
    "html": [
        {"title": "HTML & CSS Course", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "level": "Beginner"},
        {"title": "HTML Tutorial", "platform": "W3Schools", "url": "https://www.w3schools.com/html/", "level": "Beginner"},
    ],
    "css": [
        {"title": "Advanced CSS and Sass", "platform": "Udemy", "url": "https://www.udemy.com/course/advanced-css-and-sass/", "level": "Intermediate"},
        {"title": "CSS Tutorial", "platform": "W3Schools", "url": "https://www.w3schools.com/css/", "level": "Beginner"},
    ],
    
    # Cloud & DevOps
    "aws": [
        {"title": "AWS Certified Solutions Architect", "platform": "Udemy", "url": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/", "level": "Intermediate"},
        {"title": "AWS Training", "platform": "AWS", "url": "https://aws.amazon.com/training/", "level": "All Levels"},
    ],
    "azure": [
        {"title": "Microsoft Azure Fundamentals", "platform": "Microsoft Learn", "url": "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/", "level": "Beginner"},
    ],
    "docker": [
        {"title": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/", "level": "Beginner to Advanced"},
        {"title": "Docker Documentation", "platform": "Official", "url": "https://docs.docker.com/get-started/", "level": "Beginner"},
    ],
    "kubernetes": [
        {"title": "Kubernetes for Developers", "platform": "Udemy", "url": "https://www.udemy.com/course/kubernetes-for-developers/", "level": "Intermediate"},
        {"title": "Kubernetes Documentation", "platform": "Official", "url": "https://kubernetes.io/docs/tutorials/", "level": "Beginner"},
    ],
    "devops": [
        {"title": "DevOps Beginners to Advanced", "platform": "Udemy", "url": "https://www.udemy.com/course/decodingdevops/", "level": "Beginner to Advanced"},
        {"title": "DevOps Culture and Mindset", "platform": "Coursera", "url": "https://www.coursera.org/learn/devops-culture-and-mindset", "level": "Beginner"},
    ],
    
    # Machine Learning & AI
    "machine learning": [
        {"title": "Machine Learning by Andrew Ng", "platform": "Coursera", "url": "https://www.coursera.org/learn/machine-learning", "level": "Beginner to Intermediate"},
        {"title": "Machine Learning A-Z", "platform": "Udemy", "url": "https://www.udemy.com/course/machinelearning/", "level": "Beginner"},
    ],
    "deep learning": [
        {"title": "Deep Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning", "level": "Intermediate"},
        {"title": "PyTorch for Deep Learning", "platform": "Udemy", "url": "https://www.udemy.com/course/pytorch-for-deep-learning-with-python-bootcamp/", "level": "Intermediate"},
    ],
    "data science": [
        {"title": "Data Science Professional Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/ibm-data-science", "level": "Beginner"},
        {"title": "Data Science Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-data-science-course-complete-data-science-bootcamp/", "level": "Beginner to Advanced"},
    ],
    
    # System Design
    "system design": [
        {"title": "Grokking the System Design Interview", "platform": "Educative", "url": "https://www.educative.io/courses/grokking-the-system-design-interview", "level": "Intermediate to Advanced"},
        {"title": "System Design Primer", "platform": "GitHub", "url": "https://github.com/donnemartin/system-design-primer", "level": "Intermediate"},
    ],
    
    # Soft Skills
    "speech clarity": [
        {"title": "Improve Your Communication Skills", "platform": "Coursera", "url": "https://www.coursera.org/learn/wharton-communication-skills", "level": "All Levels"},
        {"title": "Public Speaking Mastery", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-public-speaking-certification-program/", "level": "Beginner"},
    ],
    "speech fluency": [
        {"title": "Speak English Fluently", "platform": "Udemy", "url": "https://www.udemy.com/course/speak-english-fluently/", "level": "Beginner to Intermediate"},
        {"title": "Communication Skills for Engineers", "platform": "Coursera", "url": "https://www.coursera.org/learn/communication-skills-engineers", "level": "Intermediate"},
    ],
    "confidence": [
        {"title": "Building Confidence and Self-Esteem", "platform": "Udemy", "url": "https://www.udemy.com/course/building-confidence-and-self-esteem/", "level": "All Levels"},
        {"title": "Developing Executive Presence", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/developing-executive-presence", "level": "Intermediate"},
    ],
    "communication": [
        {"title": "Effective Communication Skills", "platform": "Coursera", "url": "https://www.coursera.org/learn/wharton-communication-skills", "level": "All Levels"},
        {"title": "Business Communication", "platform": "Udemy", "url": "https://www.udemy.com/course/business-communication-skills/", "level": "Beginner"},
    ],
    
    # General Interview Prep
    "behavioral": [
        {"title": "Behavioral Interview Questions Mastery", "platform": "Udemy", "url": "https://www.udemy.com/course/behavioral-interview-questions/", "level": "All Levels"},
        {"title": "STAR Method Interview Prep", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/preparing-for-your-interview", "level": "Beginner"},
    ],
    "general": [
        {"title": "Interview Skills: How to Get the Job", "platform": "Udemy", "url": "https://www.udemy.com/course/interview-skills-that-win-the-job/", "level": "All Levels"},
        {"title": "Interviewing Skills", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/interviewing-techniques", "level": "All Levels"},
    ],
    
    # Interview Skills & Answer Quality
    "interview preparation": [
        {"title": "The Complete Interview Preparation Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-job-interview-preparation/", "level": "All Levels"},
        {"title": "Successful Interviewing", "platform": "Coursera", "url": "https://www.coursera.org/learn/successful-interviewing", "level": "Beginner"},
        {"title": "Interview Warmup by Google", "platform": "Google", "url": "https://grow.google/certificates/interview-warmup/", "level": "All Levels"},
    ],
    "answer clarity": [
        {"title": "Structured Communication: How to Organize Your Ideas", "platform": "Coursera", "url": "https://www.coursera.org/learn/structured-communication", "level": "Beginner"},
        {"title": "Improve Your Communication Skills", "platform": "Coursera", "url": "https://www.coursera.org/learn/wharton-communication-skills", "level": "All Levels"},
        {"title": "Clear and Effective Communication", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/communication-foundations-2", "level": "Beginner"},
    ],
    "communication flow": [
        {"title": "Speak English Professionally", "platform": "Coursera", "url": "https://www.coursera.org/learn/speak-english-professionally", "level": "Intermediate"},
        {"title": "Dynamic Public Speaking", "platform": "Coursera", "url": "https://www.coursera.org/specializations/public-speaking", "level": "Beginner"},
        {"title": "Communication Skills for Engineers", "platform": "Coursera", "url": "https://www.coursera.org/learn/communication-skills-engineers", "level": "Intermediate"},
    ],
    "confidence & assertiveness": [
        {"title": "Building Confidence and Self-Esteem", "platform": "Udemy", "url": "https://www.udemy.com/course/building-confidence-and-self-esteem/", "level": "All Levels"},
        {"title": "Developing Executive Presence", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/developing-executive-presence", "level": "Intermediate"},
        {"title": "Assertiveness and Confidence Training", "platform": "Udemy", "url": "https://www.udemy.com/course/assertiveness-training/", "level": "Beginner"},
    ],
    "expressiveness & engagement": [
        {"title": "Storytelling and Influencing: Communicate with Impact", "platform": "Coursera", "url": "https://www.coursera.org/learn/communicate-with-impact", "level": "Intermediate"},
        {"title": "Public Speaking Mastery", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-public-speaking-certification-program/", "level": "Beginner"},
        {"title": "Presentation Skills: Designing Presentation Slides", "platform": "Coursera", "url": "https://www.coursera.org/learn/presentation-skills", "level": "Beginner"},
    ],
    "answer depth": [
        {"title": "Critical Thinking & Problem Solving", "platform": "Coursera", "url": "https://www.coursera.org/learn/critical-thinking-problem-solving", "level": "Beginner"},
        {"title": "How to Answer Interview Questions Effectively", "platform": "Udemy", "url": "https://www.udemy.com/course/how-to-answer-interview-questions/", "level": "All Levels"},
    ],
    "answer thoroughness": [
        {"title": "How to Answer Interview Questions Effectively", "platform": "Udemy", "url": "https://www.udemy.com/course/how-to-answer-interview-questions/", "level": "All Levels"},
        {"title": "The Complete Interview Preparation Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-job-interview-preparation/", "level": "All Levels"},
    ],
    "star method": [
        {"title": "Master the STAR Interview Method", "platform": "Udemy", "url": "https://www.udemy.com/course/star-interview-method/", "level": "All Levels"},
        {"title": "STAR Method Interview Prep", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/preparing-for-your-interview", "level": "Beginner"},
    ],
    "problem solving": [
        {"title": "Creative Problem Solving", "platform": "Coursera", "url": "https://www.coursera.org/learn/creative-problem-solving", "level": "Beginner"},
        {"title": "Problem Solving Skills for Software Developers", "platform": "Udemy", "url": "https://www.udemy.com/course/problem-solving-skills-for-software-developers/", "level": "Intermediate"},
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
        
        # Expression scores from emotion_analysis JSON
        expression_scores = []
        for r in responses:
            if r.emotion_analysis and isinstance(r.emotion_analysis, dict):
                expr = r.emotion_analysis.get("expression_score")
                if expr is not None:
                    expression_scores.append(expr)
        
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
        
        # SCORING: All metrics are always available (estimated from text if no audio)
        # Content, Clarity, Fluency, Confidence are always scored
        # Expression requires video (emotion analyzer)
        
        if has_speech_data:
            speech_combined = (avg_clarity + avg_fluency) / 2
            final_clarity = avg_clarity
            final_fluency = avg_fluency
            final_confidence = avg_confidence if has_confidence_data else speech_combined
        else:
            # Fallback if somehow scores are missing
            speech_combined = 0
            final_clarity = 0
            final_fluency = 0
            final_confidence = 0
        
        # Expression score from emotion_analysis (text-estimated or video-analyzed)
        has_expression_data = bool(expression_scores)
        final_expression = avg_expression if has_expression_data else 0
        
        # Calculate overall from all available metrics
        # 25% content, 20% clarity+fluency, 20% confidence, 20% expression
        if has_speech_data and has_confidence_data and has_expression_data:
            raw_overall = (
                content_combined * 0.30 +
                speech_combined * 0.25 +
                final_confidence * 0.25 +
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
            "clarity": round(final_clarity, 2) if final_clarity is not None else 0,
            "fluency": round(final_fluency, 2) if final_fluency is not None else 0,
            "confidence": round(final_confidence, 2) if final_confidence is not None else 0,
            "emotion": round(final_expression, 2),
            "interview_mode": "video" if has_expression_data else ("audio" if has_speech_data else "text"),
            "detailed": {
                "average_content": round(avg_content, 2),
                "average_relevance": round(avg_relevance, 2),
                "average_clarity": round(avg_clarity, 2) if clarity_scores else 0,
                "average_fluency": round(avg_fluency, 2) if fluency_scores else 0,
                "average_confidence": round(avg_confidence, 2) if confidence_scores else 0,
                "average_expression": round(avg_expression, 2) if expression_scores else 0,
                "completion_ratio": round(completion_ratio, 2),
                "has_speech_data": has_speech_data,
                "has_confidence_data": has_confidence_data,
                "has_expression_data": has_expression_data
            }
        }
    
    def _get_suggestion_for_area(self, area: str, score: float) -> str:
        """Get a specific improvement suggestion based on area and score — warm and actionable"""
        suggestions = {
            "Answer Clarity": {
                "high": "Your answers would benefit from more structure. Try this: start with a one-sentence summary, give 2-3 supporting details, then wrap up with the impact. Frameworks like STAR (Situation, Task, Action, Result) work great for this.",
                "medium": "You're communicating your ideas, but they could be easier to follow. Try using clear transitions like 'first,' 'for example,' and 'as a result' to guide the listener through your response.",
                "low": "Your clarity is already quite good! To make it even better, make sure every answer has a punchy opening line that captures your main point right away."
            },
            "Communication Flow": {
                "high": "Let's work on making your answers flow more naturally. Try varying your sentence lengths, avoid repeating the same phrases, and use connecting words like 'furthermore,' 'as a result,' or 'specifically' to link your ideas.",
                "medium": "Your flow is decent, but could be smoother. Practice transitioning between ideas naturally — reading your answers aloud can help you spot where the flow breaks.",
                "low": "Good fluency overall! To refine it further, challenge yourself to use richer vocabulary and more varied sentence structures in your next practice session."
            },
            "Confidence & Assertiveness": {
                "high": "Confidence is built through preparation. Try replacing phrases like 'I think maybe I could...' with 'I'm confident I can...' or 'In my experience, I've successfully...' Also, prepare 3-5 specific achievements with numbers that you can reference anytime.",
                "medium": "Your tone is getting there! Start your answers with action verbs and accomplishments — 'I led,' 'I built,' 'I improved...' — this instantly makes you sound more decisive and capable.",
                "low": "Nice confidence level! To take it even further, own your achievements fully — don't downplay them with 'just' or 'only.' You earned those results, let them shine."
            },
            "Expressiveness & Engagement": {
                "high": "Interviewers want to see your personality! When discussing projects, share what genuinely excited you. Try phrases like 'What I loved about this project was...' or 'This was a fascinating challenge because...' — authenticity is key.",
                "medium": "You're showing some engagement, which is great. Add more by sharing brief moments that challenged or excited you. A sentence like 'This part was particularly interesting to me because...' adds a lot of warmth.",
                "low": "Your expressiveness is solid! To make answers even more engaging, try storytelling — set a scene, build tension around a challenge, then reveal your solution."
            }
        }
        
        if area in suggestions:
            if score < 50:
                return suggestions[area]["high"]
            elif score < 75:
                return suggestions[area]["medium"]
            else:
                return suggestions[area]["low"]
        
        # Category-based suggestions (for content areas like "Java Knowledge", "Python Knowledge", etc.)
        if score < 50:
            return f"This is a great area to focus on next. Revisit the fundamentals of {area.replace(' Knowledge', '')}, practice with sample questions, and study model answers to see how experts structure their responses."
        elif score < 65:
            return f"You have some foundation in {area.replace(' Knowledge', '')} — now deepen it by working through more examples and including specific details, metrics, and real-world experiences in your answers."
        elif score < 80:
            return f"Solid knowledge here! To level up, try adding more depth with unique insights, trade-off discussions, and structured examples that show you understand both the 'what' and the 'why.'"
        else:
            return f"Strong performance! Push for excellence by incorporating industry best practices, comparisons with alternatives, and demonstrating senior-level thinking in your responses."

    def _identify_weak_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify areas for improvement with detailed, actionable feedback"""
        
        all_areas = []
        
        # --- 1. Analyze per-question category performance (content + relevance) ---
        category_data = {}
        for response in responses:
            question = db.query(Question).filter(Question.id == response.question_id).first()
            if not question:
                continue
            
            category = question.category or question.question_type or "General"
            if category not in category_data:
                category_data[category] = {"content": [], "relevance": [], "keywords_missing": [], "questions": []}
            
            category_data[category]["content"].append(response.content_score or 0)
            category_data[category]["relevance"].append(response.relevance_score or 0)
            category_data[category]["questions"].append(question.question_text)
            
            # Collect missing keywords from NLP analysis
            if response.nlp_analysis and isinstance(response.nlp_analysis, dict):
                missing = response.nlp_analysis.get("keywords_missing", [])
                if missing:
                    category_data[category]["keywords_missing"].extend(missing)
        
        for category, data in category_data.items():
            avg_content = sum(data["content"]) / len(data["content"]) if data["content"] else 0
            avg_relevance = sum(data["relevance"]) / len(data["relevance"]) if data["relevance"] else 0
            combined = (avg_content * 0.6 + avg_relevance * 0.4)
            
            if combined < 80:
                severity = "high" if combined < 50 else ("medium" if combined < 65 else "low")
                
                # Build specific suggestion based on what's weak
                suggestion = self._get_category_suggestion(category, avg_content, avg_relevance, data["keywords_missing"])
                
                all_areas.append({
                    "area": f"{category} Knowledge",
                    "score": round(combined, 1),
                    "responses_count": len(data["content"]),
                    "severity": severity,
                    "suggestion": suggestion
                })
        
        # --- 2. Analyze communication skills across all responses ---
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        expression_scores = []
        for r in responses:
            if r.emotion_analysis and isinstance(r.emotion_analysis, dict):
                expr = r.emotion_analysis.get("expression_score")
                if expr is not None:
                    expression_scores.append(expr)
        
        # Clarity
        if clarity_scores:
            avg = sum(clarity_scores) / len(clarity_scores)
            if avg < 80:
                suggestion = (
                    "Your answers would benefit from more structure. Try starting with a clear summary sentence, then expanding with details, and ending with the impact or takeaway."
                    if avg < 60 else
                    "You're communicating your ideas, but making them easier to follow will help. Use signpost phrases like 'first,' 'for example,' and 'to summarize' to guide the listener."
                )
                all_areas.append({
                    "area": "Answer Clarity",
                    "score": round(avg, 1),
                    "severity": "high" if avg < 55 else "medium",
                    "suggestion": suggestion
                })
        
        # Fluency
        if fluency_scores:
            avg = sum(fluency_scores) / len(fluency_scores)
            if avg < 80:
                suggestion = (
                    "Let's work on making your answers flow more naturally. Practice using connecting phrases like 'as a result,' 'for instance,' and 'building on this' to link your ideas smoothly."
                    if avg < 60 else
                    "Good foundation! Try varying your sentence lengths and vocabulary to make your answers more engaging and natural-sounding."
                )
                all_areas.append({
                    "area": "Communication Flow",
                    "score": round(avg, 1),
                    "severity": "high" if avg < 55 else "medium",
                    "suggestion": suggestion
                })
        
        # Confidence
        if confidence_scores:
            avg = sum(confidence_scores) / len(confidence_scores)
            if avg < 80:
                suggestion = (
                    "You can sound much more confident by swapping tentative phrases ('I think maybe...') for assertive ones ('I'm confident that...' or 'In my experience...'). Having 3-5 prepared achievements with specific numbers also helps a lot."
                    if avg < 60 else
                    "Your confidence is growing! Start leading your answers with accomplishments and use strong action verbs like 'achieved,' 'led,' and 'implemented' to sound more decisive."
                )
                all_areas.append({
                    "area": "Confidence & Assertiveness",
                    "score": round(avg, 1),
                    "severity": "high" if avg < 55 else "medium",
                    "suggestion": suggestion
                })
        
        # Expression
        if expression_scores:
            avg = sum(expression_scores) / len(expression_scores)
            if avg < 80:
                suggestion = (
                    "Interviewers want to see the real you! When you're talking about your work, share what genuinely excites you about it. Personal stories and authentic enthusiasm make you memorable."
                    if avg < 60 else
                    "You're showing some engagement, which is great. Try adding lines like 'What I really enjoyed about this was...' or 'This challenge was fascinating because...' to bring more personality to your answers."
                )
                all_areas.append({
                    "area": "Expressiveness & Engagement",
                    "score": round(avg, 1),
                    "severity": "high" if avg < 55 else "medium",
                    "suggestion": suggestion
                })
        
        # --- 3. Check for specific answer quality patterns ---
        short_answers = sum(1 for r in responses if r.nlp_analysis and isinstance(r.nlp_analysis, dict) and r.nlp_analysis.get("word_count", 0) < 30)
        if short_answers > 0 and len(responses) > 0:
            ratio = short_answers / len(responses)
            if ratio >= 0.3:
                all_areas.append({
                    "area": "Answer Depth",
                    "score": round(max(30, 70 - ratio * 40), 1),
                    "severity": "high" if ratio >= 0.6 else "medium",
                    "suggestion": f"{short_answers} of {len(responses)} answers were quite brief. Try to aim for at least 3-4 sentences per answer — include a specific example, explain your reasoning, and describe the outcome or impact."
                })
        
        # Sort: lowest scores first
        all_areas.sort(key=lambda x: x["score"])
        
        return all_areas[:6]
    
    def _get_category_suggestion(self, category: str, content_score: float, relevance_score: float, missing_keywords: list) -> str:
        """Generate friendly, specific suggestion for a question category"""
        parts = []
        
        if content_score < 60:
            parts.append(f"Your {category} answers could use more depth — try including specific examples, technical details, or real experiences you've had.")
        elif content_score < 75:
            parts.append(f"Good start on {category}! Add more concrete examples and measurable outcomes (numbers, percentages, impact) to make your points stronger.")
        
        if relevance_score < 60:
            parts.append("Make sure to answer what's being asked first, then add context — interviewers want to see you directly address their question.")
        
        # Include missing keywords as topics to study
        unique_missing = list(set(missing_keywords))[:4]
        if unique_missing:
            parts.append(f"Brush up on these topics: {', '.join(unique_missing)} — they came up in the questions and would strengthen your answers.")
        
        if not parts:
            parts.append(f"You have a decent grasp of {category}. To take it further, try adding structured examples and quantify your impact when possible.")
        
        return " ".join(parts)
    
    def _identify_strong_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify strong performance areas with meaningful descriptions"""
        
        all_areas = []
        
        # --- 1. Analyze per-question category performance ---
        category_data = {}
        for response in responses:
            question = db.query(Question).filter(Question.id == response.question_id).first()
            if not question:
                continue
            
            category = question.category or question.question_type or "General"
            if category not in category_data:
                category_data[category] = {"content": [], "relevance": [], "keywords_found": []}
            
            category_data[category]["content"].append(response.content_score or 0)
            category_data[category]["relevance"].append(response.relevance_score or 0)
            
            if response.nlp_analysis and isinstance(response.nlp_analysis, dict):
                found = response.nlp_analysis.get("keywords_found", [])
                if found:
                    category_data[category]["keywords_found"].extend(found)
        
        for category, data in category_data.items():
            avg_content = sum(data["content"]) / len(data["content"]) if data["content"] else 0
            avg_relevance = sum(data["relevance"]) / len(data["relevance"]) if data["relevance"] else 0
            combined = (avg_content * 0.6 + avg_relevance * 0.4)
            
            if combined >= 75:
                keywords_found = list(set(data["keywords_found"]))[:3]
                
                if combined >= 90:
                    desc = f"You really nailed {category}! Your answers showed deep understanding, excellent structure, and covered all the key points. Keep this up!"
                elif combined >= 80:
                    desc = f"Great job on {category} — you demonstrated strong knowledge and gave detailed, relevant answers with good examples."
                else:
                    desc = f"Solid understanding of {category}. Your answers covered the core concepts well and showed good preparation."
                
                if keywords_found:
                    desc += f" You effectively discussed: {', '.join(keywords_found)}."
                
                all_areas.append({
                    "area": f"{category} Knowledge",
                    "score": round(combined, 1),
                    "responses_count": len(data["content"]),
                    "description": desc
                })
        
        # --- 2. Analyze communication skills ---
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        expression_scores = []
        for r in responses:
            if r.emotion_analysis and isinstance(r.emotion_analysis, dict):
                expr = r.emotion_analysis.get("expression_score")
                if expr is not None:
                    expression_scores.append(expr)
        
        if clarity_scores:
            avg = sum(clarity_scores) / len(clarity_scores)
            if avg >= 75:
                desc = (
                    "Your answers were exceptionally clear and well-organized — interviewers will find you easy to follow and understand. This is a real strength!"
                    if avg >= 85 else
                    "Good answer clarity! Your responses are structured and understandable, which makes a great impression in interviews."
                )
                all_areas.append({
                    "area": "Answer Clarity",
                    "score": round(avg, 1),
                    "description": desc
                })
        
        if fluency_scores:
            avg = sum(fluency_scores) / len(fluency_scores)
            if avg >= 75:
                desc = (
                    "Excellent communication flow! You used rich vocabulary and smooth transitions that made your answers engaging and professional."
                    if avg >= 85 else
                    "Nice fluency — your natural language and varied expressions make your answers pleasant to listen to."
                )
                all_areas.append({
                    "area": "Communication Flow",
                    "score": round(avg, 1),
                    "description": desc
                })
        
        if confidence_scores:
            avg = sum(confidence_scores) / len(confidence_scores)
            if avg >= 75:
                desc = (
                    "You projected strong confidence throughout — your assertive language and specific achievements made a compelling impression!"
                    if avg >= 85 else
                    "Good confidence level! You presented your ideas with conviction, which is exactly what interviewers want to see."
                )
                all_areas.append({
                    "area": "Confidence & Assertiveness",
                    "score": round(avg, 1),
                    "description": desc
                })
        
        if expression_scores:
            avg = sum(expression_scores) / len(expression_scores)
            if avg >= 75:
                desc = (
                    "Your answers were engaging and showed genuine enthusiasm — this kind of energy makes you a memorable candidate!"
                    if avg >= 85 else
                    "Nice expressiveness! Your answers convey real interest and engagement, which helps you connect with interviewers."
                )
                all_areas.append({
                    "area": "Expressiveness & Engagement",
                    "score": round(avg, 1),
                    "description": desc
                })
        
        # --- 3. Check for positive answer patterns ---
        detailed_answers = sum(1 for r in responses if r.nlp_analysis and isinstance(r.nlp_analysis, dict) and r.nlp_analysis.get("word_count", 0) >= 50)
        if detailed_answers > 0 and len(responses) > 0:
            ratio = detailed_answers / len(responses)
            if ratio >= 0.5:
                all_areas.append({
                    "area": "Answer Thoroughness",
                    "score": round(min(95, 70 + ratio * 25), 1),
                    "description": f"Great job providing detailed answers! {detailed_answers} of {len(responses)} responses were comprehensive and well-developed. This shows strong preparation and the ability to communicate complex ideas effectively."
                })
        
        # Sort by score (highest first)
        all_areas.sort(key=lambda x: x["score"], reverse=True)
        
        return all_areas[:6]
    
    def _generate_comprehensive_feedback(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        strong_areas: List[Dict]
    ) -> str:
        """Generate warm, human-friendly, constructive feedback like a supportive mentor"""
        
        paragraphs = []
        overall = scores["overall"]
        content = scores.get("content") or 0
        clarity = scores.get("clarity") or 0
        confidence = scores.get("confidence") or 0
        expression = scores.get("emotion") or 0
        
        # --- Opening: warm, personal, encouraging tone ---
        if overall >= 90:
            paragraphs.append(
                "You did an amazing job — seriously impressive! 🎉 Your answers were thoughtful, well-structured, "
                "and showed real depth of knowledge. You came across as someone who's prepared, confident, and genuinely "
                "engaged. This is the kind of performance that leaves a lasting impression on interviewers."
            )
        elif overall >= 80:
            paragraphs.append(
                "Great work! 👏 You showed strong skills across the board and came across as well-prepared. "
                "Your answers were solid, and you clearly have a good grasp of the topics covered. "
                "With just a few tweaks, you'll be in an excellent position for real interviews."
            )
        elif overall >= 70:
            paragraphs.append(
                "Nice effort! You demonstrated a solid understanding of the topics and communicated your ideas "
                "reasonably well. There's a good foundation here to build on. With some focused practice on the "
                "areas highlighted below, you can take your interview performance to the next level."
            )
        elif overall >= 60:
            paragraphs.append(
                "Good start! You've shown that you have the basics down, and that's a great place to begin. "
                "Every interviewer you meet started somewhere, and the fact that you're practicing puts you "
                "ahead of most. Let's focus on a few key areas that will make the biggest difference."
            )
        elif overall >= 40:
            paragraphs.append(
                "Thanks for putting in the effort — practice is the best way to improve, and you're on the right track. "
                "There are some areas that need attention, but don't worry — these are all things you can work on with "
                "consistent practice. Let's break down what went well and where you can grow."
            )
        else:
            paragraphs.append(
                "Don't be discouraged by this score — everyone starts somewhere, and the most important thing is that "
                "you're practicing. Many successful professionals struggled with interviews early on. "
                "Let's look at the specific areas you can focus on to see real improvement quickly."
            )
        
        # --- What went well (strengths acknowledgment) ---
        if strong_areas:
            strong_names = [area["area"] for area in strong_areas[:3]]
            if len(strong_names) == 1:
                strengths_text = strong_names[0]
            elif len(strong_names) == 2:
                strengths_text = f"{strong_names[0]} and {strong_names[1]}"
            else:
                strengths_text = f"{', '.join(strong_names[:-1])}, and {strong_names[-1]}"
            
            if overall >= 80:
                paragraphs.append(
                    f"You really shone in {strengths_text}. These are genuine strengths — "
                    "make sure to highlight them in real interviews. Interviewers notice when "
                    "someone speaks with this level of competence and conviction."
                )
            else:
                paragraphs.append(
                    f"On the positive side, you showed real strength in {strengths_text}. "
                    "That's something to feel good about! Build on these strengths while you "
                    "work on other areas — they'll be your anchor in real interviews."
                )
        
        # --- Where to improve (constructive, not critical) ---
        if weak_areas:
            weak_names = [area["area"] for area in weak_areas[:3]]
            if len(weak_names) == 1:
                weak_text = weak_names[0]
            elif len(weak_names) == 2:
                weak_text = f"{weak_names[0]} and {weak_names[1]}"
            else:
                weak_text = f"{', '.join(weak_names[:-1])}, and {weak_names[-1]}"
            
            if overall >= 75:
                paragraphs.append(
                    f"To go from great to outstanding, I'd suggest paying extra attention to {weak_text}. "
                    "These are minor areas, but polishing them will make your answers feel more complete and polished."
                )
            elif overall >= 55:
                paragraphs.append(
                    f"The areas where you have the most room to grow are {weak_text}. "
                    "Don't try to fix everything at once — pick one area and practice it in your next session. "
                    "Small, consistent improvements add up quickly."
                )
            else:
                paragraphs.append(
                    f"I'd recommend starting with {weak_text} — improving here will give you the biggest "
                    "boost in your overall performance. Check out the recommended courses below for structured guidance."
                )
        
        # --- Specific, conversational skill insights ---
        skill_insights = []
        
        if content >= 80:
            skill_insights.append("Your answers had great substance — you included relevant details and examples that made your points convincing.")
        elif content >= 60:
            skill_insights.append("Your answers had decent content, but try to include more specific examples, numbers, or outcomes to make them more impactful.")
        elif content > 0:
            skill_insights.append("Try to add more depth to your answers — real-world examples, specific metrics, and structured frameworks like STAR can make a big difference.")
        
        if clarity >= 80:
            skill_insights.append("Your ideas were well-organized and easy to follow — that's a skill interviewers really value.")
        elif clarity >= 60:
            skill_insights.append("Consider structuring your answers with a clear opening statement, supporting details, and a strong conclusion.")
        elif clarity > 0:
            skill_insights.append("Practice organizing your thoughts before speaking — try the \"answer first, explain second\" approach to keep your responses focused.")
        
        if confidence >= 80:
            skill_insights.append("You came across as confident and decisive — your use of assertive language was excellent.")
        elif confidence >= 60:
            skill_insights.append("You can sound more confident by replacing phrases like \"I think\" or \"maybe\" with \"I believe\" or \"In my experience.\"")
        elif confidence > 0:
            skill_insights.append("Building confidence takes practice. Start by preparing 3-5 key achievements you can reference in any interview — having these ready will help you feel more assured.")
        
        if expression >= 80:
            skill_insights.append("Your enthusiasm and engagement really came through — interviewers love candidates who show genuine interest.")
        elif expression >= 60:
            skill_insights.append("Try sharing what excites you about the topic — a little enthusiasm goes a long way in making you memorable.")
        elif expression > 0:
            skill_insights.append("Let your personality show! Interviewers want to see the real you. Share what motivates you and why you're passionate about your work.")
        
        if skill_insights:
            paragraphs.append(" ".join(skill_insights))
        
        # --- Closing: encouraging and forward-looking ---
        if overall >= 80:
            paragraphs.append("Keep up the great work — you're well on your way to acing your interviews! 🚀")
        elif overall >= 60:
            paragraphs.append("You're making good progress. Keep practicing, review the resources below, and you'll see real improvement in your next session. You've got this! 💪")
        else:
            paragraphs.append("Remember: interview skills are learnable, and every practice session makes you better. Review the tips and courses below, and come back to try again — you'll be surprised by how much you improve! 💪")
        
        return "\n\n".join(paragraphs)
    
    def _generate_recommendations(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        interview_type: str
    ) -> List[Dict]:
        """Generate specific, actionable, human-friendly recommendations"""
        
        recommendations = []
        overall = scores["overall"]
        content = scores.get("content") or 0
        clarity = scores.get("clarity") or 0
        confidence = scores.get("confidence") or 0
        expression = scores.get("emotion") or 0
        
        # Check if audio/video was used - recommend using them if not
        interview_mode = scores.get("interview_mode", "text")
        detailed = scores.get("detailed", {})
        has_audio = detailed.get("has_speech_data", False)
        has_video = scores.get("emotion") is not None
        
        if not has_audio:
            recommendations.append({
                "type": "mode",
                "priority": "high",
                "text": "Try enabling your microphone next time! Speaking your answers out loud is much closer to a real interview — plus you'll get feedback on how clear and fluent you sound.",
                "action": "enable_audio",
                "icon": "mic"
            })
        
        if not has_video:
            recommendations.append({
                "type": "mode",
                "priority": "medium",
                "text": "Consider turning on your camera for a more realistic experience. Body language, eye contact, and facial expressions play a big role in how interviewers perceive you.",
                "action": "enable_video",
                "icon": "videocam"
            })
        
        # --- Content-based recommendations ---
        if content < 50:
            recommendations.append({
                "type": "content",
                "priority": "high",
                "text": "Before your next practice, write down 3-5 key experiences or projects from your background. For each, note the situation, what you did, and the outcome. Having these ready will make your answers much stronger.",
                "action": "prepare_stories"
            })
        elif content < 70:
            recommendations.append({
                "type": "content",
                "priority": "medium",
                "text": "Your answers had good ideas but could use more specifics. Try including numbers (\"improved performance by 30%\"), tool names, or specific outcomes to make your points more convincing.",
                "action": "add_specifics"
            })
        elif content < 85:
            recommendations.append({
                "type": "content",
                "priority": "low",
                "text": "Strong content! To take it further, practice connecting your answers to the company's needs — show why your experience matters for the specific role you're targeting.",
                "action": "connect_to_role"
            })
        
        # --- Clarity recommendations ---
        if clarity > 0 and clarity < 60:
            recommendations.append({
                "type": "clarity",
                "priority": "high",
                "text": "Try the \"headline first\" technique: start each answer with a one-sentence summary, then provide details. For example: \"I led a team migration to cloud services\" → then explain how, why, and the results.",
                "action": "structure_answers"
            })
        elif clarity > 0 and clarity < 80:
            recommendations.append({
                "type": "clarity",
                "priority": "medium",
                "text": "Use signpost phrases like \"There are three main reasons...\" or \"First... Second... Finally...\" to help structure longer answers. This makes it easy for interviewers to follow your thinking.",
                "action": "add_signposts"
            })
        
        # --- Confidence recommendations ---
        if confidence > 0 and confidence < 55:
            recommendations.append({
                "type": "confidence",
                "priority": "high",
                "text": "Confidence grows with preparation. Before your next session, practice answering these 3 questions out loud: \"Tell me about yourself\", \"What's your greatest strength?\", and \"Describe a challenge you overcame.\" Repetition builds natural confidence.",
                "action": "confidence_drills"
            })
        elif confidence > 0 and confidence < 75:
            recommendations.append({
                "type": "confidence",
                "priority": "medium",
                "text": "Replace tentative language with assertive phrasing. Instead of \"I think I might be able to...\" say \"I'm confident I can...\" or \"In my experience, I've successfully...\" — small word changes make a big impact.",
                "action": "assertive_language"
            })
        
        # --- Expression recommendations ---
        if expression > 0 and expression < 60:
            recommendations.append({
                "type": "expression",
                "priority": "medium",
                "text": "Show your personality! When discussing projects, share what excited you about them. Phrases like \"What I really enjoyed about this was...\" or \"This was exciting because...\" help interviewers connect with you.",
                "action": "show_enthusiasm"
            })
        elif expression > 0 and expression < 80:
            recommendations.append({
                "type": "expression",
                "priority": "low",
                "text": "You're on the right track with expressiveness. Try varying your energy — show extra enthusiasm for topics you're passionate about, and use storytelling to make your answers more engaging.",
                "action": "vary_energy"
            })
        
        # --- Interview-type specific recommendations ---
        if interview_type == "technical":
            if content < 70:
                recommendations.append({
                    "type": "technical",
                    "priority": "high",
                    "text": "For technical interviews, practice explaining your thought process step by step. Interviewers care as much about HOW you think as WHAT you know. Try solving problems on LeetCode or HackerRank while narrating your approach.",
                    "action": "coding_practice"
                })
            else:
                recommendations.append({
                    "type": "technical",
                    "priority": "low",
                    "text": "Good technical foundation! Push yourself further by discussing trade-offs, scalability, and alternative approaches in your answers — this shows senior-level thinking.",
                    "action": "advanced_thinking"
                })
        elif interview_type == "hr" or interview_type == "behavioral":
            recommendations.append({
                "type": "behavioral",
                "priority": "medium",
                "text": "For behavioral questions, master the STAR method: briefly set the Situation, explain your Task, describe your specific Actions, and end with measurable Results. Practice with questions like \"Tell me about a time you handled conflict.\"",
                "action": "star_method"
            })
        elif interview_type == "general":
            recommendations.append({
                "type": "general",
                "priority": "medium",
                "text": "General interviews test both technical knowledge and soft skills. Practice answering a mix of \"tell me about yourself\" type questions AND role-specific questions to be ready for anything.",
                "action": "mixed_practice"
            })
        
        # --- Overall performance-based tip ---
        if overall >= 85:
            recommendations.append({
                "type": "general",
                "priority": "low",
                "text": "You're performing at a high level! Challenge yourself by trying harder difficulty settings or different interview types. Also consider doing mock interviews with a friend for real-time pressure practice.",
                "action": "increase_difficulty"
            })
        elif overall >= 65:
            recommendations.append({
                "type": "general",
                "priority": "medium",
                "text": "Record yourself answering questions and watch it back — you'll notice habits you didn't realize you had. This self-review technique is used by top performers in all fields.",
                "action": "self_review"
            })
        else:
            recommendations.append({
                "type": "general",
                "priority": "medium",
                "text": "Try doing one practice interview per day with just 3-5 questions. Consistency beats intensity — even 15 minutes of daily practice will lead to noticeable improvement within a week.",
                "action": "daily_practice"
            })
        
        # De-duplicate by action
        seen_actions = set()
        unique_recs = []
        for rec in recommendations:
            if rec["action"] not in seen_actions:
                seen_actions.add(rec["action"])
                unique_recs.append(rec)
        
        return unique_recs

    def _get_course_recommendations(
        self,
        weak_areas: List[Dict],
        interview_type: str
    ) -> List[Dict]:
        """Get course recommendations based on weak areas — always returns useful courses"""
        
        course_recommendations = []
        added_urls = set()  # Track by URL to avoid duplicates
        
        # Process each weak area
        for weak_area in weak_areas:
            area = weak_area.get("area", "")
            severity = weak_area.get("severity", "medium")
            
            # Find matching courses
            matched_courses = self._find_courses_for_topic(area)
            
            for course in matched_courses[:2]:  # Limit to 2 courses per weak area
                if course["url"] not in added_urls:
                    added_urls.add(course["url"])
                    course_recommendations.append({
                        "topic": area or "Interview Skills",
                        "severity": severity,
                        "course": course
                    })
        
        # Always include interview-type specific courses
        type_topic_map = {
            "technical": ["algorithms", "system design"],
            "hr": ["behavioral", "star method"],
            "behavioral": ["behavioral", "star method"],
            "general": ["interview preparation", "communication"],
        }
        
        type_topics = type_topic_map.get(interview_type, ["interview preparation"])
        for topic in type_topics:
            if len(course_recommendations) >= 6:
                break
            courses = self._find_courses_for_topic(topic)
            for course in courses[:1]:
                if course["url"] not in added_urls:
                    added_urls.add(course["url"])
                    course_recommendations.append({
                        "topic": topic.replace("_", " ").title(),
                        "severity": "low",
                        "course": course
                    })
        
        # Always ensure at least 3 recommendations
        fallback_topics = ["interview preparation", "communication", "confidence & assertiveness", "general"]
        for fallback in fallback_topics:
            if len(course_recommendations) >= 3:
                break
            courses = self._find_courses_for_topic(fallback)
            for course in courses[:1]:
                if course["url"] not in added_urls:
                    added_urls.add(course["url"])
                    course_recommendations.append({
                        "topic": fallback.replace("_", " ").title(),
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
        
        # Try stripping common suffixes like " Knowledge" from area names
        # e.g. "Java Knowledge" -> "java", "Python Knowledge" -> "python"
        stripped = topic_lower.replace(" knowledge", "").replace(" skills", "").strip()
        if stripped != topic_lower and stripped in self.course_database:
            matched_courses.extend(self.course_database[stripped])
        
        # Partial/keyword matching
        topic_keywords = set(topic_lower.split())
        # Also try keywords from stripped version
        if stripped != topic_lower:
            topic_keywords.update(stripped.split())
        
        # Remove common filler words for better matching
        filler_words = {"and", "the", "a", "an", "of", "for", "in", "&", "with"}
        topic_keywords -= filler_words
        
        for db_topic, courses in self.course_database.items():
            if db_topic == topic_lower or db_topic == stripped:
                continue  # Already added
            
            db_keywords = set(db_topic.split()) - filler_words
            
            # Check if any meaningful keywords match
            if topic_keywords & db_keywords:
                matched_courses.extend(courses)
            # Check if topic is contained in db_topic or vice versa
            elif topic_lower in db_topic or db_topic in topic_lower:
                matched_courses.extend(courses)
            elif stripped in db_topic or db_topic in stripped:
                matched_courses.extend(courses)
        
        # Remove duplicates while preserving order
        seen_urls = set()
        unique_courses = []
        for course in matched_courses:
            if course["url"] not in seen_urls:
                seen_urls.add(course["url"])
                unique_courses.append(course)
        
        return unique_courses
