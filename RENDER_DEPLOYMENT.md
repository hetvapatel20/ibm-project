# 🚀 Render Deployment Guide

## ✅ Pre-Deployment Checklist

### 1. **Critical Issues to Fix**

#### ❌ Model File Size Issue
- **Problem**: `yolov8s.pt` (~50MB) may exceed Render's free tier limitations
- **Solution Options**:
  ```
  Option A: Remove from repo and download at runtime
  Option B: Store on AWS S3/Google Cloud Storage and download during startup
  Option C: Use lightweight model quantization
  ```

#### ❌ Video Files Size
- **Problem**: MP4 files (traffic1.mp4 to traffic4.mp4) are large (typically 50-200MB each)
- **Solution**:
  ```bash
  # Option 1: Store videos on CDN (Cloudinary, AWS S3, etc.)
  # Option 2: Use smaller video clips for demo
  # Option 3: Use placeholder images instead of video feeds
  ```

#### ❌ Database Persistence
- **Problem**: SQLite (`smartcity_noc.db`) doesn't persist on Render's ephemeral filesystem
- **Solution**:
  ```bash
  # Use PostgreSQL instead (Render provides free tier)
  # OR use environment variable backup system
  ```

### 2. **Required Files Created**
✅ `Procfile` - Tells Render how to run the app
✅ `render.yaml` - Configuration for Render deployment
✅ `requirements.txt` - Updated with all dependencies
✅ `.gitignore` - Prevents large files from being pushed

### 3. **Deployment Steps on Render.com**

```bash
Step 1: Push code to GitHub
        git add .
        git commit -m "Prepare for Render deployment"
        git push origin main

Step 2: Go to https://render.com/dashboard
        Click "New +" > "Web Service"

Step 3: Connect GitHub repository
        Select branch: main/master

Step 4: Configure environment variables
        SECRET_KEY = smart_traffic_render_2026
        PYTHON_VERSION = 3.11
        PORT = 5000

Step 5: Set build & start commands
        Build: pip install -r requirements.txt
        Start: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1

Step 6: Click "Deploy"
```

### 4. **Important Optimizations for Render**

#### Memory & CPU Concerns
```python
# In app.py - Already set for Render:
FRAME_SKIP = 10          # Process every 10th frame
JPEG_QUALITY = 50        # 50% JPEG quality
RESIZE_DIM = (640, 360)  # Reduced resolution
```

#### Timeout Configuration
```
gunicorn timeout: 120 seconds (set in Procfile)
Reason: AI model initialization takes time
```

#### Worker Configuration
```
--workers 1  (Render free tier can't handle multiple workers)
```

### 5. **Testing URLs After Deployment**

When deployment completes, Render provides URL like: `https://traffic-management-system.onrender.com`

Test these endpoints:

```bash
1. Main Dashboard
   GET https://your-app.onrender.com/
   Expected: HTML dashboard with video feeds

2. Video Stream (Lane 1)
   GET https://your-app.onrender.com/video_feed/1
   Expected: MJPEG video stream

3. Statistics API
   GET https://your-app.onrender.com/get_stats
   Expected: JSON with lane data
   {
     "lanes": [
       {"id": 1, "pcu": 5, "counts": {...}, "signal": "GREEN", "timer": 25}
     ],
     "priority_lane": 0,
     "accident_mode": false
   }

4. Ticket Service API (if running separately)
   GET https://your-app.onrender.com/api/v1/tickets
   Expected: Ticket list or error if service not included
```

### 6. **Potential Issues & Solutions**

#### Issue 1: "No space left on device"
```
❌ Cause: Model files too large
✅ Solution: Download models at runtime from external source
```

#### Issue 2: "Python version mismatch"
```
❌ Cause: pyproject.toml or specific version requirements
✅ Solution: Explicitly set PYTHON_VERSION = 3.11 in environment vars
```

#### Issue 3: "Port already in use"
```
❌ Cause: Hard-coded port instead of environment variable
✅ Solution: Already using: port = int(os.environ.get('PORT', 5000))
```

#### Issue 4: "Video files not found"
```
❌ Cause: Static files not deployed properly
✅ Solution: 
   if not cap.isOpened():
       print(f"⚠️ Warning: Could not open {path}")
   # Falls back gracefully
```

#### Issue 5: "Model initialization timeout"
```
❌ Cause: gunicorn default timeout (30s) too short for YOLO loading
✅ Solution: Already set --timeout 120 in Procfile
```

### 7. **Next Steps After Deployment**

1. **Monitor logs**: Render Dashboard > Logs
2. **Check performance**: Look for memory warnings
3. **Test all routes**: Verify video feeds + APIs work
4. **Database setup**: If using PostgreSQL, migrate from SQLite
5. **Model optimization**: Consider faster YOLO variants or caching

### 8. **For Production (After Validation)**

```yaml
Recommend upgrading to Paid Plan:
  - Persistent storage (for DB & models)
  - More CPU/RAM (for real-time processing)
  - Auto-scaling
  - Custom domains
  - SSL certificates
```

---

✅ **Your app is now ready for Render deployment!**
