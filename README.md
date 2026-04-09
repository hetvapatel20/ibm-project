# 🚦 Smart City Traffic Management System

## 📋 Project Overview

A real-time traffic management system using AI/ML (YOLOv8) for vehicle detection and intelligent traffic signal control. Built with Flask and FastAPI for dual-service architecture.

### Key Features:
- ✅ Real-time vehicle detection using YOLOv8
- ✅ AI-powered traffic signal optimization
- ✅ 4-lane traffic monitoring dashboard
- ✅ Live video streaming (MJPEG)
- ✅ Emergency vehicle detection
- ✅ Ticket/incident reporting system
- ✅ RESTful API for integration
- ✅ Responsive web dashboard

---

## 📁 Project Structure

```
Traffic_managment/
├── app.py                      # Main Flask application
├── config.py                   # Configuration & Render setup
├── database.py                 # SQLite database utilities
├── requirements.txt            # Python dependencies
├── Procfile                    # Render deployment config
├── render.yaml                 # Advanced Render settings
├── .gitignore                  # Git ignore rules
├── RENDER_DEPLOYMENT.md        # Deployment guide
├── README.md                   # This file
│
├── ai_engine/                  # AI/ML Components
│   ├── __init__.py
│   ├── detector.py             # YOLOv8 detection engine
│   ├── traffic_logic.py        # Signal control logic
│   ├── models/
│   └── yolov8s.pt             # (Download separately)
│
├── static/
│   ├── traffic1.mp4           # Lane 1 video feed
│   ├── traffic2.mp4           # Lane 2 video feed
│   ├── traffic3.mp4           # Lane 3 video feed
│   └── traffic4.mp4           # Lane 4 video feed
│
├── templates/
│   ├── dashboard.html          # Main control center UI
│   ├── login.html              # Authentication page
│   └── service_desk.html       # Ticket service UI
│
└── ticket_service/             # FastAPI Microservice
    ├── main.py                 # FastAPI app
    ├── models.py               # Data models
    ├── routes.py               # API endpoints
    ├── schemas.py              # Request schemas
    ├── database.py             # DB models
    └── monitor.py              # Background monitoring
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- pip/conda package manager
- Git

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/traffic-management.git
cd Traffic_managment

# 2. Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download YOLOv8 model
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

# 5. Run application
python app.py
```

### Access Dashboard
- **URL**: http://localhost:5000
- **Dashboard**: Real-time traffic visualization
- **API Docs**: http://localhost:5000/api/docs (if FastAPI enabled)

---

## 📊 API Endpoints

### Flask Routes

```http
GET /
  Response: Dashboard HTML

GET /video_feed/<lane_id>
  Parameters: lane_id (1-4)
  Response: MJPEG video stream
  Example: http://localhost:5000/video_feed/1

GET /get_stats
  Response: JSON with current traffic state
  Example Response:
  {
    "lanes": [
      {
        "id": 1,
        "pcu": 12,
        "counts": {"car": 8, "bus": 1, "truck": 0},
        "signal": "GREEN",
        "timer": 25
      }
    ],
    "priority_lane": 0,
    "accident_mode": false
  }
```

### FastAPI Ticket Service

```http
GET /api/v1/tickets
  Get all tickets

POST /api/v1/tickets
  Create new ticket
  Body: {"issue_type": "...", "location": "...", "priority": "HIGH"}

PUT /api/v1/tickets/{ticket_id}
  Update ticket status
```

---

## 🌐 Render Deployment

### One-Click Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render"
   git push origin main
   ```

2. **Deploy on Render.com**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Render auto-detects `Procfile` and `render.yaml`
   - Click "Deploy"

### Deployment Status
- ✅ `Procfile` configured
- ✅ `render.yaml` configured  
- ✅ `requirements.txt` updated
- ✅ Performance optimized for free tier
- ⚠️ Model file handled dynamically
- ⚠️ Database: Use PostgreSQL for persistence

### Expected URL Format
```
https://traffic-management-system.onrender.com
```

### Test After Deployment
```bash
# Dashboard
curl https://traffic-management-system.onrender.com/

# Video Feed
curl https://traffic-management-system.onrender.com/video_feed/1

# Statistics
curl https://traffic-management-system.onrender.com/get_stats
```

---

## ⚙️ Configuration

### Environment Variables (Render)
```yaml
SECRET_KEY: your-secret-key-here
PYTHON_VERSION: 3.11
PORT: 5000
DATABASE_URL: (PostgreSQL if using premium)
```

### Performance Settings (in config.py)
```python
FRAME_SKIP = 10           # Process every 10th frame
JPEG_QUALITY = 50         # 50% compression
RESIZE_DIM = (640, 360)   # Resolution for Render
```

---

## 🧠 AI Model Details

### YOLOv8s (Small variant)
- **Size**: ~50MB
- **Speed**: Real-time on CPU
- **Classes**: car, bus, truck, motorcycle, bicycle
- **PCU Weights**: 
  - Bicycle: 0.2
  - Motorcycle: 0.5
  - Car: 1.0
  - Bus: 3.0
  - Truck: 2.5

### Vehicle Detection
- Divides each lane into Main Road (70%) and Service Lane (30%)
- Calculates Passenger Car Unit (PCU) for congestion metric
- Detects emergency vehicles

---

## 📈 Traffic Logic

### Signal Timing Algorithm
1. **Emergency Override**: Emergency vehicles get immediate green
2. **Timer Lock**: Minimum 10s green time per lane
3. **Smart Switching**: Highest PCU lane gets priority
4. **Dynamic Timing**: 
   - PCU > 40: 45 seconds green
   - PCU > 20: 25 seconds green
   - PCU < 20: 15 seconds green

---

## 🐛 Troubleshooting

### Issue: "Model not found"
```bash
Solution: python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
```

### Issue: "Video files not found"
```
Check: static/traffic1.mp4 ... traffic4.mp4 exist
Fix: Upload MP4 files to static folder
```

### Issue: "Port already in use"
```bash
Windows: netstat -ano | findstr :5000
macOS/Linux: lsof -i :5000
Kill: taskkill /PID <PID> /F
```

### Issue: "ImportError: No module named 'ultralytics'"
```bash
Solution: pip install ultralytics torch torchvision
```

### Issue: "Database locked"
```
Reason: Running multiple processes accessing SQLite simultaneously
Solution: Use PostgreSQL or Redis for production
```

---

## 📊 Monitoring & Logging

### Logs Location
- **Local**: Console output / `*.log` files
- **Render**: Render Dashboard → "Logs" section

### Key Metrics
- Vehicles detected per lane
- Average PCU per lane
- Signal state (RED/GREEN)
- Emergency events
- API response time

---

## 🔐 Security Considerations

### For Production:
1. Change `SECRET_KEY` in environment variables
2. Use HTTPS (Render provides free SSL)
3. Implement authentication for API endpoints
4. Use database credentials from environment
5. Rate limiting for API endpoints
6. CORS configured for specific domains

---

## 📦 Dependencies

See `requirements.txt` for full list:

```
flask==2.3.2
flask-cors==4.0.0
gunicorn==21.2.0
opencv-python-headless==4.8.0.74
numpy==1.24.3
ultralytics==8.0.196
torch==2.0.1
torchvision==0.15.2
fastapi==0.103.0
uvicorn==0.23.0
```

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature-name`
2. Commit changes: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature-name`
4. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: See `RENDER_DEPLOYMENT.md`
- **Dashboard URL**: https://traffic-management-system.onrender.com (after deployment)

---

## 🎯 Next Steps

- [ ] Deploy to Render
- [ ] Test all endpoints
- [ ] Monitor performance
- [ ] Optimize for production
- [ ] Add database persistence (PostgreSQL)
- [ ] Implement authentication
- [ ] Add SSL certificate
- [ ] Setup monitoring alerts

---

**Last Updated**: April 2026
**Status**: Ready for Render Deployment ✅
