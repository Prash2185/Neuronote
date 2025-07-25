# app/webcam_emotion.py
import cv2
from streamlit_webrtc import VideoProcessorBase
from av import VideoFrame as AvVideoFrame
from deepface import DeepFace
import time

class EmotionAnalyzer(VideoProcessorBase):
    def __init__(self):
        self.last_emotion = "Detecting..."
        self.emotion_history = []
        self.last_analysis_time = 0
    
    def analyze_frame(self, img):
        try:
            # Limit analysis to once per 2 seconds
            current_time = time.time()
            if current_time - self.last_analysis_time > 2:
                result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                emotion = result[0]['dominant_emotion']
                self.last_emotion = emotion
                self.emotion_history.append(emotion)
                self.last_analysis_time = current_time
                return emotion
        except Exception as e:
            pass
        return self.last_emotion
    
    def get_emotion_summary(self):
        if not self.emotion_history:
            return "No emotions detected"
        
        # Count occurrences of each emotion
        emotion_counts = {}
        for emotion in self.emotion_history:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Convert counts to percentages
        total = len(self.emotion_history)
        return {k: f"{round(v/total*100)}%" for k, v in emotion_counts.items()}
    
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        emotion = self.analyze_frame(img)
        
        # Formatted label
        label = f"🧠 Emotion: {emotion.capitalize()}"
        
        # Add shadow and main text
        cv2.putText(img, label, (32, 52), cv2.FONT_HERSHEY_COMPLEX, 1.2, (20, 20, 20), 4, cv2.LINE_AA)
        cv2.putText(img, label, (30, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (50, 150, 250), 2, cv2.LINE_AA)
        
        return AvVideoFrame.from_ndarray(img, format="bgr24")