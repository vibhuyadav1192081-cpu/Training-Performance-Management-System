import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import automated backend pipeline
from main import run_entire_pipeline

# ==========================================================
# PAGE CONFIGURATION & INJECTIONS
# ==========================================================
st.set_page_config(
    page_title="Training Performance Dashboard",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background: #0E1117; }
section[data-testid="stSidebar"] { background: #161B22; border-right: 2px solid #2C313C; }
div[data-testid="metric-container"] {
    background: #1F2937; border-radius: 18px; padding: 18px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.35); border: 1px solid #374151; transition: 0.3s;
}
div[data-testid="metric-container"]:hover { transform: scale(1.03); border: 1px solid #3B82F6; }
.stButton>button { background: #2563EB; color: white; border-radius: 10px; font-weight: bold; }
.stDownloadButton>button { background: #16A34A; color: white; border-radius: 10px; }
[data-testid="stDataFrame"] { border-radius: 15px; }
h1 { color: white; font-weight: 700; }
h2 { color: #3B82F6; }
h3 { color: white; }
</style>
""", unsafe_allow_html=True)

# Define directories
DATA_FOLDER = "data"
MASTER_CSV_PATH = "output/master_df.csv"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ==========================================================
# WATCHDOG AUTOMATIC ENGINE TRIGGER SETUP
# ==========================================================
class QuizDataFolderWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".csv"):
            st.cache_data.clear() # Clear data memory cache context smoothly

if "watcher_active" not in st.session_state:
    try:
        handler = QuizDataFolderWatcher()
        observer = Observer()
        observer.schedule(handler, path=DATA_FOLDER, recursive=False)
        observer.start()
        st.session_state["watcher_active"] = True
    except Exception as e:
        pass

# ==========================================================
# AUTOMATED PIPELINE PIPING PROCESS EXECUTION
# ==========================================================
# Check if file exists, if not, trigger a run to build it.
if not os.path.exists(MASTER_CSV_PATH):
    run_entire_pipeline()

if os.path.exists(MASTER_CSV_PATH):
    master_df = pd.read_csv(MASTER_CSV_PATH)
else:
    st.error("⚠️ Database generation is pending. Add a CSV file to the data folder.")
    st.stop()

# ==========================================================
# HEADER SECTION
# ==========================================================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=90)
with col2:
    st.markdown("<h1 style='margin-bottom:0;color:#4F9CF9;'>🎓 Training Performance Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0;color:white;'>Lloyd Institute of Engineering & Technology</h4>", unsafe_allow_html=True)
    st.caption(f"📅 {datetime.now().strftime('%d %B %Y')}")

st.markdown("---")

# ==========================================================
# SIDEBAR CONTROLS & CONTINUOUS SYSTEM LOGIC
# ==========================================================
st.sidebar.title("📋 Navigation")
menu = st.sidebar.radio("", ["🏠 Dashboard", "🏆 Top Performers", "📊 Analytics", "📚 Quiz Analysis", "🔍 Student Search"])

st.sidebar.markdown("---")
st.sidebar.header("🔄 Manual Engine Overrides")

# REFRESH DASHBOARD & RE-RUN ENTIRE PIPELINE
if st.sidebar.button("🔄 Force Re-run & Refresh Dashboard"):
    st.cache_data.clear()
    with st.spinner("Executing entire analytical pipeline engine..."):
        master_df, log_msg = run_entire_pipeline()
    st.sidebar.success(log_msg)
    time.sleep(1)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("📤 Pipeline File Uploader")
uploaded_file = st.sidebar.file_uploader("Upload New Quiz CSV", type=["csv"])

if uploaded_file is not None:
    save_path = os.path.join(DATA_FOLDER, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.sidebar.success("✅ File Uploaded Successfully!")
    
    # Instant pipeline process iteration block trigger
    with st.spinner("Watchdog triggered file processing engine automatically..."):
        master_df, log_msg = run_entire_pipeline()
    st.sidebar.success("✅ Pipeline Executed and Data Updated!")
    time.sleep(1)
    st.rerun()

# Download Active Dataset
csv_data = master_df.to_csv(index=False)
st.sidebar.download_button(label="📥 Download System Report CSV", data=csv_data, file_name="Training_Performance_Report.csv", mime="text/csv", key="sidebar_download")

# ==========================================================
# MENU VISUALIZATION MODULAR LOGIC
# ==========================================================
if menu == "🏠 Dashboard":
    st.markdown("<h2 style='color:#4F9CF9'>📊 Dashboard Overview</h2>", unsafe_allow_html=True)

    total_students = len(master_df)
    average_percentage = round(master_df["Percentage"].mean(), 2)
    highest_percentage = round(master_df["Percentage"].max(), 2)
    lowest_percentage = round(master_df["Percentage"].min(), 2)
    average_attendance = round(master_df["Attendance_%"].mean(), 2)
    topper = master_df.sort_values("Percentage", ascending=False).iloc[0]["Name"] if not master_df.empty else "N/A"

    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🎓 Students", total_students)
    col2.metric("📈 Average %", f"{average_percentage}%")
    col3.metric("🏆 Highest %", f"{highest_percentage}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("📉 Lowest %", f"{lowest_percentage}%")
    col5.metric("✅ Attendance %", f"{average_attendance}%")
    col6.metric("🥇 Top Performer", topper)

    st.markdown("---")
    st.subheader("🥇 Top 3 Performers")
    top3 = master_df.sort_values("Rank").head(3)

    colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    titles = ["🥇 GOLD", "🥈 SILVER", "🥉 BRONZE"]
    cols = st.columns(3)

    for i, (index, row) in enumerate(top3.iterrows()):
        if i < len(cols):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#1E293B; border-left:8px solid {colors[i]}; border-radius:18px; padding:20px; box-shadow:0px 8px 20px rgba(0,0,0,.35);">
                <h3 style="color:{colors[i]}; margin-top:0;">{titles[i]}</h3>
                <h2 style="color:white; margin-top:5px;">{row['Name']}</h2>
                <hr style="border-color:#374151;">
                <h3 style="color:#4F9CF9; margin-bottom:5px;">{row['Percentage']}%</h3>
                <p style="color:white; margin:0;">Grade: <b>{row['Grade']}</b></p>
                <p style="color:white; margin:0;">Rank: #{int(row['Rank'])}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🏆 Top 10 Students Table")
    st.dataframe(master_df.sort_values("Rank").head(10)[["Rank", "Name", "Percentage", "Grade", "Performance_Score"]], use_container_width=True)

elif menu == "🏆 Top Performers":
    st.header("🏆 Top Performers Details")
    top_students = master_df.sort_values("Rank")
    st.dataframe(top_students[["Rank", "Name", "Percentage", "Performance_Score", "Grade", "Attendance_%"]], use_container_width=True)

    st.subheader("🏅 Top 10 Performance Chart")
    fig = px.bar(top_students.head(10), x="Name", y="Percentage", color="Grade", text="Percentage")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📊 Analytics":
    st.header("📊 Performance Analytics")
    st.subheader("🎓 Grade Distribution Analysis")
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig1 = px.pie(master_df, names="Grade", hole=0.45, title="Grade Share Percentage")
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        grade_count = master_df.groupby("Grade").size().reset_index(name="Students")
        fig_grade_bar = px.bar(grade_count, x="Grade", y="Students", color="Grade", text="Students", title="Students per Grade Count")
        st.plotly_chart(fig_grade_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Percentage Distribution")
    fig2 = px.histogram(master_df, x="Percentage", color="Grade", nbins=10)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("📉 Attendance vs Percentage")
    fig3 = px.scatter(master_df, x="Attendance_%", y="Percentage", color="Grade", hover_name="Name", size="Performance_Score")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("🚨 Students Needing Improvement (< 60%)")
    weak = master_df[master_df["Percentage"] < 60]
    if not weak.empty:
        st.dataframe(weak[["Name", "Percentage", "Grade", "Attendance_%"]], use_container_width=True)
    else:
        st.success("Great job! No students scored below 60%.")

elif menu == "📚 Quiz Analysis":
    st.header("📚 Quiz Analysis")
    quiz_columns = [col for col in master_df.columns if col.startswith("Day") and not col.endswith("_Max")]
    quiz_summary = []

    for score_col in quiz_columns:
        attempted = master_df[score_col].count()
        avg_marks = master_df[score_col].mean()
        highest = master_df[score_col].max()
        quiz_summary.append({"Quiz": score_col, "Attempted": attempted, "Average": round(avg_marks, 2), "Highest": highest})

    if quiz_summary:
        quiz_df = pd.DataFrame(quiz_summary)
        st.dataframe(quiz_df, use_container_width=True)
        fig = px.bar(quiz_df, x="Quiz", y="Average", color="Average", text="Average")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No Quiz columns starting with 'Day' were found in the dataset.")

elif menu == "🔍 Student Search":
    st.header("🔍 Search Student Profile")
    search_query = st.selectbox("Select Student Name:", [""] + list(master_df["Name"].unique()))
    
    if search_query:
        student_data = master_df[master_df["Name"] == search_query].iloc[0]
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Rank", f"#{int(student_data['Rank'])}")
        col_s2.metric("Percentage", f"{student_data['Percentage']}%")
        col_s3.metric("Attendance", f"{student_data['Attendance_%']}%")
        
        st.markdown("### Profile Details")
        st.json(student_data.to_dict())

# ==========================================================
# SYSTEM GLOBAL FOOTER
# ==========================================================
st.markdown("---")
st.markdown("""
<center>
<p style="color:#9CA3AF; font-size: 14px;">
<b>Training Performance Management System v2.0</b><br>
Developed by <b>Vivek Yadav with ❤️ & tea ☕</b><br>
Lloyd Institute of Engineering & Technology<br>
© 2026 All Rights Reserved
</p>
</center>
""", unsafe_allow_html=True)
# ==========================================================
# GLOBAL FOOTER (Always at the absolute bottom)
# ==========================================================
# ==========================================================
# SYSTEM GLOBAL FOOTER (FIXED SYNTAX ERROR HERE)
# ==========================================================
st.markdown("---")
st.markdown("""
<center>
<p style="color:#9CA3AF; font-size: 14px;">
<b>Training Performance Management System v2.0</b><br>
Developed by <b>Vivek Yadav with ❤️ & tea ☕</b><br>
Lloyd Institute of Engineering & Technology<br>
© 2026 All Rights Reserved
</p>
</center>
""", unsafe_allow_html=True)
