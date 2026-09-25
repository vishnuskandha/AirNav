<div align="center">

# AirNav

</div>


<!-- README polish: repository metadata badges -->
<p>
  <a href="https://github.com/vishnuskandha/AirNav"><img alt="GitHub stars" src="https://img.shields.io/github/stars/vishnuskandha/AirNav?style=for-the-badge&logo=github&label=Stars"></a>
  <a href="https://github.com/vishnuskandha/AirNav/fork"><img alt="GitHub forks" src="https://img.shields.io/github/forks/vishnuskandha/AirNav?style=for-the-badge&logo=github&label=Forks"></a>
  <a href="https://github.com/vishnuskandha/AirNav/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/vishnuskandha/AirNav?style=for-the-badge&logo=github&label=Issues"></a>
  <a href="https://github.com/vishnuskandha/AirNav/commits"><img alt="Last commit" src="https://img.shields.io/github/last-commit/vishnuskandha/AirNav?style=for-the-badge&logo=git&label=Updated"></a>
</p>
<!-- End README polish -->

[![CI](https://github.com/vishnuskandha/AirNav/actions/workflows/ci.yml/badge.svg)](https://github.com/vishnuskandha/AirNav/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.md)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/vishnuskandha/AirNav)

Hands-free PC control: move your cursor, click, double-click, and drag using
hand gestures captured by your webcam. AirNav uses MediaPipe Tasks
HandLandmarker for hand tracking and a frameless picture-in-picture overlay
built with PyQt5.

## Features

- Real-time hand tracking with MediaPipe Tasks (HandLandmarker, VIDEO mode).
- Cursor movement via the left hand's index finger, with smoothing.
- Right-hand gestures: pinch thumb+index for left-click, thumb+middle for
  right-click, quick double-pinch for double-click, and pinch-and-hold to
  drag-and-drop.
- Floating, frameless picture-in-picture window that stays on top.
- Four preset sizes plus freeform edge resizing; double-click to cycle sizes.
- Suppresses MediaPipe/TFLite noise so the console stays clean.
- One-click launchers (`start.bat` / `start.ps1`) that set up Python 3.11,
  a virtual environment, dependencies, and the hand landmark model
  automatically.

## Architecture

```
+---------------------+      +------------------------+      +----------+
|  Webcam (1280x720)  | -->  |  modern_app.py         |      |          |
|  OpenCV capture     |      |  PyQt5 PiP overlay     | -->  |  Mouse   |
+---------------------+      |  (FloatingWindow)      |      |  events  |
                             +------------------------+      +----------+
                                       | process_frame
                                       v
                             +------------------------+
                             |  gesture_engine.py     |
                             |  GestureEngine         |
                             |  - MediaPipe Tasks     |
                             |  - left/right hand     |
                             |  - pinch detection     |
                             +------------------------+
                                       |
                                       v
                             +------------------------+
                             |  pynput Controller     |
                             |  move / click / drag   |
                             +------------------------+
```

`launcher.py` resolves the project's Python (preferring a local `.venv`) and
starts `modern_app.py`. `start.ps1` orchestrates the whole setup (Python,
venv, dependencies, model download) and then launches the app; `start.bat` is
a compatibility wrapper that invokes `start.ps1`.

## Quickstart

### Windows

```powershell
.\start.ps1
```

or double-click `start.bat`. The launcher finds or installs Python 3.11,
creates `.venv`, installs `requirements.txt`, downloads the hand landmark
model into `models/` if missing, and starts the app.

### Manual setup (any OS)

```bash
git clone https://github.com/vishnuskandha/AirNav.git
cd AirNav
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
python modern_app.py
```

Requirements: Python 3.9+ (3.11 recommended), a working webcam, and
`models/hand_landmarker.task` in the `models/` folder (the launcher
downloads it automatically).

## Gestures

| Gesture | Action |
| --- | --- |
| Left hand, index finger | Move the cursor |
| Right hand, pinch thumb + index (quick) | Left-click |
| Right hand, quick double pinch | Double-click |
| Right hand, pinch thumb + index (hold ~0.8 s) | Start drag; release to drop |
| Right hand, pinch thumb + middle | Right-click |

In the PiP window: drag with the mouse to move it, pull an edge to resize,
right-click for the context menu, double-click to cycle preset sizes. Stop the
app with `Ctrl+C` in the terminal.

## Configuration

Tuning is done in `gesture_engine.py`:

- `SMOOTHING` — cursor smoothing factor (higher = smoother, slower).
- `LEFT_CLICK_THRESHOLD`, `RIGHT_CLICK_THRESHOLD` — pinch sensitivity.
- `DRAG_HOLD_TIME` — seconds to hold a pinch before a drag starts.
- `click_delay` — double-click timing window.
- `DPI_FACTOR` — cursor speed multiplier.

Preset window sizes live in `modern_app.py` (`SIZES`).

## Repository layout

```
modern_app.py          PyQt5 picture-in-picture overlay + video thread
gesture_engine.py      Hand tracking, gesture detection, mouse control
launcher.py            Lightweight entrypoint that starts modern_app.py
start.ps1              One-click launcher (Python 3.11 + venv + setup)
start.bat              Batch wrapper for start.ps1
models/hand_landmarker.task   MediaPipe hand landmark model (auto-downloaded)
requirements.txt       Pinned Python dependencies
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
development setup, code style, and testing checklist.

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT License. See [LICENSE.md](LICENSE.md). Copyright (c) 2025 Vishnu Skandha.
