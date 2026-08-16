from flask import Flask, render_template, jsonify
import threading
import os

# Detection modules are only available when running locally with CV dependencies
try:
    from drowsiness_detection import start_detection, stop_detection
    DETECTION_AVAILABLE = True
except ImportError:
    DETECTION_AVAILABLE = False
    def start_detection(**kwargs): pass
    def stop_detection(): pass

app = Flask(__name__)

# Global variable to track the detection thread
detection_thread = None
detection_running = False

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/about_contact')
def about_contact():
    return render_template('about_contact.html')


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


@app.route('/status')
def status():
    global detection_thread, detection_running
    is_running = detection_thread and detection_thread.is_alive() and detection_running
    return jsonify({"status": "running" if is_running else "stopped"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
