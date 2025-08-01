# Blockmaker Build Instructions

## Quick Start

### Prerequisites
- Python 3.8+ installed
- Windows 10/11
- Administrator privileges (recommended)

### Build Steps

1. **Open Command Prompt in this directory:**
   ```cmd
   cd D:\Xaryxis\blockmaker
   ```

2. **Run setup (first time only):**
   ```cmd
   setup_blockmaker.bat
   ```

3. **Build executable:**
   ```cmd
   build_blockmaker.bat
   ```

4. **Result:** `dist/Blockmaker.exe`

## What Each Script Does

- **`setup_blockmaker.bat`** - Creates virtual environment and installs dependencies
- **`build_blockmaker.bat`** - Builds the executable using PyInstaller
- **`create_icon.bat`** - Creates proper icon file from PNG image
- **`Blockmaker.spec`** - PyInstaller configuration file
- **`blockmaker_requirements.txt`** - Python package dependencies

## Troubleshooting

### Common Issues

**"Python not found"**
- Install Python and add to PATH

**"Virtual environment not found"**
- Run `setup_blockmaker.bat` first

**"Build failed"**
- Check that PyQt5 and PyInstaller are installed
- Ensure you're running from the blockmaker directory

**"Icon format error"**
- Run `create_icon.bat` to create a proper icon file
- Or the build will use the default application icon

### Manual Commands

If scripts fail, try manually:
```cmd
cd ..
python -m venv .venv
.venv\Scripts\activate
cd blockmaker
pip install PyQt5 pyinstaller
pyinstaller --clean Blockmaker.spec
```

## File Locations

- **Virtual Environment:** `../.venv/` (parent directory)
- **Executable Output:** `dist/Blockmaker.exe`
- **Build Files:** `build/` (temporary, can be deleted)

## Testing

After build, test the executable:
```cmd
dist\Blockmaker.exe
```

For detailed documentation, see `BLOCKMAKER_BUILD_GUIDE.md` 