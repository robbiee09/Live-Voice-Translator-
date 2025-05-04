# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None

# Handle data files
data_files = []

# Add data folder if it exists
if os.path.exists('data'):
    data_files.append(('data', 'data'))

# Add icon file if it exists
icon_file = None
if os.path.exists('icon-resource.ico'):
    icon_file = 'icon-resource.ico'
elif os.path.exists('icon-resource.svg'):
    # Note: This won't actually convert the SVG, just uses it as a reference
    icon_file = 'icon-resource.svg'

# Create a simpler spec file with essential imports
a = Analysis(
    ['voice_translator.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'speech_recognition',
        'googletrans',
        'googletrans.client',
        'googletrans.models',
        'langdetect',
        'pyaudio',
        'sqlite3',
        'threading',
        'time',
        'os',
        'sys',
        'datetime',
        'tempfile'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Production build - no console
exe_prod = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file  # Use icon if available
)

# Debug build - with console
exe_debug = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceTranslator_Debug',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file  # Use icon if available
)