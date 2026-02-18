
# AirNav

## v2 (Windows 11 + MediaPipe Tasks)

This version of AirNav has been updated to:
- Use MediaPipe Tasks HandLandmarker instead of the deprecated `mp.solutions.hands` API
- Pin dependency versions in `requirements.txt` for reproducible installs
- Prefer a local `.venv` with Python 3.11 via `start.ps1`
- Use a local model file: `models/hand_landmarker.task`

For most Windows 11 users, the recommended way to start is:
```powershell
./start.ps1
```
(or double-click `start.bat`).

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.md)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/vishnuskandha/AirNav)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-red.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-orange.svg)](https://mediapipe.dev/)

**Hands-Free PC Control** — Control your computer using simple hand gestures captured by your webcam.

![AirNav Demo](./assetsgif/demo_gif.gif)

AirNav provides webcam-based hand-gesture mouse control for hands-free computer operation. Use intuitive hand gestures to move your cursor, click, and interact with your PC.

Table of Contents
- Features
- Quick Start
- Installation
- Usage
- Configuration
- Gesture reference
- Troubleshooting
- Contributing
- License & Contact

---

## Features

- Real-time hand-tracking for precise cursor movement
- Gesture-driven left/right click, double-click and drag-and-drop
- Works with any standard webcam
- No microphone or audio input required
- Lightweight — designed for low latency and simple configuration

---

## Quick Start

**The easiest way to start AirNav:**

**Option 1: PowerShell (Recommended for best visuals)**
```powershell
.\start.ps1
```
- Beautiful ANSI Shadow ASCII art with colors
- Proper UTF-8 character display
- Enhanced visual experience

**Option 2: Batch File (Maximum compatibility)**
```cmd
start.bat
```
- Or double-click `start.bat` in Windows Explorer
- Works in all terminals

Both launchers will:
- Check and install dependencies automatically
- Launch the modern PiP window interface with gesture control

**Manual start (alternative):**

```powershell
python modern_app.py
```

The modern app shows a floating Picture-in-Picture window with real-time gesture control.

---

## Installation

### Prerequisites

- **Python 3.7+** ([download](https://www.python.org/downloads/))
- **Webcam** (built-in or external USB camera)
- **Windows 10/11** (or Linux/macOS with Python + pip)

### Step 1: Clone the repository

```powershell
git clone https://github.com/vishnuskandha/AirNav.git
cd AirNav
```

### Step 2: Create a Python virtual environment (recommended)

A virtual environment isolates dependencies and prevents conflicts with other Python projects.

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### Step 3: Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Dependency Installation Guide

**Core dependencies** (always required):
- `opencv-python` — for webcam input and face/hand detection
- `mediapipe` — for hand gesture recognition
- `numpy` — for numerical computations
- `pynput` — for mouse/keyboard control

**Face recognition** (optional, recommended):
- `face-recognition` — for facial authentication
- `dlib` — face detection algorithm (comes as pre-built binary on Windows)

### Troubleshooting Installation

**Issue: `dlib` build fails on Windows**

**Solution 1: Use pre-built dlib-binary** (recommended)
```powershell
pip install dlib-binary face-recognition
```

**Solution 2: Install Visual C++ Build Tools** (if you prefer building dlib)
1. Download: https://visualstudio.microsoft.com/downloads/
2. Choose **Desktop development with C++** option
3. Restart your terminal
4. Run: `pip install -r requirements.txt`

**Solution 3: Skip face recognition** (system falls back to simple detection)
- Comment out `face-recognition` line in `requirements.txt`
- Face unlock will use OpenCV Haar Cascade (less accurate but works)

**Issue: `pip install` is slow or times out**

```powershell
# Use a faster package index
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

**Issue: Permission denied (Linux/macOS)**

```bash
# Use --user flag
pip install --user -r requirements.txt
```

### Verify Installation

Test that dependencies are installed correctly:

```powershell
python -c "import cv2, mediapipe, numpy, pynput; print('✓ All core dependencies installed')"
```

If this runs without errors, you're ready to proceed.

---

## Usage

### Quick Start (After Installation)

1. **Enroll your face** (one-time setup):
   ```powershell
   python enroll_face.py
   ```
   - Enter your name (or press Enter for default)
   - Position face in front of webcam
   - Press **SPACE** to capture
   - Your face will be saved to `known_faces.pkl`

2. **Launch the app**:
   ```powershell
   python launcher.py
   ```
   - You'll see a face unlock window (authenticate with your face)
   - After unlocking, the gesture control window will open
   - Move your hand to control the cursor

3. **Stop the app**:
   - Focus the terminal window and press **`Ctrl+C`**

### Running Multiple Times

- **First-time users**: Run `enroll_face.py` once, then always use `launcher.py`
- **Subsequent launches**: Just run `launcher.py` (no re-enrollment needed)
- **New users**: Run `enroll_face.py` again with a different name (multiple faces are supported)

### Add More Users

```powershell
python enroll_face.py
```

Repeat this for each person. All enrolled faces will be recognized by the launcher.

### Tips

- Ensure good lighting when enrolling and unlocking (shadows affect recognition)
- If authentication fails repeatedly, try re-enrolling with better lighting
- On Windows, you may need to run as Administrator for full mouse control
- The app is lightweight (~50-100MB memory during execution)

---

## Configuration

Tuning is done by editing the Python files.

**`face_unlock.py`**
- `UNLOCK_THRESHOLD`: Face matching sensitivity (0.6 default; lower = stricter)
- `CAMERA_INDEX`: Which camera to use (0 = default)

**`mouse_gestures.py`**
- `SCREEN_WIDTH`, `SCREEN_HEIGHT`: your monitor resolution
- `SMOOTHING`: cursor smoothing factor (higher = smoother, slower)
- `LEFT_CLICK_THRESHOLD`, `RIGHT_CLICK_THRESHOLD`: pinch sensitivity
- `DRAG_HOLD_TIME`: seconds holding pinch before drag starts

Adjust values and restart the app to apply.

---

## First-Time Setup Checklist

Follow this checklist after cloning the repo:

- [ ] **Python installed** — verify with `python --version` (3.7+)
- [ ] **Git clone downloaded** — repo files are on your machine
- [ ] **Virtual environment created** — `python -m venv venv` + activation
- [ ] **Dependencies installed** — `pip install -r requirements.txt` (no errors)
- [ ] **Webcam working** — test with Windows Camera or other app
- [ ] **Face enrolled** — `python enroll_face.py` completed, `known_faces.pkl` created
- [ ] **Launcher runs** — `python launcher.py` starts without crashing
- [ ] **Face unlocks** — you can see your face detected and authenticated
- [ ] **Gesture controls active** — hand landmarks are visible in the window

**All checked?** You're ready to use AirNav! 🎉

---

## Face Unlock Setup

### First-time enrollment

1. Run the enrollment script:
   ```powershell
   python enroll_face.py
   ```

2. Enter your name when prompted (or press Enter for default "User")

3. Position your face in the camera frame

4. Press **SPACE** to capture your face (ESC to cancel)

5. Your face encoding will be saved to `known_faces.pkl`

### Adding multiple users

Run `enroll_face.py` multiple times with different names. All enrolled faces will be recognized.

### Re-enrolling

Delete `known_faces.pkl` and run `enroll_face.py` again to start fresh.

---

## Gesture reference

- Left hand: move the index finger to move the cursor
- Right hand: pinch thumb+index for left-click, thumb+middle for right-click
- Hold pinch (about 1 second) to start drag; release to drop

---

## Troubleshooting

### Installation Issues

| Issue | Solution |
|-------|----------|
| `pip: command not found` | Python not installed or not in PATH. [Download Python](https://www.python.org/downloads/) and check "Add Python to PATH" during installation |
| `dlib build error` | Run `pip install dlib-binary` instead of building from source |
| `ModuleNotFoundError: No module named 'cv2'` | Activate virtual environment: `.\venv\Scripts\Activate.ps1`, then run `pip install -r requirements.txt` |
| `Permission denied` | Run terminal as Administrator (Windows) or use `pip install --user` (Linux/macOS) |

### Runtime Issues

| Issue | Solution |
|-------|----------|
| **No webcam detected** | Check camera is connected + not used by other apps (Discord, Zoom, etc.) |
| **Face unlock window closes immediately** | `known_faces.pkl` missing. Run `python enroll_face.py` first |
| **Authentication fails with correct face** | Lighting issue. Try re-enrolling in brighter environment. Or increase `UNLOCK_THRESHOLD` in `face_unlock.py` |
| **Slow performance / lag** | Close other apps, reduce `SMOOTHING` value in `mouse_gestures.py`, or use a faster computer |
| **Cursor jitter** | Increase `SMOOTHING` value in `mouse_gestures.py` (default 0.3 → try 0.5) |
| **Clicks not registering** | Adjust `LEFT_CLICK_THRESHOLD` and `RIGHT_CLICK_THRESHOLD` in `mouse_gestures.py` |
| **Console shows many warnings** | Normal on first run. Warnings are suppressed after initialization. |

### Platform-Specific Issues

**Windows:**
- If mouse control doesn't work: Run terminal as Administrator
- If `pynput` fails: Install from: `pip install pynput==1.7.6`

**Linux:**
- If camera doesn't work: `sudo apt install python3-dev` (for dependencies)
- Face recognition: `sudo apt install libopenblas-dev liblapack-dev libblas-dev gfortran`

**macOS:**
- If Homebrew is installed: `brew install openblas lapack blas gfortran`
- Face recognition: May require Xcode Command Line Tools

### Getting Help

If issues persist:
1. Check that webcam works in other apps (Windows Camera, OBS, etc.)
2. Verify Python version: `python --version` (should be 3.7+)
3. Verify dependencies: `pip list | findstr /E "(opencv|mediapipe|numpy|pynput|face-recognition)"`
4. Check `known_faces.pkl` exists: `ls known_faces.pkl` (if missing, run `enroll_face.py`)
5. Open an issue on GitHub with:
   - Python version
   - OS (Windows 10/11, Ubuntu 20.04, etc.)
   - Error message/traceback
   - Steps to reproduce

---

## Contributing

Contributions are welcome. For small fixes, open a PR. For larger features, open an issue first to discuss the design.

Please respect the license included in the repository.

---

## License & Contact

© 2025 VishnuSkandha

This project is provided for personal and educational use. See `LICENSE.md` for details.

Contact: @vishnuskandha

---

If you'd like a different tone (shorter, more tutorial-like, or a landing-page style README), tell me which style and I will adapt the structure and wording.
