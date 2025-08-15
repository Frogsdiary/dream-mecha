# -*- mode: python ; coding: utf-8 -*-

# Blockmaker with GATE CREATOR support
# Updated to include cryptography dependencies

a = Analysis(
    ['blockmaker_window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gate_creator.py', '.'),
        ('gate_portal.py', '.'),
        ('blocklock.py', '.'),
        ('icon_generator.py', '.'),
    ],
    hiddenimports=[
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.primitives.kdf',
        'cryptography.hazmat.primitives.kdf.pbkdf2',
        'cryptography.hazmat.primitives.hashes',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.default_backend',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'gate_creator',
        'gate_portal',
        'blocklock',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Blockmaker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
