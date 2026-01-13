import sqlite3

conn = sqlite3.connect("school.db")
cursor = conn.cursor()

# 学生テーブル
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    grade INTEGER NOT NULL,
    year INTEGER NOT NULL
);
""")

# 成績テーブル
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
""")

conn.commit()
conn.close()

print("DB を作成しました")
