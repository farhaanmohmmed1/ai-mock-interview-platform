import sqlite3

conn = sqlite3.connect('interview_platform.db')

# List all tables
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor]
print("Tables:", tables)

# Check response table
try:
    cursor = conn.execute("SELECT id, question_id, content_score, relevance_score, clarity_score, fluency_score, confidence_score, created_at FROM responses ORDER BY id DESC LIMIT 5")
    print("\nLast 5 responses:")
    print("id | q_id | content | relevance | clarity | fluency | confidence | created")
    for row in cursor:
        print(row)
except Exception as e:
    print(f"Error: {e}")

conn.close()
