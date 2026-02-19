import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "results.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # ── Users table (for login/signup) ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname   TEXT NOT NULL,
            username   TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Students table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no    TEXT UNIQUE NOT NULL,
            name       TEXT NOT NULL,
            class      TEXT NOT NULL,
            section    TEXT NOT NULL,
            email      TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Subjects table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            class      TEXT NOT NULL,
            max_marks  INTEGER NOT NULL DEFAULT 100
        )
    """)

    # Results table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            subject_id  INTEGER NOT NULL,
            exam_type   TEXT NOT NULL,
            marks       REAL NOT NULL,
            grade       TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # Seed default subjects
    try:
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_subject_name_class ON subjects(name, class)")
    except Exception:
        pass

    default_subjects = [
        ("Mathematics",    "Class 9",  100),
        ("Science",        "Class 9",  100),
        ("English",        "Class 9",  100),
        ("Social Studies", "Class 9",  100),
        ("Computer",       "Class 9",  100),
        ("Hindi",          "Class 9",  100),
        ("Mathematics",    "Class 10", 100),
        ("Science",        "Class 10", 100),
        ("English",        "Class 10", 100),
        ("Social Studies", "Class 10", 100),
        ("Computer",       "Class 10", 100),
        ("Hindi",          "Class 10", 100),
        ("Mathematics",    "Class 11", 100),
        ("Physics",        "Class 11", 100),
        ("Chemistry",      "Class 11", 100),
        ("English",        "Class 11", 100),
        ("Computer",       "Class 11", 100),
        ("Hindi",          "Class 11", 100),
        ("Mathematics",    "Class 12", 100),
        ("Physics",        "Class 12", 100),
        ("Chemistry",      "Class 12", 100),
        ("English",        "Class 12", 100),
        ("Computer",       "Class 12", 100),
        ("Hindi",          "Class 12", 100),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO subjects (name, class, max_marks) VALUES (?,?,?)",
        default_subjects
    )

    conn.commit()
    conn.close()
    print("[DB] Database initialised at", DB_PATH)