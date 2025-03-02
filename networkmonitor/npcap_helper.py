"""
Helper module for Npcap initialization and configuration
This module helps ensure proper detection and configuration of Npcap for use with Scapy
"""

import os
import sys
import ctypes
import platform
import logging
import subprocess
from typing import Dict, Any, Optional, Tuple, List
import winreg

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
        logger.info("Not on Windows, Npcap initialization skipped")
        return False
    
    # Check if Npcap is installed
    npcap_info = get_npcap_info()
    if not npcap_info.get('installed', False):
        logger.error("Npcap doesn't appear to be installed")
        return False
    
    # Get Npcap directory
    npcap_dir = npcap_info.get('path')
    if not npcap_dir:
        for path in NPCAP_PATHS:
            if os.path.exists(path):
                npcap_dir = path
                break
        
        if not npcap_dir:
            logger.error("Could not find Npcap directory")
            return False
    
    # Add Npcap directory to PATH environment variable
    success = _add_dll_directories()
    
    # Set specific environment variables for Scapy
    os.environ['SCAPY_USE_PCAPDNET'] = 'True'
    
    # Try to import Scapy modules to verify installation
    try:
        # Make sure we're using the updated path
        _configure_dll_path()
        
        # Force reload scapy modules
        import importlib
        if 'scapy' in sys.modules:
            for mod in list(sys.modules.keys()):
                if mod.startswith('scapy'):
                    try:
                        importlib.reload(sys.modules[mod])
                    except:
                        pass
                        
        # Try to import critical Scapy modules
        from scapy.all import conf
        import scapy.arch.windows
        
        if hasattr(scapy.arch.windows, 'get_windows_if_list'):
            try:
                interfaces = scapy.arch.windows.get_windows_if_list()
                logger.info(f"Successfully accessed {len(interfaces)} network interfaces via Scapy/Npcap")
                return True
            except Exception as e:
                logger.error(f"Error accessing network interfaces: {e}")
                return False
        else:
            logger.error("Scapy Windows module loaded but get_windows_if_list not found")
            return False
            
    except ImportError as e:
        logger.error(f"Failed to import required Scapy modules: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Npcap initialization: {e}")
        return False

def _add_dll_directories() -> bool:
    """
    Add Npcap DLL directories to the DLL search path
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Add DLL directories to path - this is more reliable than just setting PATH
    try:
        for dll_path in DLL_PATHS:
            if os.path.exists(dll_path):
                # Use AddDllDirectory for Windows 8+ to safely add DLL search paths
                try:
                    dll_path_ptr = ctypes.c_wchar_p(dll_path)
                    # Call AddDllDirectory Windows API
                    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                    if hasattr(kernel32, 'AddDllDirectory'):
                        kernel32.AddDllDirectory(dll_path_ptr)
                        logger.info(f"Added DLL directory: {dll_path}")
                except Exception as e:
                    logger.warning(f"Error adding DLL directory {dll_path}: {e}")
                
                # Also add to PATH as a fallback
                os.environ['PATH'] = f"{dll_path};{os.environ['PATH']}"
        return True
    except Exception as e:
        logger.error(f"Error configuring DLL paths: {e}")
        return False

def _configure_dll_path() -> None:
    """Configure PATH to include Npcap directories - used by Scapy"""
    for dll_path in DLL_PATHS:
        if os.path.exists(dll_path) and dll_path not in os.environ['PATH']:
            os.environ['PATH'] = f"{dll_path};{os.environ['PATH']}"

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
            info['installed'] = True
            info['path'] = path
            
            # Check for DLL files
            wpcap_path = os.path.join(path, "wpcap.dll")
            packet_path = os.path.join(path, "Packet.dll")
            
            if os.path.exists(wpcap_path):
                info['dll_files'].append("wpcap.dll")
            if os.path.exists(packet_path):
                info['dll_files'].append("Packet.dll")
            
            break
    
    # Check registry for Npcap information
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Npcap") as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    info['registry'][name] = value
                    
                    # Get version
                    if name == "Version":
                        info['version'] = value
                        
                    i += 1
                except WindowsError:
                    break
    except WindowsError:
        pass
    
    return info

def verify_npcap_installation() -> Dict[str, Any]:
    """
    Verify Npcap installation and compatibility with Scapy
    
    Returns:
        dict: Status of Npcap installation and Scapy compatibility
    """
    info = get_npcap_info()
    status = {
        'installed': info['installed'],
        'version': info['version'],
        'path': info['path'],
        'scapy_compatible': False,
        'error': None,
        'dll_files': info['dll_files']
    }
    
    if not info['installed']:
        status['error'] = "Npcap is not installed"
        return status
    
    # Try to use Scapy with Npcap
    try:
        from scapy.all import conf
        
        # Check if scapy.arch.windows has the expected functions
        import scapy.arch.windows
        if hasattr(scapy.arch.windows, 'get_windows_if_list'):
            try:
                interfaces = scapy.arch.windows.get_windows_if_list()
                status['scapy_compatible'] = True
            except Exception as e:
                status['error'] = f"Error accessing network interfaces: {e}"
        else:
            status['error'] = "Scapy Windows module loaded but missing required functions"
            
    except ImportError as e:
        status['error'] = f"Scapy cannot use Npcap: {str(e)}"
    except Exception as e:
        status['error'] = f"Unexpected error: {str(e)}"
    
    return status

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Npcap
    success = initialize_npcap()
    if success:
        logger.info("Npcap initialized successfully")
    else:
        logger.error("Failed to initialize Npcap")
    
    # Print Npcap info
    info = get_npcap_info()
    logger.info(f"Npcap info: {info}")