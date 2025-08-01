@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Blockmaker Setup Script
echo    (with GATE CREATOR support)
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

:: Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not found!
    echo Please ensure pip is installed with Python.
    pause
    exit /b 1
)

echo [1/4] Installing core dependencies...
pip install PyQt5>=5.15.0
if errorlevel 1 (
    echo ERROR: Failed to install PyQt5!
    pause
    exit /b 1
)

echo [2/4] Installing build tools...
pip install pyinstaller>=5.0.0
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller!
    pause
    exit /b 1
)

echo [3/4] Installing cryptography for GATE CREATOR...
pip install cryptography>=3.4.0
if errorlevel 1 (
    echo ERROR: Failed to install cryptography!
    echo This is required for GATE CREATOR functionality.
    pause
    exit /b 1
)

echo [4/4] Testing GATE CREATOR functionality...
python -c "from gate_creator import GateCreator; print('GATE CREATOR: OK')" 2>nul
if errorlevel 1 (
    echo WARNING: GATE CREATOR test failed!
    echo The installation may not be complete.
    echo.
    echo Try running: python test_real_cryptography.py
    echo.
    pause
) else (
    echo GATE CREATOR functionality verified!
)

echo.
echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo Dependencies installed:
echo - PyQt5 (GUI framework)
echo - PyInstaller (executable builder)
echo - Cryptography (GATE CREATOR security)
echo.
echo To test the installation:
echo python test_real_cryptography.py
echo.
echo To run Blockmaker:
echo python blockmaker_window.py
echo.
echo To build executable:
echo build_blockmaker.bat
echo.
pause 