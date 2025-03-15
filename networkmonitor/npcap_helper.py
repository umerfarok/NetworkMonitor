"""
Helper module for Npcap initialization and configuration
This module helps ensure proper detection and configuration of Npcap for use with Scapy
"""
import os
import sys
import platform
import logging
import subprocess
import ctypes
import tempfile
from typing import Any, Dict, Optional
import requests
from pathlib import Path

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
        logger.info("Npcap initialization skipped - not on Windows")
        return True
    
    # Check if Npcap is installed
    npcap_info = get_npcap_info()
    if not npcap_info.get('installed', False):
        logger.error("Npcap is not installed")
        return False
    
    # Get Npcap directory
    npcap_dir = npcap_info.get('path')
    if not npcap_dir:
        logger.error("Could not find Npcap directory")
        return False
    
    # Add Npcap directory to PATH environment variable
    success = _add_dll_directories()
    if not success:
        logger.error("Failed to add Npcap directories to PATH")
        return False
    
    # Set specific environment variables for Scapy
    os.environ['SCAPY_USE_PCAPDNET'] = 'True'
    
    # Try to import Scapy modules to verify installation
    try:
        from scapy.all import conf
        conf.use_pcap = True
        logger.info("Scapy configured to use Npcap")
        return True
    except ImportError as e:
        logger.error(f"Failed to configure Scapy: {e}")
        return False

def _add_dll_directories() -> bool:
    """Add Npcap DLL directories to the system PATH"""
    try:
        for dll_path in DLL_PATHS:
            if os.path.exists(dll_path):
                try:
                    os.add_dll_directory(dll_path)
                    logger.debug(f"Added DLL directory: {dll_path}")
                except Exception as e:
                    logger.warning(f"Could not add DLL directory {dll_path}: {e}")
        
        # Configure PATH environment variable as well
        _configure_dll_path()
        return True
    except Exception as e:
        logger.error(f"Error adding DLL directories: {e}")
        return False

def _configure_dll_path() -> None:
    """Configure system PATH to include Npcap directories"""
    try:
        current_path = os.environ.get('PATH', '')
        npcap_paths = [p for p in DLL_PATHS if os.path.exists(p)]
        
        # Add Npcap paths to PATH if not already present
        new_paths = []
        for path in npcap_paths:
            if path not in current_path:
                new_paths.append(path)
        
        if new_paths:
            os.environ['PATH'] = os.pathsep.join([current_path] + new_paths)
            logger.debug(f"Added to PATH: {new_paths}")
    except Exception as e:
        logger.warning(f"Error configuring PATH: {e}")

def get_npcap_info() -> Dict[str, Any]:
    """
    Get information about Npcap installation
    
    Returns:
        Dict with keys:
        - installed (bool): Whether Npcap is installed
        - path (str): Path to Npcap installation directory
        - version (str): Npcap version if available
    """
    info = {
        'installed': False,
        'path': None,
        'version': None
    }
    
    # Early return if not on Windows
    if platform.system() != "Windows":
        return info
    
    # Check common installation paths
    for path in NPCAP_PATHS:
        if os.path.exists(path):
            info['installed'] = True
            info['path'] = path
            break
    
    if info['installed']:
        # Try to get version information
        try:
            wpcap_path = os.path.join(info['path'], 'wpcap.dll')
            if os.path.exists(wpcap_path):
                version_info = subprocess.check_output(['powershell', '-Command',
                    f"(Get-Item '{wpcap_path}').VersionInfo.FileVersion"
                ]).decode().strip()
                info['version'] = version_info
        except Exception as e:
            logger.warning(f"Could not get Npcap version: {e}")
    
    return info

def verify_npcap_installation() -> Dict[str, Any]:
    """
    Verify Npcap installation and provide detailed status
    
    Returns:
        Dict containing verification results:
        - installed (bool): Whether Npcap is installed
        - working (bool): Whether Npcap is working properly
        - errors (List[str]): Any error messages
        - warnings (List[str]): Any warning messages
    """
    result = {
        'installed': False,
        'working': False,
        'errors': [],
        'warnings': []
    }
    
    if platform.system() != "Windows":
        result['warnings'].append("Not running on Windows - Npcap not required")
        return result
    
    # Check installation
    npcap_info = get_npcap_info()
    result['installed'] = npcap_info['installed']
    
    if not result['installed']:
        result['errors'].append("Npcap is not installed")
        return result
    
    # Check if DLLs are accessible
    dll_found = False
    for path in DLL_PATHS:
        if os.path.exists(os.path.join(path, 'wpcap.dll')):
            dll_found = True
            break
    
    if not dll_found:
        result['errors'].append("Could not find Npcap DLLs")
        return result
    
    # Try to initialize Scapy with Npcap
    try:
        if initialize_npcap():
            result['working'] = True
        else:
            result['errors'].append("Failed to initialize Npcap with Scapy")
    except Exception as e:
        result['errors'].append(f"Error testing Npcap: {str(e)}")
    
    return result

def download_npcap_installer(output_path=None) -> Optional[str]:
    """
    Download the Npcap installer
    
    Args:
        output_path: Optional path to save the installer
        
    Returns:
        str: Path to downloaded installer, or None if download failed
    """
    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), 'npcap-installer.exe')
    
    try:
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
    logging.basicConfig(level=logging.INFO)
    if platform.system() == "Windows":
        info = get_npcap_info()
        if info['installed']:
            print(f"Npcap is installed at: {info['path']}")
            if info['version']:
                print(f"Version: {info['version']}")
        else:
            print("Npcap is not installed")
            
        verify_result = verify_npcap_installation()
        if verify_result['working']:
            print("Npcap is working correctly")
        else:
            print("Npcap verification failed:")
            for error in verify_result['errors']:
                print(f"- {error}")
    else:
        print("Not running on Windows - Npcap not required")