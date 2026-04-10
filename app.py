from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for, make_response
from flask_cors import CORS
import cv2
import os
import time
import random
import csv
import requests
from io import StringIO
from functools import wraps

# --- 🛠️ LOCAL IMPORTS ---
# Khatri karo ke ai_engine folder ane database.py file Replit ma che.
from ai_engine.detector import TrafficDetector
from ai_engine.traffic_logic import TrafficController
import database

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_KEY", "VIVA_SECRET_STRICT")
CORS(app)

# --- ⚙️ PERFORMANCE CONFIG (Replit mate optimized) ---
cv2.setNumThreads(0)
FRAME_SKIP = 7
JPEG_QUALITY = 70
RESIZE_DIM = (640, 360)

# --- 📹 VIDEO PATHS (Replit Compatible) ---
base_path = os.path.dirname(os.path.abspath(__file__))
VIDEOS = [
    os.path.join(base_path, "static/traffic1.mp4"),
    os.path.join(base_path, "static/traffic2.mp4"),
    os.path.join(base_path, "static/traffic3.mp4"),
    os.path.join(base_path, "static/traffic4.mp4")
]

# Cameras initialize
cameras = []
for v in VIDEOS:
    if os.path.exists(v):
        cameras.append(cv2.VideoCapture(v, cv2.CAP_FFMPEG))
    else:
        print(f"⚠️ Warning: Video missing at {v}")

# --- 🧠 AI INITIALIZATION ---
detector = TrafficDetector()
controller = TrafficController()

current_state = {
    "lanes": [{"id": i+1, "pcu": 0, "counts": {}, "signal": "RED", "timer": 0, "is_service": False} for i in range(4)],
    "priority_lane": 0,
    "accident_mode": False,
    "helpdesk_tickets": []
}

last_db_log_time = time.time()
# Jo FastAPI alag Replit app ma hoy, to '127.0.0.1' ni jagya e eapp ni URL nakhvi.
FASTAPI_BASE_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

# --- 🔐 SECURITY ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- 📹 VIDEO GENERATOR ---
def generate_frames(lane_id):
    if lane_id >= len(cameras): return
    cam = cameras[lane_id]
    last_processed_frame = None
    frame_counter = 0

    while True:
        success, frame = cam.read()
        if not success:
            cam.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video
            continue
        
        frame = cv2.resize(frame, RESIZE_DIM)
        frame_counter += 1
        
        lane_data = current_state["lanes"][lane_id]
        
        if frame_counter % FRAME_SKIP == 0:
            processed_frame, counts, pcu, is_emergency = detector.process_frame(frame, only_emergency=lane_data["is_service"])
            current_state["lanes"][lane_id].update({"pcu": pcu, "counts": counts, "emergency": is_emergency})
            
            # Draw Signal Status on Video
            color = (0, 255, 0) if lane_data["signal"] == "GREEN" else (0, 0, 255)
            cv2.putText(processed_frame, f"LANE {lane_id+1}: {lane_data['signal']}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            last_processed_frame = processed_frame
        else:
            processed_frame = last_processed_frame if last_processed_frame is not None else frame

        ret, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# --- 🌐 ROUTES ---

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if database.verify_login(user, pw):
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html', error="Invalid Credentials" if request.method == 'POST' else None)

@app.route('/video_feed_<int:lane_id>')
@login_required
def video_feed(lane_id):
    return Response(generate_frames(lane_id-1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_stats')
@login_required
def get_stats():
    lane_logic_input = [{"pcu": l["pcu"], "emergency": l.get("emergency", False)} for l in current_state["lanes"]]
    signals, timers, active_idx = controller.decide_signal(lane_logic_input)
    
    for i in range(4):
        current_state["lanes"][i]["signal"] = signals[i]
        current_state["lanes"][i]["timer"] = timers[i]
    current_state["priority_lane"] = active_idx

    try:
        resp = requests.get(f"{FASTAPI_BASE_URL}/api/v1/tickets/", timeout=0.5)
        if resp.status_code == 200:
            current_state["helpdesk_tickets"] = resp.json()[::-1]
    except:
        current_state["helpdesk_tickets"] = database.get_active_tickets()

    return jsonify(current_state)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- 🚀 REPLIT LAUNCH ---
if __name__ == "__main__":
    database.init_db()
    # Replit mate port 8080 ane host 0.0.0.0 hovu zaruri che
    port = int(os.environ.get('PORT', 8080))
    print(f"✅ Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)