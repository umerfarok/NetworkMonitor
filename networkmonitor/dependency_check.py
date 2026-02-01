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
        
        # Add OS-specific checks
        os_type = platform.system()
        if os_type == "Windows":
            self.checks.append(("Npcap", self._check_npcap))
        elif os_type == "Darwin":  # macOS
            self.checks.append(("Admin Rights", self._check_admin_macos))
            self.checks.append(("pfctl", self._check_pfctl_macos))
        elif os_type == "Linux":  # Linux (Ubuntu)
            self.checks.append(("Admin Rights", self._check_admin_linux))
            self.checks.append(("iptables", self._check_iptables))
            self.checks.append(("tc", self._check_tc))
        
        # Check Python packages for all platforms
        self.checks.append(("Python Packages", self._check_python_packages))
    
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
    
    def _check_admin_macos(self):
        """Check for admin rights on macOS"""
        if platform.system() != "Darwin":
            return True, None
            
        try:
            # Check if user can run sudo
            result = subprocess.run(
                ["sudo", "-n", "true"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                return True, None
            else:
                return False, "Admin rights required. Some features will be limited."
        except:
            return False, "Could not check for admin rights."
    
    def _check_pfctl_macos(self):
        """Check if pfctl is available on macOS"""
        if platform.system() != "Darwin":
            return True, None
            
        try:
            result = subprocess.run(
                ["pfctl", "-h"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0 and result.returncode != 1:  # pfctl returns 1 for help
                return False, "pfctl not available. Required for network control features."
            return True, None
        except FileNotFoundError:
            return False, "pfctl not found. Required for network control features."
        except:
            return False, "Could not check for pfctl."
    
    def _check_admin_linux(self):
        """Check for admin (root) rights on Linux"""
        if platform.system() != "Linux":
            return True, None
            
        try:
            if os.geteuid() == 0:
                return True, None
            else:
                return False, "Root privileges required. Some features will be limited."
        except:
            return False, "Could not check for root privileges."
    
    def _check_iptables(self):
        """Check if iptables is available on Linux"""
        if platform.system() != "Linux":
            return True, None
            
        try:
            result = subprocess.run(
                ["iptables", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                return False, "iptables not available. Required for network control features."
            return True, None
        except FileNotFoundError:
            return False, "iptables not found. Required for network control features."
        except:
            return False, "Could not check for iptables."
    
    def _check_tc(self):
        """Check if tc (traffic control) is available on Linux"""
        if platform.system() != "Linux":
            return True, None
            
        try:
            result = subprocess.run(
                ["tc", "-help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0 and result.returncode != 1:  # tc returns non-zero for help
                return False, "tc (traffic control) not available. Required for bandwidth limiting."
            return True, None
        except FileNotFoundError:
            return False, "tc (traffic control) not found. Required for bandwidth limiting."
        except:
            return False, "Could not check for tc."
    
    def _check_python_packages(self):
        """Check if required Python packages are installed"""
        required_packages = {
            "scapy": "2.4.0",
            "flask": "2.0.0",
            "flask-cors": "3.0.0",
            "psutil": "5.8.0",
            "requests": "2.25.0",
            "click": "8.0.0"
        }
        
        # Add OS-specific packages
        if platform.system() == "Windows":
            required_packages.update({
                "wmi": "1.0.0",
                "pywin32": "300.0.0"
            })
        elif platform.system() == "Darwin":  # macOS
            required_packages.update({
                "netifaces": "0.10.0"
            })
        elif platform.system() == "Linux":  # Linux
            required_packages.update({
                "python-iptables": "0.14.0"
            })
        
        missing_packages = []
        
        for package, min_version in required_packages.items():
            try:
                installed_version = pkg_resources.get_distribution(package).version
                if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(min_version):
                    missing_packages.append(f"{package}>={min_version}")
            except pkg_resources.DistributionNotFound:
                missing_packages.append(f"{package}>={min_version}")
        
        if missing_packages:
            return False, "Missing packages: " + ", ".join(missing_packages)
        return True, None
    
    def get_installation_instructions(self):
        """Get detailed installation instructions for missing dependencies"""
        os_type = platform.system()
        
        instructions = {
            "Python Version": """
Python 3.9 or later is required.
Download and install from https://python.org
""",
            "Python Packages": """
Required Python packages are missing.
Run the following command to install them:
pip install -r requirements.txt
"""
        }
        
        # OS-specific instructions
        if os_type == "Windows":
            instructions.update({
                "Npcap": """
Npcap is required for network packet capture.
1. Download from https://npcap.com
2. Run the installer as administrator
3. Select "Install Npcap in WinPcap API-compatible Mode"
""",
                "Admin Rights": """
Administrator privileges are required.
Right-click the application and select "Run as administrator".
"""
            })
        elif os_type == "Darwin":  # macOS
            instructions.update({
                "Admin Rights": """
Admin rights are required for network control features.
Run the application with 'sudo' or when prompted, enter your password.
""",
                "pfctl": """
The pfctl utility is required for network control.
It should be included with macOS by default. If missing, please update your macOS.
"""
            })
        elif os_type == "Linux":  # Linux/Ubuntu
            instructions.update({
                "Admin Rights": """
Root privileges are required for network control features.
Run the application with 'sudo' or as root.
""",
                "iptables": """
iptables is required for network control.
Install it using:
sudo apt-get install iptables
""",
                "tc": """
Traffic Control (tc) is required for bandwidth limiting.
Install it using:
sudo apt-get install iproute2
"""
            })
        
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
        # Get OS-specific installation guide
        os_type = platform.system()
        if os_type == "Windows":
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
        elif os_type == "Darwin":  # macOS
            installation_guide = """
Please install the missing requirements:

1. Python 3.9 or later:
   - Download from https://python.org

2. Run with admin privileges:
   - Use 'sudo' to run the application
   - Required for network control features

3. Python packages:
   - Run: pip install -r requirements.txt

For detailed installation instructions, please refer to the documentation.
"""
        else:  # Linux/Ubuntu
            installation_guide = """
Please install the missing requirements:

1. Python 3.9 or later:
   - sudo apt-get install python3.9

2. Network tools:
   - sudo apt-get install iptables iproute2

3. Python packages:
   - Run: pip install -r requirements.txt

4. Run with root privileges:
   - Use 'sudo' to run the application
   - Required for network control features

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