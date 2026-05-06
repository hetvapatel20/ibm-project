from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for, make_response
from flask_cors import CORS
import cv2
from ai_engine.detector import TrafficDetector
from ai_engine.traffic_logic import TrafficController
import database
from functools import wraps 
import os
import random
import time
import csv
from io import StringIO
import requests 

# --- 🛠️ SYSTEM OPTIMIZATION (Fix for Lag) ---
cv2.setNumThreads(0) 

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY_FOR_VIVA" 
CORS(app) 

# 🔥 LIVE FASTAPI BACKEND URL (Cloud) 🔥
API_URL = "https://smartcity-api-k0r3.onrender.com/api/v1"

# 🔥 SPEED BOOSTERS FOR AI 🔥
FRAME_SKIP = 15       # Process fewer frames for massive speed boost on Dashboard
JPEG_QUALITY = 60     
RESIZE_DIM = (320, 180) # Lower resolution for ultra-fast processing without lag

VIDEOS = [
    "static/traffic1.mp4", 
    "static/traffic2.mp4",
    "static/traffic3.mp4", 
    "static/traffic4.mp4"
]

cameras = []
for v in VIDEOS:
    if isinstance(v, str) and (v.startswith("http") or v.startswith("rtsp")):
        cameras.append(cv2.VideoCapture(v))
    else:
        cameras.append(cv2.VideoCapture(v, cv2.CAP_FFMPEG))

print("⏳ Initializing AI Engines...")
detector = TrafficDetector()
controller = TrafficController()
print("✅ AI Engines Ready!")

current_state = {
    "lanes": [
        {"id": 1, "pcu": 0, "counts": {}, "signal": "RED", "timer": 0, "is_service": False},
        {"id": 2, "pcu": 0, "counts": {}, "signal": "RED", "timer": 0, "is_service": False},
        {"id": 3, "pcu": 0, "counts": {}, "signal": "RED", "timer": 0, "is_service": False},
        {"id": 4, "pcu": 0, "counts": {}, "signal": "RED", "timer": 0, "is_service": False}
    ],
    "priority_lane": 0,
    "accident_mode": False,
    "helpdesk_tickets": [] 
}

last_db_log_time = time.time()

# ==========================================
# 🛡️ SECURITY DECORATORS
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session:
                return redirect(url_for('login'))
            
            user_role = session.get('role', 'System Admin')
            if user_role not in allowed_roles:
                return jsonify({
                    "status": "error", 
                    "message": f"🚫 Access Denied! Role '{user_role}' is not authorized."
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- 📹 VIDEO GENERATOR FUNCTION ---
def generate_frames(lane_id):
    cam = cameras[lane_id]
    frame_counter = 0
    last_processed_frame = None

    while True:
        success, frame = cam.read()
        if not success: 
            cam.set(cv2.CAP_PROP_POS_FRAMES, 0) 
            continue
        
        frame = cv2.resize(frame, RESIZE_DIM) 
        frame_counter += 1
        
        lane_data = current_state["lanes"][lane_id]
        signal = lane_data["signal"]
        
        if current_state["accident_mode"]: signal = "RED"

        if frame_counter % FRAME_SKIP == 0:
            processed_frame, counts, pcu, is_emergency = detector.process_frame(frame, only_emergency=lane_data["is_service"])
            
            if signal == "RED":
                overlay = processed_frame.copy()
                cv2.rectangle(overlay, (0, 0), RESIZE_DIM, (0, 0, 100), -1) 
                cv2.addWeighted(overlay, 0.3, processed_frame, 0.7, 0, processed_frame)
                cv2.putText(processed_frame, "HALT", (100, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                cv2.putText(processed_frame, "GO", (120, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            current_state["lanes"][lane_id]["pcu"] = pcu
            current_state["lanes"][lane_id]["counts"] = counts
            current_state["lanes"][lane_id]["emergency"] = is_emergency
            last_processed_frame = processed_frame
        else:
            processed_frame = last_processed_frame if last_processed_frame is not None else frame

        if current_state["accident_mode"]:
            cv2.putText(processed_frame, "ACCIDENT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        ret, buffer = cv2.imencode('.jpg', processed_frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# --- 🧠 LOGIC UPDATER ---
def update_logic():
    global last_db_log_time
    if current_state["accident_mode"]:
        for i in range(4): current_state["lanes"][i]["signal"] = "RED"
        return

    lane_data = [{"pcu": l["pcu"], "emergency": l.get("emergency", False)} for l in current_state["lanes"]]
    signals, timers, active_idx = controller.decide_signal(lane_data)

    for i in range(4):
        current_state["lanes"][i]["signal"] = signals[i]
        current_state["lanes"][i]["timer"] = timers[i]
    current_state["priority_lane"] = active_idx

    current_time = time.time()
    if current_time - last_db_log_time > 5.0:
        for i in range(4):
            l = current_state["lanes"][i]
            database.log_traffic_data(i+1, l["counts"], l["pcu"], l["signal"])
        last_db_log_time = current_time

# ==========================================
# 🌐 WEB ROUTES
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username') 
        if not user and request.is_json:
            data = request.get_json()
            user = data.get('username')
            pw = data.get('password')
        else:
            pw = request.form.get('password')

        user_data = database.verify_login(user, pw)
        
        if user_data:
            session['logged_in'] = True
            
            if isinstance(user_data, dict):
                session['username'] = user_data.get('username', user)
                session['role'] = user_data.get('role', 'System Admin')
            else:
                session['username'] = user
                session['role'] = 'System Admin'
                
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="🚫 Invalid Credentials!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required 
def index(): 
    return render_template('dashboard.html')

@app.route('/service-desk')
@login_required
def service_desk():
    return render_template('service_desk.html')

@app.route('/video_feed_<int:lane_id>')
@login_required
def video_feed(lane_id): 
    return Response(generate_frames(lane_id-1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_stats')
@login_required
def get_stats():
    update_logic() 
    try:
        # 🔥 SPEED FIX: 0.5s Timeout to prevent lag
        response = requests.get(f"{API_URL}/tickets/", timeout=0.5)
        if response.status_code == 200:
            all_tickets = response.json()
            formatted_tickets = []
            for t in all_tickets:
                if t['status'] != 'resolved': 
                    formatted_tickets.append({
                        "type": t['issue_type'],
                        "location": t['location'],
                        "priority": t['severity'].upper()
                    })
            current_state["helpdesk_tickets"] = formatted_tickets[::-1]
        else:
            current_state["helpdesk_tickets"] = database.get_active_tickets()
    except:
        current_state["helpdesk_tickets"] = database.get_active_tickets()

    return jsonify(current_state)

@app.route('/toggle_service_mode/<int:lane_id>', methods=['POST'])
@login_required
def toggle_service_mode(lane_id):
    current_state["lanes"][lane_id-1]["is_service"] = not current_state["lanes"][lane_id-1]["is_service"]
    return jsonify({"status": "success", "new_mode": current_state["lanes"][lane_id-1]["is_service"]})

@app.route('/create_ticket', methods=['POST'])
@login_required
def create_ticket():
    try:
        data = request.get_json()
        raw_priority = data.get("priority", "low").lower()
        if "med" in raw_priority: raw_priority = "medium"
        elif "high" in raw_priority: raw_priority = "high"
        elif raw_priority not in ["low", "medium", "high", "critical"]: raw_priority = "low"

        fastapi_payload = {
            "issue_type": data.get("type", "Manual Alert"),
            "location": data.get("location", "Unknown"),
            "device_id": "DASHBOARD-001",
            "severity": raw_priority
        }

        try:
            response = requests.post(f"{API_URL}/tickets/", json=fastapi_payload, timeout=1)
            if response.status_code == 429:
                return jsonify({"status": "error", "message": "Rate Limit Exceeded!"}), 429
            if response.status_code in [200, 201]:
                res_data = response.json()
                ticket_id = res_data.get('ticket_id', random.randint(1000, 9999))
                return jsonify({"status": "success", "ticket": f"TKT-{ticket_id}"})
        except: pass

        ticket_id = f"TKT-{random.randint(1000, 9999)}"
        database.add_ticket(ticket_id, data.get("type", "General Issue"), data.get("priority", "Medium"), data.get("location", "Unknown"))
        return jsonify({"status": "success", "ticket": ticket_id})
    except:
        return jsonify({"status": "error", "message": "Server Error!"}), 500

@app.route('/toggle_accident', methods=['POST'])
@role_required('System Admin')
def toggle_accident():
    current_state["accident_mode"] = not current_state["accident_mode"]
    if current_state["accident_mode"]:
        try:
            requests.post(f"{API_URL}/tickets/", json={
                "issue_type": "CRITICAL: Collision Detected",
                "location": "Global Lockdown Triggered",
                "device_id": "SYS-SOS",
                "severity": "critical"
            }, timeout=1)
        except:
            database.add_ticket(f"SOS-{random.randint(1000, 9999)}", "CRITICAL: Collision", "CRITICAL", "Global Lockdown")
    return jsonify({"status": current_state["accident_mode"]})

# 🔥 ADMIN ROUTES 🔥
@app.route('/add_new_user', methods=['POST'])
@role_required('System Admin')
def add_new_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"status": "error", "message": "All fields are required!"}), 400

    success, msg = database.create_new_user(username, password, role)
    if success:
        return jsonify({"status": "success", "message": msg})
    else:
        return jsonify({"status": "error", "message": msg}), 400

@app.route('/export_excel')
@role_required('System Admin')
def export_excel():
    conn = database.get_connection() 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM traffic_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Node', 'Date & Time', 'Cars', 'Bikes', 'Buses', 'Trucks', 'Total PCU Density', 'Signal State'])
    
    for row in logs:
        cw.writerow([row['id'], f"NODE-0{row['node_id']}", row['timestamp'], row['cars'], row['bikes'], row['buses'], row['trucks'], round(row['total_pcu'], 1), row['signal_state']])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Traffic_Analytics.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_msg = data.get("message", "").lower()
    
    if "camera" in user_msg: reply = "🛠️ CAMERA ISSUE: Check IP address."
    elif "lag" in user_msg: reply = "⚡ PERFORMANCE: Reduce Quality."
    elif "ticket" in user_msg: reply = f"🎫 TICKETING: {len(current_state['helpdesk_tickets'])} active incidents."
    elif "excel" in user_msg: reply = "📊 EXCEL REPORT: Click the Green button."
    else: reply = "🤖 NOC AI. Ask about 'camera', 'lag', 'tickets', or 'excel'."
    return jsonify({"response": reply})

@app.route('/get_valid_users')
@login_required
def get_valid_users():
    users = database.get_all_users()
    return jsonify({"valid_users": users})

# 🔥 NEW SECURITY ROUTES FOR DELETE AND LOGS 🔥
@app.route('/delete_ticket/<int:id>', methods=['POST'])
@role_required('System Admin')
def delete_ticket(id):
    data = request.get_json()
    issue = data.get('issue_type', 'Unknown Issue')
    loc = data.get('location', 'Unknown Location')
    admin_user = session.get('username', 'Unknown Admin')
    
    # DB me Delete & Log generate
    success, msg = database.delete_ticket_with_log(id, admin_user, issue, loc)
    
    # FastAPI Backend delete call
    try:
        requests.delete(f"{API_URL}/tickets/{id}", timeout=1)
    except:
        pass # Ignore API error if it fails, local DB logged successfully
        
    if success:
        return jsonify({"status": "success", "message": "Record Destroyed & Logged!"})
    return jsonify({"status": "error", "message": msg}), 400

@app.route('/get_audit_logs')
@role_required('System Admin')
def get_audit_logs():
    logs = database.get_audit_logs()
    return jsonify({"logs": logs})

if __name__ == "__main__":
    database.init_db()
    port = int(os.environ.get('PORT', 5005))
    print(f"\n🚀 SECURE TRAFFIC AI RUNNING ON: http://0.0.0.0:{port}\n")
    app.run(debug=False, threaded=True, host='0.0.0.0', port=port)