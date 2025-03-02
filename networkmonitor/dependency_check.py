"""
Network Monitor Dependency Checker
"""

import sys
import platform
import subprocess
import logging
import importlib.util
import os
import ctypes
from typing import List, Dict, Tuple, Optional, Any

logger = logging.getLogger(__name__)

# Required dependencies by platform
DEPENDENCIES = {
    "common": ["flask", "click", "scapy", "psutil", "ifaddr"],
    "Windows": ["wmi", "win32com", "pywin32"],
    "Linux": ["iptc"],  # python-iptables
    "Darwin": ["netifaces"]  # For macOS
}

# Npcap paths to check on Windows
NPCAP_PATHS = [
    r"C:\Windows\System32\Npcap",
    r"C:\Program Files\Npcap",
    r"C:\Program Files (x86)\Npcap"
]


class DependencyChecker:
    """Class for checking and managing dependencies for Network Monitor"""
    
    def __init__(self):
        self.current_os = platform.system()
        self.logger = logging.getLogger(__name__)
    
    def is_admin(self) -> bool:
        """Check if the application is running with administrative privileges."""
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    def check_all_dependencies(self) -> Tuple[bool, List[str], List[str]]:
        """
        Check all dependencies and return status
        
        Returns:
            Tuple of (is_ready, missing_dependencies, warnings)
        """
        missing, warnings = self.check_dependencies()
        return len(missing) == 0, missing, warnings

    def check_dependencies(self) -> Tuple[List[str], List[str]]:
        """
        Check for required dependencies based on the platform.
        
        Returns:
            Tuple containing lists of missing dependencies and warnings
        """
        missing = []
        warnings = []
        
        # Check admin privileges
        if not self.is_admin():
            warnings.append("Network Monitor is not running with administrative privileges. Some features may not work.")
        
        # Check common dependencies
        for dep in DEPENDENCIES["common"]:
            if not importlib.util.find_spec(dep):
                missing.append(dep)

        # Check OS-specific dependencies
        if self.current_os in DEPENDENCIES:
            for dep in DEPENDENCIES[self.current_os]:
                if dep == "pywin32":
                    try:
                        import win32com
                        import win32api
                        import win32con
                    except ImportError:
                        missing.append(dep)
                else:
                    if not importlib.util.find_spec(dep):
                        missing.append(dep)

        # Special checks for Windows
        if self.current_os == "Windows":
            # Check Npcap
            npcap_status = self.check_npcap()
            if not npcap_status.get('scapy_compatible', False):
                missing.append("Npcap packet capture library")
                warning_msg = npcap_status.get('error') or "Npcap not properly configured"
                warnings.append(warning_msg)
        
        # Specific checks for Linux
        elif self.current_os == "Linux":
            # Check if we have permission to use raw sockets
            if not self.can_use_raw_sockets():
                warnings.append("Cannot use raw sockets. Some monitoring features may not work.")
        
        return missing, warnings

    def check_npcap(self) -> Dict[str, Any]:
        """
        Check Npcap installation and configuration status
        
        Returns:
            Dict containing Npcap status information
        """
        status = {
            'installed': False,
            'scapy_compatible': False,
            'path': None,
            'status': 'not_installed',
            'error': None,
            'dll_files': []
        }
        
        # Check for Npcap installation
        for path in NPCAP_PATHS:
            if os.path.exists(path):
                status['installed'] = True
                status['path'] = path
                status['status'] = 'installed'
                
                # Check for critical DLLs
                wpcap_dll = os.path.join(path, "wpcap.dll")
                packet_dll = os.path.join(path, "Packet.dll")
                
                if os.path.exists(wpcap_dll):
                    status['dll_files'].append("wpcap.dll")
                
                if os.path.exists(packet_dll):
                    status['dll_files'].append("Packet.dll")
                
                break
        
        # If installed, check Scapy compatibility
        if status['installed']:
            try:
                # First check if we can import Scapy
                import scapy.all
                
                # Try to import and use the Windows-specific module
                try:
                    from scapy.arch.windows import get_windows_if_list
                    interfaces = get_windows_if_list()
                    
                    # If we got here without an exception, Npcap is working with Scapy
                    status['scapy_compatible'] = True
                except ImportError as e:
                    status['status'] = 'import_error'
                    status['error'] = f"Scapy Windows module not available: {str(e)}"
                except Exception as e:
                    status['status'] = 'config_error'
                    status['error'] = f"Scapy cannot use Npcap: {str(e)}"
                    
            except Exception as e:
                status['error'] = f"Error checking Scapy compatibility: {str(e)}"
        
        return status

    def fix_npcap(self) -> Tuple[bool, str]:
        """
        Attempt to fix Npcap integration with Scapy
        
        Returns:
            Tuple of (success, message)
        """
        if platform.system() != "Windows":
            return False, "Npcap fix is only applicable on Windows"
        
        try:
            # Try to import the npcap_helper module
            from .npcap_helper import initialize_npcap, get_npcap_info
            
            # Run initialization
            success = initialize_npcap()
            
            if success:
                npcap_info = get_npcap_info()
                return True, f"Npcap initialized successfully: {npcap_info}"
            else:
                return False, "Failed to initialize Npcap"
        
        except Exception as e:
            return False, f"Error fixing Npcap: {str(e)}"

    def can_use_raw_sockets(self) -> bool:
        """Check if the application can use raw sockets (needed for packet capture)"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            s.close()
            return True
        except Exception:
            return False

    def get_installation_instructions(self) -> Dict[str, str]:
        """
        Get installation instructions for missing dependencies
        
        Returns:
            Dict mapping dependency name to installation instructions
        """
        return {
            "flask": "Install with: pip install flask",
            "click": "Install with: pip install click",
            "scapy": "Install with: pip install scapy",
            "psutil": "Install with: pip install psutil",
            "ifaddr": "Install with: pip install ifaddr",
            "wmi": "Install with: pip install wmi",
            "win32com": "Install with: pip install pywin32",
            "pywin32": "Install with: pip install pywin32",
            "iptc": "Install with: pip install python-iptables",
            "netifaces": "Install with: pip install netifaces",
            "Npcap packet capture library": "Download and install from https://npcap.com/#download. Be sure to check the 'Install Npcap in WinPcap API-compatible Mode' option during installation."
        }

    def check_all(self) -> Dict:
        """
        Run all dependency checks and return a detailed report
        
        Returns:
            Dict containing dependency check results
        """
        missing, warnings = self.check_dependencies()
        
        result = {
            "missingDeps": missing,
            "warnings": warnings,
            "isAdmin": self.is_admin(),
            "instructions": self.get_installation_instructions(),
        }
        
        # Add Npcap status for Windows
        if platform.system() == "Windows":
            result["npcapStatus"] = self.check_npcap()
        
        return result


# Keep the function-based API for backward compatibility
def is_admin() -> bool:
    """Check if the application is running with administrative privileges."""
    checker = DependencyChecker()
    return checker.is_admin()

def check_dependencies() -> Tuple[List[str], List[str]]:
    """Check for required dependencies based on the platform."""
    checker = DependencyChecker()
    return checker.check_dependencies()

def check_npcap() -> Dict[str, Any]:
    """Check Npcap installation and configuration status"""
    checker = DependencyChecker()
    return checker.check_npcap()

def fix_npcap() -> Tuple[bool, str]:
    """Attempt to fix Npcap integration with Scapy"""
    checker = DependencyChecker()
    return checker.fix_npcap()

def can_use_raw_sockets() -> bool:
    """Check if the application can use raw sockets"""
    checker = DependencyChecker()
    return checker.can_use_raw_sockets()

def get_missing_dependency_info() -> Dict[str, str]:
    """Get installation instructions for missing dependencies"""
    checker = DependencyChecker()
    return checker.get_installation_instructions()

def check_all() -> Dict:
    """Run all dependency checks and return a detailed report"""
    checker = DependencyChecker()
    return checker.check_all()


if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Create a checker instance
    checker = DependencyChecker()
    
    # Check dependencies
    missing, warnings = checker.check_dependencies()
    
    # Print results
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
    else:
        logger.info("All required dependencies are installed")
        
    for warning in warnings:
        logger.warning(warning)
    
    # Special checks for Windows
    if platform.system() == "Windows":
        npcap_status = checker.check_npcap()
        logger.info(f"Npcap status: {npcap_status}")