# ========================================
# AirNav v2 - PowerShell Launcher
# ========================================
# Fully automated: detects/installs Python 3.11,
# creates .venv, installs deps, downloads model,
# and launches AirNav. Works on fresh Windows 11.
# ========================================

# Set console to UTF-8 for proper character display
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "AirNav v2 Launcher"

# Always run from the script's directory
Set-Location -Path $PSScriptRoot

# Clear screen
Clear-Host

# ========================================
# Banner
# ========================================
$BannerBase64 = "CiDilojilojilojilojilojilZcg4paI4paI4pWX4paI4paI4paI4paI4paI4paI4pWXIOKWiOKWiOKWiOKVlyAgIOKWiOKWiOKVlyDilojilojilojilojilojilZcg4paI4paI4pWXICAg4paI4paI4pWXCuKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKVkeKWiOKWiOKVlOKVkOKVkOKWiOKWiOKVl+KWiOKWiOKWiOKWiOKVlyAg4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWX4paI4paI4pWRICAg4paI4paI4pWRCuKWiOKWiOKWiOKWiOKWiOKWiOKWiOKVkeKWiOKWiOKVkeKWiOKWiOKWiOKWiOKWiOKWiOKVlOKVneKWiOKWiOKVlOKWiOKWiOKVlyDilojilojilZHilojilojilojilojilojilojilojilZHilojilojilZEgICDilojilojilZEK4paI4paI4pWU4pWQ4pWQ4paI4paI4pWR4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWX4paI4paI4pWR4pWa4paI4paI4pWX4paI4paI4pWR4paI4paI4pWU4pWQ4pWQ4paI4paI4pWR4pWa4paI4paI4pWXIOKWiOKWiOKVlOKVnQrilojilojilZEgIOKWiOKWiOKVkeKWiOKWiOKVkeKWiOKWiOKVkSAg4paI4paI4pWR4paI4paI4pWRIOKVmuKWiOKWiOKWiOKWiOKVkeKWiOKWiOKVkSAg4paI4paI4pWRIOKVmuKWiOKWiOKWiOKWiOKVlOKVnSAK4pWa4pWQ4pWdICDilZrilZDilZ3ilZrilZDilZ3ilZrilZDilZ0gIOKVmuKVkOKVneKVmuKVkOKVnSAg4pWa4pWQ4pWQ4pWQ4pWd4pWa4pWQ4pWdICDilZrilZDilZ0gIOKVmuKVkOKVkOKVkOKVnSAK"

$BannerBytes = [System.Convert]::FromBase64String($BannerBase64)
$Banner = [System.Text.Encoding]::UTF8.GetString($BannerBytes)

Write-Host ""
Write-Host ""

foreach ($line in $Banner -split "`n") {
    Write-Host "           " -NoNewline
    foreach ($char in $line.ToCharArray()) {
        $val = [int]$char
        if ($val -eq 9608) {
            Write-Host $char -ForegroundColor Red -NoNewline
        }
        elseif ($val -ge 9550 -and $val -le 9580) {
            Write-Host $char -ForegroundColor Cyan -NoNewline
        }
        else {
            Write-Host $char -ForegroundColor DarkGray -NoNewline
        }
    }
    Write-Host ""
}

Write-Host ""
Write-Host "              Face Recognition + Hand Gesture Control System" -ForegroundColor Yellow
Write-Host "                                v2.0.0" -ForegroundColor DarkGray
Write-Host ""
Write-Host ""

# ========================================
# STEP 1: Find or install Python 3.11
# ========================================
$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$PythonCmd = $null

# 1a) Check if .venv already exists with Python 3.11
if (Test-Path $VenvPython) {
    $venvVer = & $VenvPython --version 2>&1
    if ($venvVer -match "3\.11") {
        $PythonCmd = $VenvPython
        Write-Host "[OK] Python 3.11 found in .venv" -ForegroundColor Green
    }
}

# 1b) Search common Python 3.11 locations
if (-not $PythonCmd) {
    $searchPaths = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
        "C:\Python311\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files (x86)\Python311\python.exe"
    )

    foreach ($path in $searchPaths) {
        if (Test-Path $path) {
            $ver = & $path --version 2>&1
            if ($ver -match "3\.11") {
                $PythonCmd = $path
                Write-Host "[OK] $ver found at $path" -ForegroundColor Green
                break
            }
        }
    }
}

# 1c) Try py launcher for 3.11
if (-not $PythonCmd) {
    try {
        $ver = py -3.11 --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $ver -match "3\.11") {
            # Get the actual path from py launcher
            $pyPath = py -3.11 -c "import sys; print(sys.executable)" 2>&1
            if ($LASTEXITCODE -eq 0 -and (Test-Path $pyPath)) {
                $PythonCmd = $pyPath
            } else {
                $PythonCmd = "py"  # fallback to using py command
            }
            Write-Host "[OK] $ver found via Python Launcher" -ForegroundColor Green
        }
    }
    catch {
        # py launcher not available
    }
}

# 1d) Python 3.11 not found — auto-install via winget
if (-not $PythonCmd) {
    Write-Host "[INFO] Python 3.11 not found on this system." -ForegroundColor Yellow
    Write-Host ""

    # Check if winget is available
    $hasWinget = $false
    try {
        winget --version 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $hasWinget = $true }
    }
    catch {}

    if ($hasWinget) {
        Write-Host "[INFO] Installing Python 3.11 via winget (this may take a minute)..." -ForegroundColor Cyan
        Write-Host ""
        winget install -e --id Python.Python.3.11 -h --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Failed to install Python 3.11 via winget." -ForegroundColor Red
            Write-Host "Please install Python 3.11 manually from: https://www.python.org/downloads/release/python-3119/" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }

        # Refresh PATH so we can find the newly installed Python
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

        # Find the freshly installed Python 3.11
        $freshPaths = @(
            (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"),
            "C:\Python311\python.exe",
            "C:\Program Files\Python311\python.exe"
        )
        foreach ($path in $freshPaths) {
            if (Test-Path $path) {
                $PythonCmd = $path
                break
            }
        }

        if (-not $PythonCmd) {
            # Try py launcher after install
            try {
                $ver = py -3.11 --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $pyPath = py -3.11 -c "import sys; print(sys.executable)" 2>&1
                    if (Test-Path $pyPath) { $PythonCmd = $pyPath }
                }
            }
            catch {}
        }

        if ($PythonCmd) {
            $ver = & $PythonCmd --version 2>&1
            Write-Host "[OK] $ver installed successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "[ERROR] Python 3.11 was installed but could not be located." -ForegroundColor Red
            Write-Host "Please restart your terminal and run start.bat again." -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    else {
        # No winget — manual install required
        Write-Host "[ERROR] Python 3.11 is required but not found, and winget is not available." -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Python 3.11 manually:" -ForegroundColor Yellow
        Write-Host "  https://www.python.org/downloads/release/python-3119/" -ForegroundColor White
        Write-Host ""
        Write-Host "During installation, check 'Add Python to PATH'." -ForegroundColor White
        Write-Host "After installation, run this script again." -ForegroundColor White
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""

# ========================================
# STEP 2: Create / activate virtual environment
# ========================================
$venvPath = ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "[INFO] Virtual environment detected" -ForegroundColor Cyan
    Write-Host "Activating virtual environment..."
    try {
        & $venvPath
        $PythonCmd = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
        Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
    }
    catch {
        Write-Host "[WARNING] Failed to activate virtual environment" -ForegroundColor Yellow
    }
    Write-Host ""
}
else {
    Write-Host "[INFO] Creating virtual environment with Python 3.11..." -ForegroundColor Cyan
    try {
        & $PythonCmd -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
        & $venvPath
        $PythonCmd = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
        Write-Host "[OK] Virtual environment created and activated" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Failed to create virtual environment." -ForegroundColor Red
        Write-Host "Try manually: $PythonCmd -m venv .venv"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
}

# ========================================
# STEP 3: Validate required files
# ========================================
$requiredFiles = @("requirements.txt", "modern_app.py")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "[ERROR] $file not found!" -ForegroundColor Red
        Write-Host "Please ensure you are running this from the AirNav directory."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ========================================
# STEP 4: Download model if missing
# ========================================
$modelPath = Join-Path $PSScriptRoot "models\hand_landmarker.task"
if (-not (Test-Path $modelPath)) {
    Write-Host "[INFO] Downloading MediaPipe hand_landmarker model..." -ForegroundColor Cyan
    $modelDir = Join-Path $PSScriptRoot "models"
    if (-not (Test-Path $modelDir)) {
        New-Item -ItemType Directory -Path $modelDir -Force | Out-Null
    }
    try {
        $modelUrl = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        Invoke-WebRequest -Uri $modelUrl -OutFile $modelPath -UseBasicParsing
        if (Test-Path $modelPath) {
            Write-Host "[OK] Model downloaded successfully" -ForegroundColor Green
        }
        else {
            throw "Download completed but file not found"
        }
    }
    catch {
        Write-Host "[ERROR] Failed to download hand_landmarker.task model." -ForegroundColor Red
        Write-Host "Please download manually from:" -ForegroundColor Yellow
        Write-Host "  https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -ForegroundColor White
        Write-Host "Place it in: models\hand_landmarker.task" -ForegroundColor White
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
}

# ========================================
# STEP 5: Install dependencies
# ========================================
Write-Host "Checking dependencies..."
try {
    & $PythonCmd -c "import cv2, mediapipe, numpy, pynput" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "[OK] All dependencies are installed" -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "[WARNING] Some dependencies are missing!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installing required packages (this may take a few minutes)..."
    & $PythonCmd -m pip install --upgrade pip 2>&1 | Out-Null
    & $PythonCmd -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
        Write-Host "Please run manually: .venv\Scripts\pip install -r requirements.txt"
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# ========================================
# STEP 6: Check PyQt5
# ========================================
try {
    & $PythonCmd -c "import PyQt5" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
}
catch {
    Write-Host "[WARNING] PyQt5 not found, installing..." -ForegroundColor Yellow
    & $PythonCmd -m pip install PyQt5
}

# ========================================
# STEP 7: Launch AirNav
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   STARTING AIRNAV v2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Controls:" -ForegroundColor Yellow
Write-Host "- Left hand: Move cursor with index finger"
Write-Host "- Right hand: Pinch thumb+index for click"
Write-Host "- Double-click: Quick double pinch"
Write-Host "- Drag: Hold pinch for 1 second"
Write-Host ""
Write-Host "Press Ctrl+C in this window to stop the application" -ForegroundColor Red
Write-Host ""

# Launch modern app with fallback
& $PythonCmd modern_app.py
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[WARNING] Modern app failed to start" -ForegroundColor Yellow
    Write-Host "Trying alternative launcher..."
    Write-Host ""
    if (Test-Path "launcher.py") {
        & $PythonCmd launcher.py
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
