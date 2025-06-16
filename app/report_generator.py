# app/report_generator.py
from fpdf import FPDF
from datetime import datetime
import os

def generate_report(note_analysis, emotion_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font (using built-in Helvetica)
    pdf.set_font("Helvetica", size=16)
    
    # Header
    pdf.cell(200, 10, txt="NeuroNote Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    # Notes Analysis Section
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(200, 10, txt="Notes Analysis", ln=True)
    pdf.set_font("Helvetica", size=12)
    
    if note_analysis:
        for key, value in note_analysis.items():
            pdf.cell(200, 8, txt=f"- {key.replace('_', ' ').title()}: {value}", ln=True)
    else:
        pdf.cell(200, 8, txt="No notes data available", ln=True)
    
    pdf.ln(8)
    
    # Emotion Analysis Section
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(200, 10, txt="Emotion Analysis", ln=True)
    pdf.set_font("Helvetica", size=12)
    
    if isinstance(emotion_data, dict):
        for emotion, score in emotion_data.items():
            pdf.cell(200, 8, txt=f"- {emotion}: {score}", ln=True)
    elif emotion_data:
        pdf.cell(200, 8, txt=f"- Dominant Emotion: {emotion_data}", ln=True)
    else:
        pdf.cell(200, 8, txt="No emotion data available", ln=True)
    
    # Save the report
    os.makedirs("static", exist_ok=True)
    report_path = "static/neuro_report.pdf"
    pdf.output(report_path)
    return report_path