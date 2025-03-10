# edcolonytracker.spec
import os
import shutil
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

# Clean up any existing build directories
for directory in ['build', 'dist']:
    if os.path.exists(directory):
        shutil.rmtree(directory)

block_cipher = None

a = Analysis(
    ['EDColonyTrackerPackage/main.py'],  # Updated path to main script
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[],  # Empty for now
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],  # Empty instead of a.binaries, a.zipfiles, a.datas
    exclude_binaries=True,  # This is critical
    name='EDColonyTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True for debugging
    # No icon for now
)

# Add this to collect the binaries separately
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EDColonyTracker'
)