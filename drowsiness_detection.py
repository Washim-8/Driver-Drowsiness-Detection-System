import cv2  # type: ignore
import imutils  # type: ignore
import datetime
import dlib  # type: ignore
import os
import numpy as np  # type: ignore
from playsound import playsound  # type: ignore
import sqlite3
import tkinter as tk
from tkinter import filedialog
import threading

# Global variables for GUI widgets (only used when running as main)
alarm_entry = None
screenshot_entry = None
root = None

# Global flag to control detection loop
stop_flag = threading.Event()

def stop_detection():
    """Signal the detection loop to stop"""
    global stop_flag
    stop_flag.set()


def start_detection(alarm_path=None, screenshot_folder=None, use_gui=False):
    global stop_flag
    stop_flag.clear()
    
    # Connect to SQLite database with proper path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drowsiness_data.db')
    conn = None
    vs = None
    
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        c = conn.cursor()

        # Create table if not exists
        c.execute('''CREATE TABLE IF NOT EXISTS drowsiness (
                     id INTEGER PRIMARY KEY,
                     timestamp DATETIME,
                     eye_aspect_ratio REAL
                     )''')
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        if conn:
            conn.close()
        return

    def eye_aspect_ratio(eye):
        # Compute the euclidean distances between the two sets of vertical eye landmarks (x, y)-coordinates
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])

        # Compute the euclidean distance between the horizontal eye landmark (x, y)-coordinates
        C = np.linalg.norm(eye[0] - eye[3])

        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        return ear

    def sound_alarm():
        path = alarm_path
        if use_gui and alarm_entry:
             path = alarm_entry.get()
        
        if path and os.path.exists(path):
            try:
                # Play sound in a separate thread to avoid blocking
                threading.Thread(target=lambda: playsound(path), daemon=True).start()
            except Exception as e:
                print(f"Error playing sound: {e}")
        elif path:
             print(f"Alarm file not found: {path}")
        else:
            print("No alarm path specified")

    # Function to capture screenshot with EAR value displayed
    def capture_screenshot(frame, ear):
        folder = screenshot_folder
        if use_gui and screenshot_entry:
            folder = screenshot_entry.get()
        
        if not folder:
            folder = os.path.join(os.getcwd(), "screenshots") # Default to screenshots directory

        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except:
                pass

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(folder, f"screenshot_{timestamp}.png")

        # Draw EAR value on the frame
        ear_text = f"EAR: {ear:.2f}"
        cv2.putText(frame, ear_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Save the frame with EAR value displayed
        cv2.imwrite(filename, frame)

    # Initialize video capture
    try:
        vs = cv2.VideoCapture(0)
        if not vs.isOpened():
            print("Error: Could not open webcam")
            if conn:
                conn.close()
            return
    except Exception as e:
        print(f"Error initializing camera: {e}")
        if conn:
            conn.close()
        return

    # Initialize dlib's face detector and predictor
    try:
        predictor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shape_predictor_68_face_landmarks.dat")
        if not os.path.exists(predictor_path):
            print(f"Error: Shape predictor file not found at {predictor_path}")
            vs.release()
            if conn:
                conn.close()
            return
        
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(predictor_path)
    except Exception as e:
        print(f"Error loading face detector: {e}")
        vs.release()
        if conn:
            conn.close()
        return

    # Set eye aspect ratio threshold
    EAR_THRESHOLD = 0.25

    # Initialize counters
    state = {'COUNTER': 0, 'ALARM_ON': False}

    def process_logic(frame):
        
        try:
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 0)

            for rect in rects:
                shape = predictor(gray, rect)
                shape_np = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)], dtype=int)

                left_eye = shape_np[42:48]
                right_eye = shape_np[36:42]

                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                ear = (left_ear + right_ear) / 2.0

                left_eye_hull = cv2.convexHull(left_eye)
                right_eye_hull = cv2.convexHull(right_eye)
                cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)

                if ear < EAR_THRESHOLD:
                    state['COUNTER'] += 1
                    if state['COUNTER'] >= 30:
                        if not state['ALARM_ON']:
                            state['ALARM_ON'] = True
                            sound_alarm()
                            capture_screenshot(frame, ear)
                        cv2.putText(frame, "DROWSINESS DETECTED!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        # Insert data into SQLite database
                        try:
                            assert conn is not None
                            assert c is not None
                            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            c.execute("INSERT INTO drowsiness (timestamp, eye_aspect_ratio) VALUES (?, ?)", (timestamp_str, ear))
                            conn.commit()
                        except Exception as db_error:
                            print(f"Database error: {db_error}")
                else:
                    state['COUNTER'] = 0
                    state['ALARM_ON'] = False

                cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        except Exception as e:
            print(f"Error processing frame: {e}")
        
        return frame

    try:
        if use_gui:
            # If using Tkinter, we need to adapt the loop to Tkinter's event loop
            def process_frame_tk():
                assert vs is not None
                assert conn is not None
                assert root is not None
                if stop_flag.is_set():
                    vs.release()
                    conn.close()
                    cv2.destroyAllWindows()
                    return
                
                ret, frame = vs.read()
                if not ret:
                    vs.release()
                    conn.close()
                    cv2.destroyAllWindows()
                    return

                frame = process_logic(frame)
                cv2.imshow("Drowsiness Detection", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    stop_flag.set()
                    vs.release()
                    conn.close()
                    cv2.destroyAllWindows()
                else:
                    root.after(10, process_frame_tk)
            
            process_frame_tk()
        
        else:
            # Standard loop for non-GUI (Flask) usage
            while not stop_flag.is_set():
                assert vs is not None
                ret, frame = vs.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                frame = process_logic(frame)
                cv2.imshow("Drowsiness Detection - Press 'q' to quit", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
    
    except Exception as e:
        print(f"Error during detection: {e}")
    finally:
        # Cleanup
        if vs:
            vs.release()
        if conn:
            conn.close()
        cv2.destroyAllWindows()
        print("Detection stopped and resources cleaned up")

def select_alarm_file():
    assert alarm_entry is not None
    alarm_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
    alarm_entry.delete(0, tk.END)
    alarm_entry.insert(0, alarm_path)

def select_screenshot_folder():
    assert screenshot_entry is not None
    output_folder = filedialog.askdirectory()
    screenshot_entry.delete(0, tk.END)
    screenshot_entry.insert(0, output_folder)

def main():
    global root, alarm_entry, screenshot_entry
    # Create main application window
    root = tk.Tk()
    root.title("Drowsiness Detection System")

    # Styling variables
    label_color = '#FFFFFF'
    input_bg = '#FFFFFF'
    input_fg = '#6A5ACD'
    button_bg = '#006699'
    button_fg = '#FFFFFF'

    # GUI elements for alarm and screenshot settings
    alarm_label = tk.Label(root, text="Select Alarm Sound:", bg='#333333', fg=label_color)
    alarm_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    alarm_entry = tk.Entry(root, width=40, bg=input_bg, fg=input_fg)
    alarm_entry.grid(row=0, column=1, padx=10, pady=10)

    alarm_button = tk.Button(root, text="Browse", bg=button_bg, fg=button_fg, command=select_alarm_file)
    alarm_button.grid(row=0, column=2, padx=10, pady=10)

    screenshot_label = tk.Label(root, text="Select Screenshot Folder:", bg='#333333', fg=label_color)
    screenshot_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

    screenshot_entry = tk.Entry(root, width=40, bg=input_bg, fg=input_fg)
    screenshot_entry.grid(row=1, column=1, padx=10, pady=10)

    screenshot_button = tk.Button(root, text="Browse", bg=button_bg, fg=button_fg, command=select_screenshot_folder)
    screenshot_button.grid(row=1, column=2, padx=10, pady=10)

    start_button = tk.Button(root, text="Start Detection", bg=button_bg, fg=button_fg, command=lambda: start_detection(use_gui=True))
    start_button.grid(row=2, column=1, padx=10, pady=20)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    main()
