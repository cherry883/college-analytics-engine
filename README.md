# 🌿 CampusPulse 360: Institutional Intelligence & Analytics Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-6C826D.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-2F3E32.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-8B735B.svg)](https://streamlit.io/)
[![SQLite3](https://img.shields.io/badge/SQLite-3-E2DCD2.svg)](https://www.sqlite.org/)

An end-to-end data engineering and administrative intelligence platform designed to eliminate institutional data silos across Exam Cells, Attendance Portals, and Training & Placement (T&P) departments. 

CampusPulse 360 integrates an automated **ETL Data Cleaning Pipeline**, a persistent **SQLite Database with Windowed Analytical Views**, a high-performance **FastAPI REST Service**, and an aesthetic **Sage Green & Earthy Brown Pastel Streamlit Dashboard**.

---

## 📌 Key Features

* **Automated Data Quality & Normalization Pipeline:**
  * Standardizes department aliases (e.g., `Comp Sci`, `Computer Science`, `CS` $\rightarrow$ `CSE`)[cite: 1].
  * Sanitizes names (removes honorifics like `Mr.`, `Ms.`, `Dr.`, and trims trailing whitespace)[cite: 1].
  * Fixes anomalies by clamping CGPA/SGPA to $[0.0, 10.0]$ and attendance/backlogs to valid positive ranges[cite: 1].
  * Logs unrecoverable rows to an anomaly audit trail without crashing the pipeline.
* **Unified Data Model (`student_360`):**
  * Consolidates demographics, SGPA, CGPA, attendance metrics, and placement offer data into a single source of truth.
  * Computes automated **Academic Standing** flags (`GOOD_STANDING`, `ATTENDANCE_SHORTAGE`, `ACADEMIC_DEFICIT`, `CRITICAL_RISK`).
  * Dynamically evaluates **Placement Eligibility** ($CGPA \ge 6.5$, $Attendance \ge 75\%$, $Backlogs = 0$, $Registered = True$).
* **Optimized SQL Analytical Views:**
  * **Overall College Toppers:** Top 10 institutional academic achievers, sorted alphabetically by student name (A–Z).
  * **Branch-Wise Top Performers:** Top 10 achievers per department, rendered into separate departmental tables and sorted alphabetically.
  * **Early Warning Alerts:** Students requiring intervention due to low attendance ($<75\%$) or active backlogs.
  * **Department KPIs:** Aggregated averages for CGPA, attendance rate, and placement conversion.
* **Decoupled REST API:**
  * Built with FastAPI to support dynamic parameter filtering, JSON data delivery, and multi-file multipart CSV uploads.
* **Sage & Earthy Pastel Web UI:**
  * Interactive Streamlit dashboard styled with rounded metric cards, interactive Plotly scatter & bar charts, tabbed branch navigation, and one-click CSV export options.

---

## 🛠️ Architecture & Tech Stack
[ Raw Department CSVs ] ──► [ Phase 2: ETL Pipeline (Pandas/NumPy) ]
│
▼
[ Phase 3: SQLite Database ]
(student_360 table + Analytical Views)
│
▼
[ Phase 4: FastAPI REST API ]
(Port 8000: /api/students, /api/etl/upload)
│
▼
[ Phase 5: Streamlit Web UI ]
(Port 8501: Pastel Dashboard & Department Tabs)