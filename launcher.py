import subprocess
import sys
import os
from pathlib import Path

# Resolve paths
here = Path(__file__).resolve().parent
project_root = here.parent  # AirNav/
venv_python = project_root / ".venv" / "Scripts" / "python.exe"

# Prefer the project's venv Python if it exists; fall back to current python
python_exe = str(venv_python) if venv_python.exists() else sys.executable

print("=== AirNav Launcher ===\n")

# Step 1: Face authentication
print("Step 1: Face Authentication")
try:
    from face_unlock import FaceUnlock
    
    unlock = FaceUnlock()
    if not unlock.authenticate(timeout=30):
        print("\n[DENIED] Authentication failed. Access denied.")
        sys.exit(1)
    
    print("\n[OK] Authentication successful!\n")
except ImportError as e:
    print(f"Warning: Face recognition not available ({e})")
    print("Skipping authentication...\n")
except Exception as e:
    print(f"Error during authentication: {e}")
    sys.exit(1)

# Step 2: Start gesture controls
print("Step 2: Starting gesture controls...")

# Suppress stderr/stdout from mouse_gestures subprocess (MediaPipe warnings)
with open(os.devnull, 'w') as devnull:
    subprocess.Popen(
        [python_exe, str(here / "mouse_gestures.py")],
        stdout=devnull,
        stderr=devnull
    )

print("Gesture module started. Use your hands to control the mouse.")