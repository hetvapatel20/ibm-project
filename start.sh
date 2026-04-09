#!/bin/bash
# Wait for any leftover process to release port 5000
sleep 3

# Start FastAPI ticket service in background (SQLite fallback if Supabase is down)
uvicorn ticket_service.main:app --host localhost --port 8000 &

# Start Flask main app on port 5000 using gunicorn
gunicorn --bind 0.0.0.0:5000 --worker-class gthread --threads 4 --workers 1 app:app
