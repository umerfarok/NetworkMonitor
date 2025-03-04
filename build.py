"""
Build script for NetworkMonitor service
Creates standalone executable for the backend service
"""
import os
import sys
import shutil
import platform
from pathlib import Path
import PyInstaller.__main__

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")

def check_environment():
    """Check if build environment is properly configured"""
    if sys.version_info >= (3, 12):
        print("\nWARNING: You are using Python 3.12 or higher.")
        print("This version may have compatibility issues with PyInstaller.")
        print("Recommended: Use Python 3.9-3.11 for more reliable builds.")
        if input("\nContinue with build anyway? (y/n): ").lower() != 'y':
            return False
    return True

def create_spec_file():
    """Create PyInstaller spec file based on platform"""
    print("Generating platform-specific spec file...")
    
    is_windows = platform.system() == "Windows"
    is_macos = platform.system() == "Darwin"
    
    # Get absolute paths and ensure they exist
    root_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(root_dir, 'assets')
    cli_path = os.path.join(root_dir, 'networkmonitor', 'scripts', 'networkmonitor_cli.py')  # Fixed path
    
    # Verify paths exist
    if not os.path.exists(cli_path):
        print(f"Error: networkmonitor_cli.py not found at {cli_path}")
        print("Current directory:", os.getcwd())
        print("Directory contents:", os.listdir(os.path.join(root_dir, 'networkmonitor', 'scripts')))
        return False
        
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
        print(f"Created assets directory at {assets_dir}")
    
    # Common options for all platforms
    datas = [
        (os.path.join(root_dir, 'assets'), 'assets')
    ] 
    
    # Use absolute paths for icons
    icon_path = None
    if is_windows:
        icon_file = os.path.join(assets_dir, 'icon.ico')
        if os.path.exists(icon_file):
            icon_path = icon_file
    elif is_macos:
        icon_file = os.path.join(assets_dir, 'icon.icns')
        if os.path.exists(icon_file):
            icon_path = icon_file
    
    if icon_path:
        print(f"Using icon from: {icon_path}")
    else:
        print("Warning: No platform-specific icon found")
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Get absolute paths
root_dir = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    [r'{cli_path}'],  # Use raw string for Windows compatibility
    pathex=[root_dir],
    binaries=[],
    datas={datas},
    hiddenimports=['scapy.layers.all', 'engineio.async_drivers.threading'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['networkmonitor.web'],  # Exclude web frontend
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    upx=True,"""

    if icon_path:
        spec_content += f"""
    icon=[r'{icon_path}'],"""

    if is_macos:
        spec_content += """
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    info_plist={{
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.networkmonitor.app',
        'CFBundleName': 'NetworkMonitor',
        'CFBundleDisplayName': 'NetworkMonitor',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13',
        'NSHighResolutionCapable': True,
    }}
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
    icon=os.path.join(assets_dir, 'icon.icns'),
    bundle_identifier='com.networkmonitor.app',
    info_plist={{
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.networkmonitor.app',
        'CFBundleName': 'NetworkMonitor',
        'CFBundleDisplayName': 'NetworkMonitor',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13',
        'NSHighResolutionCapable': True,
    }}
)"""

    try:
        with open('NetworkMonitor.spec', 'w') as f:
            f.write(spec_content)
        print("Generated NetworkMonitor.spec file")
        return True
    except Exception as e:
        print(f"Error creating spec file: {e}")
        return False

def build_executable():
    """Build the executable using PyInstaller with size optimizations"""
    if not check_environment():
        return False
        
    # Clean previous builds
    clean_build()
    
    try:
        # Create spec file if it doesn't exist
        if not os.path.exists('NetworkMonitor.spec') and not create_spec_file():
            print("Failed to create spec file")
            return False
        
        print("\nBuilding executable with optimized settings...")
        PyInstaller.__main__.run([
            'NetworkMonitor.spec',
            '--clean',
            '--noconfirm'
        ])
        
        print("\nBuild completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError during build: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Use Python 3.9-3.11 instead of 3.12+")
        print("2. Run 'pip install -r requirements.txt' to update dependencies")
        print("3. Delete build and dist directories, then try again")
        print("4. Check if all required dependencies are installed")
        return False

if __name__ == '__main__':
    success = build_executable()
    sys.exit(0 if success else 1)