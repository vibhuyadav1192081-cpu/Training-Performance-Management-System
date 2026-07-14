import os
import glob
import uuid
import warnings
import numpy as np
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Prevent terminal flooding
warnings.filterwarnings("ignore")

def generate_pdf_grade_card(student_row, output_path):
    """
    Helper function to dynamically generate a basic clean PDF grade card.
    Uses standard ReportLab structure to avoid missing file errors.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom Title Style
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            spaceAfter=20,
            textColor='#1E3A8A'
        )
        
        story.append(Paragraph(f"<b>STUDENT PERFORMANCE REPORT CARD</b>", title_style))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Student Name:</b> {student_row['Name']}", styles['Normal']))
        story.append(Paragraph(f"<b>Registered Email:</b> {student_row['Email']}", styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>Overall Rank:</b> {student_row['Rank']}", styles['Normal']))
        story.append(Paragraph(f"<b>Final Calculated Grade:</b> {student_row['Grade']}", styles['Normal']))
        story.append(Paragraph(f"<b>Attendance Percentage:</b> {student_row['Attendance_%']}%", styles['Normal']))
        story.append(Paragraph(f"<b>Overall Course Percentage:</b> {student_row['Overall_Percentage']}%", styles['Normal']))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Performance Review Insight:</b> <br/><i>{student_row['Insight']}</i>", styles['Normal']))
        
        doc.build(story)
        return True
    except Exception as pdf_err:
        print(f"Error generating PDF for {student_row['Name']}: {str(pdf_err)}")
        return False

def run_entire_pipeline():
    """
    Automatically aggregates all CSV files from the 'data/' folder, 
    calculates metrics, triggers performance engine, updates the dashboard database,
    generates PDF reports, and dispatches automated emails via SMTP.
    """
    DATA_FOLDER = "data"
    OUTPUT_FOLDER = "output"
    
    # Ensure standard structural directories exist
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_FOLDER, "grade_cards"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_FOLDER, "reports"), exist_ok=True)

    csv_files = sorted(glob.glob(os.path.join(DATA_FOLDER, "*.csv")))
    if not csv_files:
        return None, "Data folder completely empty. Please drop or upload a CSV file."

    try:
        # Load & Clean Dataframes
        quiz_data = [pd.read_csv(file) for file in csv_files]
        clean_quiz = []
        for df in quiz_data:
            df.columns = df.columns.str.strip()
            if "Email" in df.columns:
                df["Email"] = df["Email"].astype(str).str.lower().str.strip()
            if "Name" in df.columns:
                df["Name"] = df["Name"].astype(str).str.strip()
            clean_quiz.append(df)

        # Dynamic Extraction & Score Merges
        master_df = None
        for day_no, df in enumerate(clean_quiz, start=1):
            temp = df.copy()
            score_column = None
            for col in ["Total score", "Score", "Marks", "Result"]:
                if col in temp.columns:
                    score_column = col
                    break

            if score_column is None:
                continue

            score = temp[score_column].astype(str).str.split("/", expand=True)
            temp[f"Day{day_no}"] = score[0].str.strip().astype(float)
            temp[f"Day{day_no}_Max"] = score[1].str.strip().astype(float)

            keep_columns = ["Name", "Email", f"Day{day_no}", f"Day{day_no}_Max"]
            temp = temp[[c for c in keep_columns if c in temp.columns]]

            if master_df is None:
                master_df = temp
            else:
                if "Name" in temp.columns:
                    temp = temp.drop(columns=["Name"])
                master_df = master_df.merge(temp, on="Email", how="outer")

        # Restore Student Names via Lookup Mapping
        name_lookup = {}
        for df in clean_quiz:
            if "Email" in df.columns and "Name" in df.columns:
                for _, row in df.iterrows():
                    email = str(row["Email"]).strip().lower()
                    if email not in name_lookup and str(row["Name"]) != "nan":
                        name_lookup[email] = str(row["Name"]).strip()
        
        master_df["Name"] = master_df["Email"].map(name_lookup)
        
        # Performance Engine Core Parsing
        score_cols = sorted([c for c in master_df.columns if c.startswith("Day") and not c.endswith("_Max")])
        max_cols = sorted([c for c in master_df.columns if c.endswith("_Max")])

        master_df["Attempted_Quiz"] = (master_df[score_cols] > 0).sum(axis=1)
        master_df["Attendance"] = master_df["Attempted_Quiz"].fillna(0).astype(float)
        
        TOTAL_QUIZZES = len(score_cols) if len(score_cols) > 0 else 1
        master_df["Attendance_%"] = ((master_df["Attempted_Quiz"] / TOTAL_QUIZZES) * 100).round(2)
        master_df["Total_Obtained"] = master_df[score_cols].sum(axis=1)

        master_df["Total_Maximum"] = 0
        for score_col, max_col in zip(score_cols, max_cols):
            master_df["Total_Maximum"] += np.where(master_df[score_col] > 0, master_df[max_col], 0)

        master_df["Percentage"] = np.where(
            master_df["Total_Maximum"] == 0, 0,
            ((master_df["Total_Obtained"] / master_df["Total_Maximum"]) * 100)
        ).round(2)

        COURSE_TOTAL_MAX = master_df[max_cols].max().sum()
        if COURSE_TOTAL_MAX == 0: COURSE_TOTAL_MAX = 1
        
        master_df["Quiz_Percentage"] = master_df["Percentage"]
        master_df["Overall_Percentage"] = ((master_df["Total_Obtained"] / COURSE_TOTAL_MAX) * 100).round(2)
        master_df["Attendance_Ratio"] = (master_df["Attempted_Quiz"] / TOTAL_QUIZZES)
        master_df["Performance_Score"] = (master_df["Quiz_Percentage"] * master_df["Attendance_Ratio"]).round(2)

        # Rank, Grade, Percentile Logic
        master_df["Rank"] = master_df["Overall_Percentage"].rank(ascending=False, method="dense").astype(int)
        master_df["Percentile"] = (master_df["Overall_Percentage"].rank(pct=True) * 100).round(2)

        def assign_grade(overall_percentage):
            if overall_percentage >= 90: return "A+"
            elif overall_percentage >= 80: return "A"
            elif overall_percentage >= 70: return "B+"
            elif overall_percentage >= 60: return "B"
            elif overall_percentage >= 50: return "C"
            elif overall_percentage >= 40: return "D"
            else: return "F"

        master_df["Grade"] = master_df["Overall_Percentage"].apply(assign_grade)

        # AI Insights Auto Engine
        def generate_ai_insight(row):
            qp, op, att, attempt = row["Quiz_Percentage"], row["Overall_Percentage"], row["Attendance_%"], row["Attempted_Quiz"]
            insights = []
            if att >= 85: insights.append("Excellent attendance throughout the course.")
            elif att >= 60: insights.append("Good attendance. Try attending every quiz.")
            elif att >= 30: insights.append("Low participation. Attend more quizzes for better performance.")
            else: insights.append("Very low participation. Course performance is affected.")

            if qp >= 90: insights.append("Outstanding performance in attempted quizzes.")
            elif qp >= 75: insights.append("Strong academic performance.")
            elif qp >= 60: insights.append("Average performance with scope for improvement.")
            elif qp >= 40: insights.append("Below average performance.")
            else: insights.append("Needs significant academic improvement.")

            if op >= 85: insights.append("Consistently performing well across the course.")
            elif op >= 60: insights.append("Maintaining satisfactory overall progress.")
            elif op >= 40: insights.append("Overall progress is moderate.")
            else: insights.append("Overall course performance is currently low.")

            if attempt == 1: insights.append("Only one quiz attempted. More participation is recommended.")
            elif attempt >= 6: insights.append("Highly consistent participation across quizzes.")
            return " ".join(insights)

        master_df["Insight"] = master_df.apply(generate_ai_insight, axis=1)

        # Final Re-ordering & Export to CSV for Dashboard
        col_order = ["Name", "Email"] + [c for c in master_df.columns if c not in ["Name", "Email"]]
        master_df = master_df[col_order].sort_values(by="Rank")
        master_df.to_csv(os.path.join(OUTPUT_FOLDER, "master_df.csv"), index=False)
        
        # ==========================================================
        # SMTP AUTOMATED SYSTEM WITH RUNTIME PDF GENERATION
        # ==========================================================
        SENDER_EMAIL = "vibhuyadav1192081@gmail.com"
        SENDER_PASSWORD = "hpaj nzhp qwvw ksag"  # Google App Password config

        # Connecting SMTP server outside the loop for optimization
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            for index, row in master_df.iterrows():
                student_email = row["Email"]
                student_name = row["Name"] if pd.notna(row["Name"]) else "Student"
                student_grade = row["Grade"]
                
                if pd.isna(student_email) or "@" not in str(student_email):
                    continue
                    
                pdf_filename = f"output/grade_cards/{student_name.replace(' ', '_')}_grade_card.pdf"
                
                # Dynamic Runtime PDF creation before mailing
                pdf_created = generate_pdf_grade_card(row, pdf_filename)
                
                if pdf_created and os.path.exists(pdf_filename):
                    msg = MIMEMultipart()
                    msg['From'] = SENDER_EMAIL
                    msg['To'] = student_email
                    msg['Subject'] = f"🏆 Your Performance Grade Card - Updated"
                    
                    body = f"Hello {student_name},\n\nYour latest quiz performance analytics have been compiled. Your current standing Grade is: {student_grade}.\n\nPlease find your automated verified performance summary card attached below.\n\nBest Regards,\nAcademic Management System"
                    msg.attach(MIMEText(body, 'plain'))
                    
                    with open(pdf_filename, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(pdf_filename)}")
                        msg.attach(part)
                    
                    server.sendmail(SENDER_EMAIL, student_email, msg.as_string())
            
            server.quit()
        except Exception as smtp_global_err:
            print(f"SMTP Main Engine Connection Error: {str(smtp_global_err)}")

        return master_df, "✅ Entire Analytics Pipeline & Bulk Emails Processed Successfully!"
    except Exception as e:
        return None, f"❌ Pipeline Broken: {str(e)}"
