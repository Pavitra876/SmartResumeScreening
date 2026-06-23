"""
database.py
Handles all SQLite database setup and operations for the
Smart Resume Screening and Career Improvement System.
"""

import sqlite3
from datetime import date

DB_NAME = "database.db"


def get_connection():
    """Open a connection to the SQLite database file.
    Creates the file automatically if it doesn't exist yet."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["name"]
    return conn


def init_db():
    """Create all tables if they don't already exist.
    Safe to call every time the app starts."""
    conn = get_connection()
    cur = conn.cursor()

    # Users table: students and admins
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'  -- 'student' or 'admin'
        )
    """)

    # Job Roles table: e.g. "Data Analyst", "Backend Developer"
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_roles (
            role_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    """)

    # Skills table: master list of all known skills
    cur.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT UNIQUE NOT NULL,
            category TEXT  -- e.g. 'Technical', 'Soft Skills', 'Tools'
        )
    """)

    # Many-to-many: which skills are required for which job role
    cur.execute("""
        CREATE TABLE IF NOT EXISTS role_skills (
            role_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            PRIMARY KEY (role_id, skill_id),
            FOREIGN KEY (role_id) REFERENCES job_roles(role_id),
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        )
    """)

    # Resume table: one row per uploaded resume
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resume (
            resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            extracted_text TEXT,
            upload_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # ATS Results table: one row per analysis run
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ats_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            resume_id INTEGER NOT NULL,
            ats_score REAL NOT NULL,
            matched_skills TEXT,   -- comma-separated list
            missing_skills TEXT,   -- comma-separated list
            analysis_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (role_id) REFERENCES job_roles(role_id),
            FOREIGN KEY (resume_id) REFERENCES resume(resume_id)
        )
    """)

    conn.commit()
    conn.close()


# ---------- USERS ----------

def create_user(name, email, password_hash, role="student"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, role)
    )
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row


# ---------- JOB ROLES ----------

def add_job_role(role_name, description=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO job_roles (role_name, description) VALUES (?, ?)",
        (role_name, description)
    )
    conn.commit()
    conn.close()


def get_all_job_roles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM job_roles")
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------- SKILLS ----------

def add_skill(skill_name, category="Technical"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO skills (skill_name, category) VALUES (?, ?)",
        (skill_name, category)
    )
    conn.commit()
    conn.close()


def link_skill_to_role(role_id, skill_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO role_skills (role_id, skill_id) VALUES (?, ?)",
        (role_id, skill_id)
    )
    conn.commit()
    conn.close()


def get_skills_for_role(role_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT skills.skill_name FROM skills
        JOIN role_skills ON skills.skill_id = role_skills.skill_id
        WHERE role_skills.role_id = ?
    """, (role_id,))
    rows = cur.fetchall()
    conn.close()
    return [row["skill_name"] for row in rows]


# ---------- RESUME ----------

def save_resume(user_id, file_name, extracted_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO resume (user_id, file_name, extracted_text, upload_date) VALUES (?, ?, ?, ?)",
        (user_id, file_name, extracted_text, str(date.today()))
    )
    conn.commit()
    resume_id = cur.lastrowid
    conn.close()
    return resume_id


# ---------- ATS RESULTS ----------

def save_ats_result(user_id, role_id, resume_id, ats_score, matched_skills, missing_skills):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ats_results
        (user_id, role_id, resume_id, ats_score, matched_skills, missing_skills, analysis_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, role_id, resume_id, ats_score,
        ",".join(matched_skills), ",".join(missing_skills), str(date.today())
    ))
    conn.commit()
    conn.close()


def get_results_for_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ats_results WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    # Running this file directly (python database.py) sets up the database
    # and seeds starter job roles + skills + role-skill mappings,
    # so ATS scoring has real data to compare against.
    init_db()
    print("Database initialized successfully.")

    # ---- Seed job roles ----
    add_job_role("Data Analyst", "Analyzes data to support business decisions")
    add_job_role("Backend Developer", "Builds server-side application logic")
    add_job_role("Machine Learning Engineer", "Builds and deploys ML models")

    # ---- Seed master skills list ----
    skills_master = [
        ("Python", "Technical"), ("SQL", "Technical"), ("Excel", "Tools"),
        ("Machine Learning", "Technical"), ("Communication", "Soft Skills"),
        ("Git", "Tools"), ("Java", "Technical"), ("REST API", "Technical"),
        ("Django", "Technical"), ("Flask", "Technical"), ("Docker", "Tools"),
        ("AWS", "Tools"), ("Pandas", "Technical"), ("NumPy", "Technical"),
        ("Data Visualization", "Technical"), ("Power BI", "Tools"),
        ("Tableau", "Tools"), ("TensorFlow", "Technical"), ("PyTorch", "Technical"),
        ("Deep Learning", "Technical"), ("Statistics", "Technical"),
        ("Problem Solving", "Soft Skills"), ("Teamwork", "Soft Skills"),
        ("Leadership", "Soft Skills"),
    ]
    for name, category in skills_master:
        add_skill(name, category)

    # ---- Map which skills belong to which role ----
    # role_id 1 = Data Analyst, 2 = Backend Developer, 3 = ML Engineer
    role_skill_map = {
        "Data Analyst": ["Python", "SQL", "Excel", "Data Visualization",
                          "Power BI", "Tableau", "Statistics", "Communication", "Pandas"],
        "Backend Developer": ["Python", "Java", "REST API", "Django", "Flask",
                               "Git", "Docker", "AWS", "SQL", "Problem Solving"],
        "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning",
                                       "TensorFlow", "PyTorch", "Statistics",
                                       "NumPy", "Pandas", "SQL", "Problem Solving"],
    }

    roles = {row["role_name"]: row["role_id"] for row in get_all_job_roles()}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT skill_id, skill_name FROM skills")
    skill_ids = {row["skill_name"]: row["skill_id"] for row in cur.fetchall()}
    conn.close()

    for role_name, skill_list in role_skill_map.items():
        role_id = roles[role_name]
        for skill_name in skill_list:
            link_skill_to_role(role_id, skill_ids[skill_name])

    print("Seed data inserted (job roles, skills, and role-skill mappings).")