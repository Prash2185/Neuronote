import logging
from typing import Dict, Any
import cv2
from deepface import DeepFace
import numpy as np
from streamlit_webrtc import VideoProcessorBase

logger = logging.getLogger(__name__)

class EmotionProcessor(VideoProcessorBase):
    def __init__(self):
        self.model = None
        self.face_cascade = None
        self.connection_alive = True
        try:
            self.model = DeepFace.build_model("Emotion")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    def on_ended(self):
        self.connection_alive = False
        logger.info("Video connection ended")
            
    async def recv_async(self, frame):
        if not self.connection_alive:
            return None
        img = frame.to_ndarray(format="bgr24")
        try:
            if self.face_cascade is None or self.model is None:
                return img
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                face = img[y:y+h, x:x+w]
                face = cv2.resize(face, (48, 48))
                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                face = np.expand_dims(face, axis=0)
                
                try:
                    emotion = DeepFace.analyze(face, actions=['emotion'], 
                                            enforce_detection=False,
                                            detector_backend='opencv')
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(img, emotion[0]['dominant_emotion'], 
                              (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.9, (0, 255, 0), 2)
                except Exception as e:
                    logger.error(f"Error analyzing emotion: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            
        return img
        
    def recv(self, frame):
        return self.recv_async(frame)

def get_ice_config() -> Dict[str, Any]:
    return {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {
                "urls": [
                    "turn:openrelay.metered.ca:443",
                    "turn:openrelay.metered.ca:443?transport=tcp"
                ],
                "username": "openrelayproject",
                "credential": "openrelayproject"
            }
        ],
        "iceTransportPolicy": "all",
        "bundlePolicy": "max-bundle",
        "iceCandidatePoolSize": 1,
        "sdpSemantics": "unified-plan"
    }

# Add connection state tracker
class ConnectionState:
    def __init__(self):
        self.is_connected = False
        self.last_state = None
        
    def update(self, state: str) -> None:
        self.last_state = state
        self.is_connected = state == "connected"
        logger.info(f"ICE Connection state changed to: {state}")

connection_state = ConnectionState()

def handle_webrtc_error(error: Exception) -> str:
    logger.error(f"WebRTC error: {str(error)}")
    if "NoneType" in str(error):
        return "Connection lost. Please refresh the page."
    return f"WebRTC error: {str(error)}"
