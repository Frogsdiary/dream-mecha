@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Blockmaker Executable Builder
echo    (Now with GATE CREATOR support!)
echo ========================================
echo.

:: Check if we're in the right directory
if not exist "blockmaker_window.py" (
    echo ERROR: blockmaker_window.py not found!
    echo Please run this script from the blockmaker directory.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "..\.venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please ensure .venv directory exists in the parent directory.
    echo.
    echo To create virtual environment:
    echo cd ..
    echo python -m venv .venv
    echo .venv\Scripts\activate
    echo pip install PyQt5 pyinstaller cryptography
    pause
    exit /b 1
)

:: Activate virtual environment
echo [1/6] Activating virtual environment...
call ..\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

:: Check if PyInstaller is installed
echo [2/6] Checking PyInstaller installation...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

:: Check if PyQt5 is installed
echo [3/6] Checking PyQt5 installation...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo PyQt5 not found. Installing...
    pip install PyQt5
    if errorlevel 1 (
        echo ERROR: Failed to install PyQt5!
        pause
        exit /b 1
    )
)

:: Check if cryptography is installed (NEW)
echo [4/6] Checking cryptography installation...
python -c "import cryptography" 2>nul
if errorlevel 1 (
    echo Cryptography not found. Installing...
    pip install cryptography
    if errorlevel 1 (
        echo ERROR: Failed to install cryptography!
        echo This is required for GATE CREATOR functionality.
        pause
        exit /b 1
    )
)

:: Test GATE CREATOR functionality
echo [5/6] Testing GATE CREATOR functionality...
python -c "from gate_creator import GateCreator; print('GATE CREATOR: OK')" 2>nul
if errorlevel 1 (
    echo WARNING: GATE CREATOR module test failed!
    echo The build will continue but GATE CREATOR features may not work.
    echo.
    echo This could be due to:
    echo - Missing cryptography library
    echo - Import errors in gate_creator.py
    echo - Python path issues
    echo.
    echo Press any key to continue anyway...
    pause
) else (
    echo GATE CREATOR functionality verified!
)

:: Check for icon file (optional)
echo [6/6] Checking icon file...
if exist "..\sharkman.ico" (
    echo Icon file found: ..\sharkman.ico
    echo Note: Using default icon if sharkman.ico is not a valid ICO format
) else (
    echo No icon file found - using default application icon
)

:: Clean previous builds
echo.
echo ========================================
echo    Cleaning Previous Builds
echo ========================================
echo.

if exist "build" (
    echo Removing old build directory...
    rmdir /s /q build
)
if exist "dist" (
    echo Removing old dist directory...
    rmdir /s /q dist
)

:: Build the executable
echo.
echo ========================================
echo    Building Blockmaker Executable
echo    (with GATE CREATOR support)
echo ========================================
echo.

pyinstaller --clean Blockmaker.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed! Check the error messages above.
    echo.
    echo Common issues:
    echo - Missing dependencies: pip install PyQt5 pyinstaller cryptography
    echo - Import errors in gate_creator.py
    echo - Virtual environment not activated
    echo - Insufficient disk space
    echo.
    echo Troubleshooting:
    echo 1. Ensure all dependencies are installed
    echo 2. Check that gate_creator.py has no syntax errors
    echo 3. Verify virtual environment is working
    echo 4. Try running: python blockmaker_window.py
    echo.
    pause
    exit /b 1
)

:: Check if build was successful
if not exist "dist\Blockmaker.exe" (
    echo.
    echo ERROR: Build completed but executable not found!
    echo Check the dist directory for any output files.
    pause
    exit /b 1
)

:: Success message
echo.
echo ========================================
echo    BUILD SUCCESSFUL!
echo ========================================
echo.
echo Executable created: dist\Blockmaker.exe
echo.
echo Features included:
echo - Blockmaker pattern generation
echo - Stars and Glyph algorithms
echo - Dream Mecha integration
echo - GATE CREATOR cryptography
echo - GATE Portal functionality
echo.
echo To run the application:
echo dist\Blockmaker.exe
echo.
echo.
pause 