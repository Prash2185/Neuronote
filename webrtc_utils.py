import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_ice_config() -> Dict[str, Any]:
    return {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]}
        ],
        "iceTransportPolicy": "all",
        "bundlePolicy": "max-bundle",
    }

def handle_webrtc_error(error: Exception) -> str:
    logger.error(f"WebRTC error: {str(error)}")
    if "NoneType" in str(error):
        return "Connection lost. Please refresh the page."
    return f"WebRTC error: {str(error)}"
