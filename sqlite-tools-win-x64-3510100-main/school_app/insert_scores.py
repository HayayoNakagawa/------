import sqlite3
import random

subjects = ["国語", "数学", "英語", "情報"]

conn = sqlite3.connect("school.db")
cur = conn.cursor()

# 全学生IDを取得
cur.execute("SELECT student_id FROM students")
students = cur.fetchall()

count = 0

for (student_id,) in students:
    for subject in subjects:
        score = random.randint(40, 100)  # 点数は40〜100
        cur.execute(
            "INSERT INTO scores (student_id, subject, score) VALUES (?, ?, ?)",
            (student_id, subject, score)
        )
        count += 1

conn.commit()
conn.close()

print(f"✔ 成績データ {count} 件を挿入しました！")
