# Blockmaker Launcher Script
Write-Host "Starting Blockmaker..." -ForegroundColor Green
Write-Host ""

# Change to the project root directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and added to PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
$venvPath = "sharkenv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Using virtual environment..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "Virtual environment not found, using system Python..." -ForegroundColor Yellow
}

# Run the blockmaker
Write-Host "Running Blockmaker..." -ForegroundColor Green
try {
    python blockmaker\blockmaker_window.py
} catch {
    Write-Host ""
    Write-Host "ERROR: Blockmaker failed to start" -ForegroundColor Red
    Read-Host "Press Enter to exit"
} 