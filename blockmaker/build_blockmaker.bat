@echo off
echo Building Blockmaker executable...
echo.

REM Change to the project root directory
cd /d "%~dp0.."

REM Check if PyInstaller is available
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Build the executable
echo Building executable...
pyinstaller --onefile --windowed --name "Blockmaker" --icon "sharkman.ico" --add-data "core/style.py;core" blockmaker/blockmaker_window.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo Build successful! Executable created in dist/Blockmaker.exe
echo You can now run Blockmaker.exe directly without Python installed.
pause 