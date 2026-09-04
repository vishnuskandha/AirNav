import subprocess
from pathlib import Path
from unittest.mock import patch

import launcher


def test_run_app_propagates_process_failures() -> None:
    app_path = Path("modern_app.py")

    with patch("launcher.subprocess.run", side_effect=subprocess.CalledProcessError(7, ["python", str(app_path)])):
        try:
            launcher.run_app("python", app_path)
        except subprocess.CalledProcessError as exc:
            assert exc.returncode == 7
        else:
            raise AssertionError("run_app must propagate application failures")


def test_main_returns_application_exit_code() -> None:
    missing_venv = Path(".missing-venv-python.exe")

    with patch("launcher.venv_python", missing_venv), patch(
        "launcher.run_app",
        side_effect=subprocess.CalledProcessError(9, ["python", "modern_app.py"]),
    ):
        assert launcher.main() == 9


def test_main_returns_interrupt_code() -> None:
    missing_venv = Path(".missing-venv-python.exe")

    with patch("launcher.venv_python", missing_venv), patch(
        "launcher.run_app", side_effect=KeyboardInterrupt
    ):
        assert launcher.main() == 130
