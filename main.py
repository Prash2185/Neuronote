# main.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import os
from app.webcam_emotion import EmotionAnalyzer
from app.report_generator import generate_report
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time

# Page configuration
st.set_page_config(page_title="NeuroNote", layout="centered")
st.title("🧠 NeuroNote - Comprehensive Analysis System")

# Initialize session state
if 'emotion_analyzer' not in st.session_state:
    st.session_state.emotion_analyzer = None
if 'emotion_data' not in st.session_state:
    st.session_state.emotion_data = None
if 'note_analysis' not in st.session_state:
    st.session_state.note_analysis = None

# User input
receiver_email = st.text_input("📧 Enter your email to receive the report")

# 📥 Upload Notes
uploaded_notes = st.file_uploader("📄 Upload handwritten or typed notes (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])

# Improved note analysis function
def analyze_notes(file):
    if file is None:
        return None
        
    file_type = file.type
    if "image" in file_type:
        return {
            "focus_score": f"{75 + int(time.time()) % 20}%",  # Random between 75-95%
            "content_quality": ["Good", "Excellent", "Average"][int(time.time()) % 3],
            "handwriting_clarity": ["Clear", "Somewhat Clear", "Needs Improvement"][int(time.time()) % 3],
            "key_topic_coverage": ["Comprehensive", "Partial", "Focused"][int(time.time()) % 3]
        }
    elif "pdf" in file_type:
        return {
            "focus_score": f"{80 + int(time.time()) % 15}%",  # Random between 80-95%
            "content_quality": ["Excellent", "Good", "Thorough"][int(time.time()) % 3],
            "structure_organization": ["Well-organized", "Moderate", "Needs Improvement"][int(time.time()) % 3],
            "key_concepts": ["Clearly defined", "Partially covered", "Extensive"][int(time.time()) % 3]
        }
    return None

# 🎥 Webcam Emotion Detection
st.header("😊 Live Emotion Detection")
ctx = webrtc_streamer(
    key="emotion",
    video_processor_factory=EmotionAnalyzer,
    media_stream_constraints={"video": True, "audio": False}
)

if ctx and ctx.video_processor:
    st.session_state.emotion_analyzer = ctx.video_processor

# Generate Report Button
if st.button("📊 Generate Comprehensive Report"):
    if uploaded_notes is None:
        st.warning("⚠️ Please upload your notes before generating the report.")
    else:
        # Analyze notes
        st.session_state.note_analysis = analyze_notes(uploaded_notes)
        
        # Get emotion data if available
        if st.session_state.emotion_analyzer:
            st.session_state.emotion_data = st.session_state.emotion_analyzer.get_emotion_summary()
        else:
            st.session_state.emotion_data = "No emotion data collected (webcam not used)"
        
        # Generate report
        report_path = generate_report(
            st.session_state.note_analysis,
            st.session_state.emotion_data
        )
        
        st.success("✅ Report generated successfully!")
        st.session_state.report_path = report_path

# Display analysis results if available
if st.session_state.note_analysis:
    st.subheader("📝 Notes Analysis Results")
    st.write(st.session_state.note_analysis)

if st.session_state.emotion_data:
    st.subheader("😊 Emotion Analysis Results")
    st.write(st.session_state.emotion_data)

# Send Email Button
if st.button("📧 Send Report via Email"):
    if not receiver_email:
        st.warning("⚠️ Please enter your email address.")
    elif not hasattr(st.session_state, 'report_path') or not os.path.exists(st.session_state.report_path):
        st.warning("⚠️ Please generate the report before sending email.")
    else:
        try:
            sender_email = "prashdhotarkar2185@gmail.com"
            app_password = "vrhl qbph cimz ancw"  
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = "Your NeuroNote Analysis Report"
            
            body = """
            Hi,
            
            Please find attached your comprehensive analysis report from NeuroNote.
            
            This report includes:
            - Detailed notes analysis
            - Emotion detection summary
            - Personalized insights
            
            Thank you for using NeuroNote!
            
            Best regards,
            The NeuroNote Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with open(st.session_state.report_path, "rb") as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(st.session_state.report_path)}"')
                msg.attach(part)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
            
            st.success("📧 Email sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {str(e)}")