import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Training Performance Dashboard",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS Injector
st.markdown("""
<style>
/* Main Background */
.stApp {
    background: #0E1117;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161B22;
    border-right: 2px solid #2C313C;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background: #1F2937;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.35);
    border: 1px solid #374151;
    transition: 0.3s;
}

div[data-testid="metric-container"]:hover {
    transform: scale(1.03);
    border: 1px solid #3B82F6;
}

/* Buttons */
.stButton>button {
    background: #2563EB;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

/* Download */
.stDownloadButton>button {
    background: #16A34A;
    color: white;
    border-radius: 10px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 15px;
}

/* Headers */
h1 {
    color: white;
    font-weight: 700;
}

h2 {
    color: #3B82F6;
}

h3 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# LOAD DATA
# ==========================================================

DATA_PATH = "output/master_df.csv"

if not os.path.exists(DATA_PATH):
    st.error("master_df.csv not found.")
    st.stop()

master_df = pd.read_csv(DATA_PATH)

# ==========================================================
# PAGE HEADER
# ==========================================================

col1, col2 = st.columns([1, 5])

with col1:
    st.image("assets/logo.png", width=90)

with col2:
    st.markdown("""
    <h1 style='margin-bottom:0;color:#4F9CF9;'>
    🎓 Training Performance Management System
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h4 style='margin-top:0;color:white;'>
    Lloyd Institute of Engineering & Technology
    </h4>
    """, unsafe_allow_html=True)

    st.caption(f"📅 {datetime.now().strftime('%d %B %Y')}")

st.markdown("---")

# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

st.sidebar.title("📋 Navigation")

menu = st.sidebar.radio(
    "",
    [
        "🏠 Dashboard",
        "🏆 Top Performers",
        "📊 Analytics",
        "📚 Quiz Analysis",
        "🔍 Student Search"
    ]
)

# Common Download Button in Sidebar (With Unique Key)
st.sidebar.markdown("---")
csv = master_df.to_csv(index=False)
st.sidebar.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="Training_Report.csv",
    mime="text/csv",
    key="sidebar_download_csv"
)

# ==========================================================
# 1. HOME DASHBOARD
# ==========================================================

if menu == "🏠 Dashboard":

    st.markdown("""
    <h2 style='color:#4F9CF9'>
    📊 Dashboard Overview
    </h2>
    """, unsafe_allow_html=True)

    total_students = len(master_df)
    average_percentage = round(master_df["Percentage"].mean(), 2)
    highest_percentage = round(master_df["Percentage"].max(), 2)
    lowest_percentage = round(master_df["Percentage"].min(), 2)
    average_attendance = round(master_df["Attendance_%"].mean(), 2)
    
    # Safely get topper name
    if not master_df.empty:
        topper = master_df.sort_values("Percentage", ascending=False).iloc[0]["Name"]
    else:
        topper = "N/A"

    # Metrics Layout
    col1, col2, col3 = st.columns(3)
    col1.metric("👨‍🎓 Students", total_students)
    col2.metric("📈 Average %", f"{average_percentage}%")
    col3.metric("🏆 Highest %", f"{highest_percentage}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("📉 Lowest %", f"{lowest_percentage}%")
    col5.metric("✅ Attendance %", f"{average_attendance}%")
    col6.metric("🥇 Top Performer", topper)

    st.markdown("---")

    # 🥇 Top 3 Performers (Now properly inside the Dashboard block)
    st.subheader("🥇 Top 3 Performers")
    top3 = master_df.sort_values("Rank").head(3)

    colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    titles = ["🥇 GOLD", "🥈 SILVER", "🥉 BRONZE"]
    cols = st.columns(3)

    for i, (index, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div style="
            background:#1E293B;
            border-left:8px solid {colors[i]};
            border-radius:18px;
            padding:20px;
            box-shadow:0px 8px 20px rgba(0,0,0,.35);
            ">
            <h3 style="color:{colors[i]}; margin-top:0;">{titles[i]}</h3>
            <h2 style="color:white; margin-top:5px;">{row['Name']}</h2>
            <hr style="border-color:#374151;">
            <h3 style="color:#4F9CF9; margin-bottom:5px;">{row['Percentage']}%</h3>
            <p style="color:white; margin:0;">Grade: <b>{row['Grade']}</b></p>
            <p style="color:white; margin:0;">Rank: #{int(row['Rank'])}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Top 10 Dataframe Table
    st.subheader("🏆 Top 10 Students")
    top10 = master_df.sort_values("Rank").head(10)
    st.dataframe(
        top10[["Rank", "Name", "Percentage", "Grade", "Performance_Score"]],
        use_container_width=True
    )

# ==========================================================
# 2. TOP PERFORMERS
# ==========================================================

elif menu == "🏆 Top Performers":

    st.header("🏆 Top Performers Details")

    top_students = master_df.sort_values("Rank")

    st.dataframe(
        top_students[["Rank", "Name", "Percentage", "Performance_Score", "Grade", "Attendance_%"]],
        use_container_width=True
    )

    st.subheader("🏅 Top 10 Performance Chart")
    fig = px.bar(
        top_students.head(10),
        x="Name",
        y="Percentage",
        color="Grade",
        text="Percentage"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# 3. ANALYTICS
# ==========================================================

elif menu == "📊 Analytics":

    st.header("📊 Performance Analytics")

    # -------------------------
    # Grade Distribution
    # -------------------------
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

    # -------------------------
    # Percentage Distribution
    # -------------------------
    st.subheader("📈 Percentage Distribution")
    fig2 = px.histogram(master_df, x="Percentage", color="Grade", nbins=10)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # -------------------------
    # Attendance vs Percentage & Performance
    # -------------------------
    st.subheader("📉 Attendance vs Percentage")
    fig3 = px.scatter(
        master_df,
        x="Attendance_%",
        y="Percentage",
        color="Grade",
        hover_name="Name",
        size="Performance_Score"
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("📊 Attendance vs Performance Score")
    fig_scatter_2 = px.scatter(
        master_df,
        x="Attendance_%",
        y="Performance_Score",
        hover_name="Name",
        color="Grade",
        size="Percentage"
    )
    st.plotly_chart(fig_scatter_2, use_container_width=True)

    st.markdown("---")

    # -------------------------
    # Overall Trend & Weak Students
    # -------------------------
    st.subheader("📈 Overall Performance Trend")
    trend = master_df.sort_values("Percentage")
    fig_trend = px.line(trend, x="Name", y="Percentage", markers=True)
    fig_trend.update_layout(xaxis_title="Students", yaxis_title="Percentage")
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    st.subheader("🚨 Students Needing Improvement (< 60%)")
    weak = master_df[master_df["Percentage"] < 60]
    if not weak.empty:
        st.dataframe(
            weak[["Name", "Percentage", "Grade", "Attendance_%"]],
            use_container_width=True
        )
    else:
        st.success("Great job! No students scored below 60%.")

# ==========================================================
# 4. QUIZ ANALYSIS
# ==========================================================

elif menu == "📚 Quiz Analysis":

    st.header("📚 Quiz Analysis")

    quiz_columns = [col for col in master_df.columns if col.startswith("Day") and not col.endswith("_Max")]
    max_columns = [col for col in master_df.columns if col.startswith("Day") and col.endswith("_Max")]

    quiz_summary = []

    for score_col in quiz_columns:
        attempted = master_df[score_col].count()
        avg_marks = master_df[score_col].mean()
        highest = master_df[score_col].max()

        quiz_summary.append({
            "Quiz": score_col,
            "Attempted": attempted,
            "Average": round(avg_marks, 2),
            "Highest": highest
        })

    if quiz_summary:
        quiz_df = pd.DataFrame(quiz_summary)

        st.dataframe(quiz_df, use_container_width=True)

        fig = px.bar(
            quiz_df,
            x="Quiz",
            y="Average",
            color="Average",
            text="Average"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        best_quiz = quiz_df.loc[quiz_df["Average"].idxmax()]
        worst_quiz = quiz_df.loc[quiz_df["Average"].idxmin()]

        col1, col2 = st.columns(2)

        with col1:
            st.success("🏆 Best Quiz Performance")
            st.metric(best_quiz["Quiz"], f"{best_quiz['Average']} Avg")

        with col2:
            st.error("❄️ Toughest Quiz (Lowest Avg)")
            st.metric(worst_quiz["Quiz"], f"{worst_quiz['Average']} Avg")
    else:
        st.warning("No Quiz columns starting with 'Day' were found in the dataset.")

# ==========================================================
# 5. STUDENT SEARCH
# ==========================================================

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
# GLOBAL FOOTER (Always at the absolute bottom)
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