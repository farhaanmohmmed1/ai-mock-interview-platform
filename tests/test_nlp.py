import pytest
from ai_modules.nlp.answer_evaluator import AnswerEvaluator


@pytest.fixture
def evaluator():
    return AnswerEvaluator()


def test_evaluate_good_answer(evaluator):
    """Test evaluation of a good answer"""
    question = "What is polymorphism in object-oriented programming?"
    answer = """
    Polymorphism is a core concept in object-oriented programming that allows objects 
    of different classes to be treated as objects of a common base class. For example, 
    in Python, we can have a base class Animal with a method speak(), and derived classes 
    like Dog and Cat can override this method with their own implementations. This enables 
    code reusability and flexibility.
    """
    keywords = ["objects", "classes", "base class", "override", "flexibility"]
    
    result = evaluator.evaluate_answer(question, answer, keywords, "technical")
    
    assert result["content_score"] > 60
    assert result["relevance_score"] > 60
    assert len(result["nlp_analysis"]["keywords_found"]) > 0


def test_evaluate_short_answer(evaluator):
    """Test evaluation of a short answer"""
    question = "What is polymorphism?"
    answer = "It's about inheritance."
    
    result = evaluator.evaluate_answer(question, answer, [], "technical")
    
    assert result["content_score"] < 50
    assert "too short" in result["feedback"].lower()


def test_evaluate_empty_answer(evaluator):
    """Test evaluation of an empty answer"""
    question = "What is polymorphism?"
    answer = ""
    
    result = evaluator.evaluate_answer(question, answer, [], "technical")
    
    assert result["content_score"] == 0
    assert result["relevance_score"] == 0
