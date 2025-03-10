# -*- mode: python ; coding: utf-8 -*-

# edcolonytracker.spec
import os
import shutil
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

# Use simple paths without spaces to avoid common issues
work_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'pyibuild')
dist_dir = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'pyidist')

# Create directories if they don't exist
os.makedirs(work_dir, exist_ok=True)
os.makedirs(dist_dir, exist_ok=True)

block_cipher = None

a = Analysis(
    ['EDColonyTrackerPackage/main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[('EDColonyTrackerPackage/resources', 'resources')],
    hiddenimports=['pkg_resources', 'requests'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    # Use explicit work and dist paths
    workpath=work_dir,
    distpath=dist_dir
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
    exclude_binaries=True,  # Keep for one-dir mode
    name='EDColonyTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True  # Keep for debugging
)

# This is for the one-dir build mode
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
