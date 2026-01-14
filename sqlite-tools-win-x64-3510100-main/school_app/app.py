from flask import Flask, g, render_template
from flask import request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "school.db"

# ======================
# DB 初期化
# ======================
def init_db():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()

    # students テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL
    )
    """)

    # scores テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        student_id TEXT,
        subject TEXT,
        score INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(student_id)
    )
    """)

    db.commit()
    db.close()

# ======================
# DB 接続取得
# ======================
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# ======================
# ルーティング
# ======================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/students")
def students():
    cur = get_db().cursor()
    search = request.args.get('search', '').strip()
    
    if search:
        # 名前または学籍番号で検索
        cur.execute(
            "SELECT student_id, name, department, grade, year FROM students WHERE name LIKE ? OR student_id LIKE ? ORDER BY student_id",
            (f"%{search}%", f"%{search}%")
        )
    else:
        cur.execute("SELECT student_id, name, department, grade, year FROM students ORDER BY student_id")
    
    rows = cur.fetchall()
    return render_template("students.html", students=rows)

@app.route("/students/<student_id>")
def student_detail(student_id):
    cur = get_db().cursor()

    cur.execute(
        "SELECT student_id, name, department FROM students WHERE student_id = ?",
        (student_id,)
    )
    student = cur.fetchone()

    cur.execute(
        "SELECT subject, score FROM scores WHERE student_id = ?",
        (student_id,)
    )
    scores = cur.fetchall()

    return render_template(
        "student_detail.html",
        student=student,
        scores=scores
    )

@app.route("/scores")
def scores():
    cur = get_db().cursor()
    search = request.args.get('search', '').strip()
    
    # 動的に科目一覧を取得
    cur.execute("SELECT DISTINCT subject FROM scores ORDER BY subject")
    subjects = [r[0] for r in cur.fetchall()]

    # 学生取得（検索条件がある場合はフィルタリング）
    if search:
        cur.execute(
            "SELECT student_id, name, department, grade, year FROM students WHERE name LIKE ? OR student_id LIKE ? ORDER BY student_id",
            (f"%{search}%", f"%{search}%")
        )
    else:
        cur.execute("SELECT student_id, name, department, grade, year FROM students ORDER BY student_id")
    
    students = cur.fetchall()

    # 各学生ごとに科目->点数のマッピングを作る
    rows = []
    for student_id, name, department, grade, year in students:
        cur.execute("SELECT subject, score FROM scores WHERE student_id = ?", (student_id,))
        score_map = {r[0]: r[1] for r in cur.fetchall()}
        row = [student_id, name, department, grade, year] + [score_map.get(s) for s in subjects]
        rows.append(row)

    return render_template("scores.html", subjects=subjects, scores=rows)

@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_id = request.form["student_id"]
        name = request.form["name"]
        department = request.form["department"]
        grade = request.form["grade"]
        year = request.form["year"]

        db = sqlite3.connect(DATABASE)
        cur = db.cursor()

        # 学生情報を挿入
        cur.execute(
            "INSERT INTO students (student_id, name, department, grade, year) VALUES (?, ?, ?, ?, ?)",
            (student_id, name, department, grade, year)
        )

        # 成績を挿入（複数科目対応）
        subjects = request.form.getlist("subjects")
        scores = request.form.getlist("scores")
        
        for subject, score in zip(subjects, scores):
            if subject and score:  # 空でないもののみ挿入
                try:
                    cur.execute(
                        "INSERT INTO scores (student_id, subject, score) VALUES (?, ?, ?)",
                        (student_id, subject, int(score))
                    )
                except (ValueError, sqlite3.Error):
                    # スコアが数値でない場合やDB エラーはスキップ
                    pass

        db.commit()
        db.close()

        return redirect("/students")

    return render_template("add_student.html")

@app.route("/students/<student_id>/add_score", methods=["POST"])
def add_score(student_id):
    subject = request.form["subject"]
    score = request.form["score"]

    cur = get_db().cursor()
    cur.execute(
        "INSERT INTO scores (student_id, subject, score) VALUES (?, ?, ?)",
        (student_id, subject, score)
    )
    get_db().commit()

    return redirect(url_for("student_detail", student_id=student_id))

@app.route("/students/<student_id>/edit", methods=["POST"])
def edit_scores(student_id):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT subject FROM scores WHERE student_id = ?",
        (student_id,)
    )
    subjects = cur.fetchall()

    for (subject,) in subjects:
        new_score = request.form.get(subject)
        if new_score:
            cur.execute(
                "UPDATE scores SET score = ? WHERE student_id = ? AND subject = ?",
                (int(new_score), student_id, subject)
            )

    db.commit()
    return redirect(url_for("student_detail", student_id=student_id))

# ======================
# 起動時 DB 初期化
# ======================
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
