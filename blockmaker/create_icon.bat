@echo off
echo ========================================
echo    Blockmaker Icon Creator
echo ========================================
echo.

echo This script helps create a proper icon file for Blockmaker.
echo.
echo Requirements:
echo - A PNG image file (recommended: 256x256 pixels)
echo - Pillow library installed (pip install Pillow)
echo.

:: Check if Pillow is installed
python -c "from PIL import Image" 2>nul
if errorlevel 1 (
    echo ERROR: Pillow not found!
    echo Installing Pillow...
    pip install Pillow
    if errorlevel 1 (
        echo ERROR: Failed to install Pillow!
        pause
        exit /b 1
    )
)

echo.
echo To create an icon:
echo 1. Place a PNG image file in this directory
echo 2. Rename it to 'icon.png'
echo 3. Run this script again
echo.

if exist "icon.png" (
    echo Found icon.png - converting to ICO format...
    python -c "
from PIL import Image
import os

try:
    # Open the PNG image
    img = Image.open('icon.png')
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Create icon sizes (Windows standard)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Save as ICO
    img.save('../sharkman.ico', format='ICO', sizes=sizes)
    print('Icon created successfully: ../sharkman.ico')
    
except Exception as e:
    print(f'Error creating icon: {e}')
    print('Make sure icon.png is a valid image file.')
"
    
    if errorlevel 1 (
        echo ERROR: Failed to create icon!
        pause
        exit /b 1
    )
    
    echo.
    echo Icon created successfully!
    echo You can now run build_blockmaker.bat to create the executable with the icon.
    
) else (
    echo No icon.png found.
    echo.
    echo Instructions:
    echo 1. Create or find a PNG image (256x256 pixels recommended)
    echo 2. Save it as 'icon.png' in this directory
    echo 3. Run this script again
    echo.
    echo Example icon.png sources:
    echo - Create a simple icon in any image editor
    echo - Download a free icon from icon websites
    echo - Convert an existing image to PNG format
)

echo.
pause 