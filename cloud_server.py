from flask import Flask, render_template
import os

app = Flask(__name__)

# Master Command Center (Dashboard)
@app.route('/')
def index():
    return render_template('dashboard.html')

# IT Service Desk (Tickets)
@app.route('/service-desk')
def service_desk():
    return render_template('service_desk.html')

# Video Feed placeholder (Cloud pe error na aaye isliye)
@app.route('/video_feed_<int:lane_id>')
def video_feed(lane_id):
    return "Stream only available on Local Laptop", 404

if __name__ == '__main__':
    # Render port handle karne ke liye
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)