import os
import pandas as pd
from etl_pipeline import CollegeDataETL

student_file = "student_master.csv" if os.path.exists("student_master.csv") else "student_master_2.csv"
academics_file = "academics.csv" if os.path.exists("academics.csv") else "academics_2.csv"
attendance_file = "attendance.csv" if os.path.exists("attendance.csv") else "attendance_2.csv"
placement_file = "placement.csv" if os.path.exists("placement.csv") else "placement_2.csv"

print(f"[INFO] Ingesting files: {student_file}, {academics_file}, {attendance_file}, {placement_file}")

df_students = pd.read_csv(student_file)
df_academics = pd.read_csv(academics_file)
df_attendance = pd.read_csv(attendance_file)
df_placement = pd.read_csv(placement_file)

etl = CollegeDataETL()
clean_df, audit_df = etl.integrate_all(
    df_students, 
    df_academics, 
    df_attendance, 
    df_placement
)

clean_df.to_csv("cleaned_student_360.csv", index=False)
audit_df.to_csv("data_audit_logs.csv", index=False)

print("\n" + "=" * 70)
print(f"ETL COMPLETED: Processed {len(clean_df)} Students | Logged {len(audit_df)} Anomalies")
print("=" * 70)

# Top 10 per branch sorted alphabetically by student name
top_10 = (
    clean_df.sort_values(by=["branch", "cgpa"], ascending=[True, False])
    .groupby("branch", as_index=False)
    .head(10)
    .sort_values(by="name", ascending=True)
)

print("\n--- TOP PERFORMERS PER BRANCH (ALPHABETICAL BY STUDENT NAME) ---")
print(top_10[['name', 'branch', 'cgpa', 'attendance_pct', 'academic_standing']].to_string(index=False))

print("\n--- ANOMALY AUDIT LOGS ---")
print(audit_df.to_string(index=False))