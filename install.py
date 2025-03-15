"""
Network Monitor Installation Script
This script handles installation of dependencies for Network Monitor
"""
import os
import sys
import platform
import subprocess
import logging
import tempfile
import shutil
import ctypes
import requests
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('networkmonitor_install.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def is_admin():
    """Check if script is running with admin privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        return os.geteuid() == 0
    except:
        return False

def install_bundled_npcap():
    """Install Npcap using bundled installer"""
    if platform.system() != "Windows":
        return True

    npcap_installer = Path('bundled_resources/Npcap/npcap-installer.exe')
    if not npcap_installer.exists():
        logger.error("Bundled Npcap installer not found")
        return False

    try:
        # Run installer silently with WinPcap compatibility mode
        logger.info("Installing Npcap...")
        subprocess.run([
            str(npcap_installer),
            '/S',                # Silent install
            '/npf_startup=yes',  # Start NPF service at boot
            '/winpcap_mode=yes'  # WinPcap compatibility mode
        ], check=True)
        logger.info("Npcap installed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to install Npcap: {e}")
        return False

def install_vcruntime():
    """Install Visual C++ Runtime"""
    if platform.system() != "Windows":
        return True

    vcruntime_installer = Path('bundled_resources/vcruntime/vc_redist.x64.exe')
    if not vcruntime_installer.exists():
        logger.error("VC++ Runtime installer not found")
        return False

    try:
        logger.info("Installing Visual C++ Runtime...")
        subprocess.run([
            str(vcruntime_installer),
            '/quiet',
            '/norestart'
        ], check=True)
        logger.info("Visual C++ Runtime installed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to install VC++ Runtime: {e}")
        return False

def install_python_packages():
    """Install required Python packages"""
    try:
        logger.info("Installing Python packages...")
        requirements_file = Path('requirements.txt')
        if not requirements_file.exists():
            logger.error("requirements.txt not found")
            return False

        subprocess.run([
            sys.executable,
            '-m',
            'pip',
            'install',
            '-r',
            str(requirements_file)
        ], check=True)
        logger.info("Python packages installed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to install Python packages: {e}")
        return False

def main():
    """Main installation function"""
    if not is_admin():
        logger.error("This installation requires administrator privileges")
        print("Please run this installer as administrator")
        return 1

    # Check Windows version
    if platform.system() == "Windows" and not platform.release() >= "10":
        logger.error("Windows 10 or later required")
        print("NetworkMonitor requires Windows 10 or later")
        return 1

    print("Installing NetworkMonitor components...")
    
    # Install Npcap first on Windows
    if platform.system() == "Windows":
        if not install_bundled_npcap():
            print("Failed to install Npcap")
            return 1

    # Install VC++ Runtime on Windows
    if platform.system() == "Windows":
        if not install_vcruntime():
            print("Failed to install Visual C++ Runtime")
            return 1

    # Install Python dependencies
    if not install_python_packages():
        print("Failed to install Python packages")
        return 1

    print("Installation completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())