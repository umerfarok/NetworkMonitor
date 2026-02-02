# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for NetworkMonitor
"""
import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect all scapy layers
scapy_hiddenimports = collect_submodules('scapy.layers')

a = Analysis(
    ['networkmonitor/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
    ],
    hiddenimports=[
        'networkmonitor',
        'networkmonitor.server',
        'networkmonitor.monitor',
        'networkmonitor.launcher',
        'networkmonitor.dependency_check',
        'networkmonitor.npcap_helper',
        'networkmonitor.windows',
        'flask',
        'flask.cli',
        'flask_cors',
        'click',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.debug',
        'jinja2',
        'scapy',
        'scapy.all',
        'scapy.layers.l2',
        'scapy.layers.inet',
        'psutil',
        'requests',
        'wmi',
        'win32api',
        'win32com',
        'win32com.client',
        'win32com.shell',
        'pystray',
        'PIL',
        'PIL.Image',
        'engineio.async_drivers.threading',
    ] + scapy_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NetworkMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    uac_admin=True,
    version='file_version_info.txt',
)