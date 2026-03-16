<div align="center">

# 🚗 Driver Drowsiness Detection System

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?size=22&duration=3000&color=0F766E&center=true&vCenter=true&width=900&lines=AI-Based+Driver+Fatigue+Detection;Real-Time+Computer+Vision+System;EAR+Algorithm+for+Eye+Tracking;Flask+Dashboard+for+Monitoring" alt="Typing SVG" />
</p>

![Stars](https://img.shields.io/github/stars/Washim-8/Drowsiness_Detection?style=for-the-badge)
![Forks](https://img.shields.io/github/forks/Washim-8/Drowsiness_Detection?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-WebApp-black?style=for-the-badge&logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-ComputerVision-green?style=for-the-badge&logo=opencv)
![dlib](https://img.shields.io/badge/dlib-FacialLandmarks-red?style=for-the-badge)

</div>

---

## 📌 Overview

Driver fatigue is a silent yet significant contributor to road accidents worldwide. This project tackles that issue head-on by providing a real-time, AI-powered drowsiness detection system. Using computer vision and facial landmark mapping, the system continuously monitors the driver's eye movements. 

By analyzing the Eye Aspect Ratio (EAR), it accurately detects prolonged eye closures—an early indicator of microsleep or severe fatigue—and instantly triggers an audio-visual alarm to wake the driver, potentially saving lives.

---

## ✨ Features

- **🚗 Real-Time Monitoring:** Seamlessly tracks the driver's face via a live webcam feed.
- **👁 Precise Eye Tracking:** Utilizes a 68-point facial landmark model to accurately isolate eye regions.
- **⚡ EAR Algorithm:** Implements the mathematically robust Eye Aspect Ratio (EAR) for reliable blink and closure detection.
- **🔊 Instant Alerts:** Triggers a loud audio alarm the moment signs of drowsiness exceed a safe threshold.
- **📸 Automated Evidence Capture:** Automatically takes and stores a screenshot when an incident is detected.
- **🗄 Persistent Logging:** Records all drowsiness events into a lightweight SQLite database for later review.
- **🌐 Interactive Dashboard:** Features a clean Flask-based web UI to start, stop, and monitor the detection system effortlessly.
- **📊 Background Processing:** Runs heavy computer vision tasks in dedicated threads to keep the web interface responsive.

---

## 🛠 Tech Stack

- **Language:** Python
- **Backend:** Flask
- **Computer Vision:** OpenCV, dlib
- **Utilities:** imutils, numpy
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript
- **Audio:** playsound / threading

---

## 📂 Project Structure

```text
📦 Drowsiness_Detection
 ┣ 📜 app.py                                  # Main Flask web server and routing
 ┣ 📜 drowsiness_detection.py                 # Core computer vision and EAR logic
 ┣ 📜 requirements.txt                        # Project dependencies
 ┣ 📜 shape_predictor_68_face_landmarks.dat   # dlib facial landmark model
 ┣ 📜 sound1.mp3                              # Audio alarm file
 ┣ 📂 templates/                              # HTML templates for the dashboard UI
 ┣ 📂 static/                                 # CSS, JavaScript, and static assets
 ┣ 📂 screenshots/                            # Auto-generated directory for incident captures
 ┗ 📜 drowsiness_data.db                      # Auto-generated SQLite database for event logging
```

---

## ⚙️ How It Works

1. **Video Streaming:** The system accesses the local webcam to capture a continuous video feed.
2. **Face Detection:** Using dlib's robust HOG-based detector, it identifies the driver's face in the frame.
3. **Landmark Extraction:** The 68-point shape predictor maps out facial features, specifically isolating the coordinates for the left and right eyes.
4. **EAR Calculation:** The Eye Aspect Ratio is computed mathematically to measure how open or closed the eyes are.
5. **Threshold Monitoring:** If the EAR drops below the defined threshold (e.g., 0.25) for a consecutive number of frames, the system flags it as drowsiness.
6. **Action & Logging:** Once flagged, an alarm sounds, a screenshot is saved with the EAR value, and the event timestamp is logged into the database.

---

## ▶️ Installation & Setup

### Prerequisites
- Python 3.8+
- A working webcam

### Step-by-Step Guide

**1. Clone the repository**
```bash
git clone https://github.com/Washim-8/Drowsiness_Detection.git
cd Drowsiness_Detection
```

**2. Create and activate a virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Download the Landmark Model**
*Note: Ensure `shape_predictor_68_face_landmarks.dat` is placed in the root directory. If missing, download it from the official dlib repository.*

**5. Run the Application**
```bash
python app.py
```
*Open your browser and navigate to `http://127.0.0.1:5000` to access the dashboard.*

---

## 📸 Screenshots & Demo

*(To make the repository more engaging, consider adding the following visual assets here:)*

- **Dashboard UI:** A screenshot of the web interface.
- **Real-Time Detection:** An image showing the camera feed with the green eye contours.
- **Alert Trigger:** A screenshot showing the "DROWSINESS DETECTED!" warning and the EAR value.

### 🎥 Demo GIF Ideas
- A short clip showing the transition from normal driving to eye closure, followed by the alarm triggering.
- The interactive dashboard starting and stopping the background monitoring thread.

*Tools recommended for creating GIFs: [ScreenToGif](https://www.screentogif.com/) or OBS Studio.*

---

## 🚀 Future Improvements

- **Hardware Integration:** Deploy the system on edge devices like Raspberry Pi for in-vehicle usage.
- **Advanced Behavior Analysis:** Expand detection capabilities to recognize yawning, head tilting, and phone usage.
- **Deep Learning Upgrade:** Replace the EAR algorithm with a lightweight CNN (e.g., MobileNet) for improved accuracy in challenging lighting conditions.
- **Cloud Syncing:** Add an option to push incident logs and screenshots to an AWS S3 bucket for fleet management.
- **Mobile Companion App:** Develop a React Native app for real-time remote monitoring.

---

## 👨‍💻 About the Developer

Hi, I'm **Washim Shaikh**, an aspiring Software Engineer currently pursuing a degree in Computer Science Engineering. I am deeply passionate about blending software development with Artificial Intelligence to create systems that have a tangible, positive impact on society.

Over the years, I've honed my skills in **Python, Java, and Full-Stack Web Development**, but my true interest lies in AI/ML and intelligent automation. I enjoy the challenge of taking complex data and turning it into practical solutions. 

I've had the opportunity to build and contribute to various real-world systems, ranging from **AgriTrade** (a platform empowering farmers with fair auction mechanics) to intelligent **AI Chatbots** and secure **Fraud Detection Systems**. Whether it's analyzing financial data or deploying machine learning models, my focus is always on building robust, scalable, and user-centric applications.

Currently, I'm expanding my expertise in computer vision and cloud infrastructure to build the next generation of intelligent software.

---

## 📬 Contact

I'm always open to discussing tech, collaborating on interesting projects, or exploring new opportunities!

- 📧 **Email:** washimshaikh33@gmail.com
- 📱 **Phone:** +91 8884958185
- 💻 **GitHub:** [Washim-8](https://github.com/Washim-8)
- 🔗 **LinkedIn:** [Washim Shaikh](https://www.linkedin.com/in/washim-shaikh-349868281/)

*Feel free to connect for collaborations or opportunities.*

---

<div align="center">

### 📊 GitHub Stats

<img src="https://github-readme-stats.vercel.app/api?username=Washim-8&show_icons=true&theme=radical" alt="Washim's GitHub Stats" />
<img src="https://github-readme-streak-stats.herokuapp.com/?user=Washim-8&theme=radical" alt="Washim's GitHub Streak" />

<br><br>

✨ *Built to enhance road safety using real-time AI and computer vision.*

</div>