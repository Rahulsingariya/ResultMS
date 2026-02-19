def calculate_grade(marks, max_marks=100):
    """Return letter grade and GPA point based on percentage."""
    pct = (marks / max_marks) * 100

    if pct >= 90:
        return "A+", 10.0
    elif pct >= 80:
        return "A", 9.0
    elif pct >= 70:
        return "B+", 8.0
    elif pct >= 60:
        return "B", 7.0
    elif pct >= 50:
        return "C+", 6.0
    elif pct >= 40:
        return "C", 5.0
    elif pct >= 33:
        return "D", 4.0
    else:
        return "F", 0.0


def get_grade_color(grade):
    """CSS class name based on grade."""
    mapping = {
        "A+": "grade-aplus",
        "A":  "grade-a",
        "B+": "grade-bplus",
        "B":  "grade-b",
        "C+": "grade-cplus",
        "C":  "grade-c",
        "D":  "grade-d",
        "F":  "grade-f",
    }
    return mapping.get(grade, "grade-f")


def get_result_summary(results):
    """Return aggregate stats for a list of result rows."""
    if not results:
        return None

    total_marks    = sum(r["marks"]     for r in results)
    total_max      = sum(r["max_marks"] for r in results)
    percentage     = (total_marks / total_max) * 100 if total_max else 0
    overall_grade, gpa = calculate_grade(percentage)
    passed         = all(r["marks"] >= (r["max_marks"] * 0.33) for r in results)

    return {
        "total_marks":    total_marks,
        "total_max":      total_max,
        "percentage":     round(percentage, 2),
        "overall_grade":  overall_grade,
        "gpa":            gpa,
        "status":         "PASS" if passed else "FAIL",
        "grade_color":    get_grade_color(overall_grade),
    }
