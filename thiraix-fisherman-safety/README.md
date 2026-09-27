# THIRAIX - Fisherman Safety & Maritime Boundary Alert System
**Intelligence Beyond the Waves**

---

## 📌 VS Code Quick Start Guide

### Option 1: Run with Python Server (Recommended)
1. Extract the `thiraix-fisherman-safety.zip` file.
2. Open the extracted folder in **Visual Studio Code** (`File` -> `Open Folder...`).
3. Open the integrated terminal in VS Code (`Ctrl + ~`) or press `F5`.
4. Run the Python backend server:
   ```bash
   python app.py
   ```
5. Open your web browser and navigate to:
   ```text
   http://localhost:8080
   ```
6. Alternatively, on Windows, just double-click **`run.bat`**!

---

### Option 2: Run with VS Code Live Server Extension
1. Install the **Live Server** extension by Ritwick Dey in VS Code.
2. Right-click on `index.html`.
3. Click **"Open with Live Server"**.
4. The prototype opens automatically at `http://127.0.0.1:5500/index.html`.

---

## 🚀 Key Prototype Features
1. **Realistic Smartphone Interface**: iPhone 16 Pro styling with titanium frame, Dynamic Island, and hardware SOS Action button.
2. **5-Second Maritime Boundary Alert & Siren**: Web Audio API dual-tone siren (850Hz-1250Hz), visual flashing strobe, and 5-second countdown timer.
3. **10 Indian Languages**: Tamil, English, Hindi, Telugu, Kannada, Malayalam, Bengali, Odia, Punjabi, Urdu with Text-to-Speech (TTS).
4. **Live Ocean Wave & Weather Canvas**: Dynamic undulating waves, rainfall particles, and Beaufort wind gauge.
5. **AI Risk Prediction Engine**: Multi-factor ML scoring (Low, Medium, High) with safe return route guidance.
6. **Zero-Internet LoRa / Satellite Failover**: Offline 868MHz RF binary packet broadcaster for deep-sea operations.
7. **Coast Guard Rescue Command Dashboard**: Live Palk Strait fleet radar tracking 14 vessels with 1-click rescue interceptor dispatch.

---

## 📂 Project File Structure
```text
thiraix-fisherman-safety/
├── index.html              # Frontend Prototype & Coast Guard Dashboard
├── app.py                  # Fullstack Python Web & REST API Server
├── backend_simulation.py   # AI Risk Prediction, Geofencing & LoRa Engine
├── run.bat                 # Windows 1-Click Server Launcher
├── requirements.txt        # Optional Python Dependencies
├── README.md               # User & Evaluator Documentation
└── .vscode/
    └── launch.json         # VS Code F5 Run/Debug Configuration
```

---

## 🚢 Ready for Cloud Deployment
- **Frontend**: Can be deployed to GitHub Pages, Netlify, Vercel, or Firebase Hosting by deploying `index.html`.
- **Backend**: Can be deployed to Render, Railway, AWS EC2, or Google Cloud Run using `python app.py` or FastAPI.
