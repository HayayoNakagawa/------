from flask import Flask, g, render_template
from flask import request, redirect, url_for

import sqlite3

app = Flask(__name__)

DATABASE = "school.db"

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

@app.route("/")
def index():
    return "Hello Flask!"

@app.route("/students")
def students():
    cur = get_db().cursor()
    cur.execute("SELECT student_id, name FROM students")
    rows = cur.fetchall()
    return render_template("students.html", students=rows)

@app.route("/students/<student_id>")
def student_detail(student_id):
    cur = get_db().cursor()

    # 学生情報
    cur.execute(
        "SELECT student_id, name FROM students WHERE student_id = ?",
        (student_id,)
    )
    student = cur.fetchone()

    # 成績情報
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
            MAX(CASE WHEN scores.subject = '国語' THEN scores.score END),
            MAX(CASE WHEN scores.subject = '数学' THEN scores.score END),
            MAX(CASE WHEN scores.subject = '英語' THEN scores.score END),
            MAX(CASE WHEN scores.subject = '情報' THEN scores.score END)
        FROM students
        JOIN scores ON students.student_id = scores.student_id
        GROUP BY students.student_id, students.name
        ORDER BY students.student_id
    """)
    rows = cur.fetchall()
    return render_template("scores.html", scores=rows)

@app.route("/students/<student_id>/edit", methods=["POST"])
def edit_scores(student_id):
    db = get_db()
    cur = db.cursor()

    # この学生の成績を取得
    cur.execute(
        "SELECT subject FROM scores WHERE student_id = ?",
        (student_id,)
    )
    subjects = cur.fetchall()

    # 各科目の点数を更新
    for (subject,) in subjects:
        new_score = request.form.get(subject)
        if new_score is not None:
            cur.execute(
                """
                UPDATE scores
                SET score = ?
                WHERE student_id = ? AND subject = ?
                """,
                (int(new_score), student_id, subject)
            )

    db.commit()

    return redirect(url_for("student_detail", student_id=student_id))


if __name__ == "__main__":
    app.run(debug=True)
