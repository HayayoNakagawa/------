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
    cur.execute("SELECT student_id, name, department FROM students")
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
    cur.execute("""
        SELECT
            students.student_id,
            students.name,
            students.department,
            MAX(CASE WHEN scores.subject = '国語' THEN scores.score END),
            MAX(CASE WHEN scores.subject = '数学' THEN scores.score END),
            MAX(CASE WHEN scores.subject = '英語' THEN scores.score END),
            MAX(CASE WHEN scores.subject = '情報' THEN scores.score END)
        FROM students
        LEFT JOIN scores ON students.student_id = scores.student_id
        GROUP BY students.student_id, students.name, students.department
        ORDER BY students.student_id
    """)
    rows = cur.fetchall()
    return render_template("scores.html", scores=rows)

@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_id = request.form["student_id"]
        name = request.form["name"]
        grade = request.form["grade"]
        department = request.form["department"]

        db = sqlite3.connect(DATABASE)
        cur = db.cursor()

        cur.execute(
            """
            INSERT INTO students (student_id, name, grade, department)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, name, grade, department)
        )

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
