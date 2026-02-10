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
        
        # Calculate scores
        scores = self._calculate_all_scores(responses)
        
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
            "overall_score": 70,
            "content_score": 70,
            "clarity_score": 70,
            "fluency_score": 70,
            "confidence_score": 70,
            "emotion_score": 70,
            "weak_areas": [],
            "strong_areas": [],
            "feedback": "No responses were recorded for this interview. This may be due to a technical issue.",
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
    
    def _calculate_all_scores(self, responses: List[Response]) -> Dict:
        """Calculate all performance scores"""
        
        # Content scores
        content_scores = [r.content_score for r in responses if r.content_score is not None]
        relevance_scores = [r.relevance_score for r in responses if r.relevance_score is not None]
        
        # Speech scores
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        
        # Emotion scores
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        
        # Calculate averages
        avg_content = sum(content_scores) / len(content_scores) if content_scores else 0
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        avg_clarity = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Combined scores
        content_combined = (avg_content * 0.6 + avg_relevance * 0.4) if (content_scores or relevance_scores) else 0
        
        # Check if we have speech/emotion data
        has_speech_data = bool(clarity_scores or fluency_scores)
        has_confidence_data = bool(confidence_scores)
        
        # Calculate speech combined (use content-based estimate if no speech data)
        if has_speech_data:
            speech_combined = (avg_clarity + avg_fluency) / 2
        else:
            # Estimate speech quality based on content quality when no audio data
            speech_combined = content_combined * 0.9  # Slight reduction as estimate
            # Also set individual scores to estimated values
            avg_clarity = content_combined * 0.9
            avg_fluency = content_combined * 0.9
        
        # Use content-based estimate for confidence if not available
        if not has_confidence_data:
            avg_confidence = content_combined * 0.85  # Estimate based on content
        
        # Overall score (weighted average)
        overall = (
            content_combined * 0.40 +  # 40% content
            speech_combined * 0.30 +   # 30% speech quality
            avg_confidence * 0.30      # 30% confidence/emotion
        )
        
        return {
            "overall": round(overall, 2),
            "content": round(content_combined, 2),
            "clarity": round(avg_clarity, 2),
            "fluency": round(avg_fluency, 2),
            "confidence": round(avg_confidence, 2),
            "emotion": round(avg_confidence, 2),  # Using confidence as emotion score
            "detailed": {
                "average_content": round(avg_content, 2),
                "average_relevance": round(avg_relevance, 2),
                "average_clarity": round(avg_clarity, 2),
                "average_fluency": round(avg_fluency, 2),
                "average_confidence": round(avg_confidence, 2)
            }
        }
    
    def _identify_weak_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify weak performance areas"""
        
        weak_areas = []
        
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
        
        # Identify categories with low scores
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 65:  # Threshold for weak area
                weak_areas.append({
                    "area": category,
                    "score": round(avg_score, 2),
                    "responses_count": len(scores),
                    "severity": "high" if avg_score < 50 else "medium"
                })
        
        # Check specific skills
        # Speech clarity
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        if clarity_scores:
            avg_clarity = sum(clarity_scores) / len(clarity_scores)
            if avg_clarity < 65:
                weak_areas.append({
                    "area": "Speech Clarity",
                    "score": round(avg_clarity, 2),
                    "responses_count": len(clarity_scores),
                    "severity": "high" if avg_clarity < 50 else "medium"
                })
        
        # Speech fluency
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        if fluency_scores:
            avg_fluency = sum(fluency_scores) / len(fluency_scores)
            if avg_fluency < 65:
                weak_areas.append({
                    "area": "Speech Fluency",
                    "score": round(avg_fluency, 2),
                    "responses_count": len(fluency_scores),
                    "severity": "high" if avg_fluency < 50 else "medium"
                })
        
        # Confidence
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence < 65:
                weak_areas.append({
                    "area": "Confidence",
                    "score": round(avg_confidence, 2),
                    "responses_count": len(confidence_scores),
                    "severity": "high" if avg_confidence < 50 else "medium"
                })
        
        # Sort by severity and score
        weak_areas.sort(key=lambda x: (x["severity"] == "high", -x["score"]), reverse=True)
        
        return weak_areas[:5]  # Top 5 weak areas
    
    def _identify_strong_areas(self, responses: List[Response], db: Session) -> List[Dict]:
        """Identify strong performance areas"""
        
        strong_areas = []
        
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
        
        # Identify categories with high scores
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 75:  # Threshold for strong area
                strong_areas.append({
                    "area": category,
                    "score": round(avg_score, 2),
                    "responses_count": len(scores)
                })
        
        # Check specific skills
        # Speech clarity
        clarity_scores = [r.clarity_score for r in responses if r.clarity_score is not None]
        if clarity_scores:
            avg_clarity = sum(clarity_scores) / len(clarity_scores)
            if avg_clarity >= 75:
                strong_areas.append({
                    "area": "Speech Clarity",
                    "score": round(avg_clarity, 2),
                    "responses_count": len(clarity_scores)
                })
        
        # Speech fluency
        fluency_scores = [r.fluency_score for r in responses if r.fluency_score is not None]
        if fluency_scores:
            avg_fluency = sum(fluency_scores) / len(fluency_scores)
            if avg_fluency >= 75:
                strong_areas.append({
                    "area": "Speech Fluency",
                    "score": round(avg_fluency, 2),
                    "responses_count": len(fluency_scores)
                })
        
        # Confidence
        confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence >= 75:
                strong_areas.append({
                    "area": "Confidence",
                    "score": round(avg_confidence, 2),
                    "responses_count": len(confidence_scores)
                })
        
        # Sort by score (highest first)
        strong_areas.sort(key=lambda x: x["score"], reverse=True)
        
        return strong_areas[:5]  # Top 5 strong areas
    
    def _generate_comprehensive_feedback(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        strong_areas: List[Dict]
    ) -> str:
        """Generate comprehensive feedback"""
        
        feedback_parts = []
        
        # Overall performance
        overall = scores["overall"]
        if overall >= 80:
            feedback_parts.append("Excellent overall performance! You demonstrated strong skills across multiple areas.")
        elif overall >= 60:
            feedback_parts.append("Good performance with room for improvement in several areas.")
        elif overall >= 40:
            feedback_parts.append("Fair performance. Focus on improving key skills to enhance your interview readiness.")
        else:
            feedback_parts.append("Your performance needs significant improvement. Practice and preparation will help you succeed.")
        
        # Strong areas
        if strong_areas:
            areas_text = ", ".join([area["area"] for area in strong_areas[:3]])
            feedback_parts.append(f"Your strengths include: {areas_text}.")
        
        # Weak areas
        if weak_areas:
            areas_text = ", ".join([area["area"] for area in weak_areas[:3]])
            feedback_parts.append(f"Areas needing improvement: {areas_text}.")
        
        # Specific skill feedback
        if scores["content"] < 60:
            feedback_parts.append("Work on providing more detailed and relevant answers with concrete examples.")
        
        if scores["clarity"] < 60:
            feedback_parts.append("Practice speaking more clearly and at a moderate pace.")
        
        if scores["confidence"] < 60:
            feedback_parts.append("Build confidence through regular practice and preparation.")
        
        return " ".join(feedback_parts)
    
    def _generate_recommendations(
        self,
        scores: Dict,
        weak_areas: List[Dict],
        interview_type: str
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Based on overall score
        if scores["overall"] < 60:
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
