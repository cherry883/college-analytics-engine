import os
import pandas as pd
from etl_pipeline import CollegeDataETL
from database_setup import (
    init_database, 
    save_to_database, 
    fetch_overall_top_students,
    fetch_top_students, 
    fetch_at_risk_students, 
    fetch_department_kpis
)

# 1. Load CSVs
student_file = "student_master.csv" if os.path.exists("student_master.csv") else "student_master_2.csv"
academics_file = "academics.csv" if os.path.exists("academics.csv") else "academics_2.csv"
attendance_file = "attendance.csv" if os.path.exists("attendance.csv") else "attendance_2.csv"
placement_file = "placement.csv" if os.path.exists("placement.csv") else "placement_2.csv"

print(f"[INFO] Ingesting files: {student_file}, {academics_file}, {attendance_file}, {placement_file}")

df_students = pd.read_csv(student_file)
df_academics = pd.read_csv(academics_file)
df_attendance = pd.read_csv(attendance_file)
df_placement = pd.read_csv(placement_file)

# 2. Run ETL
etl = CollegeDataETL()
clean_df, audit_df = etl.integrate_all(
    df_students, 
    df_academics, 
    df_attendance, 
    df_placement
)

# 3. Store into SQLite
init_database()
save_to_database(clean_df, audit_df)

# 4. Display Overall College Toppers (Alphabetical)
print("\n" + "=" * 80)
print(" 🌟 OVERALL COLLEGE TOP 10 TOPPERS (ALPHABETICAL ORDER BY NAME)")
print("=" * 80)
overall_top = fetch_overall_top_students()
print(overall_top[['name', 'branch', 'cgpa', 'attendance_pct', 'academic_standing', 'overall_rank']].to_string(index=False))

# 5. Display Separate Branch-wise Tables (Alphabetical)
print("\n" + "=" * 80)
print(" 📁 BRANCH-WISE TOP PERFORMERS (SEPARATE TABLES — ALPHABETICAL BY NAME)")
print("=" * 80)
all_branch_top = fetch_top_students()
branches = sorted(all_branch_top['branch'].unique())

for branch in branches:
    b_df = all_branch_top[all_branch_top['branch'] == branch].sort_values(by="name").reset_index(drop=True)
    print(f"\n📂 BRANCH: {branch} (Top {len(b_df)} Students)")
    print("-" * 65)
    print(b_df[['name', 'cgpa', 'attendance_pct', 'academic_standing', 'rank_in_branch']].to_string(index=False))