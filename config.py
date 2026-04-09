# config.py - Render Deployment Configuration

import os
import sys

# ====================================
# RENDER ENVIRONMENT DETECTION
# ====================================
IS_RENDER = 'RENDER' in os.environ
IS_DEVELOPMENT = not IS_RENDER

# ====================================
# PORT CONFIGURATION
# ====================================
PORT = int(os.environ.get('PORT', 5000))

# ====================================
# SECRET KEY
# ====================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'SMART_TRAFFIC_SECRET_2026')

# ====================================
# DATABASE CONFIGURATION
# ====================================
if IS_RENDER:
    # Use PostgreSQL on Render (recommended)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///smartcity_noc.db')
else:
    # SQLite for local development
    DATABASE_URL = 'sqlite:///smartcity_noc.db'

# ====================================
# AI MODEL CONFIGURATION
# ====================================
MODEL_NAME = 'yolov8s.pt'
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_NAME)

def ensure_model_exists():
    """
    Ensure YOLO model exists. On Render, download if not present.
    On local dev, assume it's already there.
    """
    if not os.path.exists(MODEL_PATH):
        if IS_RENDER:
            print("⏳ Model not found. Downloading from Ultralytics...")
            try:
                from ultralytics import YOLO
                YOLO(MODEL_NAME)  # Auto-downloads to cache
                print("✅ Model downloaded successfully")
            except Exception as e:
                print(f"❌ Model download failed: {e}")
                print("⚠️ App will continue but detection will fail")
        else:
            print(f"⚠️ Model file {MODEL_NAME} not found in {MODEL_PATH}")
            print("   Download it manually or run: python -m ultralytics")

# ====================================
# VIDEO FILES CONFIGURATION
# ====================================
VIDEOS = {
    'traffic1.mp4': 'static/traffic1.mp4',
    'traffic2.mp4': 'static/traffic2.mp4',
    'traffic3.mp4': 'static/traffic3.mp4',
    'traffic4.mp4': 'static/traffic4.mp4',
}

# ====================================
# PERFORMANCE SETTINGS
# ====================================
# These are optimized for Render's free tier
FRAME_SKIP = 10           # Process every 10th frame
JPEG_QUALITY = 50         # 50% JPEG quality for faster streaming
RESIZE_DIM = (640, 360)   # Reduced resolution for performance

if IS_RENDER:
    print("✅ Running on Render (Production)")
    print(f"   Port: {PORT}")
    print(f"   Database: {DATABASE_URL}")
else:
    print("✅ Running in Development Mode (Local)")
    print(f"   Port: {PORT}")
    print(f"   Database: SQLite")

# Ensure model is ready
ensure_model_exists()
