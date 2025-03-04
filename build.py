"""
Build script for NetworkMonitor service
Creates standalone executable for the backend service
"""
import os
import sys
import shutil
import platform
from pathlib import Path
import subprocess

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
    
    try:
        import PyInstaller
        return True
    except ImportError:
        print("\nPyInstaller not found. Please install build requirements:")
        print("pip install -r requirements-build.txt")
        return False

def get_platform_settings():
    """Get platform-specific build settings"""
    system = platform.system().lower()
    
    # Base settings common to all platforms
    settings = {
        'name': 'NetworkMonitor',
        'console': True,
        'debug': False,
        'noconfirm': True,
        'clean': True,
        'icon_path': None,
        'hiddenimports': []
    }
    
    # Platform-specific settings
    if system == 'windows':
        settings.update({
            'icon_path': 'assets/icon.ico',
            'uac_admin': True,
            'hiddenimports': ['win32com', 'win32com.shell', 'win32api', 'wmi']
        })
    elif system == 'darwin':
        settings['icon_path'] = 'assets/icon.icns'
    elif system == 'linux':
        settings['icon_path'] = 'assets/icon.ico'
    
    return settings

def create_spec_file(settings) -> bool:
    """Create PyInstaller spec file based on platform"""
    try:
        # Convert settings to spec file content
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['networkmonitor/scripts/networkmonitor_cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/*', 'assets')
    ],
    hiddenimports={settings['hiddenimports']},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False
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
    upx=False,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None"""
            
        # Add icon if available
        if settings.get('icon_path'):
            spec_content += f",\n    icon=['{settings['icon_path']}']"
            
        spec_content += "\n)"
        
        # Write spec file
        with open('NetworkMonitor.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
            
        print("Generated NetworkMonitor.spec file with platform-specific settings\n")
        return True
        
    except Exception as e:
        print(f"Error creating spec file: {e}")
        return False

def build_executable() -> bool:
    """Build the executable using PyInstaller"""
    try:
        # Clean previous build
        clean_build()
        
        # Get platform-specific settings
        settings = get_platform_settings()
        
        # Create spec file
        if not create_spec_file(settings):
            return False
        
        print("Building executable with optimized settings...")
        pyinstaller_args = [
            sys.executable,
            '-m',
            'PyInstaller',
            'NetworkMonitor.spec',
            '--noconfirm'
        ]

        result = subprocess.run(pyinstaller_args, check=True)
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller build failed with return code {e.returncode}")
        if hasattr(e, 'stderr') and e.stderr:
            print("Error output:")
            print(e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr)
        return False
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
        print("Building NetworkMonitor executable...")
        if not check_environment():
            sys.exit(1)
            
        if not build_executable():
            sys.exit(1)
            
        print("\nBuild completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)