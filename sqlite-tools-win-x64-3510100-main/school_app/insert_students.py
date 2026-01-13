import sqlite3
import random

# ----------------------------
# 名前リスト（適度な量を用意）
# ----------------------------
last_names = ["佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤"]
first_names = ["太郎", "花子", "翔", "結衣", "大輝", "さくら", "海斗", "陽菜", "蓮", "美咲"]

# ----------------------------
# DB 接続
# ----------------------------
conn = sqlite3.connect("school.db")
cur = conn.cursor()

# ----------------------------
# テーブルが無ければ作る
# ----------------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    grade INTEGER NOT NULL,
    year INTEGER NOT NULL
)
""")

# ----------------------------
# 90人分の学生データを挿入
# ----------------------------
start_year = 2023
student_count_per_year = 90

for i in range(1, student_count_per_year + 1):
    student_id = f"54{start_year}{i:03d}"
    name = random.choice(last_names) + random.choice(first_names)
    department = "情報科学科"
    grade = 1
    year = start_year

    cur.execute(
        "INSERT INTO students (student_id, name, department, grade, year) VALUES (?, ?, ?, ?, ?)",
        (student_id, name, department, grade, year),
    )

conn.commit()
conn.close()

print("✔ 90名の学生データを挿入しました！")
