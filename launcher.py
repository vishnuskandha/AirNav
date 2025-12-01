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
print("Launching Modern UI...")

# Set environment variables to suppress MediaPipe/TFLite warnings
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["ABSL_MIN_LOG_LEVEL"] = "2"

# Run the modern app with stderr suppressed
try:
    subprocess.run(
        [python_exe, str(here / "modern_app.py")],
        check=True,
        stderr=subprocess.DEVNULL  # Suppress all warnings
    )
except subprocess.CalledProcessError as e:
    print(f"Application exited with error: {e}")
except KeyboardInterrupt:
    print("\nLauncher stopped.")