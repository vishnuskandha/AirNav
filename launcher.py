import os
import subprocess
import sys
from pathlib import Path


# Resolve paths
here = Path(__file__).resolve().parent
project_root = here  # AirNav/
venv_python = project_root / ".venv" / "Scripts" / "python.exe"


def run_app(python_exe: str, app_path: Path) -> None:
    """Run the AirNav application and propagate application failures."""
    subprocess.run([python_exe, str(app_path)], check=True)


def main() -> int:
    """Launch AirNav and return a useful process exit status."""
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    print("=== AirNav Launcher ===\n")
    print("Launching Modern UI...")

    # Set environment variables to suppress MediaPipe/TFLite warnings.
    os.environ["GLOG_minloglevel"] = "3"
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    os.environ["ABSL_MIN_LOG_LEVEL"] = "2"

    try:
        run_app(python_exe, here / "modern_app.py")
    except subprocess.CalledProcessError as exc:
        print(f"Application exited with error: {exc}", file=sys.stderr)
        return exc.returncode or 1
    except KeyboardInterrupt:
        print("\nLauncher stopped.")
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
