# Blockmaker Executable Build Guide

## Overview

This guide explains how to build a standalone executable for the Blockmaker application using PyInstaller. The Blockmaker is a grid-based pattern generation tool built with PyQt5.

## Prerequisites

- **Python 3.8+** installed and in PATH
- **Windows 10/11** (scripts are designed for Windows)
- **Administrator privileges** (recommended for clean builds)

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Navigate to blockmaker directory:**
   ```cmd
   cd blockmaker
   ```

2. **Run the setup script:**
   ```cmd
   setup_blockmaker.bat
   ```
   This will:
   - Create a virtual environment (`../.venv`)
   - Install all required dependencies
   - Test the installation

3. **Build the executable:**
   ```cmd
   build_blockmaker.bat
   ```
   This will:
   - Activate the virtual environment
   - Clean previous builds
   - Create the executable using PyInstaller
   - Place the result in `dist/Blockmaker.exe`

### Option 2: Manual Setup

1. **Navigate to blockmaker directory:**
   ```cmd
   cd blockmaker
   ```

2. **Create virtual environment in parent directory:**
   ```cmd
   cd ..
   python -m venv .venv
   .venv\Scripts\activate
   cd blockmaker
   ```

3. **Install dependencies:**
   ```cmd
   pip install PyQt5 pyinstaller
   ```

4. **Build executable:**
   ```cmd
   pyinstaller --clean Blockmaker.spec
   ```

## File Structure

```
Xaryxis/
├── blockmaker/
│   ├── blockmaker_window.py    # Main application (1956 lines)
│   ├── README.md               # Application documentation
│   ├── BLOCKMAKER_EXPLANATION.md # Technical details
│   ├── Blockmaker.spec         # PyInstaller configuration
│   ├── build_blockmaker.bat    # Main build script
│   ├── setup_blockmaker.bat    # Environment setup script
│   ├── blockmaker_requirements.txt # Dependencies list
│   └── dist/                   # Output directory (created after build)
│       └── Blockmaker.exe      # Final executable
├── core/
│   └── style.py                # Required for styling (referenced in spec)
└── sharkman.ico                # Application icon (optional)
```

## Build Scripts Explained

### `setup_blockmaker.bat`
- **Purpose**: Initial environment setup
- **Actions**:
  - Checks Python installation
  - Creates virtual environment (`../.venv`)
  - Installs PyQt5 and PyInstaller
  - Tests imports and basic functionality
- **Usage**: Run once before first build

### `build_blockmaker.bat`
- **Purpose**: Creates the executable
- **Actions**:
  - Activates virtual environment
  - Checks dependencies
  - Cleans previous builds
  - Runs PyInstaller with `Blockmaker.spec`
  - Validates build success
- **Usage**: Run after setup to create executable

## PyInstaller Configuration (`Blockmaker.spec`)

```python
# Key configuration points:
a = Analysis(
    ['blockmaker_window.py'],              # Main script
    datas=[('../core/style.py', 'core')],  # Required data files
    # ... other settings
)

exe = EXE(
    # ... settings
    name='Blockmaker',           # Executable name
    console=False,               # No console window
    icon=['sharkman.ico'],       # Application icon
)
```

## Dependencies

### Required Packages
- **PyQt5**: GUI framework (QtWidgets, QtCore, QtGui)
- **PyInstaller**: Executable creation

### Standard Library (No installation needed)
- `sys`, `random`, `json`, `math`, `os`
- `datetime`, `typing`

### Data Files
- `../core/style.py`: Styling constants and themes (relative to blockmaker folder)

## Troubleshooting

### Common Issues

#### 1. "Python not found in PATH"
**Solution**: Install Python and ensure it's added to PATH during installation

#### 2. "Virtual environment activation failed"
**Solution**: 
```cmd
# Recreate virtual environment in parent directory
cd ..
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
cd blockmaker
```

#### 3. "PyQt5 installation failed"
**Solution**: 
```cmd
# Try alternative installation
pip install --upgrade pip
pip install PyQt5 --force-reinstall
```

#### 4. "Build failed with import errors"
**Solution**: 
```cmd
# Check if all dependencies are installed
pip list | findstr PyQt5
pip list | findstr PyInstaller
```

#### 5. "Executable not found after build"
**Solution**: 
- Check `dist/` directory exists
- Verify `Blockmaker.exe` was created
- Check build logs for errors

#### 6. "Missing icon file warning"
**Solution**: 
- The build script creates a placeholder icon
- Replace `sharkman.ico` with actual icon file for production

### Build Logs

If build fails, check:
1. **Console output** for error messages
2. **build/Blockmaker/** directory for detailed logs
3. **PyInstaller warnings** about missing modules

### Performance Optimization

For faster builds:
```cmd
# Use --onefile for single executable (larger but portable)
pyinstaller --onefile Blockmaker.spec

# Use --windowed to hide console completely
pyinstaller --windowed Blockmaker.spec
```

## Testing the Build

### Before Distribution
1. **Test executable functionality:**
   ```cmd
   dist\Blockmaker.exe
   ```

2. **Verify all features work:**
   - Grid interaction (click/drag)
   - Pattern generation
   - ASCII export
   - Debug logging

3. **Test on clean system:**
   - Copy `dist/Blockmaker.exe` to another computer
   - Verify it runs without Python installation

## Distribution

### Single Executable
The build creates a standalone executable that includes:
- Python runtime
- PyQt5 libraries
- All required dependencies
- Application data files

### File Size
- **Typical size**: 50-100 MB
- **Dependencies**: PyQt5 (~30MB), Python runtime (~20MB)
- **Optimization**: Use UPX compression if available

### Distribution Options
1. **Direct executable**: `dist/Blockmaker.exe`
2. **Installer**: Use tools like Inno Setup
3. **Portable**: Executable runs from any location

## Development Workflow

### Making Changes
1. Edit `blockmaker_window.py`
2. Test with: `python blockmaker_window.py`
3. Rebuild with: `build_blockmaker.bat`

### Version Management
- Update version in application code
- Rebuild executable for distribution
- Test thoroughly before release

## Advanced Configuration

### Custom PyInstaller Options
Edit `Blockmaker.spec` for:
- Additional data files
- Hidden imports
- Binary exclusions
- Icon customization

### Build Variants
```cmd
# Debug build
pyinstaller --debug Blockmaker.spec

# Optimized build
pyinstaller --optimize=2 Blockmaker.spec

# Single file build
pyinstaller --onefile Blockmaker.spec
```

## Support

For issues with:
- **Build process**: Check this guide and troubleshooting section
- **Application functionality**: See `blockmaker/README.md`
- **Technical details**: See `blockmaker/BLOCKMAKER_EXPLANATION.md`

## License

The build scripts and configuration are provided under the same license as the main project. 