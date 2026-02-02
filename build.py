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

def create_spec_file():
    """Create PyInstaller spec file based on platform"""
    print("Generating platform-specific spec file...")
    
    is_windows = platform.system() == "Windows"
    is_macos = platform.system() == "Darwin"
    
    # Define settings for different platforms
    settings = {
        'hiddenimports': [
            'networkmonitor',
            'networkmonitor.server',
            'networkmonitor.monitor',
            'networkmonitor.launcher',
            'networkmonitor.dependency_check',
            'networkmonitor.npcap_helper',
            'networkmonitor.windows',
            'scapy.layers.all',
            'scapy.layers.l2',
            'scapy.layers.inet',
            'engineio.async_drivers.threading',
            'flask',
            'flask.cli',
            'flask_cors',
            'werkzeug.debug',
            'werkzeug.serving',
            'click',
            'psutil',
            'wmi',
            'win32api',
            'win32com',
            'win32com.client',
            'pystray',
            'PIL',
            'PIL.Image',
        ]
    }
    
    # Common data files
    datas = [
        ('assets/*', 'assets')
    ]
    
    icon_path = 'assets/icon.ico' if is_windows else 'assets/icon.icns' if is_macos else None
    
    # Create spec file content
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
block_cipher = None

# Get absolute paths
root_dir = os.path.dirname(os.path.abspath(SPECPATH))
assets_dir = os.path.join(root_dir, 'assets')

a = Analysis(
    [os.path.join(root_dir, 'networkmonitor', '__main__.py')],
    pathex=[root_dir],
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
    strip=False,
    upx=True,"""

    if icon_path:
        spec_content += f"""
    icon=['{icon_path}'],"""

    if is_macos:
        spec_content += """
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.networkmonitor.app',
        'CFBundleName': 'NetworkMonitor',
        'CFBundleDisplayName': 'NetworkMonitor',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13',
        'NSHighResolutionCapable': True,
    }
)"""
    elif is_windows:
        spec_content += """
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    version='file_version_info.txt'
)"""
    else:  # Linux
        spec_content += """
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
)"""

    if is_macos:
        spec_content += """
app = BUNDLE(
    exe,
    name='NetworkMonitor.app',
    icon='assets/icon.icns',
    bundle_identifier='com.networkmonitor.app',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.networkmonitor.app',
        'CFBundleName': 'NetworkMonitor',
        'CFBundleDisplayName': 'NetworkMonitor',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13',
        'NSHighResolutionCapable': True,
    }
)"""

    with open('NetworkMonitor.spec', 'w') as f:
        f.write(spec_content)
    
    print("Generated NetworkMonitor.spec file")

def build_executable():
    """Build the executable using PyInstaller with size optimizations"""
    if not check_environment():
        return False
        
    # Clean previous builds
    clean_build()
    
    try:
        # Verify PyInstaller is available
        try:
            import PyInstaller.__main__
        except ImportError:
            print("Error: PyInstaller not found. Installing required build dependencies...")
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                "-r", 
                "requirements-build.txt"
            ])
            import PyInstaller.__main__
            
        # Create spec file if it doesn't exist
        if not os.path.exists('NetworkMonitor.spec'):
            create_spec_file()
        
        print("\nBuilding executable with optimized settings...")
        PyInstaller.__main__.run([
            'NetworkMonitor.spec',
            '--clean',
            '--noconfirm'
        ])
        
        print("\nBuild completed successfully!")
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