"""
Build script for NetworkMonitor
Creates standalone executable with optimized size
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

def build_executable():
    """Build the executable using PyInstaller with size optimizations"""
    if not check_environment():
        return False
        
    # Clean previous builds
    clean_build()
    
    try:
        # Run PyInstaller using spec file
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