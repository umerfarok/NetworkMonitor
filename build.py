"""
Build script for NetworkMonitor service
Creates standalone executable for the backend service
"""
import os
import sys
import shutil
import platform
from pathlib import Path
from typing import Dict, List, Tuple

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        try:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
        except Exception as e:
            print(f"Error cleaning {dir_name}: {e}")

def check_environment() -> bool:
    """Check if build environment is properly configured"""
    if sys.version_info >= (3, 12):
        print("Warning: Python 3.12+ might have compatibility issues. Using 3.9-3.11 is recommended.")
    
    required_modules = ['PyInstaller', 'Flask', 'click', 'scapy']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
            
    if missing_modules:
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        return False
        
    return True

def get_platform_settings() -> Tuple[str, Dict]:
    """Get platform-specific build settings"""
    system = platform.system().lower()
    
    # Base settings common to all platforms
    base_settings = {
        'name': 'NetworkMonitor',
        'console': True,
        'debug': False,
        'noconfirm': True,
        'strip': True,
        'clean': True
    }
    
    # Platform-specific settings
    if system == 'windows':
        icon_file = 'assets/icon.ico'
        base_settings.update({
            'uac_admin': True,
            'win_private_assemblies': True,
            'win_no_prefer_redirects': True,
            'hiddenimports': ['win32com', 'win32com.shell', 'win32api', 'wmi']
        })
    elif system == 'darwin':
        icon_file = 'assets/icon.icns'
        base_settings['hiddenimports'] = ['pkg_resources.py2_warn']
    else:  # Linux
        icon_file = 'assets/icon.ico'  # Use .ico for Linux as well
        base_settings['hiddenimports'] = ['pkg_resources.py2_warn']
    
    return icon_file, base_settings

def create_spec_file() -> bool:
    """Create PyInstaller spec file based on platform"""
    try:
        # Get platform-specific settings
        icon_file, settings = get_platform_settings()
        
        if not os.path.exists(icon_file):
            print(f"Warning: Icon file not found at {icon_file}")
            icon_file = None
        
        # Convert settings to spec file content
        spec_content = """# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

datas = [
    ('assets/*', 'assets'),
    ('networkmonitor/web/build/*', 'web/build')
]

a = Analysis(
    ['networkmonitor/scripts/networkmonitor_cli.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports={hiddenimports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects={win_no_prefer_redirects},
    win_private_assemblies={win_private_assemblies},
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{name}',
    debug={debug},
    strip={strip},
    upx=True,
    runtime_tmpdir=None,
    console={console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,""".format(
            name=settings['name'],
            hiddenimports=settings.get('hiddenimports', []),
            win_no_prefer_redirects=settings.get('win_no_prefer_redirects', False),
            win_private_assemblies=settings.get('win_private_assemblies', False),
            debug=settings['debug'],
            strip=settings['strip'],
            console=settings['console']
        )
        
        # Add icon if available
        if icon_file:
            spec_content += f"\n    icon=['{icon_file}'],"
            
        spec_content += "\n)"
        
        # Write spec file
        with open('NetworkMonitor.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
            
        print("Generated NetworkMonitor.spec file\n")
        return True
        
    except Exception as e:
        print(f"Error creating spec file: {e}")
        return False

def build_executable() -> bool:
    """Build the executable using PyInstaller"""
    try:
        import PyInstaller.__main__
        
        # Clean previous build
        clean_build()
        
        # Create spec file
        if not create_spec_file():
            return False
            
        # Build with optimized settings
        print("Building executable with optimized settings...")
        PyInstaller.__main__.run([
            'NetworkMonitor.spec',
            '--noconfirm',
            '--clean',
            '--strip'
        ])
        
        return True
        
    except Exception as e:
        print(f"Error during build: {e}")
        print("\nTroubleshooting tips:")
        print("1. Use Python 3.9-3.11 instead of 3.12+")
        print("2. Run 'pip install -r requirements.txt' to update dependencies")
        print("3. Delete build and dist directories, then try again")
        print("4. Check if all required dependencies are installed")
        return False

if __name__ == '__main__':
    try:
        if not check_environment():
            sys.exit(1)
            
        if not build_executable():
            sys.exit(1)
            
        print("\nBuild completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)