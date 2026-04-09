# SmartCity NOC Central

An AI-powered Network Operations Center (NOC) dashboard for smart city management, focusing on live traffic monitoring, automated signal control, and incident management.

## Architecture

- *Flask* (port 5000): Main web dashboard with Jinja2 templates and video streaming
- *FastAPI* (port 8000): Ticket/Service Desk API with background monitoring
- *SQLite*: Local database (smartcity_noc.db) for traffic logs and helpdesk tickets
- *OpenCV*: Video frame processing for 4 traffic camera feeds
- *YOLOv8*: AI model for vehicle detection (model: yolov8s.pt)

## Project Structure


app.py              - Flask main application (dashboard, video feeds, stats)
database.py         - Flask app database utilities
start.sh            - Startup script (runs both Flask + FastAPI)
ai_engine/          - AI detection logic (YOLOv8 + traffic signal logic)
ticket_service/     - FastAPI service desk application
  main.py           - FastAPI app entry point
  database.py       - SQLite database config (SQLAlchemy)
  models.py         - DB models
  routes.py         - API routes
  schemas.py        - Pydantic schemas
  monitor.py        - Background monitoring (auto-creates tickets)
templates/          - Jinja2 HTML templates
  dashboard.html    - Main NOC dashboard
  login.html        - Login page
  service_desk.html - Service desk UI
static/             - Static assets (traffic1-4.mp4 video feeds)
yolov8s.pt          - Pre-trained YOLOv8 model weights
smartcity_noc.db    - SQLite database


## Workflow

- *Start application*: bash start.sh on port 5000 (webview)
  - Starts FastAPI uvicorn on localhost:8000 in background
  - Starts Flask gunicorn on 0.0.0.0:5000

## Key Notes

- The ticket service uses SQLite (local) instead of the original Supabase PostgreSQL
- Flask serves video streams via multipart MJPEG responses
- Dashboard auto-updates PCU (Passenger Car Unit) stats via polling /get_stats
- Background monitoring in FastAPI auto-creates tickets when simulated failures occur