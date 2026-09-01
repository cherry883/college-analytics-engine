import sqlite3
import pandas as pd

DB_NAME = "college_intelligence.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Master Cleaned Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_360 (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        branch TEXT NOT NULL,
        admission_year INTEGER,
        contact TEXT,
        semester INTEGER,
        sgpa REAL,
        cgpa REAL,
        backlogs INTEGER DEFAULT 0,
        total_classes INTEGER DEFAULT 0,
        attended_classes INTEGER DEFAULT 0,
        attendance_pct REAL,
        is_registered BOOLEAN DEFAULT 0,
        offers_count INTEGER DEFAULT 0,
        package_lpa REAL DEFAULT 0.0,
        status TEXT DEFAULT 'UNPLACED',
        academic_standing TEXT,
        is_placement_eligible BOOLEAN DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file TEXT,
        student_id TEXT,
        issue TEXT,
        raw_record TEXT,
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # View 1: Overall College Top 10 (Ranked by CGPA, Alphabetical by Name)
    cursor.execute("DROP VIEW IF EXISTS view_overall_top_performers;")
    cursor.execute("""
    CREATE VIEW view_overall_top_performers AS
    WITH RankedOverall AS (
        SELECT 
            student_id,
            name,
            branch,
            cgpa,
            attendance_pct,
            academic_standing,
            ROW_NUMBER() OVER (ORDER BY cgpa DESC, attendance_pct DESC) AS overall_rank
        FROM student_360
    )
    SELECT 
        name,
        branch,
        cgpa,
        attendance_pct,
        academic_standing,
        overall_rank
    FROM RankedOverall
    WHERE overall_rank <= 10
    ORDER BY name ASC;
    """)

    # View 2: Top 10 Branch-Wise (Ranked by CGPA, Alphabetical by Name within Branch)
    cursor.execute("DROP VIEW IF EXISTS view_top_performers_per_branch;")
    cursor.execute("""
    CREATE VIEW view_top_performers_per_branch AS
    WITH RankedStudents AS (
        SELECT 
            student_id,
            name,
            branch,
            cgpa,
            attendance_pct,
            academic_standing,
            ROW_NUMBER() OVER (
                PARTITION BY branch 
                ORDER BY cgpa DESC, attendance_pct DESC
            ) AS rank_in_branch
        FROM student_360
    )
    SELECT 
        name,
        branch,
        cgpa,
        attendance_pct,
        academic_standing,
        rank_in_branch
    FROM RankedStudents
    WHERE rank_in_branch <= 10
    ORDER BY branch ASC, name ASC;
    """)

    # View 3: At-Risk Students
    cursor.execute("DROP VIEW IF EXISTS view_at_risk_students;")
    cursor.execute("""
    CREATE VIEW view_at_risk_students AS
    SELECT 
        student_id,
        name,
        branch,
        cgpa,
        attendance_pct,
        backlogs,
        academic_standing
    FROM student_360
    WHERE academic_standing IN ('CRITICAL_RISK', 'ATTENDANCE_SHORTAGE', 'ACADEMIC_DEFICIT')
    ORDER BY branch ASC, name ASC;
    """)

    # View 4: Department-Wise KPIs
    cursor.execute("DROP VIEW IF EXISTS view_department_kpis;")
    cursor.execute("""
    CREATE VIEW view_department_kpis AS
    SELECT 
        branch,
        COUNT(*) AS total_students,
        ROUND(AVG(cgpa), 2) AS avg_cgpa,
        ROUND(AVG(attendance_pct), 2) AS avg_attendance_pct,
        SUM(CASE WHEN is_placement_eligible = 1 THEN 1 ELSE 0 END) AS placement_eligible_count,
        SUM(CASE WHEN offers_count > 0 THEN 1 ELSE 0 END) AS students_placed_count,
        ROUND(AVG(package_lpa), 2) AS avg_package_lpa
    FROM student_360
    GROUP BY branch
    ORDER BY branch ASC;
    """)

    conn.commit()
    conn.close()

def save_to_database(clean_df: pd.DataFrame, audit_df: pd.DataFrame = None):
    conn = get_connection()
    clean_df.to_sql('student_360', conn, if_exists='replace', index=False)
    if audit_df is not None and not audit_df.empty:
        audit_df.to_sql('audit_logs', conn, if_exists='append', index=False)
    conn.close()

def fetch_overall_top_students():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM view_overall_top_performers ORDER BY name ASC;", conn)
    conn.close()
    return df

def fetch_top_students(branch: str = None):
    conn = get_connection()
    if branch and branch != "ALL":
        query = "SELECT * FROM view_top_performers_per_branch WHERE branch = ? ORDER BY name ASC;"
        df = pd.read_sql_query(query, conn, params=[branch])
    else:
        query = "SELECT * FROM view_top_performers_per_branch ORDER BY branch ASC, name ASC;"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_at_risk_students():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM view_at_risk_students;", conn)
    conn.close()
    return df

def fetch_department_kpis():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM view_department_kpis;", conn)
    conn.close()
    return df