"""Test the new scoring system with multiple scenarios"""
from ai_modules.nlp.answer_evaluator import AnswerEvaluator

evaluator = AnswerEvaluator()

print("=" * 60)
print("SCORING SYSTEM TEST")
print("=" * 60)

# Test 1: Excellent detailed answer
answer1 = """I am a software engineer with 5 years of experience in building scalable web applications. 
I have worked extensively with Python, JavaScript, and cloud technologies like AWS. 
In my previous role at a tech startup, I led a team of 4 developers and successfully delivered multiple projects on time. 
I am passionate about clean code and best practices. 
I believe in continuous learning and stay updated with the latest technologies. 
My approach involves understanding business requirements first and then designing solutions that are both efficient and maintainable."""

result1 = evaluator.evaluate_answer(question="Tell me about yourself", answer=answer1)
print(f"\n1. EXCELLENT ANSWER (detailed, 96 words):")
print(f"   Content: {result1['content_score']}%  Relevance: {result1['relevance_score']}%")

# Test 2: Good medium answer
answer2 = """I have 3 years of experience as a software developer. I work with Python and JavaScript. 
In my current role, I build web applications and work with databases. 
I enjoy solving complex problems and learning new technologies."""

result2 = evaluator.evaluate_answer(question="Tell me about yourself", answer=answer2)
print(f"\n2. GOOD ANSWER (medium length, ~45 words):")
print(f"   Content: {result2['content_score']}%  Relevance: {result2['relevance_score']}%")

# Test 3: Brief but acceptable answer
answer3 = """I am a developer with experience in web technologies. I enjoy coding and problem solving."""

result3 = evaluator.evaluate_answer(question="Tell me about yourself", answer=answer3)
print(f"\n3. BRIEF ANSWER (~18 words):")
print(f"   Content: {result3['content_score']}%  Relevance: {result3['relevance_score']}%")

# Test 4: Very short answer
answer4 = """I am a software engineer."""

result4 = evaluator.evaluate_answer(question="Tell me about yourself", answer=answer4)
print(f"\n4. VERY SHORT ANSWER (~5 words):")
print(f"   Content: {result4['content_score']}%  Relevance: {result4['relevance_score']}%")

# Test 5: Gibberish/Lorem Ipsum
answer5 = """Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor."""

result5 = evaluator.evaluate_answer(question="Tell me about yourself", answer=answer5)
print(f"\n5. GIBBERISH (Lorem Ipsum):")
print(f"   Content: {result5['content_score']}%  Relevance: {result5['relevance_score']}%")

# Test 6: Technical answer with keywords
answer6 = """When faced with a challenging problem, I first analyze the situation to understand what went wrong.
I gather information from relevant sources and then develop a plan of action.
For example, in my previous role, we had a critical production issue that was causing downtime.
I led the team to identify the root cause, implemented a fix, and established monitoring to prevent recurrence.
The result was a 40% reduction in similar incidents."""

result6 = evaluator.evaluate_answer(
    question="Describe a time you solved a difficult problem",
    answer=answer6,
    expected_keywords=["problem", "solution", "result", "action"]
)
print(f"\n6. BEHAVIORAL ANSWER (with keywords):")
print(f"   Content: {result6['content_score']}%  Relevance: {result6['relevance_score']}%")

print("\n" + "=" * 60)
print("EXPECTED RANGES:")
print("  Excellent: 85-100%")
print("  Good: 75-85%")
print("  Acceptable: 65-75%")
print("  Needs Improvement: <65%")
print("=" * 60)
