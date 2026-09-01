import io
import sqlite3
from typing import Optional
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from etl_pipeline import CollegeDataETL
from database_setup import init_database, save_to_database, DB_NAME

app = FastAPI(
    title="College Intelligence Platform API",
    description="Unified API for student performance, attendance, and placement analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def on_startup():
    init_database()

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "College Intelligence API"}

@app.get("/api/students")
def get_students(
    branch: Optional[str] = Query(None),
    standing: Optional[str] = Query(None),
    is_placement_eligible: Optional[bool] = Query(None),
    min_cgpa: Optional[float] = Query(0.0)
):
    conn = get_db_connection()
    query = "SELECT * FROM student_360 WHERE cgpa >= ?"
    params = [min_cgpa]

    if branch:
        query += " AND branch = ?"
        params.append(branch.upper().strip())
    if standing:
        query += " AND academic_standing = ?"
        params.append(standing.upper().strip())
    if is_placement_eligible is not None:
        query += " AND is_placement_eligible = ?"
        params.append(1 if is_placement_eligible else 0)

    query += " ORDER BY name ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/students/top-performers/overall")
def get_overall_top_performers():
    """Fetches overall top 10 college performers ordered alphabetically."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM view_overall_top_performers ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/students/top-performers")
def get_top_performers(branch: Optional[str] = None):
    """Fetches top 10 per branch ordered alphabetically."""
    conn = get_db_connection()
    if branch and branch != "ALL":
        query = "SELECT * FROM view_top_performers_per_branch WHERE branch = ? ORDER BY name ASC"
        rows = conn.execute(query, (branch.upper().strip(),)).fetchall()
    else:
        query = "SELECT * FROM view_top_performers_per_branch ORDER BY branch ASC, name ASC"
        rows = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/students/at-risk")
def get_at_risk_students():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM view_at_risk_students ORDER BY branch ASC, name ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/analytics/kpis")
def get_department_kpis():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM view_department_kpis").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/etl/upload")
async def upload_and_process_data(
    file_students: UploadFile = File(...),
    file_academics: UploadFile = File(...),
    file_attendance: UploadFile = File(...),
    file_placement: UploadFile = File(...)
):
    try:
        df_students = pd.read_csv(io.BytesIO(await file_students.read()))
        df_academics = pd.read_csv(io.BytesIO(await file_academics.read()))
        df_attendance = pd.read_csv(io.BytesIO(await file_attendance.read()))
        df_placement = pd.read_csv(io.BytesIO(await file_placement.read()))

        etl = CollegeDataETL()
        clean_df, audit_df = etl.integrate_all(
            df_students, 
            df_academics, 
            df_attendance, 
            df_placement
        )

        save_to_database(clean_df, audit_df)

        return {
            "status": "success",
            "message": "Files integrated successfully",
            "processed_students_count": len(clean_df),
            "anomalies_detected_count": len(audit_df)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ETL Error: {str(e)}")