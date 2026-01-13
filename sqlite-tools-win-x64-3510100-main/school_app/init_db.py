import sqlite3

conn = sqlite3.connect("school.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS student (
    student_id TEXT PRIMARY KEY,
    name TEXT,
    grade INTEGER,
    major TEXT
);
""")

conn.commit()
conn.close()

print("DB を作成しました")
