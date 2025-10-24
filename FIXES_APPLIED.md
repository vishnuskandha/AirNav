# AirNav Fixes Applied (Oct 25, 2025)

## Problem: Persistent MediaPipe Warnings & Unicode Encoding Errors

### Issue 1: MediaPipe/TFLite Verbose Warnings
**Problem:** Console was flooded with warnings like:
```
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
W0000 00:00:1761331334.742436    6072 inference_feedback_manager.cc:114] ...
```

**Root Cause:** MediaPipe's C++ backend writes directly to OS-level stderr, bypassing Python's `sys.stderr` redirection.

**Solution:** Suppress stderr at the subprocess level in `launcher.py` when spawning `mouse_gestures.py`:
```python
with open(subprocess.DEVNULL, 'w') as devnull:
    subprocess.Popen(
        [python_exe, str(here / "mouse_gestures.py")],
        stdout=devnull,
        stderr=devnull
    )
```

**Result:** ✅ All MediaPipe warnings suppressed; clean console output

---

### Issue 2: Unicode Character Encoding Errors
**Problem:** Console charset mismatch when printing emoji/Unicode characters:
```
Error: 'charmap' codec can't encode character '\u26a0' in position 0: character maps to undefined
```

**Root Cause:** Windows console (especially PowerShell) has limited character encoding; emoji and special Unicode symbols like `⚠`, `✓`, `🔓`, `🔒` fail to display.

**Solution:** Replace all Unicode symbols with ASCII-safe alternatives:

| Before | After | Context |
|--------|-------|---------|
| `⚠` | `[!]` | Warning messages |
| `✓` | `[OK]` | Success messages |
| `✗` | `[ERROR]` | Failure messages |
| `🔓` | `[OK]` | Access granted |
| `🔒` | `[DENIED]` | Access denied |
| `⏱` | `[TIMEOUT]` | Timeout warning |

**Files Modified:**
- `launcher.py` — Unicode lock/unlock symbols → `[OK]` / `[DENIED]`
- `face_unlock.py` — Warning, success, authentication, and timeout symbols
- `enroll_face.py` — Enrollment success/failure symbols

**Result:** ✅ No encoding errors; console output displays cleanly on Windows

---

## Files Changed

### 1. `launcher.py`
- Added `subprocess.DEVNULL` redirection for `mouse_gestures.py` subprocess
- Replaced emoji with ASCII alternatives (`🔓` → `[OK]`, `🔒` → `[DENIED]`)

### 2. `mouse_gestures.py`
- Cleaned up stderr redirection code (now delegated to launcher subprocess suppression)
- Kept environment variable setup for robustness:
  - `GLOG_minloglevel=3` (suppress all glog messages)
  - `TF_CPP_MIN_LOG_LEVEL=3` (suppress TensorFlow C++ logs)
  - `TF_FORCE_GPU_ALLOW_GROWTH=true` (prevent GPU memory issues)
  - `ABSL_MIN_LOG_LEVEL=2` (suppress absl logs)

### 3. `face_unlock.py`
- Replaced `⚠` with `[!]` (warning indicator)
- Replaced `✓` with `[OK]` (success indicator)
- Replaced `⏱` with `[TIMEOUT]` (timeout indicator)
- Replaced `🔓` with `[OK]` and `🔒` with `[DENIED]` (access status)

### 4. `enroll_face.py`
- Replaced `✓` with `[OK]` (enrollment success)
- Replaced `✗` with `[ERROR]` (enrollment failure)

### 5. `requirements.txt`
- Added comprehensive comments explaining dependencies and fallback options
- Documented dlib build issue solutions (3 alternatives)
- Organized into Core, Optional, and Face Recognition sections

### 6. `README.md`
- Expanded Installation section with step-by-step beginner guide
- Added platform-specific instructions (Windows PowerShell/CMD, Linux, macOS)
- Added dependency installation troubleshooting (3 solutions for common issues)
- Expanded Troubleshooting with Installation and Runtime issues tables
- Added First-Time Setup Checklist
- Updated Usage section with clear first-time vs. subsequent launch instructions
- Added Tips and platform-specific guidance

---

## Testing & Verification

### Before Fixes:
```
PS> python launcher.py
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
W0000 00:00:1761331334.742436    6072 inference_feedback_manager.cc:114] ...
[ENCODING ERROR] 'charmap' codec can't encode character '\u26a0'
```
❌ Warnings flood output; Unicode errors crash the program; console stuck (hard to return to prompt)

### After Fixes:
```
PS> python launcher.py
=== AirNav Launcher ===

Step 1: Face Authentication
face_recognition library loaded but dlib backend not functional.
Loaded 1 known face(s)

=== Face Unlock ===
Show your face to the camera to unlock.
Timeout: 30 seconds

[!] Using simple face detection mode

[OK] Authenticated as 'vishnu' (confidence: 75.00%)

[OK] Authentication successful!

Step 2: Starting gesture controls...
Gesture module started. Use your hands to control the mouse.
^C
```
✅ Clean output; no warnings; no encoding errors; Ctrl+C returns to prompt cleanly

---

## How It Works

### Suppression Strategy (Layered Approach)

1. **Python-level controls** (`mouse_gestures.py`):
   - Set environment variables `GLOG_minloglevel=3`, `TF_CPP_MIN_LOG_LEVEL=3` (before importing mediapipe)
   - Redirect `sys.stderr` and `sys.stdout` to suppress Python-level logs

2. **OS-level controls** (`launcher.py`):
   - Spawn `mouse_gestures.py` as subprocess with `stdout=DEVNULL, stderr=DEVNULL`
   - This catches C++ library output that bypasses Python's `sys.stderr`

3. **Character encoding** (All files):
   - Use ASCII-only characters for all console output
   - Replace Unicode symbols with `[TAG]` style indicators

### Why Subprocess Suppression is Necessary

MediaPipe's C++ backend (XNNPACK delegate, TFLite inference) writes directly to the OS file descriptors (fd 1=stdout, fd 2=stderr), not to Python's `sys.stderr` object. Only subprocess-level suppression can catch this output.

---

## Result Summary

✅ **Clean Console Output** — No MediaPipe/TFLite/absl warnings  
✅ **No Encoding Errors** — All text displays correctly on Windows  
✅ **Easy Exit** — Ctrl+C cleanly returns to command prompt  
✅ **Professional Appearance** — Clean, readable output without clutter  
✅ **Beginner-Friendly Documentation** — README updated with comprehensive setup guide  

The AirNav application now provides a smooth, clean user experience with proper setup documentation.
