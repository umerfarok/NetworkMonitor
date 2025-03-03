"""
Helper module for Npcap initialization and configuration
This module helps ensure proper detection and configuration of Npcap for use with Scapy
"""
import os
import sys
import platform
import logging
import subprocess
import winreg
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)

# Npcap default paths
NPCAP_PATHS = [
    r"C:\Windows\System32\Npcap",
    r"C:\Program Files\Npcap",
    r"C:\Program Files (x86)\Npcap"
]

# DLL paths to try adding to system PATH
DLL_PATHS = [
    r"C:\Windows\System32\Npcap",
    r"C:\Windows\SysWOW64\Npcap",
    r"C:\Program Files\Npcap",
    r"C:\Program Files (x86)\Npcap",
    r"C:\Program Files\Npcap\Win10pcap"
]

# Npcap installer URL
NPCAP_INSTALLER_URL = "https://npcap.com/dist/npcap-1.71.exe"

def initialize_npcap() -> bool:
    """
    Initialize Npcap for use with Scapy by:
    1. Checking if Npcap is installed
    2. Adding Npcap directories to PATH
    3. Setting environment variables for Scapy
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    logger.info("Initializing Npcap...")
    
    if platform.system() != "Windows":
        logger.info("Not running on Windows, skipping Npcap initialization")
        return True
    
    # Check if Npcap is installed
    npcap_info = get_npcap_info()
    if not npcap_info.get('installed', False):
        logger.error("Npcap is not installed. Network monitoring will not work properly.")
        logger.info("Download and install Npcap from https://npcap.com/")
        return False
    
    # Get Npcap directory
    npcap_dir = npcap_info.get('path')
    if not npcap_dir:
        logger.error("Could not find Npcap installation directory")
        return False
    
    # Add Npcap directory to PATH environment variable
    success = _add_dll_directories()
    
    # Set specific environment variables for Scapy
    os.environ['SCAPY_USE_PCAPDNET'] = 'True'
    
    # Try to import Scapy modules to verify installation
    try:
        from scapy.arch import get_if_hwaddr
        from scapy.layers.l2 import arping
        from scapy.sendrecv import srloop
        logger.info("Scapy import successful: Npcap is correctly configured")
        return True
    except ImportError as e:
        logger.error(f"Failed to import Scapy modules: {e}")
        logger.error("Try reinstalling Npcap and check if WinPcap is also installed (they might conflict)")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Scapy import: {e}")
        return False

def _add_dll_directories() -> bool:
    """
    Add Npcap DLL directories to the DLL search path
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Add DLL directories to path - this is more reliable than just setting PATH
    try:
        # Configure PATH environment variable
        _configure_dll_path()
        
        # Use AddDllDirectory API on Windows 8+
        if hasattr(os, 'add_dll_directory'):
            for path in DLL_PATHS:
                if os.path.exists(path):
                    try:
                        os.add_dll_directory(path)
                        logger.info(f"Added DLL directory: {path}")
                    except Exception as e:
                        logger.warning(f"Failed to add DLL directory {path}: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error configuring DLL directories: {e}")
        return False

def _configure_dll_path() -> None:
    """Configure PATH to include Npcap directories - used by Scapy"""
    for dll_path in DLL_PATHS:
        if os.path.exists(dll_path) and dll_path not in os.environ['PATH']:
            os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']
            logger.info(f"Added to PATH: {dll_path}")

def get_npcap_info() -> Dict[str, Any]:
    """
    Get detailed information about Npcap installation
    
    Returns:
        dict: Information about Npcap installation
    """
    info = {
        'installed': False,
        'version': None,
        'path': None,
        'dll_files': [],
        'registry': {}
    }
    
    # Check common installation paths
    for path in NPCAP_PATHS:
        if os.path.exists(path):
            info['path'] = path
            info['installed'] = True
            
            # Look for DLL files
            if os.path.exists(path):
                files = os.listdir(path)
                info['dll_files'] = [f for f in files if f.lower().endswith('.dll')]
            
            break
    
    # Check registry for Npcap information
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Npcap') as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    info['registry'][name] = value
                    if name == 'Version':
                        info['version'] = value
                    i += 1
                except WindowsError:
                    break
    except WindowsError:
        logger.debug("Could not find Npcap registry entries")
    
    return info

def verify_npcap_installation() -> Dict[str, Any]:
    """
    Verify Npcap installation and compatibility with Scapy
    
    Returns:
        dict: Status of Npcap installation and Scapy compatibility
    """
    result = {
        'installed': False,
        'compatible': False,
        'version': None,
        'issues': [],
        'npcap_dir': None
    }
    
    # Get installation info
    info = get_npcap_info()
    result['installed'] = info['installed']
    result['version'] = info['version']
    result['npcap_dir'] = info['path']
    
    if not info['installed']:
        result['issues'].append("Npcap is not installed")
        return result
    
    # Check for npcap.dll
    if info['path'] and os.path.exists(os.path.join(info['path'], 'npcap.dll')):
        result['compatible'] = True
    else:
        result['issues'].append("Could not find npcap.dll")
    
    # Check if Scapy can use Npcap
    try:
        import scapy.all
        from scapy.arch.windows import get_windows_if_list
        
        # Try to get interfaces
        interfaces = get_windows_if_list()
        if interfaces:
            result['compatible'] = True
        else:
            result['issues'].append("No network interfaces found using Scapy")
    except ImportError:
        result['issues'].append("Could not import Scapy")
    except Exception as e:
        result['issues'].append(f"Error testing Scapy compatibility: {e}")
        
    return result

def download_npcap_installer(output_path=None) -> Optional[str]:
    """
    Download Npcap installer
    
    Args:
        output_path (str, optional): Path to save the installer to. 
                                      If None, saves to current directory.
    
    Returns:
        Optional[str]: Path to downloaded file or None if download failed
    """
    if output_path is None:
        output_path = "npcap-installer.exe"
    
    try:
        import requests
        
        logger.info(f"Downloading Npcap installer from {NPCAP_INSTALLER_URL}")
        response = requests.get(NPCAP_INSTALLER_URL, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Npcap installer downloaded to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to download Npcap installer: {e}")
        return None

if __name__ == "__main__":
    # Setup basic logging when run directly
    logging.basicConfig(level=logging.INFO)
    
    # Test Npcap initialization
    success = initialize_npcap()
    if success:
        print("Npcap initialization successful!")
    else:
        print("Npcap initialization failed. See logs for details.")
    
    # Get detailed information
    info = get_npcap_info()
    print(f"\nNpcap Info:")
    print(f"Installed: {info['installed']}")
    print(f"Version: {info['version']}")
    print(f"Path: {info['path']}")
    print(f"DLL files: {', '.join(info['dll_files'])}")