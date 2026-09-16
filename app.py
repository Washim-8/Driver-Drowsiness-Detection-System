from flask import Flask, render_template, jsonify, request, make_response
from flask_compress import Compress
import threading
import os
import sqlite3
import datetime
import time
import urllib.request

# Detection modules are only available when running locally with CV dependencies
try:
    from drowsiness_detection import start_detection, stop_detection
    DETECTION_AVAILABLE = True
except ImportError:
    DETECTION_AVAILABLE = False
    def start_detection(**kwargs): pass
    def stop_detection(): pass

app = Flask(__name__)

# ── Flask-Compress: gzip HTML/JSON responses (~60-80% size reduction) ──────────
app.config["COMPRESS_REGISTER"] = True
app.config["COMPRESS_LEVEL"]    = 6      # 1 (fast) to 9 (max). 6 = balanced
app.config["COMPRESS_MIN_SIZE"] = 500    # skip compressing responses < 500 bytes
Compress(app)

# Global variable to track the detection thread
detection_thread = None
detection_running = False


# ── Keep-Alive: prevent Render free-tier from sleeping after 15 min ────────────
def _keep_alive():
    """
    Daemon thread that self-pings /health every 10 minutes.
    Prevents Render free-tier from spinning down the service.

    Behaviour:
      - On Render:  reads RENDER_EXTERNAL_URL, waits 30s, pings every 10 min
      - Local dev:  RENDER_EXTERNAL_URL not set → exits silently
      - Thread type: daemon → auto-killed when main process dies
    """
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
    if not render_url:
        return  # Not on Render — skip silently (local dev safety)

    ping_url = f"{render_url}/health"
    print(f"[KeepAlive] Self-ping enabled → {ping_url} every 10 min")

    # Wait 30s so Gunicorn fully starts before first ping
    time.sleep(30)

    while True:
        try:
            with urllib.request.urlopen(ping_url, timeout=10) as resp:
                print(f"[KeepAlive] Pinged → HTTP {resp.status}")
        except Exception as exc:
            print(f"[KeepAlive] Ping failed: {exc}")
        time.sleep(600)  # 10 minutes


_keep_alive_thread = threading.Thread(
    target=_keep_alive,
    name="keep-alive",
    daemon=True   # dies automatically when main process exits
)
_keep_alive_thread.start()


# ── Cache-Control helper ───────────────────────────────────────────────────────
def _add_cache_headers(response, seconds=3600):
    """Attach Cache-Control headers so repeat visits load from browser cache."""
    response.cache_control.max_age = seconds
    response.cache_control.public  = True
    return response


# ── Health check routes (required by Render) ───────────────────────────────────
@app.route("/health", methods=["GET"])
@app.route("/healthz", methods=["GET"])
def health():
    """
    Health check endpoint for Render.
    - Must return HTTP 200
    - No authentication, no DB calls, no ML loading
    - Must respond in < 2 seconds
    """
    return jsonify({"status": "healthy"}), 200


# ── Page routes ────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    return _add_cache_headers(resp, seconds=60)   # dynamic page: 1 min


@app.route('/about')
def about():
    resp = make_response(render_template('about.html'))
    return _add_cache_headers(resp, seconds=3600)  # semi-static: 1 hour


@app.route('/about_contact')
def about_contact():
    resp = make_response(render_template('about_contact.html'))
    return _add_cache_headers(resp, seconds=3600)  # semi-static: 1 hour


# ── Detection API routes ───────────────────────────────────────────────────────
@app.route('/start_detection')
def start_detection_route():
    global detection_thread, detection_running

    if not DETECTION_AVAILABLE:
        return jsonify({"status": "error", "message": "Detection is not available on this server. Run the app locally to use webcam detection."})

    # Check if detection is already running
    if detection_thread and detection_thread.is_alive():
        return jsonify({"status": "error", "message": "Drowsiness detection is already running."})
    
    try:
        def run_detection():
            global detection_running
            detection_running = True
            # Get absolute paths
            base_dir = os.path.dirname(os.path.abspath(__file__))
            alarm_path = os.path.join(base_dir, "sound1.mp3")
            screenshot_folder = os.path.join(base_dir, "screenshots")
            
            # Verify alarm file exists
            if not os.path.exists(alarm_path):
                print(f"Warning: Alarm file not found at {alarm_path}")
            
            start_detection(alarm_path=alarm_path, screenshot_folder=screenshot_folder, use_gui=False)
            detection_running = False

        detection_thread = threading.Thread(target=run_detection, daemon=True)
        detection_thread.start()
        
        return jsonify({"status": "success", "message": "Drowsiness detection started successfully. Press 'q' in the video window to stop."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to start detection: {str(e)}"})


@app.route('/stop_detection')
def stop_detection_route():
    global detection_running
    try:
        stop_detection()
        detection_running = False
        return jsonify({"status": "success", "message": "Detection stopped."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error stopping detection: {str(e)}"})


@app.route('/log_event', methods=['POST'])
def log_event():
    """Receive a drowsiness event from the browser and save it to the DB."""
    try:
        data = request.get_json(force=True)
        ear  = float(data.get('ear', 0.0))
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drowsiness_data.db')
        conn = sqlite3.connect(db_path)
        c    = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS drowsiness (
                     id INTEGER PRIMARY KEY,
                     timestamp DATETIME,
                     eye_aspect_ratio REAL)''')
        c.execute("INSERT INTO drowsiness (timestamp, eye_aspect_ratio) VALUES (?, ?)",
                  (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ear))
        conn.commit()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/status')
def status():
    global detection_thread, detection_running
    is_running = detection_thread and detection_thread.is_alive() and detection_running
    return jsonify({"status": "running" if is_running else "stopped"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
