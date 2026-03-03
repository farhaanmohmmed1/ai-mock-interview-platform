from ai_modules.nlp.answer_evaluator import AnswerEvaluator

evaluator = AnswerEvaluator()

print("=" * 70)
print("SCORING BANDS TEST")
print("=" * 70)
print("""
SCORING BANDS:
0-20:  Lorem Ipsum / gibberish / test responses
20-40: Proper English but obviously off-topic / no relevance
40-60: Slightly off-topic / one or two keywords / little relevance
60-80: On topic / few keyword matches / moderate relevance
80-100: Perfect alignment / keyword matching / high relevance
""")
print("=" * 70)

question = "What motivates you in your work?"
keywords = ["motivation", "drive", "passion", "goals", "achievement"]

# BAND 0-20: Lorem Ipsum / Gibberish
print("\n[BAND 0-20] Lorem Ipsum / Gibberish:")
lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
r = evaluator.evaluate_answer(question, lorem, keywords)
print(f"  Content: {r['content_score']:.0f}% | Relevance: {r['relevance_score']:.0f}% | Avg: {(r['content_score']+r['relevance_score'])/2:.0f}%")
print(f"  Feedback: {r['feedback'][:70]}...")

# BAND 0-20: Test response
print("\n[BAND 0-20] Test/Meta Response:")
test = "Hello, this is going to be a test to check whether the evaluation system is working properly for non-relevant answers."
r = evaluator.evaluate_answer(question, test, keywords)
print(f"  Content: {r['content_score']:.0f}% | Relevance: {r['relevance_score']:.0f}% | Avg: {(r['content_score']+r['relevance_score'])/2:.0f}%")
print(f"  Feedback: {r['feedback'][:70]}...")

# BAND 20-40: Proper English but off-topic
print("\n[BAND 20-40] Proper English but Obviously Off-topic:")
offtopic = "The weather today is really nice. I enjoy playing basketball on weekends and watching movies. My favorite color is blue and I have a pet dog named Max who loves going to the park."
r = evaluator.evaluate_answer(question, offtopic, keywords)
print(f"  Content: {r['content_score']:.0f}% | Relevance: {r['relevance_score']:.0f}% | Avg: {(r['content_score']+r['relevance_score'])/2:.0f}%")
print(f"  Feedback: {r['feedback'][:70]}...")

# BAND 40-60: Slightly off-topic, few keywords
print("\n[BAND 40-60] Slightly Off-topic / Few Keywords:")
slight = "I like to work hard and do my best every day. I think having goals is important for everyone. People should always try to improve themselves at work."
r = evaluator.evaluate_answer(question, slight, keywords)
print(f"  Content: {r['content_score']:.0f}% | Relevance: {r['relevance_score']:.0f}% | Avg: {(r['content_score']+r['relevance_score'])/2:.0f}%")
print(f"  Feedback: {r['feedback'][:70]}...")

# BAND 60-80: On topic, moderate relevance
print("\n[BAND 60-80] On Topic / Moderate Relevance:")
moderate = "My motivation comes from wanting to achieve my goals. I have a passion for learning new things and improving my skills. Working with a good team also drives me to perform better."
r = evaluator.evaluate_answer(question, moderate, keywords)
print(f"  Content: {r['content_score']:.0f}% | Relevance: {r['relevance_score']:.0f}% | Avg: {(r['content_score']+r['relevance_score'])/2:.0f}%")
print(f"  Feedback: {r['feedback'][:70]}...")

# BAND 80-100: Perfect alignment
print("\n[BAND 80-100] Perfect Alignment / High Relevance:")
excellent = "What motivates me in my work is a combination of passion for problem-solving and the drive to achieve meaningful goals. I find great motivation in seeing the direct impact of my contributions. For example, when I led a project that improved our system performance by 40%, the achievement motivated me to take on even bigger challenges. I believe setting clear goals and maintaining passion for continuous learning are key drivers of success in any role."
r = evaluator.evaluate_answer(question, excellent, keywords)
print(f"  Content: {r['content_score']:.0f}% | Relevance: {r['relevance_score']:.0f}% | Avg: {(r['content_score']+r['relevance_score'])/2:.0f}%")
print(f"  Feedback: {r['feedback'][:70]}...")

print("\n" + "=" * 70)
