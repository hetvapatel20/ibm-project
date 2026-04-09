from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for, make_response
from flask_cors import CORS
import cv2
import os
import time
import random
import csv
from io import StringIO
import requests
from functools import wraps

# --- 📂 IMPORT CUSTOM MODULES ---
# Khatri karo ke aa folders/files tamari repo ma chhe
try:
    from ai_engine.detector import TrafficDetector
    from ai_engine.traffic_logic import TrafficController
    import database
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Tip: Make sure ai_engine folder and database.py are in the same directory.")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "SMART_TRAFFIC_SECRET_2026")
CORS(app)

# --- ⚙️ PERFORMANCE CONFIG ---
FRAME_SKIP = 10        # Render na free tier mate 10-15 rakhvu
JPEG_QUALITY = 50      # Quality 50% rakhi chhe performance mate
RESIZE_DIM = (640, 360) # Video resolution

# --- 📹 4 TRAFFIC CAMERAS (Static Files) ---
# Tame static folder ma traffic1.mp4 thi traffic4.mp4 mukya chhe te load thase
VIDEOS = [
    "static/traffic1.mp4", 
    "static/traffic2.mp4",
    "static/traffic3.mp4", 
    "static/traffic4.mp4"
]

cameras = []
for i, path in enumerate(VIDEOS):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"⚠️ Warning: Could not open {path}. Check if file exists in static folder.")
    else:
        print(f"✅ Camera {i+1} Initialized: {path}")
    cameras.append(cap)

# --- 🧠 AI INITIALIZATION ---
print("⏳ Loading AI Model...")
detector = TrafficDetector()
controller = TrafficController()
print("✅ System Ready!")

# --- 📊 GLOBAL STATE ---
current_state = {
    "lanes": [{"id": i+1, "pcu": 0, "counts": {}, "signal": "RED", "timer": 0} for i in range(4)],
    "priority_lane": 0,
    "accident_mode": False
}

# --- 🎥 FRAME GENERATOR ---
def generate_frames(lane_id):
    cam = cameras[lane_id]
    last_processed_frame = None
    frame_count = 0
    
    while True:
        success, frame = cam.read()
        
        # Loop Video: Jo video khatam thai jay to restart karo
        if not success:
            cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_count += 1
        
        # Performance mate har 'FRAME_SKIP' frame e j process thase
        if frame_count % FRAME_SKIP == 0:
            frame = cv2.resize(frame, (320, 180))
            
            # AI logic thi detection
            processed_frame, counts, pcu, is_emergency = detector.process_frame(frame)
            
            # State update
            current_state["lanes"][lane_id]["pcu"] = pcu
            current_state["lanes"][lane_id]["counts"] = counts
            
            # Signal Overlay (Visual)
            color = (0, 255, 0) if current_state["lanes"][lane_id]["signal"] == "GREEN" else (0, 0, 255)
            cv2.putText(processed_frame, f"LANE {lane_id+1}: {current_state['lanes'][lane_id]['signal']}", 
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            last_processed_frame = processed_frame
        else:
            processed_frame = last_processed_frame if last_processed_frame is not None else frame

        if processed_frame is not None:
            ret, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# --- 🌐 ROUTES ---

@app.route('/')
def index():
    # Login logic tame database.py ma set kari hoy to session check kari sako
    return render_template('dashboard.html')

@app.route('/video_feed_<int:lane_id>')
def video_feed(lane_id):
    # index 0 to 3 hovo joie
    if 1 <= lane_id <= 4:
        return Response(generate_frames(lane_id-1), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "Invalid Lane ID", 404

@app.route('/get_stats')
def get_stats():
    # Lane data pass kari ne signal decide karo
    lane_inputs = [{"pcu": l["pcu"], "emergency": False} for l in current_state["lanes"]]
    signals, timers, active_idx = controller.decide_signal(lane_inputs)
    
    for i in range(4):
        current_state["lanes"][i]["signal"] = signals[i]
        current_state["lanes"][i]["timer"] = timers[i]
    current_state["priority_lane"] = active_idx
    
    return jsonify(current_state)

# --- 🚀 RUN SERVER ---
if __name__ == "__main__":
    # Database initialize
    if 'database' in globals() and hasattr(database, 'init_db'):
        database.init_db()
    
    # Render mate port setting
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server running on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)
    