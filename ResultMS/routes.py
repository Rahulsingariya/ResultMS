from flask import render_template, request, redirect, url_for, flash, jsonify
from database import get_connection
from helpers import calculate_grade, get_result_summary, get_grade_color


def register_routes(app):

    # ─────────────────────────────────────────────
    # DASHBOARD
    # ─────────────────────────────────────────────
    @app.route("/")
    def dashboard():
        conn = get_connection()
        cur  = conn.cursor()

        stats = {
            "total_students": cur.execute("SELECT COUNT(*) FROM students").fetchone()[0],
            "total_subjects": cur.execute("SELECT COUNT(*) FROM subjects").fetchone()[0],
            "total_results":  cur.execute("SELECT COUNT(*) FROM results").fetchone()[0],
            "pass_count": cur.execute("""
                SELECT COUNT(*) FROM (
                    SELECT r.student_id
                    FROM results r
                    JOIN subjects s ON r.subject_id = s.id
                    GROUP BY r.student_id, r.exam_type
                    HAVING MIN(r.marks * 100.0 / s.max_marks) >= 33
                )
            """).fetchone(),
        }
        stats["pass_count"] = stats["pass_count"][0] if stats["pass_count"] else 0

        # Recent results
        recent = cur.execute("""
            SELECT st.name, st.roll_no, sub.name AS subject,
                   r.marks, s.max_marks, r.grade, r.exam_type
            FROM results r
            JOIN students st  ON r.student_id = st.id
            JOIN subjects sub ON r.subject_id = sub.id
            JOIN subjects s   ON r.subject_id = s.id
            ORDER BY r.created_at DESC LIMIT 8
        """).fetchall()

        # Class-wise count
        classes = cur.execute("""
            SELECT class, COUNT(*) as cnt FROM students GROUP BY class
        """).fetchall()

        conn.close()
        return render_template("dashboard.html", stats=stats, recent=recent, classes=classes)

    # ─────────────────────────────────────────────
    # STUDENTS
    # ─────────────────────────────────────────────
    @app.route("/students")
    def students():
        conn = get_connection()
        query = request.args.get("q", "").strip()
        cls   = request.args.get("class", "").strip()

        sql  = "SELECT * FROM students WHERE 1=1"
        params = []
        if query:
            sql += " AND (name LIKE ? OR roll_no LIKE ?)"
            params += [f"%{query}%", f"%{query}%"]
        if cls:
            sql += " AND class = ?"
            params.append(cls)
        sql += " ORDER BY roll_no"

        rows    = conn.execute(sql, params).fetchall()
        classes = conn.execute("SELECT DISTINCT class FROM students ORDER BY class").fetchall()
        conn.close()
        return render_template("students.html", students=rows, classes=classes,
                               query=query, selected_class=cls)

    @app.route("/students/add", methods=["GET", "POST"])
    def add_student():
        if request.method == "POST":
            roll_no = request.form["roll_no"].strip()
            name    = request.form["name"].strip()
            cls     = request.form["class"].strip()
            section = request.form["section"].strip()
            email   = request.form.get("email", "").strip()

            if not all([roll_no, name, cls, section]):
                flash("All fields except email are required.", "error")
                return redirect(url_for("add_student"))

            conn = get_connection()
            try:
                conn.execute(
                    "INSERT INTO students (roll_no, name, class, section, email) VALUES (?,?,?,?,?)",
                    (roll_no, name, cls, section, email)
                )
                conn.commit()
                flash(f"Student '{name}' added successfully!", "success")
            except Exception as e:
                flash(f"Roll number already exists or error: {e}", "error")
            finally:
                conn.close()
            return redirect(url_for("students"))

        return render_template("add_student.html")

    @app.route("/students/edit/<int:sid>", methods=["GET", "POST"])
    def edit_student(sid):
        conn = get_connection()
        if request.method == "POST":
            name    = request.form["name"].strip()
            cls     = request.form["class"].strip()
            section = request.form["section"].strip()
            email   = request.form.get("email", "").strip()
            conn.execute(
                "UPDATE students SET name=?, class=?, section=?, email=? WHERE id=?",
                (name, cls, section, email, sid)
            )
            conn.commit()
            conn.close()
            flash("Student updated successfully!", "success")
            return redirect(url_for("students"))

        student = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
        conn.close()
        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("students"))
        return render_template("edit_student.html", student=student)

    @app.route("/students/delete/<int:sid>", methods=["POST"])
    def delete_student(sid):
        conn = get_connection()
        conn.execute("DELETE FROM results  WHERE student_id=?", (sid,))
        conn.execute("DELETE FROM students WHERE id=?", (sid,))
        conn.commit()
        conn.close()
        flash("Student and all their results deleted.", "success")
        return redirect(url_for("students"))

    # ─────────────────────────────────────────────
    # SUBJECTS
    # ─────────────────────────────────────────────
    @app.route("/subjects")
    def subjects():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM subjects ORDER BY class, name").fetchall()
        conn.close()
        return render_template("subjects.html", subjects=rows)

    @app.route("/subjects/add", methods=["GET", "POST"])
    def add_subject():
        if request.method == "POST":
            name      = request.form["name"].strip()
            cls       = request.form["class"].strip()
            max_marks = int(request.form.get("max_marks", 100))

            if not name or not cls:
                flash("Subject name and class are required.", "error")
                return redirect(url_for("add_subject"))

            conn = get_connection()
            try:
                conn.execute("INSERT INTO subjects (name, class, max_marks) VALUES (?,?,?)",
                             (name, cls, max_marks))
                conn.commit()
                flash('Subject "' + name + '" added to ' + cls + ' successfully!', "success")
                return redirect(url_for("subjects"))
            except Exception as e:
                conn.rollback()
                if "UNIQUE constraint" in str(e):
                    flash('"' + name + '" already exists in ' + cls + '. Try a different name or class.', "error")
                else:
                    flash("Error adding subject: " + str(e), "error")
                return redirect(url_for("add_subject"))
            finally:
                conn.close()
        return render_template("add_subject.html")

    @app.route("/subjects/delete/<int:subid>", methods=["POST"])
    def delete_subject(subid):
        conn = get_connection()
        conn.execute("DELETE FROM results  WHERE subject_id=?", (subid,))
        conn.execute("DELETE FROM subjects WHERE id=?", (subid,))
        conn.commit()
        conn.close()
        flash("Subject deleted.", "success")
        return redirect(url_for("subjects"))

    # ─────────────────────────────────────────────
    # RESULTS — Enter / View
    # ─────────────────────────────────────────────
    @app.route("/results")
    def results():
        conn  = get_connection()
        cls   = request.args.get("class", "").strip()
        exam  = request.args.get("exam",  "").strip()
        query = request.args.get("q", "").strip()

        sql = """
            SELECT r.id, st.id AS student_id, st.name AS student_name,
                   st.roll_no, st.class, st.section,
                   sub.name AS subject_name, r.marks, sub.max_marks,
                   r.grade, r.exam_type
            FROM results r
            JOIN students st  ON r.student_id = st.id
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE 1=1
        """
        params = []
        if cls:
            sql += " AND st.class = ?"
            params.append(cls)
        if exam:
            sql += " AND r.exam_type = ?"
            params.append(exam)
        if query:
            sql += " AND (st.name LIKE ? OR st.roll_no LIKE ?)"
            params += [f"%{query}%", f"%{query}%"]
        sql += " ORDER BY st.roll_no, sub.name"

        rows = conn.execute(sql, params).fetchall()

        # Group rows by student
        from collections import OrderedDict
        grouped = OrderedDict()
        for r in rows:
            key = (r["student_id"], r["exam_type"])
            if key not in grouped:
                grouped[key] = {
                    "student_id":   r["student_id"],
                    "student_name": r["student_name"],
                    "roll_no":      r["roll_no"],
                    "class":        r["class"],
                    "section":      r["section"],
                    "exam_type":    r["exam_type"],
                    "subjects":     []
                }
            grouped[key]["subjects"].append({
                "id":          r["id"],
                "subject_name":r["subject_name"],
                "marks":       r["marks"],
                "max_marks":   r["max_marks"],
                "grade":       r["grade"]
            })

        # Compute summary per student group
        for key, grp in grouped.items():
            subs = grp["subjects"]
            total     = sum(s["marks"]     for s in subs)
            total_max = sum(s["max_marks"] for s in subs)
            pct       = round(total / total_max * 100, 1) if total_max else 0
            passed    = all(s["marks"] >= s["max_marks"] * 0.33 for s in subs)
            from helpers import calculate_grade
            overall_grade, _ = calculate_grade(pct)
            grp["total"]         = total
            grp["total_max"]     = total_max
            grp["percentage"]    = pct
            grp["overall_grade"] = overall_grade
            grp["status"]        = "PASS" if passed else "FAIL"

        classes = conn.execute("SELECT DISTINCT class FROM students ORDER BY class").fetchall()
        exams   = conn.execute("SELECT DISTINCT exam_type FROM results ORDER BY exam_type").fetchall()
        conn.close()
        return render_template("results.html",
                               grouped=list(grouped.values()),
                               classes=classes, exams=exams,
                               selected_class=cls, selected_exam=exam, query=query)

    @app.route("/results/add", methods=["GET", "POST"])
    def add_result():
        conn = get_connection()
        if request.method == "POST":
            student_id = int(request.form["student_id"])
            exam_type  = request.form["exam_type"].strip()

            inserted = 0
            updated  = 0

            for key, value in request.form.items():
                if not key.startswith("marks_"):
                    continue
                try:
                    subject_id = int(key.split("_", 1)[1])
                    marks      = float(value)
                except (ValueError, IndexError):
                    continue

                sub = conn.execute(
                    "SELECT max_marks FROM subjects WHERE id=?", (subject_id,)
                ).fetchone()
                max_marks = sub["max_marks"] if sub else 100
                grade, _  = calculate_grade(marks, max_marks)

                existing = conn.execute(
                    "SELECT id FROM results WHERE student_id=? AND subject_id=? AND exam_type=?",
                    (student_id, subject_id, exam_type)
                ).fetchone()

                if existing:
                    conn.execute(
                        "UPDATE results SET marks=?, grade=? WHERE id=?",
                        (marks, grade, existing["id"])
                    )
                    updated += 1
                else:
                    conn.execute(
                        "INSERT INTO results (student_id, subject_id, exam_type, marks, grade) VALUES (?,?,?,?,?)",
                        (student_id, subject_id, exam_type, marks, grade)
                    )
                    inserted += 1

            conn.commit()
            conn.close()

            msg = []
            if inserted: msg.append(f"{inserted} result(s) added")
            if updated:  msg.append(f"{updated} result(s) updated")
            flash(", ".join(msg) + " successfully!", "success")
            return redirect(url_for("results"))

        students = conn.execute("SELECT * FROM students ORDER BY class, roll_no").fetchall()
        conn.close()
        return render_template("add_result.html", students=students)

    @app.route("/results/delete/<int:rid>", methods=["POST"])
    def delete_result(rid):
        conn = get_connection()
        conn.execute("DELETE FROM results WHERE id=?", (rid,))
        conn.commit()
        conn.close()
        flash("Result deleted.", "success")
        return redirect(url_for("results"))

    # ─────────────────────────────────────────────
    # MARKSHEET  (individual student report)
    # ─────────────────────────────────────────────
    @app.route("/marksheet")
    def marksheet():
        conn      = get_connection()
        students  = conn.execute("SELECT * FROM students ORDER BY class, roll_no").fetchall()
        exams     = conn.execute("SELECT DISTINCT exam_type FROM results ORDER BY exam_type").fetchall()
        conn.close()
        return render_template("marksheet_select.html", students=students, exams=exams)

    @app.route("/marksheet/<int:sid>/<path:exam_type>")
    def marksheet_view(sid, exam_type):
        conn    = get_connection()
        student = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("marksheet"))

        rows = conn.execute("""
            SELECT sub.name AS subject, r.marks, sub.max_marks, r.grade
            FROM results r
            JOIN subjects sub ON r.subject_id = sub.id
            WHERE r.student_id=? AND r.exam_type=?
            ORDER BY sub.name
        """, (sid, exam_type)).fetchall()

        conn.close()
        summary = get_result_summary(rows)
        return render_template("marksheet_view.html",
                               student=student, results=rows,
                               exam_type=exam_type, summary=summary,
                               get_grade_color=get_grade_color)

    # ─────────────────────────────────────────────
    # API  (for dynamic subject filter in forms)
    # ─────────────────────────────────────────────
    @app.route("/api/subjects")
    def api_subjects():
        student_class = request.args.get("class", "").strip()
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, name, max_marks FROM subjects WHERE class=? ORDER BY name",
            (student_class,)
        ).fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])

    @app.route("/api/student_class/<int:sid>")
    def api_student_class(sid):
        conn = get_connection()
        row  = conn.execute("SELECT class FROM students WHERE id=?", (sid,)).fetchone()
        conn.close()
        return jsonify({"class": row["class"] if row else ""})