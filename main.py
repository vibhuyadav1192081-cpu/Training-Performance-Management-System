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
    Highly customized dynamic PDF Report Card generator featuring an official college 
    header architecture, evaluation summary grids, and structural signature elements.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        # Page Setup with exact corporate margins
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=letter,
            rightMargin=40, leftMargin=40,
            topMargin=40, bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Custom Typography & Color Schemes
        PRIMARY_COLOR = colors.HexColor("#1E3A8A")  # Corporate Dark Navy Blue
        SECONDARY_COLOR = colors.HexColor("#7F1D1D")  # Academic Crimson Maroon
        TEXT_DARK = colors.HexColor("#1F2937")
        
        # Custom Paragraph Styling Setup
        style_inst_name = ParagraphStyle('InstName', parent=styles['Heading1'], fontSize=20, leading=24, textColor=PRIMARY_COLOR, alignment=1, spaceAfter=2)
        style_inst_sub = ParagraphStyle('InstSub', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.HexColor("#4B5563"), alignment=1, spaceAfter=15)
        style_report_title = ParagraphStyle('RepTitle', parent=styles['Heading2'], fontSize=14, leading=18, textColor=SECONDARY_COLOR, alignment=1, spaceAfter=20)
        style_normal_cell = ParagraphStyle('NormCell', parent=styles['Normal'], fontSize=10, leading=13, textColor=TEXT_DARK)
        style_bold_cell = ParagraphStyle('BoldCell', parent=styles['Normal'], fontSize=10, leading=13, textColor=TEXT_DARK, fontName="Helvetica-Bold")
        
        # 1. OFFICIAL ACADEMIC HEADER ARCHITECTURE (College Name & Affiliation)
        story.append(Paragraph("<b>LLOYD INSTITUTE OF ENGINEERING & TECHNOLOGY</b>", style_inst_name))
        story.append(Paragraph("Affiliated to APJ Abdul Kalam Technical University (AKTU) | Greater Noida, UP", style_inst_sub))
        
        # Design Separator Accent Line
        header_line = Table([[""]], colWidths=[532], rowHeights=[3])
        header_line.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), PRIMARY_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_line)
        story.append(Spacer(1, 15))
        
        # Document Sub-Heading
        story.append(Paragraph("<b>AUTOMATED STUDENT PERFORMANCE REPORT CARD</b>", style_report_title))
        
        # 2. STUDENT INFORMATION PROFILE BLOCK (Clean Grid System)
        info_data = [
            [Paragraph("<b>Student Name:</b>", style_bold_cell), Paragraph(str(student_row['Name']), style_normal_cell),
             Paragraph("<b>Academic Session:</b>", style_bold_cell), Paragraph(f"{datetime.now().year}-{datetime.now().year+1}", style_normal_cell)],
            [Paragraph("<b>Registered Email:</b>", style_bold_cell), Paragraph(str(student_row['Email']), style_normal_cell),
             Paragraph("<b>Evaluation Date:</b>", style_bold_cell), Paragraph(datetime.now().strftime("%d-%b-%Y"), style_normal_cell)]
        ]
        info_table = Table(info_data, colWidths=[110, 160, 110, 152])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 25))
        
        # 3. CORE METRICS EVALUATION DATA GRID (Tabular Performance Sheet)
        metrics_data = [
            [Paragraph("<b>Performance Metric Indicator</b>", style_bold_cell), Paragraph("<b>Calculated Values / Status</b>", style_bold_cell)],
            [Paragraph("Overall Course Percentage", style_normal_cell), Paragraph(f"{student_row['Overall_Percentage']}%", style_normal_cell)],
            [Paragraph("Total Quizzes Attempted", style_normal_cell), Paragraph(str(student_row['Attempted_Quiz']), style_normal_cell)],
            [Paragraph("Course Attendance Rate", style_normal_cell), Paragraph(f"{student_row['Attendance_%']}%", style_normal_cell)],
            [Paragraph("Computed Performance Index Score", style_normal_cell), Paragraph(str(student_row['Performance_Score']), style_normal_cell)],
            [Paragraph("<b>Final Derived Grade</b>", style_bold_cell), Paragraph(f"<b>{student_row['Grade']}</b>", style_bold_cell)],
            [Paragraph("<b>Merit Position (Rank)</b>", style_bold_cell), Paragraph(f"<b>Rank #{student_row['Rank']}</b>", style_bold_cell)]
        ]
        metrics_table = Table(metrics_data, colWidths=[320, 212], rowHeights=[24]*7)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
            ('TEXTCOLOR', (0,0), (-1,0), PRIMARY_COLOR),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D1D5DB")),
            ('BACKGROUND', (0,5), (1,6), colors.HexColor("#FEF2F2")), # Highlight Grade/Rank row with light alert background
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 25))
        
        # 4. COMPUTER GENERATED PERFORMANCE SYSTEM REVIEW BADGE
        style_insight_heading = ParagraphStyle('InsHead', parent=styles['Normal'], fontSize=10, leading=12, fontName="Helvetica-Bold", textColor=PRIMARY_COLOR, spaceAfter=4)
        style_insight_body = ParagraphStyle('InsBody', parent=styles['Normal'], fontSize=9, leading=13, fontName="Helvetica-Oblique", textColor=colors.HexColor("#374151"))
        
        insight_box_data = [[
            Paragraph("<b>AUTOMATED PERFORMANCE ANALYSIS & METRIC REVIEW:</b>", style_insight_heading),
            Paragraph(str(student_row['Insight']), style_insight_body)
        ]]
        insight_table = Table(insight_box_data, colWidths=[520])
        insight_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F4F8")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BCCCDC")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(insight_table)
        story.append(Spacer(1, 45))
        
        # 5. CORPORATE LEGAL NOTICES & SIGNATURE VERIFICATION BLOCKS
        sig_data = [
            [Paragraph("<font color='#9CA3AF'>[System Verified Seal]</font>", style_normal_cell), Paragraph("___________________________", style_normal_cell)],
            [Paragraph("<b>Evaluation Engine:</b> Autonomous Processing", style_normal_cell), Paragraph("<b>Authorized Signatory</b><br/>LIET Academic Controller Office", style_normal_cell)]
        ]
        sig_table = Table(sig_data, colWidths=[280, 252])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(sig_table)
        
        # Build Document Instance safely
        doc.build(story)
        return True
    except Exception as pdf_err:
        print(f"Error generating customized dynamic PDF for {student_row.get('Name', 'Student')}: {str(pdf_err)}")
        return False

def run_entire_pipeline():
    """
    Automatically aggregates all CSV files from the 'data/' folder, 
    calculates metrics, triggers performance engine, updates the dashboard database,
    generates PDF reports, and dispatches automated emails via SMTP.
    """
    DATA_FOLDER = "data"
    OUTPUT_FOLDER = "output"
    
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
        # SMTP AUTOMATED SYSTEM WITH UPGRADED PDF DISTRIBUTION
        # ==========================================================
        SENDER_EMAIL = "vibhuyadav1192081@gmail.com"
        SENDER_PASSWORD = "tqof rmpq ehgl wtqq"

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
                
                # Triggers the brand new Dynamic College Grid Report Card
                pdf_created = generate_pdf_grade_card(row, pdf_filename)
                
                if pdf_created and os.path.exists(pdf_filename):
                    msg = MIMEMultipart()
                    msg['From'] = SENDER_EMAIL
                    msg['To'] = student_email
                    msg['Subject'] = f"🏆 Official Academic Performance Grade Card Updated - {student_name}"
                    
                    body = f"Dear {student_name},\n\nYour performance matrix has been updated by the autonomous system evaluation engine at Lloyd Institute.\n\nYour current calculated standing Grade is: {student_grade}.\n\nPlease find the official system-verified digital report card PDF file attached below.\n\nBest Regards,\nOffice of the Academic Controller\nLloyd Institute of Engineering & Technology"
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
