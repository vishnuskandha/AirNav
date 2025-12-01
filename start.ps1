# ========================================
# AirNav - PowerShell Launcher
# ========================================
# This PowerShell script handles UTF-8 characters properly
# and displays the ANSI Shadow ASCII art correctly
# ========================================

# Set console to UTF-8 for proper character display
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "AirNav Launcher"

# Clear screen
Clear-Host

# ANSI Shadow ASCII Art for AIRNAV (Base64 encoded to avoid encoding issues)
$BannerBase64 = "CiDilojilojilojilojilojilZcg4paI4paI4pWX4paI4paI4paI4paI4paI4paI4pWXIOKWiOKWiOKWiOKVlyAgIOKWiOKWiOKVlyDilojilojilojilojilojilZcg4paI4paI4pWXICAg4paI4paI4pWXCuKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVkeKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKWiOKWiOKVlyAg4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWX4paI4paI4pWRICAg4paI4paI4pWRCuKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVkeKWiOKWiOKVkeKWiOKWiOKWiOKWiOKWiOKWiOKVlOKVneKWiOKWiOKVlOKWiOKWiOKVlyDilojilojilZHilojilojilojilojilojilojilojilZHilojilojilZEgICDilojilojilZEK4paI4paI4pWU4pWQ4pWQ4paI4paI4pWR4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWX4paI4paI4pWR4pWa4paI4paI4pWX4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWR4pWa4paI4paI4pWXIOKWiOKWiOKVlOKVnQrilojilojilZEgIOKWiOKWiOKVkeKWiOKWiOKVkeKWiOKWiOKVkSAg4paI4paI4pWR4paI4paI4pWRIOKVmuKWiOKWiOKWiOKWiOKVkeKWiOKWiOKVkSAg4paI4paI4pWRIOKVmuKWiOKWiOKWiOKWiOKVlOKVnSAK4pWa4pWQ4pWdICDilZrilZDilZ3ilZrilZDilZ3ilZrilZDilZ0gIOKVmuKVkOKVneKVmuKVkOKVnSAg4pWa4pWQ4pWQ4pWQ4pWd4pWa4pWQ4pWdICDilZrilZDilZ0gIOKVmuKVkOKVkOKVkOKVnSAK"

# Decode Base64 to string
$BannerBytes = [System.Convert]::FromBase64String($BannerBase64)
$Banner = [System.Text.Encoding]::UTF8.GetString($BannerBytes)

Write-Host ""
Write-Host ""

# Display each line with character-by-character coloring using integer values
# This avoids "Unexpected token" errors from special characters in the script code
foreach ($line in $Banner -split "`n") {
    Write-Host "           " -NoNewline
    foreach ($char in $line.ToCharArray()) {
        $val = [int]$char
        
        # Solid block characters (█ = 9608) in Red
        if ($val -eq 9608) {
            Write-Host $char -ForegroundColor Red -NoNewline
        }
        # Box-drawing characters (Range 9550-9580 approx) in Cyan
        elseif ($val -ge 9550 -and $val -le 9580) {
            Write-Host $char -ForegroundColor Cyan -NoNewline
        }
        # Regular characters (spaces, newlines)
        else {
            Write-Host $char -ForegroundColor DarkGray -NoNewline
        }
    }
    Write-Host ""
}

Write-Host ""
Write-Host "              Face Recognition + Hand Gesture Control System" -ForegroundColor Yellow
Write-Host ""
Write-Host ""

# ========================================
# Check if Python is installed
# ========================================
try {
    $pyVer = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "[OK] $pyVer found" -ForegroundColor Green
    
    # Check for Python 3.13 incompatibility - HARD BLOCK
    if ($pyVer -match "3\.13") {
        Write-Host ""
        Write-Host "[ERROR] Python 3.13 is NOT COMPATIBLE with AirNav!" -ForegroundColor Red
        Write-Host ""
        Write-Host "MediaPipe (required for hand gestures) does not support Python 3.13." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "SOLUTION:" -ForegroundColor Cyan
        Write-Host "1. Download and install Python 3.10 or 3.11" -ForegroundColor White
        Write-Host "   Python 3.10: https://www.python.org/downloads/release/python-31011/" -ForegroundColor White
        Write-Host "   Python 3.11: https://www.python.org/downloads/release/python-3119/" -ForegroundColor White
        Write-Host ""
        Write-Host "2. During installation, check 'Add Python to PATH'" -ForegroundColor White
        Write-Host ""
        Write-Host "3. After installation, run this script again" -ForegroundColor White
        Write-Host ""
        Write-Host "NOTE: You can have multiple Python versions installed." -ForegroundColor Cyan
        Write-Host "To use Python 3.10/3.11 specifically, you can run:" -ForegroundColor Cyan
        Write-Host "  py -3.10 -m pip install -r requirements.txt" -ForegroundColor Gray
        Write-Host "  py -3.10 modern_app.py" -ForegroundColor Gray
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
}
catch {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10 or 3.11 from:"
    Write-Host "https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    Read-Host "Press Enter to exit"
    exit 1
}

# ========================================
# Validate required files exist
# ========================================
$requiredFiles = @("requirements.txt", "modern_app.py", "enroll_face.py")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "[ERROR] $file not found!" -ForegroundColor Red
        Write-Host "Please ensure you are running this from the AirNav directory."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ========================================
# Check for virtual environment
# ========================================
$venvPath = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "[INFO] Virtual environment detected" -ForegroundColor Cyan
    Write-Host "Activating virtual environment..."
    try {
        & $venvPath
        Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
    }
    catch {
        Write-Host "[WARNING] Failed to activate virtual environment" -ForegroundColor Yellow
        Write-Host "Using system Python instead..."
    }
    Write-Host ""
}
else {
    Write-Host "[INFO] No virtual environment found, using system Python" -ForegroundColor Cyan
    Write-Host ""
}

# ========================================
# Check if dependencies are installed
# ========================================
Write-Host "Checking dependencies..."
try {
    python -c "import cv2, mediapipe, numpy, pynput" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "[OK] All dependencies are installed" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "[WARNING] Some dependencies are missing!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installing required packages..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
        Write-Host "Please run manually: pip install -r requirements.txt"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# ========================================
# Check if face is enrolled
# ========================================
if (-not (Test-Path "known_faces.pkl")) {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "   FIRST-TIME SETUP" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "No enrolled faces found."
    Write-Host "You need to enroll your face before using AirNav."
    Write-Host ""
    Write-Host "Instructions:"
    Write-Host "1. Position your face in front of the camera"
    Write-Host "2. Press SPACE to capture"
    Write-Host "3. ESC to cancel"
    Write-Host ""
    Write-Host "Starting face enrollment..."
    Write-Host ""
    
    python enroll_face.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Face enrollment failed or cancelled." -ForegroundColor Red
        Write-Host "Please try again."
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    Write-Host "[OK] Face enrolled successfully!" -ForegroundColor Green
    Write-Host ""
}

# ========================================
# Launch the application
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   STARTING AIRNAV" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launching modern UI with PiP window..."
Write-Host ""
Write-Host "Controls:" -ForegroundColor Yellow
Write-Host "- Left hand: Move cursor with index finger"
Write-Host "- Right hand: Pinch thumb+index for click"
Write-Host "- Double-click: Quick double pinch"
Write-Host "- Drag: Hold pinch for 1 second"
Write-Host ""
Write-Host "Press Ctrl+C in this window to stop the application" -ForegroundColor Red
Write-Host ""

# Check if PyQt5 is available for modern UI
try {
    python -c "import PyQt5" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
}
catch {
    Write-Host "[WARNING] PyQt5 not found, installing..." -ForegroundColor Yellow
    pip install PyQt5
}

# Launch modern app with fallback
python modern_app.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARNING] Modern app failed to start" -ForegroundColor Yellow
    Write-Host "Trying alternative launcher..."
    Write-Host ""
    if (Test-Path "launcher.py") {
        python launcher.py
    }
    else {
        Write-Host "[ERROR] No alternative launcher found" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   APPLICATION CLOSED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Thanks for using AirNav!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit"
