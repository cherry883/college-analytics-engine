import pandas as pd
import streamlit as st
import requests
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="College Intelligence & Analytics",
    page_icon="🌿",
    layout="wide"
)

API_BASE = "http://127.0.0.1:8000"

# --- PASTEL SAGE GREEN & WARM EARTHY BROWN THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main background */
    .stApp {
        background-color: #F8F9F5;
        color: #2F3E32;
    }

    /* Sidebar Aesthetic */
    section[data-testid="stSidebar"] {
        background-color: #EFECE6;
        border-right: 1px solid #E2DCD2;
    }

    /* Custom Metric Cards */
    .aesthetic-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 15px rgba(62, 59, 50, 0.04);
        border: 1px solid #EBE7DF;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 15px;
    }
    .aesthetic-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(62, 59, 50, 0.07);
    }
    .aesthetic-card-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #7A7265;
        margin-bottom: 6px;
    }
    .aesthetic-card-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2F3E32;
    }
    .aesthetic-card-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 20px;
        margin-top: 6px;
    }
    .badge-green { background-color: #E2ECE3; color: #2E5A36; }
    .badge-brown { background-color: #F2ECE4; color: #735338; }
    .badge-warn  { background-color: #FAEEE5; color: #9A5332; }

    /* Headers */
    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #2F3E32;
        margin-top: 10px;
        margin-bottom: 4px;
    }
    .section-subtitle {
        font-size: 0.9rem;
        color: #7A7265;
        margin-bottom: 20px;
    }

    /* Styled Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ECE8E1;
        border-radius: 12px;
        padding: 8px 20px;
        color: #5A5348;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6C826D !important;
        color: #FFFFFF !important;
        font-weight: 700;
    }

    /* Styled Buttons */
    .stButton > button, div.stDownloadButton > button {
        background-color: #8B735B !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 8px 22px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 10px rgba(139, 115, 91, 0.15);
    }
    .stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #735C45 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(139, 115, 91, 0.25);
    }

    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #EBE7DF;
    }
</style>
""", unsafe_allow_html=True)

def fetch_api(endpoint: str, params: dict = None):
    try:
        res = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=5)
        if res.status_code == 200:
            return pd.DataFrame(res.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# Sidebar Brand Header
st.sidebar.markdown("""
<div style="padding: 10px 0 20px 0;">
    <h2 style="color: #2F3E32; font-weight: 700; margin: 0; font-size: 1.35rem;">🌿 EduPortal</h2>
    <p style="color: #7A7265; font-size: 0.85rem; margin-top: 2px;">Institutional Intelligence Suite</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", [
    "🌿 Executive Overview", 
    "✨ Overall College Toppers",
    "📁 Branch-Wise Toppers", 
    "🔔 Early Warning & Risks", 
    "📤 Ingest Department Files"
])

# -------------------------------------------------------------------
# 1. EXECUTIVE DASHBOARD
# -------------------------------------------------------------------
if menu == "🌿 Executive Overview":
    st.markdown('<div class="section-title">Institutional Health & Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Real-time cross-departmental academic indicators and risk diagnostics</div>', unsafe_allow_html=True)

    students_df = fetch_api("/api/students")
    kpi_df = fetch_api("/api/analytics/kpis")

    if not students_df.empty:
        total_students = len(students_df)
        avg_cgpa = students_df['cgpa'].mean()
        avg_attendance = students_df['attendance_pct'].mean()
        at_risk_count = students_df[students_df['academic_standing'] != 'GOOD_STANDING'].shape[0]

        # Aesthetic Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="aesthetic-card">
                <div class="aesthetic-card-title">Enrolled Students</div>
                <div class="aesthetic-card-val">{total_students}</div>
                <span class="aesthetic-card-badge badge-green">Active Master Records</span>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="aesthetic-card">
                <div class="aesthetic-card-title">Institutional CGPA</div>
                <div class="aesthetic-card-val">{avg_cgpa:.2f} <span style="font-size: 1rem; color: #7A7265;">/ 10</span></div>
                <span class="aesthetic-card-badge badge-brown">Campus Average</span>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="aesthetic-card">
                <div class="aesthetic-card-title">Mean Attendance</div>
                <div class="aesthetic-card-val">{avg_attendance:.1f}%</div>
                <span class="aesthetic-card-badge badge-green">Lecture Consistency</span>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="aesthetic-card">
                <div class="aesthetic-card-title">Intervention Required</div>
                <div class="aesthetic-card-val" style="color: #9A5332;">{at_risk_count}</div>
                <span class="aesthetic-card-badge badge-warn">Attendance / Backlogs</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Visual Charts with High-Contrast Dark Earthy Labels
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("##### 🍃 Attendance vs CGPA Distribution")
            fig_scatter = px.scatter(
                students_df,
                x="attendance_pct",
                y="cgpa",
                color="academic_standing",
                hover_data=["student_id", "name", "branch"],
                labels={
                    "attendance_pct": "Attendance (%)",
                    "cgpa": "CGPA (0–10)",
                    "academic_standing": "Standing"
                },
                color_discrete_map={
                    "GOOD_STANDING": "#4D6B50",
                    "ATTENDANCE_SHORTAGE": "#D68C45",
                    "ACADEMIC_DEFICIT": "#B85D38",
                    "CRITICAL_RISK": "#8B261D"
                }
            )
            fig_scatter.update_traces(marker=dict(size=10, opacity=0.9))
            fig_scatter.update_layout(
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAF8F5',
                font=dict(family="Plus Jakarta Sans", color="#2F3E32", size=12),
                margin=dict(l=40, r=20, t=50, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(color="#2F3E32", size=11),
                    title=dict(font=dict(color="#2F3E32", size=12, weight="bold"))
                ),
                xaxis=dict(
                    title=dict(text="Attendance Percentage (%)", font=dict(color="#2F3E32", size=13, weight="bold")),
                    tickfont=dict(color="#2F3E32", size=11, weight="bold"),
                    gridcolor="#E8E3DA",
                    showline=True,
                    linecolor="#C2B8A8",
                    zeroline=False
                ),
                yaxis=dict(
                    title=dict(text="CGPA", font=dict(color="#2F3E32", size=13, weight="bold")),
                    tickfont=dict(color="#2F3E32", size=11, weight="bold"),
                    gridcolor="#E8E3DA",
                    showline=True,
                    linecolor="#C2B8A8",
                    zeroline=False
                )
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_chart2:
            st.markdown("##### 🪵 Department-Wise Mean CGPA")
            if not kpi_df.empty:
                fig_bar = px.bar(
                    kpi_df,
                    x="branch",
                    y="avg_cgpa",
                    text="avg_cgpa",
                    labels={"branch": "Department / Branch", "avg_cgpa": "Mean CGPA"},
                    color_discrete_sequence=["#8B735B"]
                )
                fig_bar.update_traces(
                    textposition='outside',
                    textfont=dict(color="#2F3E32", size=12, family="Plus Jakarta Sans", weight="bold"),
                    cliponaxis=False
                )
                fig_bar.update_layout(
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FAF8F5',
                    font=dict(family="Plus Jakarta Sans", color="#2F3E32", size=12),
                    margin=dict(l=40, r=20, t=30, b=40),
                    xaxis=dict(
                        title=dict(text="Department / Branch", font=dict(color="#2F3E32", size=13, weight="bold")),
                        tickfont=dict(color="#2F3E32", size=12, weight="bold"),
                        showline=True,
                        linecolor="#C2B8A8"
                    ),
                    yaxis=dict(
                        title=dict(text="Average CGPA", font=dict(color="#2F3E32", size=13, weight="bold")),
                        tickfont=dict(color="#2F3E32", size=11, weight="bold"),
                        gridcolor="#E8E3DA",
                        showline=True,
                        linecolor="#C2B8A8",
                        range=[0, 10.5]
                    )
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("##### 📋 Department KPI Breakdown")
        st.dataframe(kpi_df, use_container_width=True)
    else:
        st.warning("Backend API is offline. Start FastAPI (`uvicorn api_service:app --reload`).")

# -------------------------------------------------------------------
# 2. OVERALL COLLEGE TOPPERS
# -------------------------------------------------------------------
elif menu == "✨ Overall College Toppers":
    st.markdown('<div class="section-title">✨ Institutional Top Performers</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Top 10 academic achievers across the entire college, arranged alphabetically by student name.</div>', unsafe_allow_html=True)

    overall_df = fetch_api("/api/students/top-performers/overall")

    if not overall_df.empty:
        st.dataframe(
            overall_df[['name', 'branch', 'cgpa', 'attendance_pct', 'academic_standing', 'overall_rank']],
            use_container_width=True
        )
        csv = overall_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Overall Toppers (CSV)",
            data=csv,
            file_name="overall_college_toppers.csv",
            mime="text/csv"
        )
    else:
        st.warning("No records found. Please ensure database is initialized.")

# -------------------------------------------------------------------
# 3. BRANCH-WISE TOPPERS
# -------------------------------------------------------------------
elif menu == "📁 Branch-Wise Toppers":
    st.markdown('<div class="section-title">📁 Department Top Performers</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Top 10 students for each individual department, sorted alphabetically by name.</div>', unsafe_allow_html=True)

    top_df = fetch_api("/api/students/top-performers")

    if not top_df.empty:
        branches = sorted(top_df['branch'].unique())
        tabs = st.tabs([f"🌿 {b}" for b in branches])

        for tab, branch in zip(tabs, branches):
            with tab:
                branch_students = (
                    top_df[top_df['branch'] == branch]
                    .sort_values(by="name", ascending=True)
                    .reset_index(drop=True)
                )
                
                st.markdown(f"#### Department of {branch}")
                st.caption(f"Displaying top {len(branch_students)} students sorted A–Z")
                st.dataframe(
                    branch_students[['name', 'cgpa', 'attendance_pct', 'academic_standing', 'rank_in_branch']],
                    use_container_width=True
                )
                
                csv = branch_students.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download {branch} List (CSV)",
                    data=csv,
                    file_name=f"{branch}_top_performers.csv",
                    mime="text/csv",
                    key=f"btn_{branch}"
                )
    else:
        st.warning("No records found.")

# -------------------------------------------------------------------
# 4. AT-RISK EARLY WARNING
# -------------------------------------------------------------------
elif menu == "🔔 Early Warning & Risks":
    st.markdown('<div class="section-title">🔔 Early Warning & Academic Mentorship</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Students requiring intervention due to low attendance (&lt;75%) or academic deficits.</div>', unsafe_allow_html=True)

    risk_df = fetch_api("/api/students/at-risk")

    if not risk_df.empty:
        st.dataframe(
            risk_df[['name', 'student_id', 'branch', 'cgpa', 'attendance_pct', 'backlogs', 'academic_standing']],
            use_container_width=True
        )
    else:
        st.info("No students currently flagged for academic risk.")

# -------------------------------------------------------------------
# 5. INGEST DEPARTMENT FILES
# -------------------------------------------------------------------
elif menu == "📤 Ingest Department Files":
    st.markdown('<div class="section-title">📤 Department Data Intake</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Upload updated departmental CSV records to trigger automated normalization and database upsert.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        f_master = st.file_uploader("1. Student Master CSV", type=["csv"])
        f_acad = st.file_uploader("2. Academics CSV", type=["csv"])
    with col2:
        f_att = st.file_uploader("3. Attendance CSV", type=["csv"])
        f_place = st.file_uploader("4. Placement CSV", type=["csv"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Process & Ingest Datasets"):
        if f_master and f_acad and f_att and f_place:
            files = {
                "file_students": (f_master.name, f_master.getvalue(), "text/csv"),
                "file_academics": (f_acad.name, f_acad.getvalue(), "text/csv"),
                "file_attendance": (f_att.name, f_att.getvalue(), "text/csv"),
                "file_placement": (f_place.name, f_place.getvalue(), "text/csv")
            }
            with st.spinner("Executing normalization & validation rules..."):
                res = requests.post(f"{API_BASE}/api/etl/upload", files=files)
                if res.status_code == 200:
                    st.success(f"✨ Successfully integrated {res.json()['processed_students_count']} students!")
                else:
                    st.error("ETL processing encountered an issue.")
        else:
            st.warning("Please upload all four departmental files.")