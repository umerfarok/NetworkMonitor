"""Dependency checking module for NetworkMonitor"""
import os
import sys
import logging
import subprocess
import pkg_resources
import platform

logger = logging.getLogger(__name__)

class DependencyChecker:
    """Class for checking and managing NetworkMonitor dependencies"""
    
    def __init__(self):
        """Initialize the dependency checker"""
        self.checks = [
            ("Python Version", self._check_python_version),
        ]
        
        if platform.system() == "Windows":
            self.checks.append(("Npcap", self._check_npcap))
        
    
    def check_all_dependencies(self):
        """
        Check all dependencies and return status
        
        Returns:
            Tuple[bool, List[str], List[str]]: (passed, missing_deps, warnings)
        """
        all_passed = True
        missing_deps = []
        warnings = []
        
        for name, check_func in self.checks:
            passed, message = check_func()
            if not passed:
                all_passed = False
                missing_deps.append(f"{name}: {message}")
                logger.error(f"Dependency check failed - {name}: {message}")
            else:
                logger.info(f"Dependency check passed - {name}")
        
        return all_passed, missing_deps, warnings
    
    def _check_python_version(self):
        """Check if Python version meets requirements"""
        required_version = (3, 9)
        current_version = sys.version_info[:2]
        
        if current_version < required_version:
            return False, f"Python {required_version[0]}.{required_version[1]} or higher required (current: {current_version[0]}.{current_version[1]})"
        return True, None
    
    def _check_npcap(self):
        """Check if Npcap is installed (Windows only)"""
        if platform.system() != "Windows":
            return True, None
            
        # Check for Npcap installation
        npcap_paths = [
            "C:\\Windows\\System32\\Npcap",
            "C:\\Program Files\\Npcap",
            "C:\\Program Files (x86)\\Npcap"
        ]
        
        for path in npcap_paths:
            if os.path.exists(path):
                return True, None
                
        return False, "Npcap is not installed. Please download and install from https://npcap.com"
    
    
    def get_installation_instructions(self):
        """Get detailed installation instructions for missing dependencies"""
        instructions = {
            "Python Version": """
Python 3.9 or later is required.
Download and install from https://python.org
""",
            "Npcap": """
Npcap is required for network packet capture.
1. Download from https://npcap.com
2. Run the installer as administrator
3. Select "Install Npcap in WinPcap API-compatible Mode"
""",
            "Python Packages": """
Required Python packages are missing.
Run the following command to install them:
pip install -r requirements.txt
"""
        }
        return instructions

# For backwards compatibility, keep the standalone functions
def check_python_version():
    """Check if Python version meets requirements"""
    return DependencyChecker()._check_python_version()

def check_npcap():
    """Check if Npcap is installed (Windows only)"""
    return DependencyChecker()._check_npcap()


def check_system_requirements():
    """Check system requirements and dependencies"""
    checker = DependencyChecker()
    all_passed, missing_deps, _ = checker.check_all_dependencies()
    
    message = ""
    if not all_passed:
        installation_guide = """
Please install the missing requirements:

1. Python 3.9 or later:
   - Download from https://python.org

2. Npcap (Windows only):
   - Download from https://npcap.com
   - Install with "WinPcap API-compatible Mode" option

3. Python packages:
   - Run: pip install -r requirements.txt

For detailed installation instructions, please refer to the documentation.
"""
        message = "\n".join(missing_deps) + "\n" + installation_guide
    
    return all_passed, message

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    passed, message = check_system_requirements()
    if not passed:
        print(message)
        sys.exit(1)
    print("All dependency checks passed!")